"""Persist a daily nutrition goal. Writes to goal.json (current) and goals table (history)."""
from __future__ import annotations
import argparse
import json
from db import connect, today_local, GOAL_PATH


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--calories", type=float, required=True)
    p.add_argument("--protein", type=float, required=True)
    p.add_argument("--fat", type=float, required=True)
    p.add_argument("--carbs", type=float, required=True)
    p.add_argument("--rationale", default="")
    args = p.parse_args()

    payload = {
        "calories": args.calories,
        "protein_g": args.protein,
        "fat_g": args.fat,
        "carbs_g": args.carbs,
        "rationale": args.rationale,
    }
    GOAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    GOAL_PATH.write_text(json.dumps(payload, indent=2))

    with connect() as conn:
        conn.execute(
            """INSERT INTO goals (effective_from, calories, protein_g, fat_g, carbs_g, rationale)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (today_local().isoformat(), args.calories, args.protein, args.fat, args.carbs, args.rationale),
        )
        conn.commit()

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
