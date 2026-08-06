---
name: Technical Audit
description: 'Comprehensive technical SEO audit of the site — crawlability, indexing, sitemap, redirects, internal linking, page performance, structured data, metas — combining Ahrefs Site Audit findings with hands-on checks, ending in ACTION: PRs, drafted tickets, or platform fixes. Run monthly by schedule, after onboarding, or ad-hoc when something looks broken.'
metadata:
  version: "1.0.0"
---

# Technical Audit

Not a report generator — an audit that **ends in fixes**. Findings without a shipped PR,
a drafted ticket, or an applied platform change are unfinished work.

Read `/workspace/seo/STATE.md` and `/workspace/seo/config.json` first (site, publishing
path, autonomy grants).

## Phase 1 — Gather

1. **Ahrefs Site Audit** (if a crawl exists): pull the latest project's issues via the
   API where available, else read the report in the browser. Note crawl date; if stale
   (>30d), kick off a re-crawl for next time and work with what exists + your own checks.
2. **GSC**: Index coverage signals — pages with impressions that 404/redirect, big
   position/impression drops per page (`seo-dashboard` snapshot + `gsc_query.py`).
3. **Own crawl of the essentials** (curl + parsing; a small script is fine):
   - `robots.txt` — present, sane, not blocking real content; sitemap declared.
   - `sitemap.xml` — present, valid, reachable; URL count by section; every URL 200s
     (sample if huge); no redirects/dupes inside; lastmod plausible. Diff vs the last
     audit's count (catch silent deindexing).
   - `llms.txt` — present? (cheap win if not).
   - Home + each key template (blog post, category/listing, product page): status,
     canonical, title/meta uniqueness + length, H1, JSON-LD validity (parse it),
     OG/Twitter tags, noindex accidents, hreflang if multilingual.
   - **Redirects**: http→https, apex↔www single-hop 301s; sample old URLs from
     GSC/Ahrefs top pages for chains/302s/404s.
   - **Internal linking**: from the sitemap sample, find orphan-ish pages (few internal
     inlinks), check key pages are ≤3 clicks from home, anchor text is descriptive,
     important pages are linked from high-traffic pages.
   - Duplicate content smells: parameter URLs indexed, /page/1 vs base, trailing-slash
     duplication.
4. **Performance**: PageSpeed Insights API (free, keyless at low volume:
   `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=...&strategy=mobile`)
   on home + the 2–3 key templates. Record LCP/CLS/INP + the top opportunities. Mobile
   first — that's what Google scores.

## Phase 2 — Prioritize

Rank findings by (indexing impact, traffic at risk, effort). Three buckets:
- **P0 — blocking indexing/crawling** (noindex accidents, sitemap 404s, robots blocks,
  redirect loops, missing canonicals on duplicated content).
- **P1 — ranking drag** (slow LCP, broken structured data, thin/duplicate titles,
  orphan money pages, 404s with backlinks — reclaim with 301s).
- **P2 — hygiene** (llms.txt, minor meta lengths, image alts, lastmod).

## Phase 3 — ACT (the point of the skill)

Per the publishing path + autonomy grants in STATE.md/CLAUDE.md:
- **Site in a repo you can access** → open PRs (small, one concern each, with the
  finding + evidence in the description). Merge only if the autonomy grant covers it;
  otherwise request review.
- **Engineer will do the work** → draft tickets (Linear/Jira/Asana via connected
  account, or markdown handoff): symptom, evidence URL(s), suggested fix, priority.
- **Hosted platform** (Framer/Webflow/Shopify/Wix/Squarespace) → fix directly via the
  platform API/MCP where one exists, else offer to drive the UI via browser with the
  user watching; document what was changed.
- **CMS-level fixes** (metas, alts, structured data fields) → apply through the
  configured CMS path like any surface unit.

Queue anything needing the owner (DNS, billing, agency coordination) in
`seo/link-backlog.md` "Needs owner" or the weekly report's decisions list.

## Phase 4 — Record

- Write `/workspace/reports/technical-audit-YYYY-MM-DD.md`: findings table
  (issue / evidence / priority / action taken or ticket/PR link), performance numbers,
  deltas vs last audit.
- Append a `log.md` entry; add follow-up `[surface]` items to the content backlog for
  anything that becomes recurring work.
- Deliver the report per the report channel (email via `email-report` / Slack / 
  `deliver_file`) if run standalone; if run inside the weekly session, fold the summary
  into the weekly report.
