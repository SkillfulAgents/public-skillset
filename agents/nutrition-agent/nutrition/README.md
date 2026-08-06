# Nutrition Tracker

Personal calorie + macro tracker. Designed as a template — every piece of state lives in `data/` and is created by the bootstrap script.

## Layout

```
nutrition/
├── data/
│   ├── nutrition.db      # SQLite DB (meals, goals tables)
│   └── goal.json         # current daily goal (single source of truth)
├── scripts/
│   ├── db.py             # shared helpers — DB connect, PST tz, paths
│   ├── init_db.py        # bootstrap (idempotent — safe to re-run)
│   ├── log_meal.py       # insert one meal row
│   ├── today.py          # JSON: today's meals + totals + goal
│   ├── history.py        # JSON: last N days for the dashboard
│   ├── set_goal.py       # persist new daily goal
│   └── status_card.py    # render rings PNG to output/status.png
└── output/
    └── status.png        # generated each time status is requested
```

The dashboard lives at `/workspace/artifacts/nutrition-dashboard/` and reads `data/nutrition.db` directly (read-only).

## Bootstrap

```bash
cd scripts && uv run init_db.py
```

## Timezone

All day boundaries use **America/Los_Angeles**. Timestamps are stored with tz offset; `local_day` is denormalized for fast `GROUP BY day`.

## Skills

- `/log-meal` — log a meal (description or photo, agent estimates macros)
- `/nutrition-status` — generate the rings status card
- `/set-nutrition-goal` — conversational goal setter (Mifflin-St Jeor + macro split)
- `/nutrition-dashboard` — open the history dashboard
