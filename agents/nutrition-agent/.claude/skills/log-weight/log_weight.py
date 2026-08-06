#!/usr/bin/env python3
"""Log a body-weight reading into the nutrition DB (weights table)."""
import argparse
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

DB = "/workspace/nutrition/data/nutrition.db"
TZ = ZoneInfo("America/Los_Angeles")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("weight_lbs", type=float)
    p.add_argument("--day", help="local day YYYY-MM-DD (default: today PST)")
    p.add_argument("--note")
    a = p.parse_args()
    day = a.day or datetime.now(TZ).strftime("%Y-%m-%d")
    c = sqlite3.connect(DB)
    c.execute(
        "INSERT INTO weights (local_day, weight_lbs, note) VALUES (?, ?, ?) "
        "ON CONFLICT(local_day) DO UPDATE SET weight_lbs=excluded.weight_lbs, "
        "note=COALESCE(excluded.note, weights.note)",
        (day, a.weight_lbs, a.note),
    )
    c.commit()
    prev = c.execute(
        "SELECT local_day, weight_lbs FROM weights WHERE local_day < ? "
        "ORDER BY local_day DESC LIMIT 1",
        (day,),
    ).fetchone()
    print(f"Logged {a.weight_lbs} lbs for {day}.")
    if prev:
        d = a.weight_lbs - prev[1]
        print(f"Previous ({prev[0]}): {prev[1]} lbs  ({d:+.1f} lbs)")


if __name__ == "__main__":
    main()
