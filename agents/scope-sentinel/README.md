---
category: Ops
icon: shield-check
tags:
  - Scope Creep
  - Change Orders
  - Agency Ops
  - Statements of Work
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
  - type: api_account
    slug: googledrive
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Scope Sentinel

> Catch the quick extra ask, map it to the SOW, and have the change order drafted before anyone starts the work.

## What it does

Scope Sentinel owns out-of-scope asks for founder-led marketing, creative, and web shops. After kickoff it watches client email, Slack, and the project channel for new asks and classifies each one as in-scope, out-of-scope, or unclear against the SOW in your Drive folder. Unclear goes to you with the question rather than a guess.

For out-of-scope work it drafts a short change order: the extra work, an estimate or T&M from the rate card, the timeline bump, and a yes/no ask, then queues it for one-tap send. It never tells the team to just do it, never invents rates or timelines, and never guesses scope when the SOW file is missing.

## What you'll need

- **Gmail** — required for watching client asks and drafting the change order.
- **Slack** — required for the project channels and the founder review of each CO.
- **Google Drive** — required for the SOW folder and the rate card.
- **Client tracker** — optional. A sheet or tracker where the agent logs each change order.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your SOW folder, rate card, which channels asks arrive in, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Scan this week's client asks against the SOW, flag out-of-scope, and draft change orders without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Scan this week's client asks against the SOW and draft change orders
- Is the new landing page ask from Orbit in scope, and draft the CO if not
- Every day at noon, check the project channels for new asks and flag scope creep

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led agencies that leak hours on quick extra asks.
- Change orders stay in draft until the founder one-tap sends.
