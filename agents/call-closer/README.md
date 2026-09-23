---
category: Sales
icon: phone-call
tags:
  - Call Follow-Up
  - Meeting Recaps
  - CRM Hygiene
  - Google Calendar
  - Professional Services
works_with:
  - type: mcp
    slug: granola
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: asana
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Call Closer

> Turn every client call into a sent recap, assigned tasks, a clean CRM record, and the next meeting on the calendar.

## What it does

Call Closer owns the after-call close-out for founder-led consulting, accounting, insurance, and staffing firms. From the transcript or notes it drafts a client-facing recap of what you heard, what you promised, and the next step. It lists internal tasks with owners and due dates and creates them in your tracker or Asana when connected.

It updates the CRM with stage, notes, amount if discussed, next step, and date, without overwriting a newer note. If a next meeting was agreed, it books it against real calendar availability and drafts the invite. Recaps and invites stay in draft until you approve, and the agent never invents a promise that was not on the call.

## What you'll need

- **Granola** — recommended for call transcripts and notes, through the Granola MCP. Pasted notes work too.
- **Google Calendar** — required to book the next meeting against real availability.
- **HubSpot** — the supported CRM connector. Another CRM can be configured during onboarding.
- **Asana** — optional, for creating the internal tasks.
- **Gmail** — required for recap and invite drafts.
- **Slack** — required for the founder close-out summary.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your notes source, your CRM, the recap voice, who owns default tasks, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Close out the last call: recap, tasks, CRM, and next meeting, all in draft.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Close out my last call: recap, tasks, CRM update, and next meeting
- Draft the client recap for today's Harper call and list who owes what
- After every Granola call, run the full close-out and Slack me the drafts

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms whose follow-up dies in the notes doc.
- This is not a meeting-notes agent. A run is not done until recap, tasks, CRM, and next meeting are all handled.
- The agent never books a time the calendar does not allow.
