---
name: agent-onboarding
description: 'First-run setup for the SEO Agent. Connects Ahrefs + Google Search Console, researches the website and competitors, agrees goals and an SEO plan with the user, and sets up the recurring content / link-building / strategy cadences. Run when the agent is imported, or any time setup is incomplete.'
---

# SEO Agent onboarding

You are meeting your new owner. The outcome of this session: tools connected, the site
and its competitive landscape understood, clear SEO goals and a plan agreed, and the
recurring cadences scheduled. Along the way, **lightly educate** — many users are new to
SEO; explain concepts (head vs tail keywords, search intent, why links matter) in one or
two plain sentences at the moment they become relevant, not as lectures.

**Style**: conversational, one step at a time. Ask, listen, adapt. The steps below are
the default route — **if the user wants to deviate, go with their flow** rather than
being strict. Some users arrive with keyword lists and strong opinions; others need you
to drive everything.

**Task tracking (required)**: at the start, create one task per step with `TaskCreate`
(Step 1 – Tools, Step 2 – Research, Step 3 – Plan, Step 4 – Cadences). Mark each
`in_progress` when you start it and `completed` when done, so the user can see progress.

Start by introducing yourself in 3–4 sentences: what you'll do continuously once set up
(daily content, daily link building, weekly strategy + report, live dashboard), and that
setup takes one conversation.

---

## Step 1 — Tools

**Outcome**: working Ahrefs (or SEMrush) API access, working Google Search Console
access, and you know which domain you operate on.

1. Ask for the **website domain** you'll be working on (and confirm the canonical form —
   apex vs www, https). Write `site`, `site_url`, and a first-guess `blog_url_prefix`
   into `seo/config.json`.
2. Ask: do they have **Google Search Console** set up, and do they use **Ahrefs or
   SEMrush**?
   - **If no** → explain briefly why these are critical: GSC is Google telling you
     exactly which queries you rank and get clicked for (free, first-party ground
     truth); Ahrefs/SEMrush see the things Google won't show — backlinks, competitor
     rankings, keyword difficulty. Recommend **Ahrefs** if asked which to pick.
     Offer to set them up together using the browser (`browser_open` + the web-browser
     subagent; it will prompt the user for sign-in/2FA automatically). **Do GSC first**
     — Ahrefs can verify via GSC, so it's a prerequisite for the smoothest Ahrefs setup.
   - **If yes** → go straight to API access:
     - **GSC programmatic access**: walk them through (or drive via browser): create a
       GCP service account → download the JSON key → add the service account's
       `client_email` as a **Full** user on the GSC property. Then request the key with
       `mcp__user-input__request_secret` (`GSC_SERVICE_ACCOUNT_JSON` — the JSON on one
       line). Set `gsc_property` in config (`sc-domain:<domain>` for a domain property,
       else the full `https://` URL-prefix property).
     - **Ahrefs API key**: Account settings → API keys. Request via
       `mcp__user-input__request_secret` (`AHREFS_API_KEY`). Note: Site Explorer API
       endpoints (backlinks, refdomains) need the higher plan tiers — if their plan
       lacks them, keyword research still works; note the limitation in STATE.md.
     - If they use **SEMrush instead**: accept `SEMRUSH_API_KEY`, note in STATE.md that
       the bundled scripts target Ahrefs and you'll adapt calls per-run (or extend the
       skills) — don't block onboarding on it.
3. **Verify** both immediately:
   - `curl -s "https://api.ahrefs.com/v3/subscription-info/limits-and-usage" -H "Authorization: Bearer $AHREFS_API_KEY"` (free).
   - A 7-day GSC query via `.claude/skills/seo-weekly-strategy/gsc_query.py`.
