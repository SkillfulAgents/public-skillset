---
category: Customer Success
icon: refresh-cw
tags:
  - Contract Renewals
  - End Dates
  - Professional Services
  - HubSpot
  - Google Drive
works_with:
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Renewal Clerk

> Every contract end date is tracked and every renewal is drafted before the term quietly dies.

## What it does

Renewal Clerk owns contract renewals for founder-led consulting, accounting, insurance, and staffing firms. It maintains end dates from the contract folder, the CRM, or a sheet and checks them daily. When usage or retained-hours systems are connected it pulls the usage picture and cites the source.

Inside the lead time you set, it drafts the renewal note and the next-term order form from your template and current price, then queues them for one-tap send and logs sent, replied, renewed, and churn risk. Nothing auto-renews, no usage or savings are invented, and no discount or term change happens without approval.

## What you'll need

- **HubSpot** — the supported CRM connector for contract records and renewal logging. Another CRM can be configured during onboarding.
- **Google Drive** — required for the contract folder and the order form template.
- **Gmail** — required for renewal drafts.
- **Slack** — required. Upcoming renewals and churn risks land in your founder channel.
- **Billing or usage system** — optional, for the usage picture. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your contract folder, renewal lead times, usage source, renewal voice, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: List contracts inside the renewal window, attach usage if available, and draft renewals without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List contracts inside the renewal window and draft the renewals
- Draft the Beacon renewal with their usage this term and the current price
- Every morning, check end dates and Slack me anything within 60 days

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms whose terms die because nobody drafted the renewal.
- Renewals stay in draft until the founder sends. The agent flags a missing end date rather than ignoring it.
