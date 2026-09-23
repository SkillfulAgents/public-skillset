---
category: Sales
icon: file-text
tags:
  - Proposals
  - Rate Card Pricing
  - Call Notes
  - Professional Services
  - Granola
works_with:
  - type: mcp
    slug: granola
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Proposal Pilot

> Go from call notes to a sendable proposal, priced from the rate card, without starting from a blank page.

## What it does

Proposal Pilot owns the proposal for founder-led consulting, accounting, insurance, and staffing firms. It starts from Granola, the CRM notes, or a pasted call summary and writes the proposal in your template: situation, scope, approach, timeline, price, and next step. Every price comes from the rate card, never a guess.

It Slacks you the draft with gaps called out, such as a missing price, fuzzy scope, or legal language, then places the approved proposal in Gmail or as a Doc link email for one-tap send. It never reuses another client's confidential work and never changes the price after approval without asking again.

## What you'll need

- **Granola** — recommended for call notes, through the Granola MCP. Pasted notes work too.
- **Google Drive** — required for the proposal template and the finished Doc.
- **HubSpot** — the supported CRM connector for deal notes and logging. Another CRM can be configured during onboarding.
- **Gmail** — required for the send draft.
- **Slack** — required. Drafts with gaps land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your proposal template, rate card, call notes source, and who approves price, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Turn the latest call notes into a sendable proposal, in draft.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Turn my latest call notes into a sendable proposal from our template
- Draft the Meridian proposal and call out any gaps in scope or price
- After each discovery call in Granola, draft the proposal and Slack me the gaps

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms that still rebuild every proposal from a blank page.
- Proposals stay in draft until the founder one-tap sends.
