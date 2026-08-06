---
name: Log Weight
description: Log a daily body-weight reading into the nutrition SQLite DB (weights table). Use whenever the user reports their weight, e.g. "163 lbs this morning", "weighed in at 165", "log my weight". One row per local day (latest wins). Confirms the entry and the change vs the previous reading.
metadata:
  version: "1.0.0"
---

# Log Weight

Records a body-weight reading into the `weights` table of `/workspace/nutrition/data/nutrition.db`.
The table stores one weight per local day (America/Los_Angeles); re-logging the same day overwrites it.

## Usage

```bash
uv run /workspace/.claude/skills/log-weight/log_weight.py 163.0
# optional: backfill a specific day or add a note
uv run /workspace/.claude/skills/log-weight/log_weight.py 163.0 --day 2026-06-05 --note "post-run"
```

The script prints the logged value and the delta vs the previous day's reading.
