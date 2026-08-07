#!/usr/bin/env python3
"""Meeting tracking, sourced from the sender's calendar.

  uv run --with pyyaml meetings.py [--since ISO] [--until ISO] [--sender ID] [--json]

Meetings booked are the outcome this whole motion exists to produce, and a reply
is not how most of them arrive. The common path is a prospect clicking a booking
link and never writing back, which the mailbox never sees and the `replies`
table therefore cannot record. This reads the calendar instead and writes
first-class `meetings` rows.

Matching is exact: an event counts only when one of its attendee addresses is a
known prospect's work email, case-folded. Nothing is matched on name or company.
A false positive here corrupts the one metric the operator trusts, and a missed
meeting is cheap by comparison.

Promotion from `booked` to `held` happens when the event has ended and was not
cancelled. This is scheduled-and-not-cancelled, not confirmed attendance. A
calendar records intent, never who dialled in, so nothing in this script can
produce a `no_show`. That status exists for a human to set.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters, config as cfgmod, db  # noqa: E402

DEFAULT_DAYS_BACK = 30
DEFAULT_DAYS_FORWARD = 60

HELD_CAVEAT = (
    "'held' means scheduled-and-not-cancelled, not confirmed attendance. A "
    "calendar cannot tell you who showed up, so nothing here is ever marked "
    "no_show. Set that by hand when you know."
)

OFF_MESSAGE = """Meeting tracking is off: adapters.calendar is 'none'.

Most booked meetings never produce a reply, so with the slot disabled the only
meetings on record are the ones a human flagged. A low number means nothing is
watching, not that nothing is booking.

To turn it on:
  1. set `adapters.calendar: google` in {config}
  2. fill in `adapter_config.google_calendar.connected_account_id_env`
  3. give each sender a `calendar_id` (defaults to their own address)
