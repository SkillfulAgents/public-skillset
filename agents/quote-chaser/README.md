---
category: Sales
icon: badge-dollar-sign
avatar:
  color: tonal-forest
  shape: arch
tags:
  - Estimate Follow-Up
  - Quotes
  - Follow-Up Cadence
  - Home Services
  - Field Service
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Quote Chaser

> Sitting estimates get a follow-up in the shop voice until they are won, lost, or handed to you.

## What it does

Quote Chaser owns sitting estimates for founder-led home services shops. Every weekday morning it pulls open estimates from Jobber, Housecall Pro, ServiceTitan, or the quote sheet, and works out where each one stands: estimate sent, customer replied, paperwork out, won. Then it runs a fixed, configurable cadence instead of vague check-ins. By default that means nudges on days 2, 5, and 10 after the estimate goes out and days 3 and 7 after approval paperwork, then a founder call.

Each nudge is a short draft in the founder's voice that names the job, the date, and a clear next step: approve, pick a start window, or say no. It is queued in Gmail, the field-service tool, or the approval message for one-tap send. A reply pauses the cadence. The agent flags site visits with no estimate yet, estimates expiring this week, and anything slipping past its window. It never changes a quote amount, promises a discount, or marks a quote won or lost on its own.

Quote Chaser chases estimates your shop already sent. It does not write them. Its sibling, Proposal Pilot, writes and follows up professional-services proposals.

## What you'll need

- **Gmail** — required for follow-up drafts and to see replies. Outlook works too.
- **Slack** — for the daily digest of drafts to approve, sent from the agent's own Slack app. Email or in-app also work.
- **Jobber, Housecall Pro, or ServiceTitan** — one is needed for open estimates. No registry connector; connected during onboarding by API key or browser sign-in, or use a quote sheet.
- **SMS line** — optional, for text follow-ups through your field-service tool. No registry connector.
- **API keys:** only if your field-service tool needs one.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your estimate system, the follow-up cadence, how soon estimates should go out after a visit, quiet hours for texts, and where the digest goes, then saves the answers into `AGENTS.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends without sending. After you approve, it schedules the daily chase.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Review sitting estimates and draft follow-ups for the ones going cold
- Draft a last nudge for every estimate that expires this week
- Every weekday at 7am, chase quiet estimates and Slack me the drafts to approve

## What's inside

- `AGENTS.md` — the daily chase and weekly scoreboard routines, the estimate stages and cadence, the Gamut setup, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules, runs a supervised chase, and schedules it.

## Notes

- Built for 2-200 person founder-led home services shops with estimates sitting quiet.
- Follow-ups stay in draft until the founder one-tap sends. The agent never nudges more often than the configured cadence.
