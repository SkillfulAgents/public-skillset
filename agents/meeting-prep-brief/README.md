---
category: "Sales"
icon: calendar-check
avatar:
  color: tonal-orange
  shape: pill
tags:
  - "Meeting Prep"
  - "Account Research"
  - "Google Calendar"
  - "Gmail"
  - "Sales Calls"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: gmail
  - type: mcp
    slug: granola
  - type: api_account
    slug: gong
  - type: api_account
    slug: salesforce
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Meeting Prep Brief

> Walk into every outside call knowing who is in the room, what you promised last time, and the one thing to ask.

## What it does

Meeting Prep Brief reads your calendar, skips internal meetings by attendee email domain, and writes one short, phone-friendly brief for each external, first-time or high-stakes meeting. Each brief leads with the one thing to say or ask, then who is in the room, your email history with them, what each side promised last time (open items first), what has changed since you last spoke, and recent company news with dates and links.

- **Depth by meeting type**: a first meeting gets the full who-are-they picture; a routine check-in gets only what changed and what is open.
- **Your timing**: one message the evening before, or a brief per meeting shortly before each call.
- **Optional enrichments**: call notes from Granola or Gong, the deal record from Salesforce, HubSpot or Attio, and internal Slack chatter about the account.
- **Optional deck**: if you have a slides agent in your workspace, it can ask that agent for a tailored deck, with your OK.
- **Read-only**: it never contacts attendees, never touches your calendar, and never sends anything as you.

## What you'll need

- **Google Calendar or Outlook** — required, to find the meetings worth briefing.
- **Gmail or Outlook mail** — required, for history with each attendee and past promises.
- **Granola, Gong, Fireflies, Otter or Fathom** — optional, for what was said and promised on past calls.
- **Salesforce, HubSpot or Attio** — optional, for stage, amount and next step.
- **Slack** — optional, for internal chatter about the account; also an optional delivery channel through the agent's own Slack app.
- **API keys:** none. Web research and people lookups use built-in search and enrichment.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill: it connects your calendar and mail, asks which domains are internal, which meetings count, when to deliver and where, then writes a supervised brief for a real upcoming meeting.
3. Once you approve the brief, it schedules the planning runs and briefs land on their own.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Prep me for my next external meeting on Google Calendar
- What did we promise the Acme team on our last Gong call?
- Brief every first-time call 45 minutes before it starts

## What's inside

- `PROMPT.md` — the editable setup request placed in your message box after import.
- `AGENTS.md` — the agent's routines, research rules, Gamut mechanics and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup, dry run and scheduling.
- `.claude/skills/meeting-triage/` — which meetings get a brief, the depth for each meeting type, and the brief format.

## Notes

- LinkedIn is read through search-result snippets, not by opening profile pages, so some titles may be missing or flagged as unconfirmed.
- Rescheduled meetings are briefed once at their new time; cancelled or declined meetings get no brief.
- Recurring 1:1s are left to the One-On-One Prep template unless you opt them in.

## Privacy

The agent reads your calendar, mail and any notes or CRM you connect, and keeps a short business-only note per external company in its workspace. Briefs go only to you.

## Credits

Adapted from the original prompt by [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/meeting-prep-brief/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