Then re-run this script."""

# Statuses that outrank a meeting, so a booking never quietly un-suppresses
# someone who asked not to be contacted.
_NEVER_DOWNGRADE = {"meeting", "unsubscribed", "suppressed"}


def _parse(value: str, label: str) -> dt.datetime:
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = dt.datetime.fromisoformat(f"{text}T00:00:00")
        except ValueError as e:
            raise SystemExit(f"--{label} is not ISO8601: {value!r}") from e
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _as_utc(value: str | None) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def prospects_by_email(conn) -> dict[str, dict]:
    """Work email -> prospect. The only key this script will ever match on."""
    index: dict[str, dict] = {}
    for row in conn.execute(
            "SELECT id, name, email, company, status FROM prospects "
            "WHERE email IS NOT NULL AND email != ''").fetchall():
        index.setdefault(row["email"].casefold(), dict(row))
    return index


def calendar_id_for(sender: dict) -> str:
    return str(sender.get("calendar_id") or sender.get("email") or "").strip()


def existing_meeting(conn, provider: str, event_id: str):
    return conn.execute(
        "SELECT * FROM meetings WHERE provider = ? AND provider_event_id = ?",
        (provider, event_id)).fetchone()


def classify(ev: dict, now: dt.datetime) -> str:
    if ev.get("cancelled"):
        return "cancelled"
    ends = _as_utc(ev.get("ends_at"))
    if ends and ends < now:
        return "held"
    return "booked"


def outcome_of(prior, final: str) -> str:
    if prior is None:
        return "new"
    if prior["status"] == final:
        return "unchanged"
    if final == "held":
        return "promoted_held"
    if final == "cancelled":
        return "cancelled"
    return "updated"


def sync_sender(cfg, conn, ad, sender: dict, by_email: dict,
                since: str, until: str, now: dt.datetime) -> dict:
    cal_id = calendar_id_for(sender)
    result = {
        "sender_id": sender.get("id"),
        "calendar_id": cal_id,
        "events_read": 0,
        "matched": 0,
        "new": 0,
        "promoted_held": 0,
        "cancelled": 0,
        "updated": 0,
        "unchanged": 0,
        "multi_prospect": 0,
        "meetings": [],
        "error": None,
    }
    if not cal_id:
        result["error"] = ("no calendar_id and no email on this sender; "
                           "nothing to read")
        return result

    ctx = adapters.context(cfg, ad)
    try:
        evs = ad.events(ctx, cal_id, since, until) or []
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        return result
    result["events_read"] = len(evs)

    with db.transaction(conn):
        for ev in evs:
            event_id = ev.get("provider_event_id")
            if not event_id:
                continue

            prior = existing_meeting(conn, ad.name, event_id)
            attendees = [str(a).casefold() for a in (ev.get("attendees") or []) if a]
            matched = [by_email[a] for a in attendees if a in by_email]

            if not matched:
                # Google strips the attendee list off a deleted event, so a
                # cancellation can only be identified by the row we already
                # wrote when the identity was established. Anything else with
                # no prospect attendee is an internal event.
                if ev.get("cancelled") and prior:
                    matched = [{"id": prior["prospect_id"],
                                "email": prior["attendee_email"],
                                "name": None, "status": None}]
                else:
                    continue

            result["matched"] += 1
            if len(matched) > 1:
                result["multi_prospect"] += 1
            prospect = matched[0]

            status = classify(ev, now)
            # Mirror upsert_meeting's refusal to clobber a locally decided
            # status, so the printed summary matches what was actually stored.
            final = status
            if (status == "booked" and prior
                    and prior["status"] in ("held", "no_show")):
                final = prior["status"]
            outcome = outcome_of(prior, final)

            mid = db.upsert_meeting(conn, {
                "prospect_id": prospect["id"],
                "sender_id": sender.get("id"),
                "provider": ad.name,
                "provider_event_id": event_id,
                "title": ev.get("title") or "",
                "attendee_email": prospect.get("email"),
                "starts_at": ev.get("starts_at"),
                "ends_at": ev.get("ends_at"),
                "status": status,
                "source": "calendar",
            })

            if final in ("booked", "held") and prospect["id"]:
                conn.execute(
                    "UPDATE prospects SET status = 'meeting' WHERE id = ? "
                    f"AND status NOT IN ({','.join('?' * len(_NEVER_DOWNGRADE))})",
                    (prospect["id"], *sorted(_NEVER_DOWNGRADE)))

            db.log_decision(
                conn, "meeting", outcome,
                f"{final} {ev.get('starts_at') or '?'} {(ev.get('title') or '')[:60]}",
                layer=ad.name, prospect_id=prospect["id"], ref=event_id)

            result[outcome] += 1
            result["meetings"].append({
                "meeting_id": mid,
                "prospect_id": prospect["id"],
                "prospect": prospect.get("name"),
                "attendee_email": prospect.get("email"),
                "title": ev.get("title") or "",
                "starts_at": ev.get("starts_at"),
                "ends_at": ev.get("ends_at"),
                "status": final,
                "outcome": outcome,
            })
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default=None, help="ISO8601 lower bound (UTC)")
    ap.add_argument("--until", default=None, help="ISO8601 upper bound (UTC)")
    ap.add_argument("--sender", default=None, help="only this sender id")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    ad = adapters.load(cfg, "calendar")
    if ad is None:
        message = OFF_MESSAGE.format(config=cfg.config_path.name)
        if args.json:
            print(json.dumps({"enabled": False, "reason": "adapters.calendar is 'none'",
                              "message": message}, indent=2))
        else:
            print(message)
        return 0

    now = dt.datetime.now(dt.timezone.utc)
    since = (_parse(args.since, "since") if args.since
             else now - dt.timedelta(days=DEFAULT_DAYS_BACK))
    until = (_parse(args.until, "until") if args.until
             else now + dt.timedelta(days=DEFAULT_DAYS_FORWARD))
    if since >= until:
        print(f"--since {since.isoformat()} is not before --until {until.isoformat()}",
              file=sys.stderr)
        return 2

    senders = cfg.senders
    if args.sender:
        senders = [s for s in senders if s.get("id") == args.sender]
        if not senders:
            print(f"unknown sender {args.sender!r}; configured: "
                  f"{[s.get('id') for s in cfg.senders]}", file=sys.stderr)
            return 2

    by_email = prospects_by_email(conn)
    per_sender = [sync_sender(cfg, conn, ad, s, by_email,
                              since.isoformat(), until.isoformat(), now)
                  for s in senders]

    totals = {k: sum(r[k] for r in per_sender)
              for k in ("events_read", "matched", "new", "promoted_held",
                        "cancelled", "updated", "unchanged", "multi_prospect")}
    on_file = conn.execute("SELECT COUNT(*) FROM meetings").fetchone()[0]
    errors = [r for r in per_sender if r["error"]]

    result = {
        "enabled": True,
        "provider": ad.name,
        "at": now.isoformat(),
        "window": {"since": since.isoformat(), "until": until.isoformat()},
        "prospects_indexed": len(by_email),
        "senders": per_sender,
        "totals": totals,
        "meetings_on_file": on_file,
        "held_means": ("scheduled-and-not-cancelled, not confirmed attendance; "
                       "no_show cannot be detected from a calendar"),
    }

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 1 if errors else 0

    print(f"Meeting sync via {ad.name} at {now.isoformat()}")
    print(f"  window  {since.date()} .. {until.date()}"
          f"  |  {len(by_email)} prospect email(s) indexed\n")

    for r in per_sender:
        head = f"  {r['sender_id']}  ({r['calendar_id'] or 'no calendar'})"
        if r["error"]:
            print(f"{head}\n      ERROR: {r['error']}")
            continue
        print(f"{head}\n      {r['events_read']} event(s) read, "
              f"{r['matched']} matched a prospect")
        print(f"      {r['new']} new, {r['promoted_held']} promoted to held, "
              f"{r['cancelled']} cancelled, {r['updated']} updated, "
              f"{r['unchanged']} unchanged")
        for m in r["meetings"][:10]:
            if m["outcome"] == "unchanged":
                continue
            print(f"        {m['outcome']:<14} {m['status']:<10} "
                  f"{(m['starts_at'] or '?')[:16]}  "
                  f"{m['attendee_email'] or '?'}  {m['title'][:40]}")
        if r["multi_prospect"]:
            print(f"      NOTE: {r['multi_prospect']} event(s) had more than one "
                  f"prospect attendee; recorded against the first")

    print(f"\nTOTAL  {totals['new']} new, {totals['promoted_held']} promoted to held, "
          f"{totals['cancelled']} cancelled  ({on_file} meeting(s) on file)")
    print(f"\n{HELD_CAVEAT}")
    if errors:
        print(f"\n{len(errors)} sender(s) failed to sync. The counts above are "
              f"incomplete.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
