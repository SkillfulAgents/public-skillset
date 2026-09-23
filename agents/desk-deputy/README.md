---
category: Ops
icon: inbox
tags:
  - Front Desk
  - Inbox Drafts
  - Scheduling
  - Missed Calls
  - Small Business
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Desk Deputy

> One agent runs the whole front desk: inbox drafts, calendar moves, and a text back for every missed call.

## What it does

Desk Deputy is the one front-desk owner for micro-owners and founder-led SMBs that still run the desk themselves. It watches your inbox for customer, vendor, and is-this-spam mail and drafts replies in your voice. It books, reschedules, and reminds against your real calendar, offering only times that are actually free.

When a missed call or voicemail lands on the business line, it drafts a text back: we saw it, here is the next step. Inbox, calendar, and phone stay one job with one context instead of three workflows. Sends stay in draft until you approve, unless you pre-authorize a routine path during onboarding.

## What you'll need

- **Gmail** — required for the inbox and reply drafts.
- **Google Calendar** — required for booking, rescheduling, and reminders.
- **Slack** — required. Spicy exceptions and the daily desk summary land here.
- **OpenPhone** — optional, for missed calls and voicemail. No registry connector; connect the line during onboarding or forward voicemails to the inbox.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your inbox, calendar, phone line, voice samples, and which sends may go out automatically, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Work today's inbox, calendar, and missed calls as one desk, drafting replies, invites, and texts without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Work today's inbox, calendar, and missed calls and show me the drafts
- Draft a text back to every voicemail from this morning with the next step
- Every weekday at 5pm, summarize the desk and what still needs my reply

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners and founder-led SMBs still running the desk themselves.
- The agent never answers legal, HR, or payment disputes on its own and never asks for passwords or 2FA codes in chat.
- It will not invent availability or hide a calendar conflict.
