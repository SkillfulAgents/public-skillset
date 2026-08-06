---
name: Set Nutrition Goal
description: Discuss and set the user's daily nutrition goal (calories + macros). Use when the user says "set my goal", "update goal", "I want to lose/gain/maintain", "what should my calories be", or anything goal-related. This skill is conversational — collect the inputs needed, propose a well-reasoned target backed by standard formulas, confirm with the user, then persist.
---

# Set Nutrition Goal

Discuss with the user, then persist a daily goal to `/workspace/nutrition/data/goal.json` and append history to the `goals` table.

## Conversation flow

1. **Collect inputs** (ask only for what's missing — be efficient, prefer batching with AskUserQuestion):
   - Biological sex (for BMR formula)
   - Age
   - Height (cm or ft/in)
   - Weight (kg or lb)
   - Activity level: sedentary / light / moderate / very active
   - Objective: cut / maintain / lean bulk / aggressive bulk
   - Any preference / constraint (e.g. "high protein", "low carb", "vegetarian", "lifting 4x/week")

2. **Compute** using Mifflin-St Jeor:
   - Men: BMR = 10·kg + 6.25·cm − 5·age + 5
   - Women: BMR = 10·kg + 6.25·cm − 5·age − 161
   - TDEE = BMR × activity multiplier (sedentary 1.2, light 1.375, moderate 1.55, very active 1.725)
   - Calorie target:
     - cut: TDEE − 400 to 500
     - maintain: TDEE
     - lean bulk: TDEE + 200 to 300
     - aggressive bulk: TDEE + 500
   - Macros:
     - Protein: 1.6–2.2 g/kg bodyweight (use 1.8 g/kg as default, 2.0+ if cutting or lifting heavy)
     - Fat: 0.8–1.0 g/kg (default 0.9 g/kg, min 20% of calories)
     - Carbs: remainder from calories (1 g protein/carb = 4 kcal, 1 g fat = 9 kcal)

3. **Present** the proposed goal with a short rationale (1–3 sentences explaining BMR/TDEE assumptions and any tradeoffs). Ask the user to confirm or tweak.

4. **Persist** once confirmed:
   ```bash
   cd /workspace/nutrition/scripts && uv run set_goal.py \
     --calories <kcal> --protein <g> --fat <g> --carbs <g> \
     --rationale "<one-line summary of inputs and approach>"
   ```

## Notes
- Day boundaries are PST. Goal takes effect today.
- Round calories to nearest 50, macros to nearest 5 g for cleaner targets.
- If user pushes back, iterate — don't lecture, just adjust and re-present.
