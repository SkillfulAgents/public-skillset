---
category: Sales
icon: phone-call
avatar:
  color: tonal-forest
  shape: circle
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

Call Closer owns the after-call close-out for founder-led consulting, accounting, insurance, and staffing firms. When a client call's notes are ready, it confirms which client and engagement the call belongs to, asking you whenever it is not sure, and never mixes details between clients. It drafts a client-facing recap in your Gmail of what you heard, what you promised, what you asked for, and the next step. It also creates internal tasks with owners and due dates, marking every inferred date as an estimate and updating existing tasks instead of duplicating them.

It logs a concise call note in your CRM, or in a Google Sheet if you don't use one, without overwriting a newer human note. Stage changes follow your stage map and are proposed for approval. It never moves a deal to lost or pass on its own. If a next meeting was agreed, it proposes real times from your calendar. Each call is processed exactly once, and an hourly sweep catches notes that arrive late.

## What you'll need

- **Granola** — recommended for call transcripts and notes, through the Granola MCP. Fathom, Fireflies, Otter, Gong, Zoom, the agent joining the call, or pasted notes also work.
- **Google Calendar** — required to tell client calls from internal ones and to propose the next meeting against real availability.
- **HubSpot** — the supported CRM connector. Salesforce, Attio, Pipedrive, Close, or a Google Sheet can be configured during onboarding.
- **Asana** — optional, for creating the internal tasks.
- **Gmail** — required for recap and invite drafts. Outlook works too.
- **Slack** — for the founder close-out summary, sent from the agent's own Slack app. Email or in-app also work.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your notes source, calendar, mailbox, and CRM, and asks for your stage map, default task owner, recap voice, and where close-out summaries go. Then it saves the answers into `AGENTS.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Close out the last call: recap, tasks, CRM, and next meeting, all in draft. Once you approve it, the agent sets up the transcript trigger or the hourly sweep.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Close out my last call: recap, tasks, CRM update, and next meeting
- Draft the client recap for today's Harper call and list who owes what
- After every Granola call, run the full close-out and Slack me the drafts

## What's inside

- `AGENTS.md` — the close-out routine with its attribution, CRM, and task guardrails, the Gamut setup, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that connects your systems, captures your stage map, voice, and approval rules, runs a supervised close-out, and schedules the runs.

## Notes

- Built for 2-200 person founder-led professional firms whose follow-up dies in the notes doc.
- This is not a meeting-notes agent. A run is not done until recap, tasks, CRM, and next meeting are all handled.
- Internal meetings are skipped; the Meeting Actions template covers those.
- Recaps and invites stay in draft until you approve the exact version. The agent never books a time the calendar does not allow.
