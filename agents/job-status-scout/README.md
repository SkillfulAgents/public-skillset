---
category: Customer Success
icon: map-pin
tags:
  - Home Services
  - Customer Updates
  - Arrival Windows
  - Field Service
  - Escalations
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Job Status Scout

> Answer every when-are-you-coming with the real window from the board, and escalate the late, missing, and angry ones.

## What it does

Job Status Scout owns the when-are-you-coming question for founder-led home services shops. It watches SMS, voicemail, Gmail, and the field-service inbox for where-is-the-tech and are-you-still-coming messages, then reads the promised window, live ETA, and assigned tech from Jobber, Housecall Pro, or ServiceTitan.

It drafts a short reply in the shop voice with the real window and who is coming. If the job is late, the window is gone, or the customer is angry, it Slacks you the facts and a recommended make-good draft instead of auto-sending. It never guesses soon when the board has a time and never promises a tighter ETA than the board shows.

## What you'll need

- **Gmail** — required for catching status asks by email and drafting replies.
- **Slack** — required. Late, missing, and angry jobs land in your founder channel with a make-good draft.
- **Jobber, Housecall Pro, or ServiceTitan** — one is needed for the real window. No registry connector; connected during onboarding.
- **SMS line** — optional, for text asks and replies. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your status inbox, which board holds the real window, whether on-time replies may auto-send, and the Slack channel for spicy jobs, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Answer today's when-are-you-coming messages with the real window from the board, drafting replies and holding the spicy ones.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Answer today's when-are-you-coming messages with the real window
- Which of today's jobs are late or have no window, and draft the make-goods
- Every 30 minutes, check the status inbox and reply with the board window

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops buried in when-are-you-coming texts.
- Replies stay in draft until approved, except on-time replies the founder later pre-authorizes. The agent never reroutes a tech.
