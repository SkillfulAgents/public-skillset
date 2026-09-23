---
category: Sales
icon: handshake
tags:
  - Estimates
  - Verbal Yes
  - Follow-Up
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

# Handshake Closer

> Every verbal yes becomes a sent estimate, one nudge, and a clear flag when they go quiet.

## What it does

Handshake Closer owns the gap between a verbal yes and a sent estimate for micro-owners and founder-led SMBs. It watches notes, SMS, voicemail, and the inbox for a yes, a handshake, or a send-it-over, then drafts the estimate from your rate card or the number they already heard, plus a one-line scope.

If they go quiet after send, it drafts exactly one nudge after the wait you configure (default 3 days). If they are still silent after that, it Slacks you the file and stops. No seven-touch sequence, no fuzzy maybe treated as a yes, and no job marked won without a real yes on the sent estimate.

## What you'll need

- **Gmail** — required for catching yeses and drafting the estimate and nudge.
- **Slack** — required. Silence flags and exceptions land in your founder channel.
- **SMS line and estimate system** — optional. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for where yeses land, your rate card, the silence wait, and your one-nudge voice, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Find verbal yeses that still have no sent estimate, draft the estimates, and flag any silence after one nudge.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Find every verbal yes that still has no sent estimate and draft them
- Draft the estimate for the Ramirez fence job from Tuesday's call notes
- Each morning, check for silence after a nudge and Slack me the files to call

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners who get a verbal yes and never send the estimate.
- Estimates and the one nudge stay in draft until the founder sends. The agent never nudges more than once.
