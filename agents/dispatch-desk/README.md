---
category: Ops
icon: truck
tags:
  - Dispatch
  - Home Services
  - Customer Texts
  - Field Service
  - Scheduling
works_with:
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Dispatch Desk

> Tomorrow's board built, crew and parts checked, and every customer texted a real arrival window.

## What it does

Dispatch Desk owns tomorrow's board and the customer window for founder-led home services shops. It pulls tomorrow's jobs from Jobber, Housecall Pro, ServiceTitan, or the dispatch calendar, checks that the named crew is actually on the schedule and not already out of area, and flags jobs whose parts notes say nothing about what is on the truck.

Then it drafts the window text for each customer in your voice: who is coming, the real window, and how to prep. Each text is queued for founder or dispatcher one-tap send unless you pre-authorize on-time window texts after a clean trial. This is not a routing engine and it never reassigns crews.

## What you'll need

- **Slack** — required. The board, parts flags, and text drafts land in your dispatch channel.
- **Jobber, Housecall Pro, or ServiceTitan** — one is needed for the dispatch board. No registry connector; connect during onboarding or point the agent at your dispatch calendar.
- **SMS line** — required to send the customer window texts. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your dispatch board, where parts notes live, your window-text voice, and who approves customer texts, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Build tomorrow's board with crew, parts, and windows, and draft the customer texts without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Build tomorrow's board with crew, parts, and windows and draft the texts
- Which of tomorrow's jobs have a crew conflict or missing parts notes
- Every day at 4pm, build the next day's board and queue the window texts

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops that need tomorrow's board and the customer text owned.
- The agent never invents a customer window the board does not show or assumes parts are on the truck when the job does not say so.
