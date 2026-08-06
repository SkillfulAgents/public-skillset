# Nutrition Agent

> Track calories, macros, and body weight with fast meal logging, a visual dashboard, and smart goal setting.

## What it does

A personal nutrition tracker you can message naturally. Describe what you ate (or send a photo), and the agent estimates macros and logs it. It tracks daily calories, protein, fat, and carbs against your goal, logs body weight over time, and gives you a beautiful dashboard to see trends. It can also research restaurant dishes before you order.

## What you'll need

- **Accounts:** None required. Optionally connect Telegram for on-the-go logging.
- **API keys:** None.

## Getting started

1. Import this template into Superagent.
2. On import, a setup session starts automatically. The **agent-onboarding** skill will:
   - Ask your name
   - Collect body metrics (sex, age, height, weight, activity level)
   - Calculate your TDEE and propose daily calorie + macro targets
   - Log your baseline weight
   - Ask about coffee/logging preferences
   - Optionally connect Telegram so you can log meals from your phone
3. Once setup finishes, just tell the agent what you ate!

You can re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## What's inside

- `CLAUDE.md` — the agent's instructions (logging style, response format).
- `.claude/skills/agent-onboarding/` — first-run setup: TDEE interview, goal setting, Telegram connection.
- `.claude/skills/log-meal/` — log food from description or photo.
- `.claude/skills/log-weight/` — record daily body weight.
- `.claude/skills/edit-meal/` — fix or delete a logged meal.
- `.claude/skills/nutrition-status/` — generate Apple-Fitness-style progress ring PNG.
- `.claude/skills/nutrition-dashboard/` — open the interactive web dashboard.
- `.claude/skills/research-food/` — look up restaurant dish nutrition before ordering.
- `.claude/skills/set-nutrition-goal/` — recalculate TDEE and update goals anytime.
- `nutrition/` — Python scripts, SQLite database, and meal cheatsheet.
- `artifacts/nutrition-dashboard/` — Bun-based dashboard (calories, macros, weight charts, meal history).
- `nutrition/data/nutrition.db` + `nutrition/data/nutrition.db.bootstrap.sql` — empty database and schema.

## Notes

- All day boundaries use **America/Los_Angeles** (PST/PDT).
- The agent estimates macros from food descriptions and photos — it's not a precision scale, but it's consistent and fast.
- The cheatsheet (`nutrition/cheatsheet.md`) builds up over time with dishes you eat often, so estimates get faster and more accurate.
- To reset everything, delete `nutrition/data/nutrition.db` and re-run `uv run nutrition/scripts/init_db.py`.
