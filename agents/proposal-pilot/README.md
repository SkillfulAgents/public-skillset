---
category: Sales
icon: file-text
avatar:
  color: tonal-blue
  shape: circle
tags:
  - Proposals
  - Rate Card Pricing
  - Follow-Up Cadence
  - Call Notes
  - Professional Services
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

> Go from call notes to a sendable proposal, priced from the rate card, and never let it go cold after it is sent.

## What it does

Proposal Pilot owns the proposal for founder-led consulting, accounting, insurance, and staffing firms. It starts from Granola, the CRM notes, or a pasted call summary and writes the proposal in your template: situation, scope, approach, timeline, price, and next step. Every price comes from the rate card, never a guess. It sends you the draft with gaps called out, then leaves the approved proposal in a Gmail draft for one-tap send.

After that, it tracks each deal through its milestones: discovery done, proposal sent, client reply, contract out, signed. It runs a fixed cadence instead of vague check-ins, by default follow-ups on days 2, 5, and 10 after the proposal and days 3 and 7 after the contract. Every follow-up is a draft in the original thread for your approval. It measures how fast proposals go out after discovery, flags anything slipping past its window, and proposes stage moves. It never marks a deal lost on its own.

Proposal Pilot writes the proposal. Its sibling, Quote Chaser, chases estimates that a home services shop has already sent.

## What you'll need

- **Granola** — recommended for call notes, through the Granola MCP. Other notes tools or pasted notes work too.
- **Google Drive** — required for the proposal template, the rate card, and the finished Doc.
- **HubSpot** — the supported CRM connector for deal stages and follow-up tasks. Another CRM or a Google Sheet can be configured during onboarding.
- **Gmail** — required for proposal and follow-up drafts, and to detect sends and replies.
- **Slack** — for the daily digest and gap lists, sent from the agent's own Slack app. Email or in-app also work.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your proposal template, rate card, call notes source, stage mapping, follow-up cadence, speed target, and who approves price, then saves the answers into `AGENTS.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Turn the latest call notes into a sendable proposal, in draft. After you approve the dry run, it sets up the mail trigger and the daily cadence check.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Turn my latest call notes into a sendable proposal from our template
- Which proposals are due a follow-up today, and which ones are slipping?
- After each discovery call in Granola, draft the proposal and Slack me the gaps

## What's inside

- `AGENTS.md` — the drafting, follow-up cadence, and weekly speed routines, the deal stages, the Gamut setup, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, stages, cadence, voice, and approval rules, runs a supervised draft, and schedules the runs.

## Notes

- Built for 2-200 person founder-led professional firms that still rebuild every proposal from a blank page.
- Proposals and follow-ups stay in draft until the founder one-tap sends. The agent never nudges more often than the configured cadence.
