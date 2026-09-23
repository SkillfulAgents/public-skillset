---
category: Sales
icon: badge-dollar-sign
tags:
  - Estimate Follow-Up
  - Quotes
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

Quote Chaser owns sitting estimates for founder-led home services shops. On your cadence it pulls open estimates from Jobber, Housecall Pro, ServiceTitan, or the quote sheet, then flags the ones past the follow-up window, expiring this week, or high-value and quiet.

For each one it drafts a short founder-voice nudge that names the job, the date, and a clear next step: approve, pick a start window, or say no. The exact draft is queued in Gmail, SMS, or the field-service message for one-tap send. It never changes a quote amount, promises a discount, or marks a quote won or lost without evidence.

## What you'll need

- **Gmail** — required for follow-up drafts and replies.
- **Slack** — required. Cold estimates and handoffs land in your founder channel.
- **Jobber, Housecall Pro, or ServiceTitan** — one is needed for open estimates. No registry connector; connected during onboarding, or use a quote sheet.
- **SMS line** — optional, for text follow-ups. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your estimate system, the quiet-day window, when the last nudge goes out, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Review sitting estimates and draft follow-ups for the ones going cold
- Draft a last nudge for every estimate that expires this week
- Every Wednesday, chase quiet estimates and Slack me the drafts to approve

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops with estimates sitting quiet.
- Follow-ups stay in draft until the founder one-tap sends. The agent never nudges more often than the configured cadence.
