"""Edit, delete, or list meal rows.

Subcommands:
  list    Print recent meals (default 10) as JSON, newest first
  update  Update fields on a meal by id (only fields you pass are changed)
  delete  Delete a meal by id

Examples:
  uv run edit_meal.py list --days 2
  uv run edit_meal.py update --id 7 --calories 650 --desc "Chicken bowl (no rice)"
  uv run edit_meal.py update --id 7 --ts 2026-05-19T13:15:00-07:00
  uv run edit_meal.py delete --id 7
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta
from db import connect, TZ, today_local

EDITABLE = {
    "name": "name",
    "desc": "description",
    "calories": "calories",
    "protein": "protein_g",
    "fat": "fat_g",
    "carbs": "carbs_g",
}


def cmd_list(args: argparse.Namespace) -> None:
    with connect() as conn:
        if args.days:
            since = (today_local() - timedelta(days=args.days - 1)).isoformat()
            rows = conn.execute(
                """SELECT id, ts, local_day, name, description, calories, protein_g, fat_g, carbs_g
                   FROM meals WHERE local_day >= ? ORDER BY ts DESC""",
                (since,),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, ts, local_day, name, description, calories, protein_g, fat_g, carbs_g
                   FROM meals ORDER BY ts DESC LIMIT ?""",
                (args.limit,),
            ).fetchall()
    print(json.dumps([dict(r) for r in rows], indent=2, default=str))


def cmd_update(args: argparse.Namespace) -> None:
    sets: list[str] = []
    vals: list = []

    for cli_key, col in EDITABLE.items():
        v = getattr(args, cli_key)
        if v is not None:
            sets.append(f"{col} = ?")
            vals.append(v)

    if args.ts is not None:
        dt = datetime.fromisoformat(args.ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=TZ)
        dt = dt.astimezone(TZ)
        sets.append("ts = ?")
        vals.append(dt.isoformat())
        sets.append("local_day = ?")
        vals.append(dt.date().isoformat())

    if not sets:
        print("Nothing to update — pass at least one field.", file=sys.stderr)
        sys.exit(2)

    vals.append(args.id)
    with connect() as conn:
        before = conn.execute("SELECT * FROM meals WHERE id = ?", (args.id,)).fetchone()
        if not before:
            print(f"No meal with id={args.id}", file=sys.stderr)
            sys.exit(1)
        conn.execute(f"UPDATE meals SET {', '.join(sets)} WHERE id = ?", vals)
        conn.commit()
        after = conn.execute("SELECT * FROM meals WHERE id = ?", (args.id,)).fetchone()

    print(json.dumps({"before": dict(before), "after": dict(after)}, indent=2, default=str))


def cmd_delete(args: argparse.Namespace) -> None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM meals WHERE id = ?", (args.id,)).fetchone()
        if not row:
            print(f"No meal with id={args.id}", file=sys.stderr)
            sys.exit(1)
        conn.execute("DELETE FROM meals WHERE id = ?", (args.id,))
        conn.commit()
    print(json.dumps({"deleted": dict(row)}, indent=2, default=str))


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pl = sub.add_parser("list", help="List recent meals")
    pl.add_argument("--limit", type=int, default=10)
    pl.add_argument("--days", type=int, default=None, help="Override limit; show last N PST days")
    pl.set_defaults(func=cmd_list)

    pu = sub.add_parser("update", help="Update fields on a meal by id")
    pu.add_argument("--id", type=int, required=True)
    pu.add_argument("--name")
    pu.add_argument("--desc")
    pu.add_argument("--calories", type=float)
    pu.add_argument("--protein", type=float)
    pu.add_argument("--fat", type=float)
    pu.add_argument("--carbs", type=float)
    pu.add_argument("--ts", help="ISO timestamp; assumed PST if no offset given")
    pu.set_defaults(func=cmd_update)

    pd = sub.add_parser("delete", help="Delete a meal by id")
    pd.add_argument("--id", type=int, required=True)
    pd.set_defaults(func=cmd_delete)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
