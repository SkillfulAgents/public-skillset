---
category: Sales
icon: badge-dollar-sign
avatar:
  color: tonal-purple
  shape: hexagon
tags:
  - CRM Hygiene
  - Pipeline Management
  - Deal Re-Engagement
  - Win-Back
  - Forecasting
  - HubSpot
works_with:
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: salesforce
  - type: api_account
    slug: attio
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: googlecalendar
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Pipeline Doctor

> Stop forecasting on stale deals and start reviving the ones you gave up on too early.

## What it does

Pipeline Doctor is the CRM-honesty and revival specialist. It runs four routines against your own CRM and mailbox:

- **Weekly hygiene digest.** Flags open deals with past-due or repeatedly pushed close dates, deals that have gone quiet, missing amounts or contacts, and deals stuck in a stage longer than your own norm. Each flag comes with the specific fix, sorted so the biggest and latest-stage deals come first.
- **Stalled deal nudges.** Works out where each stalled deal stopped and who owes the next move, skips deals where you are genuinely waiting, and drafts a nudge with a concrete reason to reply. No "circling back".
- **Closed-lost win-back.** Every other week it finds deals lost for reasons that can change (timing, budget, no champion, a competitor) and checks for a real trigger such as new funding, a new leader, or a competitor stumble. When it finds one, it drafts a "why now" email and cites the source.
- **End-of-day CRM update.** Turns today's meetings, emails and calls with prospects into activity notes, next steps and suggested stage changes. It matches each one to the right deal, skips anything already logged, flags what is unclear, and waits for your approval.

Everything it writes to buyers is a draft in your own Gmail or Outlook. It never sends anything, and it never changes the CRM until you approve.

## What you'll need

- **A CRM:** HubSpot, Salesforce or Attio as a connected account, or Pipedrive or Close through their MCP servers. Required.
- **Gmail or Outlook:** required. Nudge and win-back drafts land in your own mailbox.
- **Google Calendar:** required for the end-of-day update (Outlook calendar also works).
- **Meeting notes:** optional. Granola, Fireflies, Otter, Gong, Fathom or Zoom make the end-of-day notes richer.
- **Delivery channel:** in-app, or the agent's own Slack app, email inbox, Telegram or iMessage for digests and approval batches.
- **API keys:** none. Web search and lead enrichment for win-back triggers are built in.

## Getting started

1. Import the template into Gamut. The `agent-onboarding` skill starts automatically.
2. Onboarding connects your CRM, mailbox and calendar. It reads your stages and computes how long deals normally sit in each one. Then it asks about your thresholds, opt-outs, where reports should go and how much to do without asking, and runs a dry pass on your real pipeline.
3. Ask for your first hygiene digest, then let the weekly schedules take over.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Check my HubSpot pipeline and show me what is rotting
- Draft nudges for my stalled late-stage deals with a real reason to reply
- Every other Monday, find closed-lost deals worth reviving and draft emails

## What's inside

- `AGENTS.md`: the four routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup, dry run, schedules and config.
- `.claude/skills/pipeline-triage-rubric/`: hygiene thresholds, stalled-deal triage order, and win-back scoring.

## Notes

- Stage norms come from your own closed deals. With little history it uses the norms you give it and says so.
- Optional: a pipeline health dashboard showing flagged deals, close-date pushes and revived deals.
- Pairs with `deal-desk-autopilot` (deal strategy) and `crm-from-your-phone` (pipeline Q&A in Slack).

## Privacy

Pipeline Doctor reads your CRM, mailbox and calendar through your own connected accounts. Its run-state files keep only deal ids, dates and statuses, not email bodies. It never sends email, and it never writes to the CRM without your approval.
