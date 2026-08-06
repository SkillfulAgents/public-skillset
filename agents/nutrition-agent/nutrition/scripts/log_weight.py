"""Log a daily body weight (lbs). One row per local day — re-logging overwrites.

Usage:
  uv run log_weight.py --lbs 166.6
  uv run log_weight.py --lbs 170 --day 2026-05-18
  uv run log_weight.py --lbs 166.6 --note "post-workout"
"""
from __future__ import annotations
import argparse
import json
from db import connect, today_local


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--lbs", type=float, required=True)
    p.add_argument("--day", default=None, help="local YYYY-MM-DD; default = today (PST)")
    p.add_argument("--note", default=None)
    args = p.parse_args()

    day = args.day or today_local().isoformat()

    with connect() as conn:
        conn.execute(
            """INSERT INTO weights (local_day, weight_lbs, note) VALUES (?, ?, ?)
               ON CONFLICT(local_day) DO UPDATE SET
                 weight_lbs = excluded.weight_lbs,
                 note = excluded.note""",
            (day, args.lbs, args.note),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, local_day, weight_lbs, note FROM weights WHERE local_day = ?",
            (day,),
        ).fetchone()

    print(json.dumps(dict(row), indent=2))


if __name__ == "__main__":
    main()
