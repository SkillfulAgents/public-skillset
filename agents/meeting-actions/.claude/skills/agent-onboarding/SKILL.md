---
name: agent-onboarding
description: 'First-run setup for Meeting Actions: connects calendar, transcripts, tracker, and Slack routing, maps people, clients, and topics, chooses how tasks are filed, runs a supervised pass on a recent meeting, and sets up the trigger or sweep.'
first_prompt: 'Set up Meeting Actions for me'
---

# Meeting Actions onboarding

## 1. Welcome

Explain in three sentences: after each meeting, this agent pulls out decisions, owned and dated action items, and open questions; files tasks in your tracker without duplicates; routes pieces to the right people; and keeps a decisions log. Show the plan:

1. Calendar and where your transcripts come from.
2. Which meetings are in scope.
3. Your tracker, and whether tasks are filed as you or as the agent.
4. Who is who (attendees to tracker users) and where topics route.
5. Clients and their domains.
6. The leadership decisions log.
7. Where your recap goes and how much the agent does alone.
8. A supervised pass on a real recent meeting.

Skip anything already in `## Your context`.

## 2. Discover connections

Call `mcp__user-input__search_connection_options` for the calendar, the transcript source, the tracker, Slack, Gmail or Outlook, and Google Docs or Notion. Call `mcp__chat__list_agent_integrations` to see whether the agent already has a Slack app, Linear app, GitHub app, or email inbox.

## 3. Ask, one question at a time

1. **Calendar.** Google Calendar or Outlook? Which calendar?
2. **Transcripts.** Where do transcripts or notes come from? (Granola / Fathom / Fireflies / Otter / Gong / Zoom recordings / Invite the agent to listen.) If "invite the agent", which recurring meetings should it join? Mention that attendees will see it, and recording-consent rules may apply.
3. **Scope.** Which meetings? (All internal / Leadership and staff only / Internal plus client delivery / Only meetings I tag.) Anything to always skip (1:1s, interviews, personal, specific titles)? If Call Closer or Call Follow-Up Drafter is installed, which meetings are theirs?
4. **Leadership series.** Which recurring meeting is the leadership or staff meeting? Where should the decisions log live (Google Doc / Notion page / Google Sheet), and may the agent create it?
5. **Tracker.** Which tracker? (Linear / Jira / Asana / Monday / Todoist / Notion / GitHub Issues / Google Sheet.) Which team or project by default?
6. **Filing identity.** If Linear or GitHub: file as you or as the agent's own app? Explain the tradeoff from `AGENTS.md` in two sentences. Default: as you.
7. **People map.** Confirm the mapping from frequent attendees to tracker users. Pre-fill it from recent calendar attendees and the tracker's user list, and ask only about the ones that don't match.
8. **Routing map.** Which topics go where? Example: product feedback → #product, customer asks → the account owner, hiring → you only. Which topics are sensitive and never routed?
9. **Clients.** Client names with email domains, and active engagements per client. Where does the client next-step log live (Sheet / tracker project per client)?
10. **Recap delivery.** (Agent's Slack DM / Agent's email to you / Telegram / iMessage / In-app only.)
11. **Open Loops.** If Open Loops is installed, should delegations and your own items be handed to it? (Yes / No.)
12. **Autonomy.** Confirm: "First three meetings: show items and ask before filing or posting. After that: file tasks and post internal routes alone. External messages and group follow-ups always stay drafts." Offer "always ask" as the alternative.

## 4. Connect

- `mcp__user-input__request_connected_account` for the calendar, tracker (`linear`, `jira`, `asana`, `monday`, `todoist`, `notion`, `github`, `googlesheets`), `gmail` or `outlook`, and `googledocs` if needed.
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies, or Otter with the URL from `search_connection_options`.
- Agent integrations (Slack app for routing; Linear or GitHub app if chosen): `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup` when the provider says to hand setup to the user (Linear and GitHub usually do). Confirm with `list_agent_integrations`, then check the Slack app is in each routing channel with `mcp__chat__list_chat_channels`.

## 5. Supervised dry run

Pick the most recent in-scope meeting with a transcript. Extract with the `meeting-ledger` skill and show the full recap, the tasks you would create (titles, owners, dates, project), the routes you would post, and the draft follow-up. Create nothing yet. Ask what is wrong: missed items, wrong owners, over-capture, wrong project, routing. Fix the maps, rerun on the same meeting, and on approval create the tasks and drafts for real. Mark the meeting processed.

## 6. Schedule and trigger

- Check `mcp__user-input__get_available_triggers` on the Fathom, Zoom, or Gong account. If a transcript-ready event exists, `mcp__user-input__setup_trigger` with a self-contained prompt.
- Otherwise `mcp__user-input__schedule_task`, cron `15 9-19 * * 1-5`, prompt:

> Run Meeting Actions. Process meetings that ended 30 minutes to 24 hours ago and are not in `/workspace/state/meeting-actions/processed-meetings.json`. Config: `/workspace/.claude/skills/agent-onboarding/config.json`. Follow `AGENTS.md` and the `meeting-ledger` skill. Tracker: `<tracker>`, filing as `<user|agent app>`. Autonomy: `<confirm|auto>`. Recap via `send_chat_message` on integration `<id>`. Never send external email; drafts only. Never create a task whose fingerprint exists. If no meetings are ready, send nothing.

- If the agent attends meetings, schedule the join check (`*/10 8-18 * * 1-5`) for the listed series only.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 7. Save

Write the answers under `## Your context` in `AGENTS.md` and create `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "calendar": {"provider": "googlecalendar", "calendar_id": "primary"},
  "transcript_source": {"type": "granola", "via": "mcp", "trigger_id": null, "agent_joins": []},
  "scope": {"include": ["internal", "leadership", "client"], "skip_titles": ["1:1", "Interview"], "owned_by_other_agents": []},
  "internal_domains": ["example.com"],
  "leadership_series": {"title": "Weekly leadership", "event_id": "", "log": {"type": "googledocs", "doc_id": ""}},
  "tracker": {"type": "linear", "filing_as": "user", "default_team": "OPS", "projects": {}},
  "people": [{"name": "Teammate", "email": "teammate@example.com", "tracker_user_id": ""}],
  "routing": [{"topic": "product feedback", "to": {"type": "slack_channel", "id": ""}}],
  "sensitive_topics": ["compensation", "performance", "hiring", "legal", "fundraising"],
  "clients": [{"name": "Example Client", "domains": ["client.example"], "engagements": ["Phase 2 rollout"], "log": {"type": "googlesheets", "sheet_id": "", "tab": "Example Client"}}],
  "recap": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "handoff_to_open_loops": false,
  "autonomy": {"mode": "confirm", "confirm_first_n": 3}
}
```

Summarize what will run when, where tasks and recaps go, and that external messages are drafts only.
