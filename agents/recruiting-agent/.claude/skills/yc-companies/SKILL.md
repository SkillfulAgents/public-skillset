---
name: YC Companies Directory
description: Filter the public YC companies directory (6k+ companies) by batch, industry, tags, team size, region, hiring status, or keyword. Use for sourcing — build seed-company lists for LinkedIn similarity search and find companies whose founders/early engineers are candidate targets.
metadata:
  version: "1.0.0"
---

# YC Companies Directory

Filters the community-maintained YC directory API (`yc-oss.github.io`, refreshed daily; cached locally for 24h). No auth needed.

## Usage

```bash
uv run --with requests /workspace/.claude/skills/yc-companies/yc.py \
  [--keyword "infra"] [--tags "AI,Developer Tools"] [--industry "B2B"] \
  [--batch "Winter 2024,Summer 2024"] [--batch-since 2023] \
  [--min-team 2] [--max-team 20] [--region "United States"] \
  [--status Active] [--hiring] [--top] \
  [--limit 50] [--sort batch|team_size] [--format table|csv|json] [--refresh]
```

## Sourcing recipes

- **Founder/early-engineer targets**: `--batch-since 2022 --max-team 15 --tags "AI"` → small recent companies; each result's `yc_url` (ycombinator.com/companies/<slug>) lists founders with LinkedIn links — open in browser to extract them. Small team = everyone there is early.
- **Seed companies for LinkedIn similarity search**: filter by the role's space (`--keyword`/`--tags`/`--industry`), take the company names as Sales Navigator seeds.
- **Acquired/wound-down alumni** (people likely open to moves): `--status Acquired` or `--status Inactive` in the relevant space.

## Notes

- Fields per company: name, slug, batch, team_size, status, industry, subindustry, tags, regions, one_liner, long_description, website, isHiring, top_company, yc_url.
- `--keyword` searches name + one-liner + description + tags (case-insensitive).
- Founder names/backgrounds are NOT in this API — they're on each company's `yc_url` page (browser).
- Default sort: most recent batch first. `--limit 0` = no limit.
