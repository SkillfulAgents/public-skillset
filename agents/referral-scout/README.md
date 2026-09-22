---
category: Sales
icon: user-search
tags:
  - Referrals
  - Warm Intros
  - Professional Services
  - HubSpot
  - Gmail
works_with:
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

# Referral Scout

> Know who to ask for an intro this week, have the ask drafted, and never lose track of who named whom.

## What it does

Referral Scout owns the referral ask for founder-led consulting, accounting, insurance, and staffing firms. From the CRM, recent wins, and completed jobs it lists people who are happy, recent, and not already asked inside the quiet window, then drafts a short founder-voice ask that names the kind of intro you want and makes it easy to say no.

When you send, it logs the date, who was asked, and who they named. If an intro goes quiet it drafts one follow-up to the introducer or the new person, never both on the same day. It never spams the whole book on one cadence and stops asking after a no.

## What you'll need

- **HubSpot** — the supported CRM connector for wins, contacts, and the intro log. Another CRM can be configured during onboarding.
- **Gmail** — required for ask and follow-up drafts.
- **Slack** — required. The weekly who-to-ask list lands in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for who is askable, the kind of intro you want, the quiet window, your ask voice, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: List who to ask for an intro this week, draft the asks, and show the open intro log, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List who to ask for an intro this week and draft the asks
- Show the open intro log and draft a follow-up for anything quiet
- Every Monday, pick three people to ask and Slack me the drafts

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms that know they should ask for intros and never do.
- Asks stay in draft until the founder sends. Every intro gets logged.
