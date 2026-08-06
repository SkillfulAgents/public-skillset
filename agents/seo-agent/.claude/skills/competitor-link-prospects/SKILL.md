---
name: Competitor Link Prospects
description: 'Find link-building outreach prospects by pulling competitor backlinks from Ahrefs Site Explorer and filtering to listicles / reviews / comparisons / "alternatives" pages where your product could plausibly be added. Dedupes by referring domain and ranks pages that mention multiple competitors highest. Use for off-page SEO / outreach target lists.'
metadata:
  version: "1.1.0"
---

# Competitor Link Prospects

Generates a ranked link-building prospect list for outreach. For each competitor
domain it pulls Ahrefs `site-explorer/all-backlinks` (one link per referring
domain, `history=live`), filters referring-page **titles** to listicle/review/
comparison signals (`best`, `top`, `alternative`, `review`, `vs`, `tools`,
`comparison`, ...), then merges across competitors so a domain that mentions
**multiple** competitors ranks highest (hottest prospect — already covers the category).

## Usage
```bash
uv run --env-file .env --with requests \
  .claude/skills/competitor-link-prospects/prospect.py \
  --domains competitor1.com,competitor2.com,competitor3.com \
  --out /workspace/output/link-prospects \
  --limit 150 --min-dr 20
```
Outputs `<out>.csv` ranked by (# competitors mentioned, domain rating, traffic),
with columns: rank, refdomain, url_from, title, domain_rating, traffic_domain,
is_dofollow, competitors_mentioned, n_competitors, first/last_seen.

## Curate the raw list → outreach shortlist
`prospect.py` output is broad (PBN spam, directories, off-topic pages, competitor
self-links). Run `curate.py` to get a vetted, editorial-only shortlist classified by
outreach format (roundup / comparison / alternatives / review):
```bash
uv run .claude/skills/competitor-link-prospects/curate.py \
  --in /workspace/output/link-prospects.csv \
  --out /workspace/output/link-prospects-shortlist --min-dr 30
```
Drops: nofollow, DR<min, PBN/`.shop`/`seolink` spam, directories (toolify,
producthunt, cbinsights, f6s, capterra/g2...), social/video/app stores,
competitor-owned domains, content-farm subdomains (random `-12345` subdomains), and
pages whose title doesn't touch the category unless they mention 2+ competitors.

**Configure your niche first** (agent-onboarding writes these; keep them in sync):
- `seo/config.json` → `link_prospecting.self_domains`: the competitor domains you
  prospect (so their own sites aren't treated as prospects).
- `seo/config.json` → `link_prospecting.topic_terms`: category vocabulary for the
  title on-topic gate (e.g. for a CRM product: `["crm", "sales", "pipeline", ...]`).
  Empty = gate disabled (broader, noisier list).

Writes `<out>.csv`; pair with a small markdown generator for a readable grouped brief.

## Notes / gotchas
- Needs `AHREFS_API_KEY`. Costs Ahrefs units (Site Explorer). A ~4-competitor
  run used ~6k units. Check budget first: `/v3/subscription-info/limits-and-usage`.
- Lower-tier Ahrefs plans cap `all-backlinks` at **100 rows/call** regardless of
  `--limit`, so each competitor contributes its top-100-by-DR filtered links.
  Use **`--banded`** to break the cap: it paginates by domain-rating bands
  (90-100, 80-90, ... down to `--min-dr`), one ≤100-row call per band, disjoint so
  dedup is clean. ~7 calls/competitor. This is the lever for a large pool.
- **Depth per competitor has a real ceiling** — most competitors only have ~100-250
  DR≥30 editorial backlinks. To grow the pool, **add more competitors** (each surfaces
  fresh "best X tools" roundups), not more depth.
- Pages mentioning **multiple competitors** are the priority tier (they already cover
  the category, so adding one more tool is the easiest sell). The merge step recomputes
  `n_competitors` across all pulls; sort by it.
- The title filter is deliberately broad → expect false positives (podcasts with
  "vs", academic "review" articles, "Top 100 B2B" lists). Human-vet before outreach.
- **Programmatic / auto-generated** targets (CBInsights "Top X Alternatives",
  ProductHunt alternatives, directories) appear but rarely accept manual additions —
  deprioritize vs. editorial listicles (blogs, magazines).
- `mode=domain` + `aggregation=1_per_domain` keeps the list to one best link per
  referring domain. Bump `--min-dr` to tighten quality.
