---
name: Ahrefs Keywords
description: Keyword research + expansion via the Ahrefs API v3 Keywords Explorer. Pull overview metrics (volume, difficulty, cpc, intents, traffic potential) for seed keywords, and expand with matching-terms / related-terms / search-suggestions. Use to pick primary + secondary keywords for SEO content.
metadata:
  version: "1.0.0"
---

# Ahrefs Keywords

Wraps the Ahrefs v3 Keywords Explorer endpoints. Auth via `AHREFS_API_KEY` in `/workspace/.env`.
Costs API units (overview of ~2 keywords ≈ 86 units; invalid requests cost 0). Check the
budget anytime for free: `GET /v3/subscription-info/limits-and-usage`.

## Usage

```bash
# Overview metrics for one or more keywords (comma-separated)
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py overview "crm software,best crm software"

# Expansion: terms that CONTAIN the seed phrase
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py matching "crm software" --limit 50

# Expansion: related terms (same SERP / topically related)
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py related "crm software" --limit 50

# Google autocomplete-style suggestions
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py suggestions "crm software" --limit 50
```

Default country is `us` (override with `--country gb`). Output is JSON to stdout.

## Notes
- `overview` select columns: keyword, volume, difficulty, cpc, cps, clicks, global_volume,
  parent_topic, traffic_potential, intents, serp_features (a bad `select` column returns a
  400 listing all valid columns, and costs 0 units — useful for discovery).
- Expansion endpoints return keyword + volume + difficulty; sort/filter client-side.
- Costs units — prefer one batched `overview` call over many singles.
