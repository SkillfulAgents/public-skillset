---
category: Productivity
icon: calendar-check
avatar:
  color: tonal-brown
  shape: diamond
tags:
  - Calendar
  - Executive Assistant
  - Scheduling
  - Google Calendar
  - Outlook
  - Slack
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: outlook
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Calendar Guardian

> Know the moment a meeting breaks, get the reschedule email already drafted, and never find an invite you didn't make.

## What it does

Calendar Guardian watches one calendar: yours, or a principal's you manage as an executive assistant. Four routines:

- **Conflict alarm.** On every calendar change it checks for double-bookings on protected commitments, key meetings moved or declined by the other side, in-person meetings with no travel time, missing locations or dial-ins, and anything booked outside hours, on a no-meeting day or over PTO. Real problems arrive ranked and deduplicated. For a true clash it drafts a reschedule email in your mailbox that offers three open slots.
- **Health audit.** Twice each weekday it sweeps the next few business days for unanswered invites, overlaps, missing conferencing, back-to-backs without transit and overloaded days, and sends one briefing. It can color-code the calendar to a scheme you choose. That is off by default.
- **Open-time blocks (optional).** It keeps placeholder "Open" blocks in step with real free time: weekdays, business hours, holidays skipped, gaps of 30 minutes or more. It writes only to blocks it created.
- **Client slip alert (optional).** When a client declines or reschedules by email to a shared inbox, it checks the calendar, then posts once to that client's Slack channel from its own Slack app. If it isn't sure which client it is, it DMs you instead.

It never creates, moves, accepts, declines or deletes a real meeting, and it never sends an email.

## What you'll need

- **Google Calendar or Outlook**: required. Your own calendar, or your access as a delegate to a principal's calendar.
- **Gmail or Outlook mail**: required for the reschedule drafts. A shared inbox account is needed only for the slip alert.
- **Slack**: optional. The agent's own Slack app posts slip alerts and can DM you alerts. Slack read access for audit context is also optional.
- **Google Maps**: optional, for live drive-time estimates between in-person meetings.
- **A task tool or notes app**: optional, for audit context.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks whose calendar this is, your hours and protected commitments, where alerts should land and which optional routines to turn on, then connects the accounts.
3. Ask for a supervised first audit of the next three business days, then let it set up the change trigger and the twice-daily schedule.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Audit my next three business days and tell me what needs fixing
- Find my double-bookings this week and draft reschedule emails for them
- Keep my Open blocks synced to real free time for the next two weeks

## What's inside

- `AGENTS.md`: the four routines, Gamut mechanics, safe operating rules and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup, supervised dry run, triggers, schedules and `config.json`.
- `.claude/skills/calendar-checks/`: the issue rubric, collision priority order, alert fingerprinting, slot finding and placeholder rules.

## Notes

- Drafts only. Reschedule emails wait in your Drafts folder, and proposed slots are not held.
- Color-coding, open-time blocks and the slip alert are all off until you turn them on.
- If your calendar provider has no change trigger available, the agent checks every 10 minutes during waking hours instead.

## Privacy

The agent reads event details and, for the slip alert, calendar replies in the shared inbox. Slack posts include the meeting title, time and change, never email bodies or attachments. State files keep event IDs and alert fingerprints only, and old ones are pruned once events pass.
