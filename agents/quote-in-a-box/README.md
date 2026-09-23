---
category: Sales
icon: package
tags:
  - Quotes
  - Rate Card Pricing
  - One-Tap Send
  - Small Business
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

# Quote in a Box

> The last conversation becomes a one-page quote with price, scope, and a yes/no ask, ready to send with one tap.

## What it does

Quote in a Box owns the boxed quote for micro-owners and founder-led SMBs who quote from memory and then forget to send it. It starts from the last email, text, call note, or walk-in note, builds a plain-language scope, and prices it from your rate card or menu.

Every quote ends with a single yes/no ask, or a pick-a-start-window ask, on one page or in one email. It is queued for your approval and only that exact draft gets sent. The agent never invents a price list or a job the conversation did not describe, and never writes a long proposal when a boxed quote will do.

## What you'll need

- **Gmail** — required for conversation source and the quote draft.
- **Slack** — required. Quotes awaiting approval land in your founder channel.
- **Rate card** — required. A sheet, doc, or pasted menu captured during onboarding.
- **SMS line** — optional, for text conversations and quotes. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your rate card, where conversations happen, your quote voice, and when to box versus go custom, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Turn the last conversation into a boxed quote with price, scope, and a yes/no ask, in draft.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Turn my last conversation into a boxed quote with price, scope, and a yes/no
- Quote the deck staining job from yesterday's text thread using our rate card
- Each evening, draft a boxed quote for every conversation that ended without one

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners who quote from memory and then forget to send it.
- Quotes stay in draft until the founder one-tap sends. The agent never changes the price after approval without asking again.
