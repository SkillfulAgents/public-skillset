---
category: "Sales"
icon: badge-dollar-sign
tags:
  - "CRM Hygiene"
  - "Forecasting"
  - "Call Notes"
  - "Salesforce"
  - "MEDDICC"
  - "Revenue Operations"
works_with:
  - type: api_account
    slug: salesforce
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: granola
  - type: api_account
    slug: gong
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Forecast Notes Updater

> Walk into your forecast call with every opportunity already updated from what was actually said.

## What it does

After each customer call, demo or meaningful email exchange, Forecast Notes Updater reads the transcript, the thread and any Slack discussion about the deal, finds the right contact and opportunity, and drafts the note in your exact format and qualification framework. Gaps in your framework are called out, not filled in, and numbers and dates are quoted exactly as they were said.

It runs in the modes you choose:

- **Per-call updates** — as soon as a transcript is ready, a proposed note, next step and framework update for that deal. Each meeting is processed once.
- **End-of-day batch** — at 5pm, the day's calls, meetings and buyer emails drafted into one batch to approve, with duplicates of what is already logged removed.
- **Forecast-call digest** — optional: what changed on your in-play deals since last week, and what never got logged.

Stage and forecast changes are only suggested, each with the line from the call that supports it. The agent never moves a deal to closed lost or pass, never touches amounts or close dates on its own, and never overwrites a note a teammate edited later. For the first week it writes nothing without your approval; after that you can let it log plain notes on its own.

## What you'll need

- **Salesforce** — the primary CRM. HubSpot or Attio also work, and a Google Sheet if you have no CRM. Required, one of them.
- **Meeting notes** — Granola or Gong recommended. Fathom, Fireflies, Otter, Zoom recordings, or inviting the agent to listen in on calls also work.
- **Gmail or Outlook** — recommended, to read threads with buyers.
- **Google Calendar** — recommended, to know which meetings happened and who attended.
- **Slack** — optional, to read deal channels you allow.
- **A delivery channel** — the agent's own Slack app, its own email inbox, Telegram, or in-app only, for approval batches.
- **API keys:** none.

## Getting started

1. Import the template into Gamut and send the setup message that is already in the message box.
2. The `agent-onboarding` skill connects your CRM, notes, mail and calendar, asks for your note format, framework, stage rules and in-play deals, and picks the modes and delivery channel.
3. It runs on your last few calls and shows the proposed updates before writing anything.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft the Salesforce update from my call with Example Co this morning
- Show me today's proposed CRM updates and write the ones I approve
- Every Monday before forecast, tell me what changed on my in-play deals

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the three routines, matching and guardrail rules, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, runs a supervised week, sets schedules, and writes `config.json`.
- `.claude/skills/crm-note-format/` — note structure, framework mapping, matching and dedupe rules, and how to write to Salesforce, HubSpot, Attio or a Sheet.

## Notes

- Run state (processed meetings, pending batches, a log of every write) lives under `state/forecast-notes-updater/` in the agent's workspace and holds IDs and field values, not transcripts.
- If Pipeline Doctor is also installed, onboarding asks which agent owns the end-of-day CRM batch so the work is not duplicated.

## Credits

Adapted from the original prompt by [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/forecast-notes-updater/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
