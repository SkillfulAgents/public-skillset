# SEO Master Dashboard — build spec

Audience: **the site owner** (technical, terse). They open this to answer, in order:
1. Is organic growing? (non-brand clicks is the north star)
2. Are links growing, and are they real links or spam?
3. Which content is actually working / decaying?
4. Is the SEO program shipping, and what needs me?

## Data

One JSON payload: `GET /api/data` → the contents of `/workspace/seo/dashboard/data.json`.

Server responsibilities (Bun.serve):
- `GET /api/data` — run the collector, then serve the JSON. The collector self-caches
  (GSC 15 min, Ahrefs 6 h), so this is ~0.5 s warm and ~10 s when GSC is stale.
  `Bun.spawn(["uv","run","--env-file",".env","--with","google-auth,requests",
  ".claude/skills/seo-dashboard/collect.py"], {cwd:"/workspace"})`, await exit, then read
  `/workspace/seo/dashboard/data.json`. If the collector exits non-zero, still serve the
  last good `data.json` and include `{"stale": true, "error": "..."}` so the UI can warn.
- `POST /api/refresh` — same but add `--refresh-ahrefs --refresh-gsc` (forces a live
  Ahrefs pull, ~2,700 units). Return the fresh payload.
- Never block first paint on the collector: render from `/api/data` with a loading state.

### Payload shape (real values from today's run)

```
generated_at, gsc_data_through: "2026-08-04"   // GSC lags ~2 days — SHOW THIS
ahrefs_fetched_at, ahrefs_cached, gsc_fetched_at, gsc_cached
units: {used: 98472, limit: 1000000, reset, spent_this_pull}

kpis: [{label, value, prev, delta, delta_pct, unit, good_up, hint}]
  // 9 tiles: Non-brand clicks (/wk), Non-brand impressions, Total clicks, Total
  // impressions, Avg position (good_up:false!), Domain Rating, Referring domains,
  // Ranking keywords, Outreach replies. prev/delta are null for Ahrefs tiles.

targets: [{label, current, target, pct, note}]   // 4 rows, 12-month goals

gsc: {
  daily:          [{date, clicks, impressions, ctr, position}]   // 60d, all queries
  daily_nonbrand: [{date, clicks, impressions, ctr, position}]   // same, non-brand only
  queries: [{query, clicks, impressions, ctr, position, prev_clicks, prev_impressions,
             prev_position, d_clicks, d_impressions, d_position, is_new, brand}]  // top 250 by impressions, 28d vs prior 28d
  pages:   [{page, ...same deltas...}]                            // top 250
  page_queries: {"<url>": [{query, clicks, impressions, position, brand}]}  // top 10/page
  periods: {week: {cur, prev, cur_nb, prev_nb}, month: {...}}      // each {clicks, impressions, ctr, position}
  ranges:  {cur, prev, week, prev_week}                            // [start, end] date pairs
}
  // NOTE d_position is sign-flipped so POSITIVE = improved rank. Label it "rank change".

ahrefs: {domain_rating: 32, ahrefs_rank, backlinks: {live, all_time, live_refdomains,
         all_time_refdomains}, metrics: {org_keywords, org_keywords_1_3, org_traffic,
         org_cost, paid_keywords, paid_traffic, paid_cost}, history: [{date, org_traffic,
         org_cost, paid_traffic, paid_cost}], organic_keywords: [{keyword, best_position,
         best_position_url, volume, keyword_difficulty, sum_traffic}], top_pages: [...]}
  // org_cost/paid_cost are in CENTS. paid_traffic dwarfs organic — that's the SEM spend,
  // keep it out of the organic charts (a small "paid vs organic" aside is fine).

refdomains: {all, new_30d, new_30d_count: 80, new_30d_suspect: 47, clean_count: 59,
             suspect_count: 88, lost, dr_buckets: {"0-19","20-39","40-59","60+"}}
  // rows: {domain, dr, first_seen, lost, last_seen, links, dofollow, traffic, age_days, suspect}
  // `suspect` = spam-signature TLD or (traffic<10 and DR<15). THIS MATTERS: refdomains
  // went 9 -> 169 but 88 are suspect. Show clean vs suspect side by side, never one number.

kpi_history: [{date, dr, refdomains, backlinks, org_keywords, org_traffic, org_keywords_1_3}]
  // one row per Ahrefs pull day, accumulates over time. Only 1 row today — the chart must
  // degrade gracefully (<3 points: show a dot/rule, not an empty axis).
kpi_history_state: [...]  // weekly rows parsed from STATE.md (has WoW history back to 2026-07-20)

articles: [{title, slug, url, published_at, age_days, primary_kw, volume, kd, clicks,
            impressions, ctr, position, d_clicks, d_impressions, ranking_keywords,
            best_rank, best_rank_kw, top_query, top_query_position, queries: [...]}]
  // 33 posts, sorted by impressions. primary_kw is null for pre-backlog posts — fall back
  // to top_query in the UI. Expandable row -> that post's `queries` table.

backlog: {content: [{type, status, date, title, section, url, primary_kw, volume, kd}],
          content_counts: {article_todo: 18, article_done: 11, surface_todo, surface_done},
          links: [{done, section, title, needs_owner}],
          link_counts: {open: 24, done: 8, needs_owner: 4}}

outreach: {config, total: 39, by_status: {...}, funnel: {prospected: 39, delivered: 33,
           replied: 2, won: 0}, bounced, response_rate: 5.1, bounce_rate: 15.4,
           followups_due: [{domain, dr, touch, due, overdue, contact}],
           active: [{domain, dr, status, note, contact}], won: [], send_timeline: [{date, touches}]}

activity: [{date, label, type, summary, bullets, published, article_title,
            followups_sent, new_sends}]   // 39 entries, newest first.
  // type ∈ content | links | weekly | setup | technical | other

velocity: [{week, articles, content_runs, link_runs, touches, other}]   // 3 weeks so far
```

