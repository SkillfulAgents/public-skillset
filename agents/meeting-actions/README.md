---
category: Productivity
icon: list-checks
avatar:
  color: tonal-purple
  shape: pill
tags:
  - Meeting Notes
  - Action Items
  - Decision Log
  - Task Management
  - Linear
  - Granola
works_with:
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: granola
  - type: api_account
    slug: linear
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googledocs
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Meeting Actions

> Every meeting ends with owners, due dates, and tasks already filed, and nothing agreed in the room gets lost by Friday.

## What it does

Meeting Actions reads the transcript of each team, staff, leadership, or client-delivery meeting and pulls out three things: decisions, action items with an owner and a due date, and open questions. Estimated dates are labeled. Owners are matched against the attendee list, and anything ambiguous comes back to you to confirm instead of being guessed.

It then does the admin you would otherwise do by hand:

- **Files tasks** in Linear, Jira, Asana, Monday, Todoist, Notion, GitHub Issues, or a Google Sheet. Tasks are filed as you, or as the agent's own Linear or GitHub app if you prefer automated work to be visibly labeled. It checks for an existing task before creating one, so the same commitment raised in three meetings is still one task.
- **Routes the pieces**: product feedback to the product channel, a customer ask to the account owner. Internal posts come from the agent's own Slack app, and anything external waits as a draft in your Gmail or Outlook.
- **Keeps a leadership decisions log**, newest first, that flags reversals of earlier decisions and carries open follow-through items into the next meeting.
- **Logs client next steps** against the right client and engagement, and never blends two clients together.

Sales and client close-out calls belong to Call Closer and Call Follow-Up Drafter. This template is for the meetings where your own team decides and divides work.

## What you'll need

- **Google Calendar** — required, to find meetings, attendees, and your recurring leadership series. Outlook calendar also works.
- **Granola** — or another transcript source: Fathom, Fireflies, Otter, Gong, Zoom recordings, or the agent joining the call in listen mode.
- **Linear** — or your tracker of choice: Jira, Asana, Monday, Todoist, Notion, GitHub Issues, or a Google Sheet.
- **Gmail** — recommended, for group follow-up and external drafts. Outlook also works.
- **Google Docs** — for the decisions log. Notion or a Google Sheet also works.
- **Slack** — optional. The agent's own Slack app posts routed items to channels and teammates.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your calendar, transcripts, and tracker, maps attendees to tracker users and topics to channels, sets up your client domains and decisions log, and asks how much the agent may do alone.
3. It processes your most recent meeting as a supervised dry run, creating nothing until you approve, then sets up a transcript-ready trigger or an hourly workday sweep.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Pull the action items from this morning's staff meeting and show me
- File Linear issues for every action item from Tuesday's leadership sync
- What did leadership decide this month, and what reversed?

## What's inside

- `AGENTS.md` — the three routines, the filing-identity tradeoff, the no-duplicates rule, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, builds the people, routing, and client maps, and writes `config.json`.
- `.claude/skills/meeting-ledger/` — extraction rules, owner resolution, task fingerprinting and tracker search, the recap layout, and the decisions-log format.

## Notes

- Each meeting is processed exactly once. Where your transcript tool has no "transcript ready" event, an hourly workday sweep picks meetings up 30 minutes after they end.
- For the first three meetings, the agent shows its work and asks before filing or posting. External messages are always drafts.
- Pairs with Open Loops, which can receive each meeting's delegations and chase them.

## Privacy

Transcripts are read through your own connected accounts. Sensitive topics such as compensation, performance, and legal matters are never routed to channels. If the agent joins a call to listen, every attendee can see it in the participant list.
