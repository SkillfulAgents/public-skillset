---
category: Productivity
icon: briefcase
tags:
  - Venture Capital
  - Deal Flow
  - Portfolio Management
  - Board Meetings
  - Investor Relations
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: googlesheets
  - type: mcp
    slug: granola
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# VC Associate

> The associate who sorts your inbox like an investor, keeps every portfolio company and board meeting prepped, and never lets an LP or introducer go quiet.

## What it does

VC Associate is built for GPs, angels and platform or associate roles. It runs up to seven routines, and you choose which ones to turn on. Each has its own trigger or schedule:

- **Investor Inbox Triage** labels every email as Today's Focus, Action Required, Scheduling or Delegated, archives noise against your skip list, keeps LP and fund-admin mail apart from deal flow, escalates founder deadlines that slipped, and sends a morning digest with a one-line reason for each urgent item. A term sheet or signed document is always top of the list.
- **Deal Flow to Pipeline** turns intros, decks and data-room links into deduplicated rows in your deal sheet or CRM, scored against your thesis and allowlists, and surfaces the high-priority ones.
- **Living Portfolio Briefs** keeps one doc per portfolio company current from investor updates, their attachments and links, and your meeting notes: top asks, who owes whom, a 4-quarter snapshot, and sources for every number.
- **Board Meeting Prep** turns forwarded board materials into a 7-section memo in Drive, with a health call, a 3-period financial table and four questions tied to specific numbers in the deck.
- **LP Meeting Prep Brief** sends you the relationship context, recent interactions, everyone you know at the firm and open follow-ups before each LP meeting.
- **LP Re-Engagement Digest** lists the LPs you have gone quiet on each month, with a recent-news hook and a tailored draft for each.
- **Warm Intro Thank-You** checks that a meeting with an introduced founder actually happened, then drafts a short thank-you to the introducer in the original thread, once per intro.

It labels, logs and writes internal docs on its own. Anything addressed to founders, LPs or introducers stays a draft in your mailbox until you send it.

## What you'll need

- **Gmail** — required for triage, deal intake and drafts. Outlook works as an alternative.
- **Google Calendar** — needed for LP meeting prep and intro thank-yous.
- **Google Drive and Google Docs** — needed for portfolio briefs, board memos and opening Drive links in updates.
- **Google Sheets** — the default deal tracker, created for you if it doesn't exist.
- **Granola** — optional and recommended, for meeting notes. Fireflies, Otter or Fathom also work.
- **CRM** — optional. Affinity through an API key or the browser, or Attio or HubSpot through a connected account. A Google Sheet works too.
- **Carta** — optional, for ownership and invested capital in briefs.
- **The agent's own email inbox** — recommended, so you can forward board materials to it.
- **API keys:** `AFFINITY_API_KEY` only if you use Affinity through its API.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs automatically. You pick the routines you want, connect your mailbox, calendar, Drive and CRM, set your thesis, skip list and board-prep keyword, and choose where digests reach you. Each routine gets a supervised dry run on your real data before anything is scheduled.
3. Ask for a first triage pass over your unread mail, or forward your next board deck with "BOD prep".

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Triage today's unread and tell me what's in Today's Focus and why
- Prep me for the Acme board meeting from the deck I just forwarded
- On the first of each month, list the LPs I haven't talked to in 30 days

## What's inside

- `CLAUDE.md` — the seven routines, how each runs on Gamut, and the safe operating rules.
- `.claude/skills/agent-onboarding/` — routine selection, connections, thesis and rules, dry run, triggers and schedules.
- `.claude/skills/board-prep-memo/` — the fixed 7-section memo, health thresholds and file naming.
- `.claude/skills/portfolio-brief-format/` — the per-company brief structure and dating rules.
- `.claude/skills/deal-intake/` — gating, allowlists, priority rubric and thread-level dedup.
- `.claude/skills/crm-access/` — reading Affinity, Attio, HubSpot or a sheet, and the tracker columns.

## Notes

- Affinity has no connected account, so the agent uses your Affinity API key (on plans that include API access) or signs in through the browser.
- Data rooms behind an NDA, a verification code or click-through terms are never opened on your behalf. They are logged as not opened.
- Numbers come only from the materials. Anything that didn't parse is flagged, never estimated.

## Privacy

The agent reads your mailbox, calendar, Drive and CRM through your own accounts. Portfolio briefs, board memos and LP records stay in your own Drive or CRM and are never shared outside your accounts. Run state is kept in small ledger files in the agent's workspace.
