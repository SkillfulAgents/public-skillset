"""Emit daily history JSON for the dashboard. Defaults to last 30 days."""
from __future__ import annotations
import argparse
import json
from datetime import timedelta
from db import connect, today_local, GOAL_PATH


def load_goal() -> dict:
    if GOAL_PATH.exists():
        return json.loads(GOAL_PATH.read_text())
    return {"calories": 2200, "protein_g": 160, "fat_g": 70, "carbs_g": 220}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=30)
    args = p.parse_args()

    end = today_local()
    start = end - timedelta(days=args.days - 1)

    with connect() as conn:
        rows = conn.execute(
            """SELECT local_day,
                      SUM(calories) AS calories,
                      SUM(protein_g) AS protein_g,
                      SUM(fat_g) AS fat_g,
                      SUM(carbs_g) AS carbs_g,
                      COUNT(*) AS meal_count
               FROM meals
               WHERE local_day >= ? AND local_day <= ?
               GROUP BY local_day
               ORDER BY local_day""",
            (start.isoformat(), end.isoformat()),
        ).fetchall()

        meals = conn.execute(
            """SELECT id, ts, local_day, name, description, calories, protein_g, fat_g, carbs_g
               FROM meals WHERE local_day >= ? AND local_day <= ? ORDER BY ts DESC""",
            (start.isoformat(), end.isoformat()),
        ).fetchall()

    days_by = {r["local_day"]: dict(r) for r in rows}
    days = []
    d = start
    while d <= end:
        key = d.isoformat()
        row = days_by.get(key, {"local_day": key, "calories": 0, "protein_g": 0, "fat_g": 0, "carbs_g": 0, "meal_count": 0})
        days.append(row)
        d += timedelta(days=1)

    print(json.dumps({
        "goal": load_goal(),
        "today": end.isoformat(),
        "days": days,
        "meals": [dict(m) for m in meals],
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
