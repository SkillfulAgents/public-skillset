---
category: Personal
icon: house
avatar:
  color: tonal-black
  shape: triangle
tags:
  - Family
  - School
  - Calendar
  - Kids Activities
  - Google Calendar
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: googledrive
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Family Calendar Keeper

> Every flyer, newsletter and last-minute pickup change becomes one shared plan the whole family can trust.

## What it does

Family Calendar Keeper reads mail only from the senders your family approves: teachers, the front office, coaches, clubs, class newsletters, school platforms and other parents. That includes schedules sent as PDFs, flyers and screenshots. It keeps one shared living doc organized per kid, with upcoming events, need-to-knows (forms, payments, RSVPs, "bring X", dress-up days, half-days) and what's due. New items go on top, and each one notes the email it came from.

The doc is the source of truth, and the agent keeps your family calendar matching it: it adds, updates and removes events and flags clashes. For the first week it asks before each calendar change; after that it syncs on its own and you can undo any change. Same-day changes, such as a moved pickup or a cancelled practice, reach you right away. Every early afternoon it checks today's and tomorrow's pickups and activities and tells you who's covering what and where you need a carpool or sitter. If a fix needs someone else to change plans, it drafts the message for you. It stays silent when the day is clean.

If you want them, it also sends ten at-home game ideas each week, tied to what the kids are learning and using only things you have. They come with a small printable pack for the car, and the agent remembers which games landed.

## What you'll need

- **Gmail**: required. It reads only the senders on your allowlist and keeps drafts. Outlook mail also works.
- **Google Calendar**: required, for the family calendar and the calendars it reads for pickups.
- **Google Docs and Google Drive**: required, for the shared family doc and sharing it with your partner, sitter or grandparents.
- **A way to reach you**: Telegram, iMessage, the agent's Slack app or its own email inbox, for urgent pings and digests.
- **Google Maps**: optional, for real drive times between schools and venues.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It learns your kids and their activities, proposes a sender allowlist from your recent mail for you to approve, connects mail, calendar and docs, and picks where urgent pings go.
3. Ask it to build the family doc from this week's school mail and show the calendar changes it would make.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Build our family doc from this week's school and team emails
- Check tomorrow's pickups and tell me if anything clashes
- Every Friday, send me ten games tied to what the kids learned this week

## What's inside

- `AGENTS.md`: the three routines, Gamut mechanics, safe operating rules and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run interview, allowlist builder, supervised dry run, schedules and `config.json`.
- `.claude/skills/family-doc-sync/`: the doc layout, item format, calendar reconcile rules, first-week approval mode and undo.

## Notes

- It never messages teachers, coaches, carpools or sitters, and it never pays, signs or RSVPs. Messages are drafts for you to send.
- It edits or removes only calendar events it created; events a person added are flagged, never changed.
- Different from `household-coordinator`, which is a daily household review built on Apple Messages and grades. The two can run side by side.

## Privacy

Only allowlisted senders are read; the rest of your inbox is never searched. The shared doc holds logistics only. Health, grades and custody details stay out of it unless you ask otherwise. The doc is shared only with the people you name, never by public link.
