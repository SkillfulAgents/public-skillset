---
name: Log Meal
description: Log a meal the user just ate into the nutrition SQLite DB. Use whenever the user describes food they've eaten, sends a meal photo, or says something like "log this", "I just had X", "add to my food log". You estimate macros (calories, protein, fat, carbs) from the description/image, classify the meal name (breakfast/lunch/dinner/snack) from the current PST time, and insert via the log_meal.py script. After logging, briefly confirm what was logged and the running daily totals.
---

# Log Meal

Logs a meal into `/workspace/nutrition/data/nutrition.db`.

## How to use

1. Look at the description and/or any attached image of the meal.
2. **Check the cheatsheet first.** Grep `/workspace/nutrition/cheatsheet.md` for any plausible match (dish name, restaurant, aliases, ingredients). If you find one, use those macros — sum base + any chosen add-ons. This beats guessing AND beats web research.
3. **Estimate macros** (only if no cheatsheet hit): calories (kcal), protein (g), fat (g), carbs (g). Be reasonable — use standard reference portions if the user doesn't specify quantity. If a portion is highly ambiguous, ask one quick clarifying question; otherwise just estimate and note the assumption.
   - If the meal is a specific dish from a specific restaurant (DoorDash, UberEats, dine-in at a known place), delegate the estimate to the `research-food` skill — it'll find official nutrition or build a defensible estimate from the menu listing + photo.
   - If the meal looks like something the user eats regularly (a repeating home recipe, a frequent order), offer to add it to the cheatsheet after logging.
4. **Classify meal name** from current PST time unless the user says otherwise:
   - 4:00–10:30 → `breakfast`
   - 10:30–14:30 → `lunch`
   - 14:30–17:00 → `snack`
   - 17:00–21:30 → `dinner`
   - otherwise → `snack`
5. **Insert** with:
   ```bash
   cd /workspace/nutrition/scripts && uv run --with pillow log_meal.py \
     --name <breakfast|lunch|dinner|snack> \
     --desc "<short description>" \
     --calories <kcal> --protein <g> --fat <g> --carbs <g>
   ```
   Pass `--ts <ISO>` only if the user explicitly says the meal was at a different time.
6. **Confirm briefly** — show what was logged AND the new daily totals. Run:
   ```bash
   cd /workspace/nutrition/scripts && uv run today.py
   ```
   Summarize in 2–3 lines: macros logged, then "Today so far: X / Y kcal, P / Q g protein".

7. **Update the cheatsheet** at `/workspace/nutrition/cheatsheet.md` if this meal is repeatable. Follow the existing format. Decision rule:
   - **Repeatable** (write/update an entry): named restaurant dishes, specific home recipes with concrete ingredients/portions, packaged products with stable macros (yogurts, bars, shakes), staple ingredients used in multiple meals.
   - **One-off** (skip): generic items with no specific quantity ("some nuts", "a piece of fruit"), miscellaneous restaurant snacks, anything the user describes vaguely.
   - If an entry for this dish + source already exists, **update in place** (bump `last_verified`, refine macros if they shifted) rather than duplicating. If the meal had add-ons, record those as `add-ons:` deltas so the base entry stays portable.
   - Briefly mention what you added/updated (one short line).

## Notes
- Day boundaries are in America/Los_Angeles (PST/PDT), not UTC. The scripts handle this — just call them.
- Don't generate a status card automatically; the user has a separate skill for that.
