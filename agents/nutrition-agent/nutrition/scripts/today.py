"""Print today's nutrition totals + goal as JSON.

Optional --date YYYY-MM-DD to query a different day.
"""
from __future__ import annotations
import argparse
import json
from db import connect, today_local, GOAL_PATH


def load_goal() -> dict:
    if GOAL_PATH.exists():
        return json.loads(GOAL_PATH.read_text())
    return {"calories": 2200, "protein_g": 160, "fat_g": 70, "carbs_g": 220, "rationale": "default placeholder"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=None)
    args = p.parse_args()

    day = args.date or today_local().isoformat()

    with connect() as conn:
        rows = conn.execute(
            """SELECT id, ts, name, description, calories, protein_g, fat_g, carbs_g
               FROM meals WHERE local_day = ? ORDER BY ts""",
            (day,),
        ).fetchall()

    totals = {"calories": 0.0, "protein_g": 0.0, "fat_g": 0.0, "carbs_g": 0.0}
    meals = []
    for r in rows:
        meals.append(dict(r))
        for k in totals:
            totals[k] += r[k]

    goal = load_goal()
    print(json.dumps({"date": day, "goal": goal, "totals": totals, "meals": meals}, indent=2, default=str))


if __name__ == "__main__":
    main()
