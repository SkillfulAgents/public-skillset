---
category: Sales
icon: calendar-check
tags:
  - Inbound Leads
  - Lead Qualification
  - Call Booking
  - HubSpot
  - Professional Services
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Inquiry Desk

> Take every inbound inquiry all the way to a qualified call on your calendar, not a polite we-will-be-in-touch.

## What it does

Inquiry Desk owns inbound for founder-led consulting, accounting, insurance, and staffing firms. It watches the web form, email, chat, and referral intros for new inquiries and scores each one against your fit rules: company size, problem, budget signal if they gave one, geography, and conflicts.

For a fit, it reads the founder's calendar and offers two or three real windows, then queues the invite and confirmation for one-tap send. Poor fits get a polite, honest reply instead of a ghost. Invites stay in draft unless you pre-authorize qualified bookings after a trial, and the agent never quotes fees unless a published rate is in config.

## What you'll need

- **Gmail** — required for inquiry intake and reply drafts.
- **Google Calendar** — required to offer real windows and book the call.
- **HubSpot** — the supported CRM connector for logging inquiries. Another CRM can be configured during onboarding.
- **Slack** — required. New qualified leads and edge cases land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your inquiry sources, fit rules, who takes the call, which calendar to book against, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Work today's inbound inquiries through a qualified call on the calendar, drafting invites for approval.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Work today's inbound inquiries and draft invites for the qualified ones
- Score this week's web form leads against our fit rules and show who to call
- Every hour during business hours, triage new inquiries and Slack me the fits

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms with inbound sitting in the inbox.
- The agent never books a time the calendar does not show and never stops at a qualified-lead list without offering a call.
