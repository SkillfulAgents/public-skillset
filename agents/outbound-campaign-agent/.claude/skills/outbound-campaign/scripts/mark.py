#!/usr/bin/env python3
"""Record what only a human can know.

  uv run --with pyyaml mark.py --prospect 12 --linkedin-accepted
  uv run --with pyyaml mark.py --prospect 12 --replied "sounds interesting" \
      [--sentiment positive|referral|objection|not_now|negative] [--channel linkedin]
  uv run --with pyyaml mark.py --prospect 12 --unsubscribed
  uv run --with pyyaml mark.py --meeting 3 --meeting-status no_show

The automated detectors cover email replies (sender adapter) and calendar
bookings (calendar adapter). Everything else arrives as the operator saying it
out loud: "Dana accepted my invite", "he replied on LinkedIn", "she no-showed".
Without a recording path those facts live in chat history and the cadence keeps
firing at people who already answered. This writes them where the motion reads:

  --linkedin-accepted   unlocks cadence steps conditioned on invite_accepted
  --replied             STOPS the cadence, like every reply, and logs it
  --unsubscribed        terminal; the local suppression layer sees it
  --meeting-status      no_show / held / cancelled on a meetings row, because a
                        calendar can prove a meeting was scheduled and not
                        cancelled but never that anyone showed up
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import config as cfgmod, db  # noqa: E402

SENTIMENTS = {"positive", "referral", "objection", "not_now", "negative",
              "unsubscribe"}
MEETING_STATUSES = {"held", "no_show", "cancelled", "booked"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prospect", type=int)
    ap.add_argument("--meeting", type=int, help="meetings.id")
    ap.add_argument("--linkedin-accepted", action="store_true")
    ap.add_argument("--replied", metavar="SNIPPET",
                    help="what they said, roughly; stops the cadence")
    ap.add_argument("--sentiment", choices=sorted(SENTIMENTS))
    ap.add_argument("--channel", default="linkedin",
                    help="where the manual reply arrived (default linkedin)")
    ap.add_argument("--unsubscribed", action="store_true")
    ap.add_argument("--meeting-status", choices=sorted(MEETING_STATUSES))
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    actions = [args.linkedin_accepted, args.replied is not None,
               args.unsubscribed, args.meeting_status is not None]
    if sum(bool(a) for a in actions) != 1:
        ap.error("exactly one of --linkedin-accepted / --replied / "
                 "--unsubscribed / --meeting-status")

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    if args.meeting_status:
        if args.meeting is None:
            ap.error("--meeting-status needs --meeting <id>")
        row = conn.execute("SELECT * FROM meetings WHERE id = ?",
                           (args.meeting,)).fetchone()
        if row is None:
            print(f"no meeting with id {args.meeting}", file=sys.stderr)
            return 1
        with db.transaction(conn):
            conn.execute(
                "UPDATE meetings SET status = ?, source = 'manual', "
                "detected_at = datetime('now') WHERE id = ?",
                (args.meeting_status, args.meeting))
        print(f"meeting {args.meeting} ({row['title'] or 'untitled'}, "
              f"{row['starts_at']}) marked {args.meeting_status}")
        return 0

    if args.prospect is None:
        ap.error("this action needs --prospect <id>")
    p = conn.execute("SELECT * FROM prospects WHERE id = ?",
                     (args.prospect,)).fetchone()
    if p is None:
        print(f"no prospect with id {args.prospect}", file=sys.stderr)
        return 1

    if args.linkedin_accepted:
        with db.transaction(conn):
            conn.execute("UPDATE prospects SET linkedin_accepted = 1 WHERE id = ?",
                         (args.prospect,))
            db.log_decision(conn, "linkedin", "accepted",
                            "operator reported invite accepted",
                            layer="manual", prospect_id=args.prospect)
        print(f"{p['name']}: invite accepted. Cadence steps conditioned on "
              f"invite_accepted are now eligible.")
        return 0

    if args.unsubscribed:
        with db.transaction(conn):
            conn.execute("UPDATE prospects SET status = 'unsubscribed' WHERE id = ?",
                         (args.prospect,))
            db.log_decision(conn, "suppression", "unsubscribed",
                            "operator reported opt-out", layer="manual",
                            prospect_id=args.prospect)
        print(f"{p['name']}: unsubscribed. Terminal; nothing sends to them again.")
        return 0

    # --replied
    sentiment = args.sentiment
    with db.transaction(conn):
        conn.execute(
            "INSERT INTO replies (prospect_id, snippet, sentiment, is_positive,"
            " confidence) VALUES (?,?,?,?,?)",
            (args.prospect, f"[{args.channel}] {args.replied}", sentiment,
             1 if sentiment in ("positive", "referral") else
             0 if sentiment else None,
             "operator_reported"))
        conn.execute("UPDATE prospects SET status = 'replied' WHERE id = ?",
                     (args.prospect,))
        db.log_decision(conn, "reply", "manual",
                        f"operator reported a {args.channel} reply",
                        layer="manual", prospect_id=args.prospect)
    print(f"{p['name']}: reply recorded ({args.channel}"
          + (f", {sentiment}" if sentiment else "") + "). Cadence stopped.")
    if not sentiment:
        print("  no --sentiment given; the reply board shows it unclassified "
              "until one is set")
    return 0


if __name__ == "__main__":
    sys.exit(main())
