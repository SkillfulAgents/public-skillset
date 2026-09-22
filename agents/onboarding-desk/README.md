---
category: Customer Success
icon: list-checks
tags:
  - Client Onboarding
  - Kickoff
  - Agency Ops
  - Google Drive
  - Google Calendar
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: dropbox
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

# Onboarding Desk

> A newly signed client lands in the folder, the tracker, a kickoff on the calendar, and a first report date within the hour.

## What it does

Onboarding Desk owns the first ten days after a client signs for founder-led marketing, creative, and web shops. It watches for a signed SOW, a paid first invoice, or a founder this-one-is-in note, then creates the client folder in Drive or Dropbox from your template structure and adds the client to the tracker.

It drafts the kickoff agenda and the client-facing kickoff note, books the kickoff against real calendar availability, and sets the first report date from the SOW cadence (default 30 days) on both the tracker and the calendar. Client emails stay in draft until you send, and the agent never starts billable work the SOW does not include.

## What you'll need

- **Google Drive or Dropbox** — one is required for the client folder.
- **Google Calendar** — required to book the kickoff and the first report date.
- **Gmail** — required for the kickoff note draft.
- **Slack** — required. New-client notices and drafts land in your founder channel.
- **Client tracker** — optional. A sheet or tracker the agent adds each client to.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your folder template, what counts as signed, kickoff attendees, the first report cadence, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Onboard the newest signed client into the folder, the tracker, a kickoff on the calendar, and a first report date, with the client note in draft.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Onboard the newest signed client: folder, tracker, kickoff, first report date
- Draft the kickoff agenda and client note for Northwind from their SOW
- Whenever a first invoice is paid, run onboarding and Slack me the kickoff draft

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led agencies that lose the first 10 days after a client signs.
- The agent never asks for passwords, cookies, or 2FA codes in chat and never invents a folder structure when the agency has a template.
