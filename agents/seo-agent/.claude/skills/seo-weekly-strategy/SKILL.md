---
name: SEO Weekly Strategy
description: 'Weekly SEO strategy session — KPI pull, audit of the week''s daily runs, backlog review/replenishment, technical SEO checks, and the weekly report delivered to the owner. Monthly mini competitor sweep on the first Monday; quarterly full sweep. Invoked by the Monday scheduled task.'
metadata:
  version: "2.0.0"
---

# SEO Weekly Strategy

The steering loop. Runs Mondays; produces `/workspace/reports/seo-weekly-YYYY-MM-DD.md`
and delivers it per the report channel in `seo/config.json` (email or Slack).

## Procedure

### 1. KPI pull
- **Start with the `seo-dashboard` skill** — `collect.py --refresh` produces one snapshot
  (Ahrefs + GSC + activity) in `/workspace/seo/dashboard/data.json`. Read the KPIs from
  there so the weekly report and the dashboard never disagree. The raw pulls below are
  for anything the snapshot doesn't already carry.
- Report refdomains as **clean vs suspect** (`refdomains.clean_count` / `suspect_count`),
  never the raw total alone — low-quality profiles often carry many spam-signature domains.
- Ahrefs (cheap, do every week): `domain-rating`, `backlinks-stats`, `metrics`
  (mode=subdomains) for the site; `organic-keywords` limit 30. Budget check first:
  `GET /v3/subscription-info/limits-and-usage`.
- GSC (property from `seo/config.json`): pull last-7d vs prior-7d
  clicks/impressions/CTR/position + top movers by query and page using the bundled helper:
  `uv run --env-file .env --with google-auth,requests .claude/skills/seo-weekly-strategy/gsc_query.py --start YYYY-MM-DD --end YYYY-MM-DD --dimensions query,page --limit 100`
  (add `--filter 'query notContains <brand term>'` for the non-brand view; run once per
  period and diff). GSC data lags ~2 days — use Mon−9d…Mon−3d vs the week before.
- Rank spot-checks: Ahrefs `serp-overview` (or organic-keywords position) for the
  target keywords of articles published ≥2 weeks ago.
- Update the KPI table in `/workspace/seo/STATE.md` (append a dated row — keep history).

### 2. Audit the week
- Read `/workspace/seo/log.md` for the week: units shipped vs plan (default target 7:
  4 articles + 3 surface — use the cadence agreed in STATE.md), sends/replies/links won,
  failures.
- Check the published articles are indexed (site: search or GSC URL inspection if
  available) and rendering correctly.
- If a daily runbook repeatedly hit the same friction: **edit the skill** (they live in
  `/workspace/.claude/skills/seo-daily-*`) and note the change in the report. The loop
  is self-improving — runbook edits are in scope.

### 3. Backlog review + replenishment
- Content: reprioritize on evidence (GSC movers, new SERP intel); replenish to ≥3 weeks
  of runway (≥12 articles + ≥9 surface units `todo`) using `ahrefs-keywords`
  (matching-terms on winning clusters; while DR is low, favor KD comfortably below the
  site's DR — a useful rule of thumb: KD ≤ ~30 while DR < 45).
- Links: replenish section A with new directories found; if the outreach shortlist is
  running low (<100 uncontacted), re-run `competitor-link-prospects` with 2–3 NEW
  competitor domains (more competitors > more depth per competitor). Add them to
  `config.link_prospecting.self_domains` too.
- Prune: kill backlog items invalidated by new data.

### 4. Technical checks
- Sitemap fetch + diff vs last week (page-count by section — catch accidental
  deindexing/drops).
- Spot-check 5 recently changed URLs: 200 status, title/meta, JSON-LD validity.
- robots.txt + llms.txt present and sane.
- Check for 404s: any URL in GSC/Ahrefs top pages that no longer resolves.
- Core signals occasionally (monthly): PageSpeed on the home page + key templates.
- Anything deeper → the `technical-audit` skill (scheduled monthly; run ad-hoc if
  something looks broken).

### 5. Monthly / quarterly extras
- **First Monday of month**: mini competitor sweep — Ahrefs `metrics` + `metrics-history`
  for the competitor list in `seo/config.json` → `competitors`; flag big moves (new
  sections, traffic jumps). If a competitor runs paid search, their `paid` keyword list
  = proven converting terms worth targeting organically.
- **First Monday of Jan/Apr/Jul/Oct**: full competitive re-analysis — re-run
  `competitor-link-prospects` across the full set, re-pull competitor keyword rankings,
  and refresh the strategy section of STATE.md.

### 6. Report
Write `/workspace/reports/seo-weekly-YYYY-MM-DD.md`:
- KPI table w/ WoW deltas (clicks, impressions, DR, refdomains, keywords ranking).
- Shipped this week (articles w/ URLs + target kw; surface units; links won).
- Outreach funnel: sent → replied → won (cumulative + this week).
- Movers: queries/pages up or down meaningfully.
- Issues found + fixes applied; runbook changes.
- Next week's plan (top backlog items); decisions needed from the owner (from
  "needs owner" queues).
Keep it under ~1 page of dense content. Deliver per `config.report.channel`:
- **email** → the `email-report` skill (renders markdown as formatted HTML — raw
  markdown reads terribly in Gmail):
  ```bash
  uv run --env-file .env --with markdown,requests \
    .claude/skills/email-report/send_report.py \
    --md reports/seo-weekly-YYYY-MM-DD.md \
    --subject 'SEO weekly — YYYY-MM-DD' \
    --preheader '<one-line hook: the week in a sentence>' \
    --summary-md /tmp/highlights.md
  ```
  Write `/tmp/highlights.md` first — a 4–6 bullet TL;DR plus the decisions needed; it
  renders as the "Highlights" box above the report.
- **slack** → `mcp__chat__send_chat_message` with the TL;DR + key table, link/attach the
  full report file.

Also deliver the report file via `mcp__user-input__deliver_file`. Append a log entry.
