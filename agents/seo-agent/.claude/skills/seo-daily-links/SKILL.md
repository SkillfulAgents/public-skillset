---
name: SEO Daily Links
description: 'Daily link-building session — check outreach replies and send due follow-ups, then work the link backlog (directory/listing submissions, GitHub PRs, new outreach sends within ramp limits). Invoked by the daily scheduled task.'
metadata:
  version: "2.0.0"
---

# SEO Daily Links

Runs the daily link-building loop from `/workspace/seo/link-backlog.md` and
`/workspace/seo/outreach/crm.json`.

## Procedure

1. **Read context**: `/workspace/seo/STATE.md`, `link-backlog.md`, `outreach/crm.json`,
   last ~3 entries of `log.md`.

2. **Inbox pass** (only if `crm.config.inbox_connected` is true — check the
   `CONNECTED_ACCOUNTS` env var for the gmail account and update crm.config if it just
   became available):
   - Fetch new replies via the Gmail API through the proxy
     (`$PROXY_BASE_URL/<account_id>/gmail.googleapis.com/gmail/v1/...`).
   - For each reply, update the prospect in the CRM:
     - Positive ("sure, send details / added you") → respond helpfully same-run, status
       `won` when the link is live (verify!) or keep `replied` with a next action.
     - Negative / unsubscribe → status `lost`, never contact again.
     - Bounce → status `bounced`.
   - **Follow-ups due**: prospects with status `sent`/`followed_up` whose last touch is
     ≥ `followup_days` business days old and touches < `max_touches` → send a short
     follow-up, update CRM.

3. **New work** (aim ~30–45 min of value; don't grind for hours):
   - **If inbox NOT connected**: listings only. Work section A of the backlog top-down —
     ~2–3 submissions per run. Use the browser (`browser_open` + web-browser agent) for
     form submissions; GitHub API for awesome-list PRs where relevant. Record the
     submitted-listing URL.
   - **If inbox connected**: new outreach sends up to today's cap.
     - Cap = ramp value from crm.config (week counted from `first_send_date`; set it on
       the first-ever send). Follow-ups count toward the daily cap. Hard ceiling 20/day.
     - Source prospects: the current shortlist CSV in `seo/outreach/` (from
       `competitor-link-prospects`) — Tier 1 first (n_competitors ≥ 2), then alternatives
       pages, then roundups by DR desc. Skip domains already in the CRM.
     - Per prospect: find a contact (site contact/about page, author byline, public
       email — never scraped/paid lists), write a **personalized 4–6 sentence pitch**:
       reference their specific article, one concrete reason the product fits (use the
       positioning line from `seo/config.json` → `company`), link to the most relevant
       page on the site, no attachments. Sign per `crm.config.sender_identity`.
     - Add to CRM: id, domain, url_from, contact, pitch_angle, status `sent`, date,
       Gmail thread id.
   - Mix in listings alongside outreach while section A still has items.

4. **Wrap up**: move completed backlog items to Done (+ resulting URL); write CRM;
   append log entry (replies processed, follow-ups sent, new sends, listings done,
   links won). If a new link went live, note the refdomain for the weekly KPI diff.

## Rules
- Send only from the outreach inbox configured in `crm.config` — set up at onboarding.
  Best practice is a **dedicated inbox on a separate (warmed) domain** so outreach never
  risks the main domain's deliverability. Label outreach threads and track every thread
  in the CRM.
- Voice: match `crm.config.sender_identity` — modest and honest tone, no marketing-speak.
  A real person's name is on it — nothing spammy ever leaves this inbox.
- NEVER exceed the ramp cap; never a 4th touch; honor every opt-out instantly.
- No link-scheme language (no "link exchange", no paying for links, no PBNs).
- Claims in pitches must be true (traffic numbers, feature claims).
- Items marked "needs owner" in the backlog are prep-only: draft the asset/pitch, put it
  in the backlog item, flag in the weekly report — do not act on the owner's behalf.
- If Gmail auth fails or quota errors: log it, do listings instead, flag in weekly report.
