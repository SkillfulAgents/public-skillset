# SEO Operations — State

> Operating doc for the ongoing SEO program. Every scheduled SEO session reads this first.
> Filled in by the `agent-onboarding` skill; kept current by the weekly strategy session.

## Mission
<!-- onboarding: one paragraph — what site, what market, what the growth thesis is,
     and what the #1 bottleneck is (links? content? technical?). -->
_Not yet configured — run agent-onboarding._

## Cadence (scheduled tasks)
<!-- onboarding: fill in the actual schedules created. Defaults shown. -->
| Task | Schedule | Runbook skill | What it does |
|---|---|---|---|
| Daily content | — | `seo-daily-content` | 1 unit/day: Mon–Thu = article (pipeline→publish), Fri–Sun = surface work |
| Daily links | — | `seo-daily-links` | Check replies → follow-ups due → work backlog items (listings/outreach) |
| Weekly strategy | — | `seo-weekly-strategy` | KPIs, audit the week, replenish backlogs, technical checks, report |
| Dashboard snapshot | — | `seo-dashboard` | One `collect.py --refresh` run; appends the day's KPI row to `dashboard/history.jsonl` |
| Monthly technical audit | — | `technical-audit` | Full crawl-level audit → fixes as PRs/tickets |

## Autonomy grants
<!-- onboarding: record exactly what the owner approved. Be conservative by default. -->
- Auto-publish blog content after the full QC pipeline: **not granted** (draft + hand off).
- Outreach sends from a dedicated inbox: **not granted** (no inbox connected).
- Site-repo PR merge: **not granted** (open PRs, human merges).
- NOT autonomous (always): launches, founder-voiced press/podcast pitches (draft only),
  creating public repos, anything spending money — queue in link-backlog "needs owner".

## KPI baseline
<!-- onboarding: fill from the first dashboard collect. -->
| Metric | Value | Source |
|---|---|---|
| DR / refdomains (live) | — | Ahrefs |
| Non-brand organic clicks | — | GSC |
| Total clicks / impressions (3mo) | — | GSC |
| Sitemap URLs | — | sitemap.xml |
| Ahrefs tracked organic keywords | — | Ahrefs |

12-month targets: <!-- onboarding: agreed targets, mirrored in seo/config.json `targets` -->

## KPI history
| Date | DR | Refdoms | GSC clicks | GSC imp | NB clicks | NB imp | Ahrefs org kw | Sitemap URLs | Notes |
|---|---|---|---|---|---|---|---|---|---|
