"""Insert a meal record. Called by the log-meal skill after the agent estimates macros.

Usage:
  uv run log_meal.py --name lunch --desc "Chicken burrito bowl" \\
    --calories 720 --protein 48 --fat 22 --carbs 78 [--ts 2026-05-19T13:15:00-07:00]

If --ts is omitted, uses current PST time.
"""
from __future__ import annotations
import argparse
import json
from db import connect, now_local, TZ
from datetime import datetime


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True, help="breakfast|lunch|dinner|snack")
    p.add_argument("--desc", required=True)
    p.add_argument("--calories", type=float, required=True)
    p.add_argument("--protein", type=float, required=True)
    p.add_argument("--fat", type=float, required=True)
    p.add_argument("--carbs", type=float, required=True)
    p.add_argument("--ts", default=None, help="ISO timestamp; default = now (PST)")
    args = p.parse_args()

    if args.ts:
        dt = datetime.fromisoformat(args.ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ)
        dt = dt.astimezone(TZ)
    else:
        dt = now_local()

    local_day = dt.date().isoformat()
    # Truncate to millisecond precision — JS Date() rejects microseconds in some browsers
    dt = dt.replace(microsecond=(dt.microsecond // 1000) * 1000)
    ts_iso = dt.isoformat(timespec="milliseconds")

    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO meals (ts, local_day, name, description, calories, protein_g, fat_g, carbs_g)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ts_iso, local_day, args.name, args.desc, args.calories, args.protein, args.fat, args.carbs),
        )
        conn.commit()
        meal_id = cur.lastrowid

    print(json.dumps({"id": meal_id, "ts": ts_iso, "local_day": local_day}, indent=2))


if __name__ == "__main__":
    main()
