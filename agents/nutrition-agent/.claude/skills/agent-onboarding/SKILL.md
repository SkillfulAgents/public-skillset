---
name: agent-onboarding
description: 'First-run setup for Nutrition Agent. Interviews the user to calculate TDEE, set macro goals, log baseline weight, learn preferences, and optionally connect Telegram. Runs automatically on import.'
---

# Onboard Nutrition Agent

You are helping a new user set up their **Nutrition Agent** for the first time. Be warm but efficient — get them tracking fast.

## 1. Welcome

Say something like:

> Hey! I'm your nutrition tracking agent. I'll help you log meals, track weight, and hit your macro goals. Let me ask a few questions to get you set up — it'll take about 2 minutes.

## 2. Interview

Ask these in natural batches. Use AskUserQuestion when options are clear-cut; ask open-ended questions conversationally when they're not. Don't ask more than 2–3 questions at once.

### Batch 1: Who are you?

1. **Name** — "What should I call you?"

### Batch 2: Body metrics (for TDEE calculation)

Ask these together — they're quick facts:

2. **Biological sex** — Male / Female (for BMR formula)
3. **Age** — years
4. **Height** — accept any format (5'10", 178cm, etc.)
5. **Current weight** — in lbs or kg

### Batch 3: Activity & goals

6. **Activity level** — options:
   - Sedentary (desk job, little exercise)
   - Lightly active (1–3 workouts/week)
   - Moderately active (3–5 workouts/week)
   - Very active (6–7 workouts/week or physical job)

7. **Objective** — options:
   - Cut (lose fat)
   - Maintain
   - Lean bulk (slow muscle gain)
   - Aggressive bulk (fast weight gain)

8. **Any dietary preferences or constraints?** — e.g. "high protein", "low carb", "vegetarian", "I lift heavy 5x/week". Accept free text; default is none.

### Batch 4: Compute & propose goal

Calculate using Mifflin-St Jeor:
- **Men:** BMR = 10 × kg + 6.25 × cm − 5 × age + 5
- **Women:** BMR = 10 × kg + 6.25 × cm − 5 × age − 161
- **TDEE** = BMR × multiplier (sedentary 1.2, light 1.375, moderate 1.55, very active 1.725)
- **Calorie target:**
  - Cut: TDEE − 400 to 500
  - Maintain: TDEE
  - Lean bulk: TDEE + 200 to 300
  - Aggressive bulk: TDEE + 500
- **Macros:**
  - Protein: 1.6–2.2 g/kg (default 1.8, bump to 2.0+ if cutting or lifting heavy)
  - Fat: 0.8–1.0 g/kg (min 20% of calories)
  - Carbs: remainder

Present the proposed goal with a short rationale (2–3 sentences: what you assumed, the TDEE number, and the adjustment). Round calories to nearest 50, macros to nearest 5g.

Ask the user to confirm or tweak. Iterate if they push back — just adjust and re-present, don't lecture.

### Batch 5: Preferences

9. **Coffee** — "Do you drink coffee? If so, what do you usually add (cream, sugar, black)?" This sets the default so they can just say "coffee" and you'll log it correctly.

10. **Anything else I should know?** — Open-ended. Capture any other logging preferences (e.g. "I eat the same breakfast every day", "I track in grams not ounces").

### Batch 6: Telegram

11. **Telegram** — "Want to connect Telegram so you can log meals on the go by messaging me? I'll walk you through it if so."

## 3. Write everything back

### 3a. Initialize the database

If the database is empty or missing tables, bootstrap it:
```bash
cd /workspace/nutrition/scripts && uv run init_db.py
```

### 3b. Set the nutrition goal

```bash
cd /workspace/nutrition/scripts && uv run set_goal.py \
  --calories <kcal> --protein <g> --fat <g> --carbs <g> \
  --rationale "<one-line summary: sex, age, height, weight, activity, objective, TDEE>"
```

### 3c. Log baseline weight

```bash
uv run /workspace/.claude/skills/log-weight/log_weight.py <weight_lbs>
```

### 3d. Update CLAUDE.md

Append the user's context to the `## Preferences` and `## Project Notes` sections of `/workspace/CLAUDE.md`. Do NOT overwrite the existing instructions — only append below the comments.

Under `## Preferences`, add things like:
- Coffee default (e.g. "When user logs coffee, include 2 tbsp half-and-half unless specified otherwise")
- Any other logging preferences they mentioned

Under `## Project Notes`, add:
- User's name
- Their metrics summary (for context, not for recalculation): e.g. "Male, 27, 5'10", 170 lb, very active, cutting"

### 3e. Connect Telegram (if user said yes)

Use the chat integration tools:

1. First check available providers:
   ```
   mcp__chat__list_available_chat_providers
   ```

2. Tell the user to create a Telegram bot:
   - Open Telegram and message @BotFather
   - Send `/newbot`
   - Choose a name (e.g. "My Nutrition Agent")
   - Choose a username (must end in `bot`)
   - Copy the API token BotFather gives them

3. Once they provide the token, connect it:
   ```
   mcp__chat__add_chat_integration with toolkit: "telegram" and the token
   ```

4. Tell them to open their new bot in Telegram and send `/start`, then try logging a meal.

## 4. Verify

- Confirm the database has its tables:
  ```bash
  python3 -c "import sqlite3; c=sqlite3.connect('/workspace/nutrition/data/nutrition.db'); print(c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()); c.close()"
  ```
- Confirm goal.json was written:
  ```bash
  cat /workspace/nutrition/data/goal.json
  ```
- Start the dashboard to confirm it works:
  Use `mcp__dashboards__start_dashboard` with slug `nutrition-dashboard`.
- Optionally generate a status card as a smoke test:
  ```bash
  cd /workspace/nutrition/scripts && uv run --with pillow status_card.py
  ```
  Then deliver it with `mcp__user-input__deliver_file`.

## 5. Done

Summarize what you set up:
- Their daily targets (calories + macros)
- Whether Telegram is connected
- That the dashboard is running

Then tell them how to get started:
> You're all set! Just tell me what you ate and I'll log it. You can also:
> - Send a photo of your meal
> - Say "status" or "rings" to see your progress
> - Say "dashboard" to open the full history view
> - Log your weight anytime ("163 lbs")
>
> You can re-run this setup anytime by asking me to run `agent-onboarding`.
