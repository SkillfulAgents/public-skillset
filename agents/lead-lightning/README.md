---
category: Sales
icon: zap
tags:
  - Inbound Leads
  - Same-Day Booking
  - Home Services
  - Lead Response
  - Google Calendar
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Lead Lightning

> Turn today's web, phone, and form leads into booked same-day slots while the customer is still deciding.

## What it does

Lead Lightning owns inbound through a booked slot the same day for founder-led home services shops. During business hours it watches your web form, phone or voicemail, marketplace, and chat sources, then checks service area, job type, and whether the request is a same-day fit under your rules.

For a fit, it reads today's remaining windows on the connected board or calendar, holds the slot, and drafts the confirmation with the window, address, and what to expect. Confirms are queued for one-tap send unless you pre-authorize same-day confirms after a clean trial. It never guarantees a window the board does not show or books work outside the service area.

## What you'll need

- **Google Calendar** — required when the calendar is the booking source for today's windows.
- **Gmail** — required for form and email leads and confirm drafts.
- **Slack** — required. Booked slots, misses, and edge cases land in your founder channel.
- **Jobber, Housecall Pro, or ServiceTitan** — optional, as the booking board instead of the calendar. No registry connector; connected during onboarding.
- **SMS line or OpenPhone** — optional, for phone leads and text confirms. No registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your service area, the same-day cutoff, which board or calendar to book against, the confirm channel, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Handle today's new web, phone, and form leads through a booked same-day slot where the board allows, drafting confirms for approval.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Handle today's new leads and draft same-day confirms where the board allows
- Qualify this morning's form leads and hold slots for the ones in our area
- During business hours, watch every lead source and Slack me each booked slot

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops that need inbound on a same-day booked slot, not a lead alert.
- The agent never quotes a final price unless pricing rules are in config.
