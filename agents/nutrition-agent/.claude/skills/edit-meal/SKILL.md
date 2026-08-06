---
name: Edit Meal
description: Edit, fix, or delete a previously logged meal row. Use whenever the user says "fix that last meal", "I actually had 2 of those", "change the calories on X", "delete that entry", "wrong meal", "undo that log", or otherwise wants to modify what's already in the nutrition DB. Always look up the target row first via `edit_meal.py list` so you have the correct id, then run `update` or `delete`.
---

# Edit Meal

Edits or deletes a row in `/workspace/nutrition/data/nutrition.db` using `scripts/edit_meal.py`.

## How to use

1. **Find the id.** Almost always start here — the user refers to meals by description ("the burrito"), not id.
   ```bash
   cd /workspace/nutrition/scripts && uv run edit_meal.py list --days 2
   ```
   Use `--limit N` for the N newest rows across all time, or `--days N` for the last N PST days.

2. **Pick the right row.** If multiple matches, confirm with the user before mutating ("Did you mean the 1:15pm chicken bowl or the 6pm one?").

3. **Update** — pass only the fields that change:
   ```bash
   uv run edit_meal.py update --id 7 --calories 650 --protein 50
   uv run edit_meal.py update --id 7 --desc "Chicken bowl (no rice)"
   uv run edit_meal.py update --id 7 --ts 2026-05-19T13:15:00-07:00
   ```
   The script prints `before` and `after` JSON — confirm to the user what changed.

4. **Delete** when the meal shouldn't exist at all:
   ```bash
   uv run edit_meal.py delete --id 7
   ```

## Notes
- Day boundaries are PST — if you change `--ts`, `local_day` is recomputed automatically.
- Don't re-log a meal as a fix. Edit the existing row so totals and history stay correct.
- After a meaningful edit, optionally show new daily totals: `uv run today.py`.
