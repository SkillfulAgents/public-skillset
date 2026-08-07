#!/usr/bin/env python3
"""The Friday digest: one week of numbers, meetings first. Posts nothing by default.

  uv run --with pyyaml weekly_report.py [--send] [--week ISO_DATE] [--config PATH]

Meetings lead the digest because they are the only number in it that a revenue
forecast can be built from. Reply rate is a leading indicator of the copy;
booked meetings are the outcome, and burying them under activity metrics is how
a team optimises for sends.

Dry run by default, exactly like send.py: without `--send` the digest is printed
and nothing leaves the machine. That ordering matters for a scheduled job, since
the first thing anyone does with a new digest is run it once to read it, and a
default that posts turns that into a channel message nobody meant to send.

Rate suppression is the same rule the main report enforces (`reporting.n_floor`):
below the floor the raw count is shown and the percentage is withheld. A weekly
window is small by construction, so most weeks that floor is doing real work.

Delivery goes through the configured `notify` adapter. Never call a vendor API
from here; the adapter is the seam that lets Slack become something else without
touching this file.

Suggested schedule (the operator wires this up, this script does not):
`reporting.schedule.weekly_report_cron`, default "0 15 * * 5", Friday 15:00 local.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

import report  # noqa: E402  sibling script; the metric definitions live there
from lib import adapters, config as cfgmod, db  # noqa: E402

UPCOMING_HORIZON_DAYS = 7
LIST_LIMIT = 12


def _as_of(cfg, week: str | None) -> dt.datetime:
    """End of the reporting week.

    `--week` names a date inside the week of interest and the window is the
    trailing 7 days ending at the end of that day, so re-running last Friday's
    digest reproduces last Friday's numbers rather than sliding with the clock.

    Returned in UTC, because that is what SQLite's datetime('now') writes into
    every row. The day boundary is still the operator's local one, so "end of
    Friday" means their Friday, not UTC's.
    """
    if not week:
        return dt.datetime.utcnow()
    try:
        d = dt.date.fromisoformat(week)
    except ValueError as e:
        raise SystemExit(f"--week must be an ISO date (YYYY-MM-DD): {e}")
    local_end = dt.datetime.combine(d, dt.time(23, 59, 59), tzinfo=cfg.tz)
    return local_end.astimezone(dt.timezone.utc).replace(tzinfo=None)


def _pick_window(payload: dict) -> tuple[str, dict, str | None]:
    """The week window, or the shortest one configured, said out loud.

    Silently reporting a 30 day window under a "this week" heading would be a
    lie the reader has no way to catch.
    """
    windows = payload.get("windows") or {}
    if "week" in windows:
        return "week", windows["week"], None
    order = [k for k in ("month", "quarter") if k in windows]
    if not order:
        raise SystemExit(
            "reporting.windows is empty, so there is nothing to report. "
            "Add `week` to reporting.windows in the config.")
    key = order[0]
    return key, windows[key], (
        f"reporting.windows does not include `week`, so this digest covers the "
        f"{key} window ({windows[key]['label']}) instead.")


def _rate(d: dict | None) -> str:
    """Same renderer the main report uses, so the two never disagree."""
    if not d:
        return "n/a"
    return report._rate_text(d)


def _cap_breaches(cfg, conn, start: dt.date, end: dt.date) -> list[dict]:
    """Days in the window where one sender went over its own daily cap.

    Per sender, not org-wide: caps are enforced per mailbox, and an org total
    that looks fine can still hide one mailbox at double its cap.
    """
    rows = conn.execute(
        "SELECT date(sent_at) AS day, sender_id, COUNT(*) AS n FROM sends "
        "WHERE channel = 'email' AND date(sent_at) BETWEEN ? AND ? "
        "GROUP BY day, sender_id ORDER BY day, sender_id",
        (start.isoformat(), end.isoformat())).fetchall()

    out = []
    for r in rows:
        sid = r["sender_id"] or "(unassigned)"
        try:
            cap = cfg.effective_cap(r["sender_id"]) if r["sender_id"] else None
        except Exception:
            cap = None
        if cap is None:
            # An unknown sender has no cap to breach, but it also means sends
            # went out under an id the governor cannot police. Worth saying.
            out.append({"day": r["day"], "sender_id": sid, "sends": r["n"],
                        "cap": None,
                        "detail": "sender is not in config, so no cap applied"})
        elif r["n"] > cap:
            out.append({"day": r["day"], "sender_id": sid, "sends": r["n"],
                        "cap": cap, "detail": f"{r['n']}/{cap}, over by {r['n'] - cap}"})
    return out


def compose(cfg, conn, payload: dict, as_of: dt.datetime) -> str:
    """The digest text. Same numbers as report.py, ordered for a human."""
    key, win, substitution = _pick_window(payload)
    floor = payload["config"]["n_floor"]
    t = win["totals"]
    m = win.get("meetings") or {}
    rates = m.get("rates") or {}
    start = dt.date.fromisoformat(win["start"])
    end = dt.date.fromisoformat(win["end"])

    L: list[str] = []
    L.append(f"{payload['config']['subtitle']}: week of {win['start']} to {win['end']}")
    if substitution:
        L.append(substitution)
    L.append("")

    L.append("MEETINGS")
    L.append(f"  booked            {m.get('booked', 0)}")
    L.append(f"  held              {m.get('held', 0)}")
    L.append(f"                    {report.HELD_NOTE}")
    if m.get("cancelled"):
        L.append(f"  cancelled         {m['cancelled']} (not counted as booked)")
    if m.get("no_show"):
        L.append(f"  no shows          {m['no_show']} (counted as booked: the send earned it)")
    L.append(f"  meeting rate      {_rate(rates.get('meeting_rate'))}")
    L.append(f"  meeting to opp    {_rate(rates.get('meeting_to_opp'))}")

    booked_list = m.get("booked_list") or []
    if booked_list:
        L.append("")
        L.append(f"  Booked this week ({len(booked_list)}):")
        for e in booked_list[:LIST_LIMIT]:
            when = e.get("starts_at") or "no start time"
            L.append(f"    {when}  {e['prospect_name']}, {e['company']} "
                     f"[{e['status']}, via {e['source']}, {e['sender_id']}]")
        if len(booked_list) > LIST_LIMIT:
            L.append(f"    and {len(booked_list) - LIST_LIMIT} more")
    else:
        L.append("")
        L.append("  Nothing booked in this window.")

    horizon = as_of + dt.timedelta(days=UPCOMING_HORIZON_DAYS)
    ahead = []
    for e in m.get("upcoming") or []:
        starts = report._parse(e.get("starts_at"))
        if starts is not None and starts <= horizon:
            ahead.append(e)
    L.append("")
    if ahead:
        L.append(f"  On the calendar next week ({len(ahead)}):")
        for e in ahead[:LIST_LIMIT]:
            L.append(f"    {e.get('starts_at') or 'no start time'}  "
                     f"{e['prospect_name']}, {e['company']} [{e['sender_id']}]")
        if len(ahead) > LIST_LIMIT:
            L.append(f"    and {len(ahead) - LIST_LIMIT} more")
    else:
        L.append("  Nothing on the calendar for next week.")

    for note in m.get("notes") or []:
        L.append(f"  Note: {note}")

    L.append("")
    L.append("ACTIVITY")
    L.append(f"  emails sent       {t['sends']}"
             + (f" (+{t['other_channel_touches']} non-email touches)"
                if t.get("other_channel_touches") else ""))
    L.append(f"  prospects touched {t['prospects']}")
    L.append(f"  reply rate        {_rate(win['rates'].get('reply_rate'))}")
    L.append(f"  positive replies  {_rate(win['rates'].get('positive_reply_rate'))}")
    L.append(f"  (rates below {floor} in the denominator are shown as counts, not percentages)")

    dl = win["deliverability"]
    L.append("")
    L.append("DELIVERABILITY")
    L.append(f"  status            {dl['status'].upper()}")
    L.append(f"  bounce rate       {_rate(dl['bounce_rate'])} "
             f"(warn {dl['warn']:.1%}, halt {dl['halt']:.1%})")
    L.append("  auth              " + "  ".join(
        f"{k.upper()}={v['status']}" for k, v in payload["config"]["auth"].items()))

    breaches = _cap_breaches(cfg, conn, start, end)
    L.append("")
    L.append("CAP BREACHES")
    if breaches:
        for b in breaches:
            L.append(f"  {b['day']}  {b['sender_id']}: {b['detail']}")
        L.append("  A breach is an approval-gate conversation, not a config edit.")
    else:
        L.append("  None. Every sender stayed inside its daily cap all week.")

    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true",
                    help="actually post through the notify adapter (default: print only)")
    ap.add_argument("--week", default=None,
                    help="ISO date inside the week to report; defaults to now")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))
    as_of = _as_of(cfg, args.week)
    payload = report.build(cfg, conn, now=as_of)
    text = compose(cfg, conn, payload, as_of)
    conn.close()

    print(text)
    print()

    ad = adapters.load(cfg, "notify")
    dest = cfg.get("escalation.digest_to")

    if ad is None:
        print("NOT SENT. adapters.notify is `none`, so there is no destination "
              "configured for this digest.")
        print("  To wire one up: set `adapters.notify` in the config to an "
              "installed notify adapter (see `adapters/notify/`), set "
              "`escalation.digest_to` to the channel or address, fill in the "
              "matching `adapter_config` block, then re-run with --send.")
        return 0

    if not args.send:
        print(f"NOT SENT. Dry run. Would post via notify:{ad.name}"
              + (f" to {dest}." if dest else ".")
              + " Re-run with --send to post it.")
        return 0

    if not dest:
        # The adapter knows its own channel, so this is a warning rather than a
        # refusal, but a digest with no declared audience is usually a mistake.
        print("WARNING: escalation.digest_to is null, so the destination is "
              "whatever the notify adapter is configured with.")

    try:
        ad.post(adapters.context(cfg, ad), text)
    except Exception as e:
        print(f"SEND FAILED via notify:{ad.name}: {e}", file=sys.stderr)
        return 1
    print(f"Posted via notify:{ad.name}" + (f" to {dest}." if dest else "."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
