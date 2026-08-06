---
name: SEO Daily Content
description: 'Daily content unit — pick the top item from the content backlog and ship it end-to-end (article via blog-pipeline + publish, or a surface/cleanup unit via CMS edit or site PR). Invoked by the daily scheduled task; can also be run manually to burn down the backlog.'
metadata:
  version: "2.0.0"
---

# SEO Daily Content

Ships exactly **one content unit per run** from `/workspace/seo/content-backlog.md`.

## Procedure

1. **Read context**: `/workspace/seo/STATE.md`, `/workspace/seo/content-backlog.md`, and the
   last ~3 entries of `/workspace/seo/log.md` (avoid duplicating an already-shipped unit —
   the backlog status is the source of truth).
2. **Pick unit type by day (UTC)**: Mon–Thu → `[article]`; Fri–Sun → `[surface]`.
   (Target mix: 4 articles + 3 surface units/week — adjust if STATE.md says the agreed
   cadence differs.) If no `todo` item of today's type exists, take the other type. Take
   the **topmost** `todo` item of that type (backlog is priority-ordered).
3. Mark the item — set its status to `[in-progress]` in the backlog before starting.

### Article path
1. Refine keywords if needed with `ahrefs-keywords` (cheap overview call; the backlog
   entry usually already has vol/KD).
2. Run the **`blog-pipeline`** skill end-to-end for the item's primary/secondary keywords
   (research → draft → fact-check → humanize → AI-detector QC → media → publish via the
   configured CMS path).
3. Internal links: at least 3 internal links to relevant existing pages, and edit 1–2
   older relevant posts to link TO the new article.
4. **Publish** only if the auto-publish grant in CLAUDE.md is active; otherwise stop at
   a ready-to-publish draft and flag it for human review. Verify the page renders live
   (curl the URL, check title/meta/JSON-LD) and record it in
   `seo/content-inventory.json` (blog-pipeline step 7).
5. For alternatives/comparison posts naming competitors: factual, sourced claims only —
   no disparagement; verify every competitor feature/pricing claim against their site.

### Surface path
Execute the unit as described in the backlog entry — typical surface units:
- CMS content changes (titles, metas, body patches, freshness dates) via the configured
  CMS path.
- Site code changes (llms.txt, robots.txt, sitemap fixes, structured data, components) →
  repo PR if the site is in git and the CLAUDE.md autonomy rules allow merging; otherwise
  prepare the change and hand off.
- Set/update a "last updated" date on any meaningfully edited page (freshness signal).

## Wrap up (always)
- Update the backlog item: `[done]` + date + live URL(s).
- Append a dated entry to `/workspace/seo/log.md`: unit shipped, URL, primary kw, notes.
- If the backlog has <5 `todo` articles or <3 `todo` surface units, note "backlog low" in
  the log (weekly strategy replenishes; don't replenish here).
- If the run fails partway (pipeline error, CI red): revert item to `[todo]`, log the
  failure + cause. Do NOT publish anything that failed QC.

## Rules
- One unit per run — never more.
- Meta description ≤160 chars, unique; valid Article JSON-LD where the site supports it;
  image alts set.
- 1500–2500 words for articles — when your domain authority is below the incumbents',
  depth is the edge; thin posts don't rank without DR behind them.
- Never fabricate stats/quotes; fact-check pass is mandatory (part of blog-pipeline).
