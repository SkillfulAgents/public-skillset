---
name: Nutrition Status
description: Generate the user's current nutrition status card — an Apple-Fitness-style PNG with two concentric progress rings (calories outer, protein inner) and all 4 macros listed on the right. Use whenever the user asks for status, "how am I doing today", "rings", "where am I at", "status card", or similar. Output the image via deliver_file.
---

# Nutrition Status

Generates a status card PNG showing today's progress vs. goal.

## How to use

1. Run:
   ```bash
   cd /workspace/nutrition/scripts && uv run --with pillow status_card.py
   ```
   This writes `/workspace/nutrition/output/status.png` and prints the path. Add `--date YYYY-MM-DD` for a different day.
2. Deliver the file with `mcp__user-input__deliver_file` pointing at `/workspace/nutrition/output/status.png`.
3. Add a 1-line text summary like "1,420 / 2,200 kcal — 64%. Protein 88 / 160 g — 55%."

## Notes
- Day is computed in America/Los_Angeles.
- The outer ring is calories, inner is protein. Fat and carbs are shown numerically only (per user's request — 2 rings).
- If `data/goal.json` is missing, a sensible default is used and you should suggest running `/set-nutrition-goal`.
