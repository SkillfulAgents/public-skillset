---
name: Blog Pipeline
description: 'End-to-end runbook for producing an SEO blog post from a target keyword — keyword expansion, multi-angle research, drafting, fact-checking, humanizing (beating AI detectors), media sourcing, and publishing via the CMS path configured at onboarding. Use whenever a keyword/topic needs to become a blog post.'
metadata:
  version: "2.0.0"
---

# Blog Pipeline

Turns a target keyword into a fact-checked, humanized, media-rich blog post, published
through whatever CMS this site uses (configured in `seo/config.json` → `cms`). Composes
the other skills + a bundled workflow script. Follow in order.

## Step 1 — Keyword research & selection (`ahrefs-keywords`)
```bash
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py matching "<seed>" --limit 100
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py related  "<seed>" --limit 100
uv run --env-file .env /workspace/.claude/skills/ahrefs-keywords/ahrefs.py overview "<seed>,<cand1>,<cand2>,..."
```
Pick a **primary** (best volume × low difficulty × right intent) and a **secondary cluster**
(shared parent topic). Note the search intent. (Backlog items usually arrive with this
already done by the weekly strategy session.)

## Steps 2–4 — Research → Draft → Fact-check → Humanize (Workflow)
Run the bundled workflow script, passing the keywords as args. `company` comes from
`seo/config.json` → `company` (one-line positioning written at onboarding):
```
Workflow({ scriptPath: "/workspace/.claude/skills/blog-pipeline/blog-content-pipeline.workflow.js",
  args: {
    primary: "<primary keyword>",
    secondary: ["<secondary 1>", "..."],
    intent: "informational",
    company: "<config.company>",
    angleNotes: "optional editor steer"
  }})
```
It returns `{meta, cta, media_brief, links, claims_checked, final_markdown, ai_tells_removed}`.
Save `final_markdown` to a file (e.g. `/workspace/output/<slug>.md`).

### Step 4.2 — AI-detector QC (browser)
Strip markdown to plain prose (drop code/lists), then run a ~400-word excerpt through
detectors via the browser + web-browser subagent:
- Scribbr (QuillBot): https://www.scribbr.com/ai-detector/  (the reliable signal)
- Ahrefs: https://ahrefs.com/writing-tools/ai-content-detector  (aggressive; high false-positive on technical prose — don't over-optimize for it)
If Scribbr isn't mostly "human", re-run a humanization pass (see the workflow's Humanize
prompt) and re-test. Always re-check `grep "—"` = 0 em dashes after any edit.

## Step 5 — Media (`stock-media`)
For each `media_brief` entry, search, download, eyeball (Read the file), pick the best:
```bash
uv run --env-file .env /workspace/.claude/skills/stock-media/media.py unsplash "<terms>" --n 6
uv run /workspace/.claude/skills/stock-media/media.py openverse "<terms>" --n 6   # keyless fallback
uv run --env-file .env /workspace/.claude/skills/stock-media/media.py download "<url>" hero.jpg
```
Record photographer + source for captions. (Unsplash: hitting download triggers the
photo's `download` endpoint per their API guidelines — see the media skill.)

## Step 6 — Publish via the configured CMS path
The publish mechanics depend on `seo/config.json` → `cms` (set at onboarding, documented
in CLAUDE.md under "Publishing path"). Common shapes:
- **Headless CMS with an API** (Sanity, Contentful, Strapi, WordPress REST, Ghost Admin):
  convert markdown to the CMS's content format, set SEO fields (metaTitle ≤60,
  metaDescription ≤160), upload images with alt text, create the post via API. If the
  site's schema/conventions are non-obvious, read a recently published post via the API
  first and mirror its shape.
- **Git-based** (markdown/MDX in a repo — Next.js, Astro, Hugo, Jekyll): add the file +
  frontmatter + images on a branch, open a PR, merge per the autonomy rules in CLAUDE.md.
- **Hosted builders** (Webflow, Framer, Wix, Squarespace, Shopify blog): use the platform
  API where one exists, else drive the editor via the browser (web-browser subagent).
- **No access / human publishes**: write the final markdown + meta + images to
  `/workspace/output/<slug>/`, deliver to the user, and record the handoff in the log.

Whatever the path: set meta title/description, image alts, and internal links
(≥3 links to relevant existing pages; also edit 1–2 older posts to link TO the new one).

## Step 7 — Record the publish (required)
Append to `/workspace/seo/content-inventory.json` (array of
`{"title", "url", "published_at"}`). The dashboard's per-article performance table joins
GSC data on these URLs — a post missing here is invisible to reporting.

### Validate before declaring done
- Page returns 200 and renders (curl the live URL; check title, meta description, JSON-LD).
- Images have alt text; internal links resolve.
- The content-inventory entry exists.

## Notes
- Everything factual goes through the fact-check pass — never fabricate stats/quotes.
- 1500–2500 words for articles unless the intent clearly calls for less.
- One natural, non-salesy product tie-in near the end + CTA; nothing more.