## Layout (single scrolling page, sectioned)

1. **Header** — "SEO Master" + `gsc_data_through` freshness chip + last-refresh time +
   Refresh button (spinner; warn that it spends ~2.7k Ahrefs units) + Ahrefs budget
   micro-bar (`units.used/limit`).
2. **KPI row** — the 9 `kpis` tiles. Delta colored by `good_up` (Avg position inverts).
   Non-brand clicks is the hero tile (larger). Null-prev tiles show no delta, not "0%".
3. **Trend** — GSC clicks + impressions over the 60d `daily` series, with a
   brand / non-brand toggle (`daily` vs `daily_nonbrand`). Dual axis or two stacked panels;
   impressions dwarf clicks so do NOT put them on one linear axis.
4. **Targets** — the 4 `targets` as progress meters with `note` as caption.
5. **Content performance** — `articles` table: title, published, age, target kw (or
   top_query), clicks, Δclicks, impressions, Δimpr, position, best Ahrefs rank. Sortable.
   Highlight decay (d_clicks < 0 on an older post) and rising (d_clicks > 0). Row expands
   to the post's `queries`.
6. **Queries & pages** — two tabbed tables from `gsc.queries` / `gsc.pages` with a
   brand/non-brand filter and a "movers only" toggle. Show Δclicks and rank change.
7. **Links** — clean vs suspect refdomain split (the headline), DR bucket distribution,
   `new_30d` table (domain, DR, first seen, traffic, suspect flag), lost domains.
8. **Outreach** — funnel (prospected → delivered → replied → won), status breakdown,
   `active` opportunities as cards (nordicapis DR75 guest post is the live one),
   `followups_due` list with overdue flagged red.
9. **Program activity** — `velocity` weekly bars (articles / link runs / touches) +
   an `activity` feed (date, type chip, summary, published links). Feed is long: cap at
   ~15 with "show more".
10. **Backlog** — runway counters (articles todo, surface todo, link items open,
    needs-owner) + the next few `todo` items and the `needs_owner` list.

## Style
- Read the `dataviz` skill BEFORE writing chart code and follow it.
- Dark, dense, engineering-console feel. Tabular numbers, no gratuitous animation.
- Empty/zero states must read as "no data yet", never as a broken chart. Several series
  (kpi_history, outreach.won, velocity) have very few points today.
- No fabricated data. If a field is null, render "—".