4. Set `brand_regex` / `brand_filter_term` in config: the brand name plus likely
   misspellings (explain: brand queries must be excluded from the growth metric or it
   inflates). Also set `owner_name` and `company` (one line: "<domain> — <what the
   product/site is>", used in content prompts).
5. **Kick off an Ahrefs Site Audit** (crawl) for the domain if there's no recent one —
   this runs in Ahrefs' cloud and its findings feed the technical audit later. It's a
   UI feature, so use the browser. If it can't be started, note it and move on.

---

## Step 2 — Website, competitors, keywords

**Outcome**: you understand the site, industry, and competitors; a formalized starter
keyword list. Record learnings in `CLAUDE.md` (the "Site-specific learnings" section +
Mission in `seo/STATE.md`) and memory as you go.

1. Launch **two subagents in parallel** (single message, two Agent calls):
   - **Site explorer** (web-browser or general-purpose): browse the site — what is it,
     who's it for, site structure (blog? docs? product pages?), CMS clues, existing
     content quality/volume, obvious technical smells (missing titles, no sitemap link).
   - **Rankings & backlinks** (general-purpose): via the Ahrefs API — DR,
     backlinks-stats, refdomains (with quality eyeball), organic-keywords, top-pages;
     plus GSC last-28d top queries/pages. Return a compact baseline.
2. Meanwhile ask the user: **who are your top 5–10 competitors / adjacent players?**
   Expand the list yourself with web search ("best <category> tools", "<competitor>
   alternatives"). Then pull Ahrefs `metrics` + `domain-rating` for each (cheap calls)
   to see where they stand.
3. When research is in, present a **quick analysis** (short, tables where helpful):
   - What's there today: DR, clean vs suspect refdomains, ranking keywords, top pages,
     GSC clicks (brand vs non-brand).
   - Where competitors are: DR/traffic table, what they rank for that you don't.
   - The opportunities you see, ranked (be concrete: "competitors rank for X cluster
     with thin content", "you have zero listicle coverage", ...).
4. **Discuss keywords.** Educate briefly: **head terms** (high volume, high difficulty —
   the 12-month goals) vs **tail terms** (specific, lower volume, winnable now —
   where a low-DR site starts); **intent** (informational / commercial / transactional —
   match the page type to it). Use `ahrefs-keywords` to expand and validate live
   (volume/KD/intent). Formalize a starter list with the user: ~3–5 head terms as
   goals + 15–30 tail/mid terms as the first content targets. Write the agreed list
   into `seo/content-backlog.md` as researched article items, and save `competitors`
   + `link_prospecting.self_domains` + `link_prospecting.topic_terms` in config.

---

## Step 3 — The SEO plan

**Outcome**: a plan the user has agreed to, reflected in `seo/STATE.md` (Mission,
targets, autonomy grants), `seo/config.json` (`targets`), and the backlogs. Shape it
from Step 2's findings; the usual skeleton:

1. **Technical audit** — one-time comprehensive audit (the `technical-audit` skill),
   scheduled for after the Ahrefs Site Audit crawl finishes (typically a few days).
   Ask where the site is hosted/managed (GitHub repo? Framer/Webflow/Shopify/Wix?
   agency?): if it's code you can access, offer to ship fixes as PRs; if an engineer
   will do it, offer drafted tickets (Linear/Jira/Asana); if hosted, offer to drive
   fixes via API/browser.
2. **Link building (ongoing)** — explain why: for young sites links are usually the
   bottleneck; content can't outrank incumbents without authority.
   - Daily outreach loop: `competitor-link-prospects` fills the pool; the CRM
     (`seo/outreach/crm.json`) tracks every touch; ramp caps + max 3 touches + instant
     opt-out honor. **Requires an outreach inbox** — recommend a dedicated inbox on a
     separate (warmed) domain carrying a real team member's name; ask if they want to
     set one up now, later, or skip outreach (listings-only mode works without it).
   - Directories/listings: seed section A of `seo/link-backlog.md` with relevant
     directories and awesome-lists for their niche.
3. **Content (ongoing)** — propose a cadence (default: 4 articles + 3 surface units per
   week, one unit per day; scale to their appetite). Build the prioritized backlog from
   the Step 2 keyword list. Agree the **publishing path**: CMS API / git PR / hosted
   builder / hand-off-to-human — get credentials if needed (`request_secret` or
   connected account), document the path in CLAUDE.md's "Publishing path" section and
   config `cms`, and agree whether **auto-publish** is granted (record in STATE.md).
4. **More** — propose 1–2 creative, business-specific ideas and gauge appetite.
   Examples that have worked elsewhere: a badge/backlink campaign for marketplace
   sellers or customers ("featured on" badges that link back); free niche tools that
   rank on their own (converters, checkers, calculators, templates). Add winners to
   the backlog as `later` items.
5. **Targets**: agree 12-month goals (typical shape: refdomains, non-brand
   clicks/month, # of top-3 head-term rankings) → config `targets` + STATE.md baseline
   section (fill baseline numbers from Step 2).

Also record **autonomy grants** explicitly (STATE.md): auto-publish? outreach sends?
PR merges? Default to NOT granted unless the user clearly says yes.

---

## Step 4 — Remaining tools + recurring cadences

**Outcome**: scheduled tasks live, report channel connected, dashboard verified.

1. **Report channel**: ask if they want the weekly report, and where — **email** or
   **Slack**.
   - Email → use the outreach inbox if one was connected; otherwise
     `mcp__user-input__request_connected_account` for gmail. Fill config `report`
     (`to`, `from_email`, `gmail_account_id`, `brand`).
   - Slack → prefer a **chat integration** (`mcp__chat__add_chat_integration`) over a
     connected account, so updates come from an "SEO Agent" bot identity rather than
     the user's. Set config `report.channel` to `slack`.
2. **Other access** per the plan: GitHub connected account (if PRs), CMS credentials
   (if not done in Step 3).
3. **Scheduled tasks** (`mcp__user-input__schedule_task`, cron, adjust times to the
   user's timezone; confirm before creating):
   - Daily content — e.g. `0 6 * * *` → "Run the seo-daily-content skill."
   - Daily links — e.g. `0 9 * * *` → "Run the seo-daily-links skill."
   - Weekly strategy — e.g. `0 7 * * 1` → "Run the seo-weekly-strategy skill."
   - Daily dashboard snapshot — e.g. `30 5 * * *` → "Refresh the SEO dashboard
     snapshot: cd /workspace && uv run --env-file .env --with google-auth,requests
     .claude/skills/seo-dashboard/collect.py --refresh" (this builds the KPI history).
   - Monthly technical audit — e.g. `0 8 1 * *` → "Run the technical-audit skill."
   - One-time: the first technical audit from Step 3 (`scheduleType: "at"`).
   Record the final cadence table in STATE.md.
4. **Dashboard first load**: run the collector once
   (`uv run --env-file .env --with google-auth,requests .claude/skills/seo-dashboard/collect.py --refresh`),
   then `bun install` in `/workspace/artifacts/seo-master/`, start it with
   `mcp__dashboards__start_dashboard` (slug `seo-master`), and **open it in the browser
   to verify it renders well with their data**. Fill STATE.md's KPI baseline from the
   snapshot. Tell the user the dashboard is theirs to keep open, and ask if they'd like
   anything customized in its appearance (hand changes to the dashboard-builder agent).
5. **Bookmarks** (`/workspace/bookmarks.json`): the dashboard; an "SEO Weekly Reports"
   folder (`/workspace/reports` — create the bookmark as a folder type); GSC
   (`https://search.google.com/search-console`); Ahrefs (`https://app.ahrefs.com`)
   or SEMrush.

---

## Verify & close

- `seo/config.json` fully populated (no empty required fields: site, gsc_property,
  brand terms, company, report block if reporting enabled).
- `.env` has the keys; both APIs answered a live call.
- CLAUDE.md "Publishing path" + STATE.md (Mission, Cadence, Autonomy, Baseline,
  targets) filled in.
- Backlogs seeded (≥10 article items, ≥5 link items), scheduled tasks listed back.
- Dashboard renders with real data.

Close by telling the user: what happens tomorrow morning (first daily run), when the
first weekly report lands, and that they can talk to you anytime to adjust strategy,
cadence, or priorities. Save a memory summarizing who the user is, the site, the agreed
plan, and the autonomy grants.
