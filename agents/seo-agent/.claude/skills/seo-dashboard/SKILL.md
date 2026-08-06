---
name: SEO Dashboard
description: 'Collect and refresh the SEO master dashboard snapshot — Ahrefs (DR, refdomains + quality split, organic keywords, top pages), Search Console (clicks/impressions/queries/pages with WoW deltas), per-article performance, and SEO program activity (backlogs, outreach CRM, run log). Use to refresh the seo-master dashboard, to pull current SEO KPIs for a report, or when the collector needs extending with a new metric.'
metadata:
  version: "2.0.0"
---

# SEO Dashboard

Backs the **`seo-master`** dashboard (`/workspace/artifacts/seo-master/`).
`collect.py` is the single source of truth for the numbers — the weekly report and the
dashboard should read the same snapshot rather than each re-deriving KPIs.

Site settings (domain, GSC property, brand terms, targets) come from
`/workspace/seo/config.json` — written by `agent-onboarding`.

## Usage

```bash
cd /workspace   # the --env-file path is relative
uv run --env-file .env --with google-auth,requests \
  .claude/skills/seo-dashboard/collect.py [flags]
```

| Flag | Effect |
|---|---|
| *(none)* | Serve from cache when warm — GSC 15 min, Ahrefs 6 h. ~0.5 s. |
| `--refresh-gsc` | Force a live Search Console pull (free, ~8 s). |
| `--refresh-ahrefs` | Force a live Ahrefs pull (**~500–600 units**, ~6 s). |
| `--refresh` | Force both. |
| `-o FILE` | Output path (default `/workspace/seo/dashboard/data.json`). |

Writes `/workspace/seo/dashboard/data.json` and appends a row to
`/workspace/seo/dashboard/history.jsonl` on every live Ahrefs pull (that file is the
long-run KPI series — the dashboard's trend charts get denser the longer this runs).
Caches live in `/workspace/seo/dashboard/cache/`; delete them to force a cold pull.

The payload shape is documented in `/workspace/seo/dashboard/SPEC.md`.

## Dashboard

`mcp__dashboards__start_dashboard` with slug `seo-master`. First run: `bun install` in
the dashboard directory (`package.json`'s `start` script builds then serves). The server
(`serve.js`) exposes `GET /api/data` (runs the collector, honours its caches, falls back
to the last good snapshot with `stale:true` if the collector fails) and
`POST /api/refresh` (forces both). So **Search Console is effectively live on page load**
and Ahrefs is at most 6 h old, with a Hard refresh button for a forced pull.

Before shipping frontend edits run `bun run check-render.jsx` in the dashboard directory —
it SSRs every section against the live payload *and* against empty/null payloads.

## Data sources

- **Ahrefs** Site Explorer: `domain-rating`, `backlinks-stats`, `metrics`,
  `metrics-history`, `refdomains` (limit 1000), `organic-keywords`, `top-pages`.
- **GSC** via a service account (`GSC_SERVICE_ACCOUNT_JSON`), property from config:
  120 d daily series (all + non-brand), 28 d vs prior 28 d by query and by page, and
  page×query rows for the per-article drilldown. Data lags ~2 days.
- **Content inventory**: `seo/content-inventory.json` (published posts appended by the
  daily content skill), joined to GSC pages for per-article performance.
- **Program files**: `seo/STATE.md` (KPI history), `content-backlog.md`,
  `link-backlog.md`, `outreach/crm.json`, `log.md`.

## Gotchas encoded here (don't re-debug)

- Ahrefs `organic-keywords` returns **one row per locale**, so a keyword repeats with
  different volume/position. The collector rolls up by keyword+URL (min position, max
  volume, summed traffic, `locales` count) so the list agrees with `metrics.org_keywords`.
  Passing `country=us` instead would drop terms that only rank outside the US.
- **Refdomain counts need a quality split.** Young profiles attract spam links (junk TLD,
  or traffic < 10 and DR < 15) — `refdomains.clean_count` vs `suspect_count`; never
  report the raw total alone. Ahrefs' own `live_refdomains` differs from the live row
  count by a few because of its live/lost accounting.
- **Brand filtering must catch misspellings** (set `brand_regex` in config to include
  the typos people actually type) or the non-brand north-star metric is inflated.
- `gsc.page_queries` keys are trailing-slash-stripped; `gsc.pages` rows carry a matching
  `page_key`. Join on that. Only a minority of pages have query rows — GSC suppresses
  low-volume queries; that's expected, not a bug.
- `org_cost` / `paid_cost` from Ahrefs are in **cents**. If the site runs paid search,
  `paid_traffic` can dwarf organic — keep it out of organic charts.
- `units.spent_this_pull` is clamped at 0 because the counter resets monthly and can run
  backwards mid-pull.
- `d_position` in the GSC tables is **sign-flipped so positive = rank improved**.
