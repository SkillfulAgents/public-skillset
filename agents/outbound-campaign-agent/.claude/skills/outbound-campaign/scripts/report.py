#!/usr/bin/env python3
"""Campaign metrics, and the dashboard payload built from them.

  uv run --with pyyaml report.py [--window week|month|quarter]
      [--group-by icp_tier] [--json] [--write-dashboard]

Three rules this file exists to enforce, because every one of them has been
broken by a hand-rolled outbound report before:

  1. No rate without its denominator. Every ratio here is a `Rate`, which
     carries num/den and refuses to render a percentage when den is below
     `reporting.n_floor`. A "50% reply rate" off 2 sends is noise presented as
     signal, and operators act on it.
  2. Every division is guarded. A zero denominator yields None, never a
     ZeroDivisionError and never NaN in the JSON.
  3. Opens are not computed, anywhere. `reporting.track_opens` is false by
     design: the pixel costs more deliverability than the number is worth. If
     you are about to add an `opens` field, the answer is no.

Meetings come from the `meetings` table, which the calendar sync owns, and not
from flags on `replies`. The reply flags undercount badly: the common path is a
prospect clicking a booking link and never writing back, which produces a
calendar event and no reply row at all. When the table is absent the legacy
reply-flag path still runs so the report never dies mid-migration, but wherever
the table exists it is authoritative.

`held` here means scheduled and not cancelled. It does NOT mean attendance was
confirmed: a calendar cannot prove someone showed up, and a held count read as
attendance is the single easiest way to make a program look healthier than it
is. Every surface that prints the number carries that qualifier.

A/B significance uses a two-proportion z-test (pooled SE, two-tailed):
  Significant  p < 0.05  AND both arms >= n_floor sends
  Trending     p < 0.20  AND both arms >= n_floor sends
  Directional  anything else with sends in both arms
The n_floor precondition is not optional. At 12 sends per arm a p < 0.05 is
mostly luck, so the label stays Directional no matter what the p-value says.
`sends_to_significance` is the additional sends per arm needed to reach
alpha=0.05 at 80% power for the effect size currently observed.

Windows are trailing periods ending now: week=7d, month=30d, quarter=90d.
Trailing beats calendar here because the question is always "how are we doing
lately", not "how did October close".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import pathlib
import sqlite3
import sys
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import config as cfgmod, db  # noqa: E402

WINDOW_DAYS = {"week": 7, "month": 30, "quarter": 90}
COHORT_WEEKS = 12
SERIES_DAYS = 30

# A cancelled meeting was not a meeting. Everything else that reached the
# calendar counts as booked, including a no_show: the send earned the booking.
MEETING_COUNTED = ("booked", "held", "no_show")
MEETING_SOURCES = ("calendar", "reply", "manual")
UPCOMING_LIMIT = 20

# Printed next to every held count, on every surface. See the module docstring.
HELD_NOTE = ("held means scheduled and not cancelled, not confirmed attendance: "
             "a calendar cannot prove someone showed up")

# Title -> cluster. A heuristic, not a taxonomy: it exists so "VP Sales" and
# "Head of Sales" land in the same row instead of two rows of one.
TITLE_CLUSTERS = [
    ("exec", ("ceo", "chief executive", "chief operating", "founder", "co-founder",
              "president", "owner", "coo", "chief of staff")),
    ("ops", ("operations", "ops", "revops", "rev ops")),
    ("sales", ("sales", "revenue", "account executive", "business development")),
    ("marketing", ("marketing", "demand", "growth", "brand")),
    ("finance", ("finance", "controller", "accounting", "cfo", "chief financial")),
    ("people", ("people", "talent", "recruit", "hr", "human resources")),
    ("product", ("product", "design")),
    ("engineering", ("engineer", "technology", "cto", "technical")),
]


@dataclass(frozen=True)
class Rate:
    """A ratio that will not render as a percentage without enough denominator.

    `floor` is `reporting.n_floor`. Below it the consumer shows `num` as a raw
    count. `value` is None when den is 0, which is what makes every division in
    this file safe by construction.
    """
    num: int
    den: int
    floor: int

    @property
    def value(self) -> float | None:
        return (self.num / self.den) if self.den > 0 else None

    @property
    def reliable(self) -> bool:
        return self.den >= self.floor

    def to_dict(self) -> dict:
        return {"value": self.value, "n": self.num, "d": self.den,
                "reliable": self.reliable, "floor": self.floor}

    def text(self) -> str:
        if self.den <= 0:
            return f"n/a  ({self.num} of 0)"
        if not self.reliable:
            return f"{self.num} of {self.den}  (n<{self.floor}, rate suppressed)"
        return f"{self.value:.1%}  ({self.num}/{self.den})"


@dataclass
class Segment:
    """One group-by dimension, already bucketed. `display` is a hint, not CSS."""
    key: str
    title: str
    column: str
    display: str
    rows: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"key": self.key, "title": self.title, "column": self.column,
                "display": self.display, "rows": self.rows}


@dataclass
class WindowReport:
    key: str
    label: str
    start: str
    end: str
    totals: dict
    rates: dict
    kpis: list
    meetings: dict
    deliverability: dict
    funnel: list
    sentiment: list
    ab_test: dict
    segments: list

    def to_dict(self) -> dict:
        return {
            "key": self.key, "label": self.label, "start": self.start, "end": self.end,
            "totals": self.totals,
            "rates": {k: v.to_dict() for k, v in self.rates.items()},
            "kpis": self.kpis,
            "meetings": self.meetings,
            "deliverability": self.deliverability,
            "funnel": self.funnel,
            "sentiment": self.sentiment,
            "ab_test": self.ab_test,
            "segments": [s.to_dict() for s in self.segments],
        }


# -- loading ---------------------------------------------------------------

def _rows(conn) -> tuple[list[dict], list[dict]]:
    """All email sends joined to their prospect, and all replies. Unwindowed.

    Loaded whole because reply attribution needs sends from before the window
    boundary: a reply inside the window may answer a send just outside it.
    """
    sends = [dict(r) for r in conn.execute(
        "SELECT s.id, s.prospect_id, s.step_index, s.channel, s.variant, s.sender_id,"
        "       s.bounced, s.sent_at,"
        "       p.icp_tier, p.industry, p.title, p.buyer_tier, p.company_domain"
        "  FROM sends s JOIN prospects p ON p.id = s.prospect_id"
        " ORDER BY s.sent_at"
    )]
    replies = [dict(r) for r in conn.execute(
        "SELECT id, prospect_id, replied_at, sentiment, is_positive, meeting_booked,"
        "       meeting_held, is_opportunity FROM replies ORDER BY replied_at"
    )]
    return sends, replies


def _meeting_rows(conn) -> list[dict] | None:
    """Every meeting joined to its prospect, or None when the table is absent.

    The calendar sync owns this table. A workspace that has not run the
    migration yet gets None and falls back to the legacy reply flags, because a
    report that crashes mid-migration is worse than one that undercounts and
    says so. `prospect_id` is nullable, hence the LEFT JOIN: a calendar event
    that could not be matched to anyone is still a meeting that happened.
    """
    try:
        return [dict(r) for r in conn.execute(
            "SELECT m.id, m.prospect_id, m.sender_id, m.provider, m.title,"
            "       m.attendee_email, m.starts_at, m.ends_at, m.status, m.source,"
            "       m.booked_at,"
            "       p.name AS prospect_name, p.company AS company"
            "  FROM meetings m LEFT JOIN prospects p ON p.id = m.prospect_id"
            " ORDER BY m.booked_at"
        )]
    except sqlite3.OperationalError:
        return None


def _legacy_meetings(replies: list[dict]) -> list[dict]:
    """Meetings reconstructed from `replies` flags, for pre-migration workspaces.

    Every row is `source='reply'` by construction, which is exactly the bias the
    meetings table exists to remove: a prospect who books without replying is
    invisible here.
    """
    out = []
    for r in replies:
        if not r.get("meeting_booked"):
            continue
        out.append({
            "id": r["id"], "prospect_id": r["prospect_id"], "sender_id": None,
            "provider": None, "title": None, "attendee_email": None,
            "starts_at": None, "ends_at": None,
            "status": "held" if r.get("meeting_held") else "booked",
            "source": "reply", "booked_at": r.get("replied_at"),
            "prospect_name": None, "company": None,
        })
    return out


def _attribute(sends: list[dict], events: list[dict],
               at_key: str = "replied_at") -> dict[int, int]:
    """event id -> send_id of the last email that prospect got before the event.

    Without this, per-step and per-variant rates cannot exist: a reply or a
    meeting row knows its prospect, not which touch earned it. Last-touch is the
    honest default; it under-credits the opener and we live with that.

    Shared by replies (`replied_at`) and meetings (`booked_at`) on purpose, so
    meeting rate slices by tier, industry, step, send-day and variant on exactly
    the same rule as reply rate rather than a second one that drifts.
    """
    by_prospect: dict[int, list[dict]] = {}
    for s in sends:
        if s["channel"] == "email":
            by_prospect.setdefault(s["prospect_id"], []).append(s)

    out: dict[int, int] = {}
    for e in events:
        candidates = by_prospect.get(e.get("prospect_id"), [])
        at = str(e.get(at_key) or "")
        prior = [s for s in candidates if str(s["sent_at"]) <= at]
        chosen = (prior or candidates)
        if chosen:
            out[e["id"]] = chosen[-1]["id"]
    return out


def _counted(meetings: list[dict]) -> list[dict]:
    return [m for m in meetings
            if str(m.get("status") or "").lower() in MEETING_COUNTED]


def _status_is(meetings: list[dict], status: str) -> int:
    return sum(1 for m in meetings
               if str(m.get("status") or "").lower() == status)


def _is_positive(reply: dict) -> bool:
    if reply.get("is_positive") is not None:
        return bool(reply["is_positive"])
    return str(reply.get("sentiment") or "").lower() in ("positive", "referral")


def _title_cluster(title: str | None) -> str:
    t = (title or "").lower()
    if not t:
        return "unknown"
    for name, needles in TITLE_CLUSTERS:
        if any(n in t for n in needles):
            return name
    return "other"


def _step_labels(cfg) -> dict[int, str]:
    labels = {}
    for i, step in enumerate(cfg.get("cadence.steps", []) or []):
        intent = step.get("intent") or step.get("channel") or f"step {i}"
        labels[i] = f"Day {step.get('day', '?')} {intent}"
    return labels


# -- bucketing -------------------------------------------------------------

_DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def _bucketer(cfg, dim: str):
    """(label_fn, title, column, display) for a `reporting.group_by` value."""
    steps = _step_labels(cfg)
    known = {
        "icp_tier": (lambda s: s.get("icp_tier") or "unclassified",
                     "By ICP tier", "Tier", "table"),
        "industry": (lambda s: s.get("industry") or "unknown",
                     "By industry", "Industry", "table"),
        "title_cluster": (lambda s: _title_cluster(s.get("title")),
                          "By title cluster", "Title cluster", "table"),
        "buyer_tier": (lambda s: s.get("buyer_tier") or "unassigned",
                       "By buyer tier", "Buyer tier", "table"),
        "sender": (lambda s: s.get("sender_id") or "unassigned",
                   "By sender", "Sender", "table"),
        "cadence_step": (lambda s: steps.get(s["step_index"], f"step {s['step_index']}"),
                         "By cadence step", "Step", "bars"),
        "send_day": (lambda s: _weekday(s["sent_at"]),
                     "By send day", "Day", "bars"),
        "variant": (lambda s: s.get("variant") or "unassigned",
                    "By variant", "Variant", "table"),
    }
    return known.get(dim)


def _weekday(sent_at: str) -> str:
    d = _parse(sent_at)
    return _DAY_ORDER[d.weekday()] if d else "unknown"


def _parse(value) -> dt.datetime | None:
    """SQLite stores naive 'YYYY-MM-DD HH:MM:SS'. Tolerate ISO-T and bare dates."""
    if not value:
        return None
    text = str(value).replace("T", " ").split("+")[0].split(".")[0].strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _sort_key(dim: str, name: str, row: dict):
    if dim == "send_day":
        return (_DAY_ORDER.index(name) if name in _DAY_ORDER else 99,)
    if dim == "cadence_step":
        return (row.get("order", 99),)
    return (-row["sends"], name)


def _segment(cfg, dim: str, sends: list[dict], replies_by_send: dict[int, list[dict]],
             meetings_by_send: dict[int, list[dict]], floor: int) -> Segment | None:
    spec = _bucketer(cfg, dim)
    if spec is None:
        return None
    label_fn, title, column, display = spec

    buckets: dict[str, dict] = {}
    for s in sends:
        name = str(label_fn(s))
        b = buckets.setdefault(name, {"name": name, "sends": 0, "bounces": 0,
                                      "replies": 0, "positive": 0, "meetings": 0,
                                      "meetings_held": 0, "order": s["step_index"]})
        b["sends"] += 1
        b["bounces"] += int(s["bounced"] or 0)
        b["order"] = min(b["order"], s["step_index"])
        for r in replies_by_send.get(s["id"], []):
            b["replies"] += 1
            b["positive"] += int(_is_positive(r))
        # Meetings arrive from the meetings table, attributed by the same
        # last-touch rule as replies, so a booking with no reply still lands in
        # the tier / step / variant row that earned it.
        for m in meetings_by_send.get(s["id"], []):
            b["meetings"] += 1
            b["meetings_held"] += int(str(m.get("status") or "").lower() == "held")

    rows = []
    for name, b in buckets.items():
        rows.append({
            "name": name, "sends": b["sends"], "replies": b["replies"],
            "positive": b["positive"], "meetings": b["meetings"],
            "meetings_held": b["meetings_held"], "bounces": b["bounces"],
            "rates": {
                "reply_rate": Rate(b["replies"], b["sends"], floor).to_dict(),
                "positive_reply_rate": Rate(b["positive"], b["sends"], floor).to_dict(),
                "meeting_rate": Rate(b["meetings"], b["sends"], floor).to_dict(),
            },
            "_sort": _sort_key(dim, name, b),
        })
    rows.sort(key=lambda r: r.pop("_sort"))
    return Segment(dim, title, column, display, rows)


# -- A/B -------------------------------------------------------------------

Z_ALPHA = 1.959964   # two-tailed 0.05
Z_POWER = 0.841621   # 80% power


def _two_proportion(n1: int, d1: int, n2: int, d2: int) -> tuple[float | None, float | None]:
    """(z, two-tailed p). None when either arm has no denominator."""
    if d1 <= 0 or d2 <= 0:
        return None, None
    p1, p2 = n1 / d1, n2 / d2
    pooled = (n1 + n2) / (d1 + d2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / d1 + 1 / d2))
    if se == 0:
        return None, None
    z = (p1 - p2) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def _required_n(p1: float, p2: float) -> int | None:
    """Sends per arm for alpha=0.05 at 80% power, given the observed split."""
    if p1 == p2:
        return None
    delta = (p1 - p2) ** 2
    return math.ceil((Z_ALPHA + Z_POWER) ** 2
                     * (p1 * (1 - p1) + p2 * (1 - p2)) / delta)


def _ab_test(variant_seg: Segment | None, floor: int) -> dict:
    """Honest state label. `Significant` requires n_floor in BOTH arms."""
    rows = [r for r in (variant_seg.rows if variant_seg else [])
            if r["name"] != "unassigned"]
    arms = sorted(rows, key=lambda r: -r["sends"])[:2]
    if len(arms) < 2:
        return {"state": "No data", "arms": [a for a in arms], "leader": None,
                "p_value": None, "z": None, "sends_to_significance": None,
                "required_n_per_arm": None,
                "note": "Variant comparison appears once sends are split across "
                        "two arms."}

    a, b = arms
    z, p = _two_proportion(a["replies"], a["sends"], b["replies"], b["sends"])
    both_floored = a["sends"] >= floor and b["sends"] >= floor

    if p is not None and p < 0.05 and both_floored:
        state = "Significant"
    elif p is not None and p < 0.20 and both_floored:
        state = "Trending"
    else:
        state = "Directional"

    p1 = a["replies"] / a["sends"] if a["sends"] else 0.0
    p2 = b["replies"] / b["sends"] if b["sends"] else 0.0
    required = _required_n(p1, p2)
    remaining = (max(0, required - min(a["sends"], b["sends"]))
                 if required is not None else None)

    leader = None
    if a["sends"] and b["sends"] and p1 != p2:
        leader = a["name"] if p1 > p2 else b["name"]

    note = ("Both arms must clear the n_floor before this can read Significant, "
            "whatever the p-value says. Weight reply sentiment over rate deltas "
            "at low volume.")
    if not both_floored:
        note = (f"At least one arm is under the n_floor of {floor} sends, so the "
                f"state is held at Directional regardless of p-value.")

    return {"state": state, "arms": [a, b], "leader": leader,
            "p_value": p, "z": z, "sends_to_significance": remaining,
            "required_n_per_arm": required, "note": note}


# -- headline metrics ------------------------------------------------------

# key -> (label, rate key or None, count key or None, denominator prose).
# The dashboard knows none of these names: it renders whatever this emits, so a
# team that edits `reporting.primary_metrics` changes the KPI row with no code.
METRIC_SPECS = {
    "reply_rate": ("Reply rate", "reply_rate", "replies", "replies / sends"),
    "positive_reply_rate": ("Positive reply rate", "positive_reply_rate",
                            "positive_replies", "positive / sends"),
    "meeting_rate": ("Meeting rate", "meeting_rate", "meetings_booked",
                     "booked / sends"),
    "meeting_to_opp": ("Meeting to opp", "meeting_to_opp", "opportunities",
                       "opps / booked"),
    "bounce_rate": ("Bounce rate", "bounce_rate", "bounces", "bounces / sends"),
    "meetings_booked": ("Meetings booked", None, "meetings_booked", ""),
    "meetings_held": ("Meetings held", "meeting_held_rate", "meetings_held",
                      "scheduled and not cancelled / booked"),
    "opportunities": ("Opportunities", None, "opportunities", ""),
    "sends": ("Emails sent", None, "sends", ""),
    "prospects": ("Prospects touched", None, "prospects", ""),
}

FEATURE_METRIC = "positive_reply_rate"   # the one card that gets the accent border


def _kpis(cfg, totals: dict, rates: dict[str, Rate]) -> list[dict]:
    wanted = list(cfg.get("reporting.primary_metrics") or
                  ["reply_rate", "positive_reply_rate", "meetings_booked",
                   "meetings_held"])
    out = []
    for key in wanted:
        spec = METRIC_SPECS.get(key)
        if spec is None:
            continue
        label, rate_key, count_key, denom = spec
        rate = rates.get(rate_key) if rate_key else None
        out.append({
            "key": key,
            "label": label,
            "kind": "rate" if rate is not None else "count",
            "rate": rate.to_dict() if rate is not None else None,
            "count": int(totals.get(count_key, 0)) if count_key else 0,
            "denominator_label": denom,
            "feature": key == FEATURE_METRIC,
        })
    return out


SENTIMENT_TONES = {
    "positive": "good", "referral": "good", "interested": "good",
    "not_now": "warn", "objection": "warn", "wrong_person": "warn",
    "negative": "bad", "unsubscribe": "bad", "bounce": "bad",
}


# -- meetings --------------------------------------------------------------

def _meeting_entry(m: dict) -> dict:
    """One meeting, flattened for display. Every fallback string is decided here
    so the dashboard renders the payload rather than inventing labels."""
    return {
        "id": m.get("id"),
        "prospect_id": m.get("prospect_id"),
        "prospect_name": (m.get("prospect_name") or m.get("attendee_email")
                          or "unmatched attendee"),
        "company": m.get("company") or "unknown company",
        "sender_id": m.get("sender_id") or "unassigned",
        "title": m.get("title") or "",
        "status": str(m.get("status") or "").lower(),
        "source": str(m.get("source") or "").lower() or "unknown",
        "starts_at": m.get("starts_at"),
        "booked_at": m.get("booked_at"),
    }


def _by_source(meetings: list[dict]) -> list[dict]:
    """How much of the number each detection path is actually catching.

    The reason this is on the dashboard: if `calendar` is near zero after the
    integration is live, the integration is broken, and the booked count is
    reading low for a reason nobody would otherwise notice.
    """
    counts: dict[str, int] = {}
    for m in meetings:
        src = str(m.get("source") or "").lower() or "unknown"
        counts[src] = counts.get(src, 0) + 1
    known = [{"source": s, "count": counts.pop(s, 0)} for s in MEETING_SOURCES]
    extra = [{"source": s, "count": n} for s, n in sorted(counts.items())]
    return known + extra


def _upcoming(meetings: list[dict], now: dt.datetime) -> tuple[list[dict], int]:
    """Still-booked meetings whose start time is in the future, soonest first.

    Not window-scoped: a trailing window looks backwards and these have not
    happened yet.
    """
    future = []
    for m in meetings:
        if str(m.get("status") or "").lower() != "booked":
            continue
        starts = _parse(m.get("starts_at"))
        if starts is None or starts <= now:
            continue
        future.append((starts, _meeting_entry(m)))
    future.sort(key=lambda pair: pair[0])
    return [e for _, e in future[:UPCOMING_LIMIT]], len(future)


def _meetings_block(meetings: list[dict], attribution: dict[int, int],
                    send_ids: set[int], start: dt.datetime, now: dt.datetime,
                    backend: str) -> dict:
    """Window-scoped meeting counts, split by whether an in-window send earned them.

    Three buckets, because a meeting can miss the send cohort in two different
    ways and both have to stay visible:

      attributed    the send it is attributed to is in this window. Only these
                    can appear in a segment row, which is what makes meeting
                    rate slice by tier, step, send-day and variant.
      lagged        booked in this window off a send that predates it. Long-lag
                    bookings are common and dropping them would make a monthly
                    meeting count disagree with the operator's own calendar.
      unattributed  booked in this window with no send to attribute to at all.

    All three count toward the total. Neither of the last two is reassigned to
    some nearby send, because that would be a guess dressed up as attribution.
    """
    attributed, lagged, unattributed = [], [], []
    for m in meetings:
        booked = _parse(m.get("booked_at"))
        # A booking made after the as-of moment did not exist yet. Only a
        # backdated report can see one, and it must not.
        if booked is not None and booked > now:
            continue
        sid = attribution.get(m["id"])
        if sid is not None and sid in send_ids:
            attributed.append(m)
            continue
        if booked is not None and booked < start:
            continue
        (lagged if sid is not None else unattributed).append(m)

    counted_attributed = _counted(attributed)
    counted_lagged, counted_unattributed = _counted(lagged), _counted(unattributed)
    counted = counted_attributed + counted_lagged + counted_unattributed
    upcoming, upcoming_total = _upcoming(meetings, now)

    by_send: dict[int, list[dict]] = {}
    for m in counted_attributed:
        by_send.setdefault(attribution[m["id"]], []).append(m)

    notes = []
    if backend == "reply_flags":
        notes.append("The meetings table is not present in this database, so these "
                     "counts come from flags on replies. Anyone who booked without "
                     "replying is missing.")
    off_cohort = len(counted_lagged) + len(counted_unattributed)
    if off_cohort:
        why = []
        if counted_unattributed:
            why.append(f"{len(counted_unattributed)} with no attributable send")
        if counted_lagged:
            why.append(f"{len(counted_lagged)} earned by a send from before this window")
        notes.append(
            f"{off_cohort} of {len(counted)} booked meetings are in this total but "
            f"in none of the segment breakdowns: {', '.join(why)}.")

    return {
        "backend": backend,
        "booked": len(counted),
        "held": _status_is(counted, "held"),
        "no_show": _status_is(counted, "no_show"),
        "cancelled": _status_is(attributed + lagged + unattributed, "cancelled"),
        "unattributed": len(counted_unattributed),
        "attributed_earlier": len(counted_lagged),
        "held_note": HELD_NOTE,
        "by_source": _by_source(counted),
        "booked_list": [_meeting_entry(m) for m in
                        sorted(counted, key=lambda m: str(m.get("booked_at") or ""))],
        "upcoming": upcoming,
        "upcoming_total": upcoming_total,
        "notes": notes,
        "_by_send": by_send,
    }


# -- window ----------------------------------------------------------------

def _window(cfg, key: str, sends: list[dict], replies: list[dict],
            attribution: dict[int, int], meetings: list[dict],
            meeting_attribution: dict[int, int], backend: str,
            now: dt.datetime, floor: int) -> WindowReport:
    days = WINDOW_DAYS[key]
    start = now - dt.timedelta(days=days)

    # Bounded at both ends. The upper bound only matters when `now` is not the
    # real clock, which is exactly what a backdated report does: without it,
    # re-running last month's report would fold in everything sent since and
    # quietly disagree with what that report said at the time.
    def _in(row) -> bool:
        t = _parse(row["sent_at"])
        return t is None or start <= t <= now

    in_window = [s for s in sends if s["channel"] == "email" and _in(s)]
    ids = {s["id"] for s in in_window}
    other_channel = [s for s in sends if s["channel"] != "email" and _in(s)]

    replies_by_send: dict[int, list[dict]] = {}
    attributed: list[dict] = []
    for r in replies:
        got = _parse(r.get("replied_at"))
        if got is not None and got > now:
            continue
        sid = attribution.get(r["id"])
        if sid in ids:
            replies_by_send.setdefault(sid, []).append(r)
            attributed.append(r)

    mtg = _meetings_block(meetings, meeting_attribution, ids, start, now, backend)
    meetings_by_send = mtg.pop("_by_send")

    n_sends = len(in_window)
    n_bounces = sum(int(s["bounced"] or 0) for s in in_window)
    n_replies = len(attributed)
    n_positive = sum(1 for r in attributed if _is_positive(r))
    n_booked = mtg["booked"]
    n_held = mtg["held"]
    n_opps = sum(int(r["is_opportunity"] or 0) for r in attributed)
    delivered = max(0, n_sends - n_bounces)

    totals = {
        "prospects": len({s["prospect_id"] for s in in_window}),
        "sends": n_sends,
        "other_channel_touches": len(other_channel),
        "delivered": delivered,
        "bounces": n_bounces,
        "replies": n_replies,
        "positive_replies": n_positive,
        "meetings_booked": n_booked,
        "meetings_held": n_held,
        "meetings_cancelled": mtg["cancelled"],
        "meetings_unattributed": mtg["unattributed"],
        "opportunities": n_opps,
    }

    rates = {
        "reply_rate": Rate(n_replies, n_sends, floor),
        "positive_reply_rate": Rate(n_positive, n_sends, floor),
        "meeting_rate": Rate(n_booked, n_sends, floor),
        "meeting_held_rate": Rate(n_held, n_booked, floor),
        "meeting_to_opp": Rate(n_opps, n_booked, floor),
        "bounce_rate": Rate(n_bounces, n_sends, floor),
    }
    mtg["rates"] = {k: rates[k].to_dict() for k in
                    ("meeting_rate", "meeting_held_rate", "meeting_to_opp")}

    warn = float(cfg.get("reporting.deliverability.bounce_rate_warn", 0.02) or 0.02)
    halt = float(cfg.get("reporting.deliverability.bounce_rate_halt", 0.05) or 0.05)
    br = rates["bounce_rate"].value
    if br is None:
        status = "none"
    elif br >= halt:
        status = "halt"
    elif br >= warn:
        status = "warn"
    else:
        status = "ok"

    sentiment_counts: dict[str, int] = {}
    for r in attributed:
        label = str(r.get("sentiment") or ("positive" if _is_positive(r) else "uncategorized"))
        sentiment_counts[label] = sentiment_counts.get(label, 0) + 1

    funnel = [
        {"name": "Sent", "count": n_sends},
        {"name": "Delivered", "count": delivered},
        {"name": "Replied", "count": n_replies},
        {"name": "Positive", "count": n_positive},
        {"name": "Meeting booked", "count": n_booked},
        {"name": "Meeting scheduled, not cancelled", "count": n_held},
        {"name": "Opportunity", "count": n_opps},
    ]

    dims = list(cfg.get("reporting.group_by", []) or [])
    segments = [s for s in (_segment(cfg, d, in_window, replies_by_send,
                                     meetings_by_send, floor)
                            for d in dims) if s]
    variant_seg = next((s for s in segments if s.key == "variant"), None)
    if variant_seg is None:
        variant_seg = _segment(cfg, "variant", in_window, replies_by_send,
                               meetings_by_send, floor)

    return WindowReport(
        key=key,
        label=f"trailing {days} days",
        start=start.strftime("%Y-%m-%d"),
        end=now.strftime("%Y-%m-%d"),
        totals=totals,
        rates=rates,
        kpis=_kpis(cfg, totals, rates),
        meetings=mtg,
        deliverability={"sends": n_sends, "bounces": n_bounces, "status": status,
                        "bounce_rate": rates["bounce_rate"].to_dict(),
                        "warn": warn, "halt": halt},
        funnel=funnel,
        sentiment=[{"label": k, "count": v,
                    "tone": SENTIMENT_TONES.get(k.lower(), "neutral")}
                   for k, v in sorted(sentiment_counts.items(), key=lambda kv: -kv[1])],
        ab_test=_ab_test(variant_seg, floor),
        segments=segments,
    )


def _cohorts(sends, replies, attribution, now, floor) -> list[dict]:
    """ISO-week cohorts by send date. Answers "is this decaying"."""
    emails = [s for s in sends if s["channel"] == "email"]
    cutoff = now - dt.timedelta(weeks=COHORT_WEEKS)
    by_send = {s["id"]: s for s in emails}

    weeks: dict[str, dict] = {}
    for s in emails:
        d = _parse(s["sent_at"])
        if not d or d < cutoff or d > now:
            continue
        iso = d.isocalendar()
        key = f"{iso[0]}-W{iso[1]:02d}"
        w = weeks.setdefault(key, {"label": key, "prospects": set(), "sends": 0,
                                   "replies": 0, "positive": 0})
        w["sends"] += 1
        w["prospects"].add(s["prospect_id"])

    for r in replies:
        s = by_send.get(attribution.get(r["id"], -1))
        d = _parse(s["sent_at"]) if s else None
        if not d or d < cutoff or d > now:
            continue
        iso = d.isocalendar()
        w = weeks.get(f"{iso[0]}-W{iso[1]:02d}")
        if w:
            w["replies"] += 1
            w["positive"] += int(_is_positive(r))

    out = []
    for key in sorted(weeks):
        w = weeks[key]
        out.append({
            "label": w["label"],
            "prospects": len(w["prospects"]),
            "sends": w["sends"],
            "replies": w["replies"],
            "rates": {
                "reply_rate": Rate(w["replies"], w["sends"], floor).to_dict(),
                "positive_reply_rate": Rate(w["positive"], w["sends"], floor).to_dict(),
            },
        })
    return out


def _daily_series(sends, now, cap) -> list[dict]:
    counts: dict[str, int] = {}
    for s in sends:
        if s["channel"] != "email":
            continue
        d = _parse(s["sent_at"])
        if d and now - dt.timedelta(days=SERIES_DAYS) <= d <= now:
            counts[d.strftime("%Y-%m-%d")] = counts.get(d.strftime("%Y-%m-%d"), 0) + 1
    out = []
    for i in range(SERIES_DAYS - 1, -1, -1):
        day = (now - dt.timedelta(days=i)).strftime("%Y-%m-%d")
        out.append({"date": day, "count": counts.get(day, 0), "over_cap": counts.get(day, 0) > cap})
    return out


def _auth(cfg) -> dict:
    """SPF/DKIM/DMARC status, if the team recorded it. Never guessed."""
    configured = cfg.get("reporting.deliverability.auth") or {}
    out = {}
    for key in ("spf", "dkim", "dmarc"):
        entry = configured.get(key) if isinstance(configured, dict) else None
        if isinstance(entry, dict):
            out[key] = {"status": str(entry.get("status", "unknown")),
                        "detail": str(entry.get("detail", ""))}
        elif isinstance(entry, str):
            out[key] = {"status": entry, "detail": ""}
        else:
            out[key] = {"status": "unknown",
                        "detail": "not recorded in reporting.deliverability.auth"}
    return out


def build(cfg, conn, now: dt.datetime | None = None) -> dict:
    """The whole payload. The dashboard renders this and nothing else."""
    # UTC, because every timestamp in the database is written by SQLite's
    # datetime('now'), which is UTC. A local-clock `now` sits behind the newest
    # rows by the UTC offset and silently drops the sends made today, which is
    # the exact window an operator checks the report against.
    now = now or dt.datetime.utcnow()
    floor = int(cfg.get("reporting.n_floor", 10) or 10)
    if cfg.get("reporting.track_opens"):
        print("WARNING: reporting.track_opens is true but open rates are not "
              "computed by design. Set it false.", file=sys.stderr)

    sends, replies = _rows(conn)
    attribution = _attribute(sends, replies)

    rows = _meeting_rows(conn)
    backend = "meetings_table" if rows is not None else "reply_flags"
    meetings = rows if rows is not None else _legacy_meetings(replies)
    meeting_attribution = _attribute(sends, meetings, at_key="booked_at")

    cap = cfg.total_daily_capacity
    keys = [w for w in (cfg.get("reporting.windows") or list(WINDOW_DAYS))
            if w in WINDOW_DAYS]

    return {
        "schema": "outbound-report/1",
        "demo": False,
        "generated_at": now.isoformat(timespec="seconds"),
        "config": {
            "title": "Outbound performance",
            "subtitle": f"{cfg.get('company.name', 'outbound')} campaign health",
            "n_floor": floor,
            "daily_cap": cap,
            "track_opens": False,
            "windows": keys,
            "default_window": "month" if "month" in keys else (keys[0] if keys else "week"),
            "thresholds": {
                "bounce_warn": float(cfg.get("reporting.deliverability.bounce_rate_warn", 0.02) or 0.02),
                "bounce_halt": float(cfg.get("reporting.deliverability.bounce_rate_halt", 0.05) or 0.05),
            },
            "auth": _auth(cfg),
            "benchmarks": cfg.get("reporting.benchmarks") or None,
            "notes": [
                f"Rates are suppressed below {floor} in the denominator and shown "
                f"as raw counts instead.",
                "Open tracking is deliberately absent: the pixel costs more "
                "deliverability than the metric is worth.",
            ],
        },
        "daily_send_series": _daily_series(sends, now, cap),
        "cohorts": _cohorts(sends, replies, attribution, now, floor),
        "windows": {k: _window(cfg, k, sends, replies, attribution, meetings,
                               meeting_attribution, backend, now, floor).to_dict()
                    for k in keys},
    }


# -- output ----------------------------------------------------------------

def _print_text(payload: dict, window: str, group_by: str | None) -> None:
    win = payload["windows"].get(window)
    if win is None:
        print(f"window {window!r} not in reporting.windows "
              f"({list(payload['windows'])})", file=sys.stderr)
        return
    floor = payload["config"]["n_floor"]
    t = win["totals"]

    print(f"{payload['config']['subtitle']}  |  {window} ({win['label']}, "
          f"{win['start']} to {win['end']})")
    print(f"generated {payload['generated_at']}  |  n_floor {floor}\n")

    dl = win["deliverability"]
    print(f"  deliverability   {dl['status'].upper()}  "
          f"bounce {_rate_text(dl['bounce_rate'])}  "
          f"(warn {dl['warn']:.1%} / halt {dl['halt']:.1%})")
    over = [d for d in payload["daily_send_series"] if d["over_cap"]]
    print(f"  volume           {t['sends']} email sends, cap "
          f"{payload['config']['daily_cap']}/day, "
          f"{len(over)} day(s) over cap in the last {SERIES_DAYS}")
    print(f"  auth             " + "  ".join(
        f"{k.upper()}={v['status']}" for k, v in payload["config"]["auth"].items()))
    print()
    print(f"  {'prospects':<18} {t['prospects']}")
    print(f"  {'emails sent':<18} {t['sends']}"
          + (f"  (+{t['other_channel_touches']} non-email touches)"
             if t["other_channel_touches"] else ""))
    for k in win["kpis"]:
        detail = (_rate_text(k["rate"]) if k["kind"] == "rate"
                  else str(k["count"]))
        if k["kind"] == "rate" and k["denominator_label"]:
            detail += f"  [{k['denominator_label']}]"
        print(f"  {k['label'].lower():<18} {detail}")

    _print_meetings(win)

    if win["sentiment"]:
        print("\n  sentiment        " + ", ".join(
            f"{s['label']} {s['count']}" for s in win["sentiment"]))

    ab = win["ab_test"]
    print(f"\n  A/B              {ab['state']}"
          + (f"  leader={ab['leader']}" if ab.get("leader") else ""))
    if ab.get("p_value") is not None:
        line = f"                   p={ab['p_value']:.4f}"
        if ab.get("sends_to_significance") is not None:
            line += (f"  needs ~{ab['sends_to_significance']} more sends/arm "
                     f"({ab['required_n_per_arm']} total/arm)")
        print(line)
    print(f"                   {ab['note']}")

    if payload["cohorts"]:
        print("\n  weekly cohorts")
        for c in payload["cohorts"]:
            print(f"    {c['label']}  {c['sends']:>4} sends  {c['replies']:>3} replies"
                  f"  reply {_rate_text(c['rates']['reply_rate'])}")

    wanted = [s for s in win["segments"] if group_by in (None, s["key"])]
    for seg in wanted:
        print(f"\n  {seg['title']}")
        print(f"    {seg['column']:<24} {'sends':>6} {'repl':>5}  reply rate")
        for row in seg["rows"]:
            print(f"    {row['name'][:24]:<24} {row['sends']:>6} {row['replies']:>5}  "
                  f"{_rate_text(row['rates']['reply_rate'])}")
    if group_by and not wanted:
        print(f"\n  no segment {group_by!r}; configured: "
              f"{[s['key'] for s in win['segments']]}", file=sys.stderr)


def _print_meetings(win: dict) -> None:
    """The outcome block. Printed with the held qualifier, always."""
    m = win.get("meetings") or {}
    rates = m.get("rates") or {}
    src = ", ".join(f"{s['source']} {s['count']}" for s in (m.get("by_source") or []))

    print(f"\n  meetings         {m.get('booked', 0)} booked"
          + (f"  ({src})" if src else ""))
    print(f"  {'held':<18} {m.get('held', 0)}  ({HELD_NOTE})")
    print(f"  {'cancelled':<18} {m.get('cancelled', 0)}  (not counted as booked)")
    if m.get("no_show"):
        print(f"  {'no shows':<18} {m['no_show']}  (counted as booked: the send "
              f"earned it)")
    for key, label in (("meeting_rate", "meeting rate"),
                       ("meeting_held_rate", "held rate"),
                       ("meeting_to_opp", "meeting to opp")):
        if rates.get(key):
            print(f"  {label:<18} {_rate_text(rates[key])}")

    upcoming = m.get("upcoming") or []
    if upcoming:
        total = m.get("upcoming_total", len(upcoming))
        print(f"  {'upcoming':<18} {total} scheduled ahead")
        for e in upcoming:
            print(f"    {str(e.get('starts_at') or 'no start time'):<20} "
                  f"{e['prospect_name']}, {e['company']}  ({e['sender_id']})")
    for note in m.get("notes") or []:
        print(f"    note: {note}")


def _rate_text(d: dict) -> str:
    """Display form of a serialized Rate.

    The numerator-without-denominator case is spelled out rather than left as
    "n/a (2 of 0)", which reads like a bug. It is not one: a meeting booked
    this week off a send from last month is real, and the window it landed in
    has no sends to rate it against.
    """
    if d["d"] <= 0 and d["n"] > 0:
        return f"n/a  ({d['n']} counted, nothing in the denominator this window)"
    return Rate(d["n"], d["d"], d["floor"]).text()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default="month", choices=sorted(WINDOW_DAYS))
    ap.add_argument("--group-by", default=None,
                    help="restrict the text output to one reporting.group_by dimension")
    ap.add_argument("--json", action="store_true", help="emit the full payload")
    ap.add_argument("--write-dashboard", action="store_true",
                    help="write the payload to reporting.dashboard_data_path")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))
    payload = build(cfg, conn)
    conn.close()

    if args.write_dashboard:
        out = cfg.path("reporting.dashboard_data_path", "data/dashboard.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2) + "\n")
        print(f"wrote {out}")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_text(payload, args.window, args.group_by)
    return 0


if __name__ == "__main__":
    sys.exit(main())
