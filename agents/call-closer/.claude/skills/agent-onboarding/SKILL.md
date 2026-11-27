---
name: agent-onboarding
description: 'Configures Call Closer for the firm: notes source, calendar, mailbox, CRM or Sheet, stage map and guardrails, task tracker, voice, summary channel, then a supervised close-out and the trigger or hourly sweep.'
first_prompt: 'Set up Call Closer for me'
---

# Agent Onboarding

Welcome. This onboarding configures your Call Closer workspace so the agent can run against your own tools and process. Tell the founder up front what you will cover: where call notes live, your calendar and mailbox, your CRM and stage rules, where tasks go, how your recaps sound, where you send the close-out summary, and what the agent may do alone. Then one supervised close-out on a real call before anything runs on its own.

Ask one question at a time and wait for each answer. Use `AskUserQuestion` when the options are discrete.

## 1. Connect the systems

For each service, call `mcp__user-input__search_connection_options` first, and check `CONNECTED_ACCOUNTS`, the remote MCP list, and `mcp__chat__list_agent_integrations` so you never ask for something already connected.

1. **Firm.** What is the firm name, and which email domains are yours? (Used to tell client calls from internal ones.)
2. **Call notes.** `AskUserQuestion`: Granola, Fathom, Fireflies, Otter, Gong, Zoom recordings, the agent joins calls to take notes, or pasted notes. Connect with `mcp__user-input__request_remote_mcp` (`granola`, `fireflies-ai`, `otter-ai`) or `mcp__user-input__request_connected_account` (`fathom`, `gong`, `zoom`).
3. **Calendar and mailbox.** Google or Microsoft? Request `googlecalendar` and `gmail`, or `outlook`. Explain: "Recaps land as drafts in your mailbox. I never send."
4. **CRM.** `AskUserQuestion`: HubSpot, Salesforce, Attio, Pipedrive, Close, other, or no CRM (Google Sheet). Connect it, or create the Sheet with the columns in `AGENTS.md`. For a CRM with no connector, ask whether an API key is available (`mcp__user-input__request_secret`).
5. **Tasks.** Where do internal tasks go: the CRM's tasks, Asana, Linear, ClickUp, Monday, Todoist, or nowhere? Connect if needed.
6. **Summary channel.** `AskUserQuestion`: in-app, a Slack channel or DM from the agent's own Slack app, an email from the agent's own inbox, or Telegram. Set it up with `mcp__chat__add_agent_integration` (or `mcp__user-input__request_integration_setup`) and send a test with `mcp__chat__send_chat_message`.

## 2. Rules of the job

7. Who owns follow-up tasks when the call did not name someone?
8. **Stage map.** Show the CRM's pipeline stages and ask what call outcomes map to which stage. Ask which forward moves, if any, the agent may make without asking. Moves to lost, pass, or closed, and backward moves, are always proposals.
9. **Voice.** Paste a recap that sounds like you, or let me read five recent follow-ups from your sent mail. Do you want a welcome-email version for kickoff calls?
10. **Next meeting.** `AskUserQuestion`: always one-tap (default), or book automatically when the client already agreed a specific time on the call. Ask working hours, buffers, and which calendar to book on.
11. Which meetings should be skipped (recurring internal, interviews, specific clients)?
12. Timezone, and do you want the end-of-day sweep?

## 3. Supervised dry run

Pick the most recent client call with notes. Run the full close-out without writing anything: show the attribution and why, the recap draft, the task list with owners and dates (estimates marked), the CRM note and proposed stage change, and the proposed next-meeting times. Ask what to change, fix the config, and rerun once. When the founder approves, save the draft, create the tasks, and write the CRM note. Record the meeting in `processed-meetings.json`.

## 4. Schedule

1. Call `mcp__user-input__get_available_triggers` on the notes source's connected account. If a transcript-ready event exists, create it with `mcp__user-input__setup_trigger` and the self-contained prompt from `AGENTS.md`. Never guess a slug.
2. Otherwise create the hourly sweep with `mcp__user-input__schedule_task` (`scheduleType: "cron"`, `20 9-19 * * 1-5`, founder's timezone) and the same prompt.
3. Create the end-of-day sweep if wanted (`0 18 * * 1-5`).
4. Verify with `mcp__user-input__list_triggers` and `mcp__user-input__list_scheduled_tasks`, and tell the founder what runs when.

## Configuration to save

Write the answers into `AGENTS.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json` with this structure:

```json
{
  "company_name": "",
  "firm_domains": [],
  "service_areas": [],
  "source_system": "",
  "source_system_connected": false,
  "calendar": "",
  "mailbox": "",
  "crm": {"system": "", "sheet_url": "", "stage_map": {}, "auto_forward_moves": [], "never_auto": ["lost", "pass", "closed", "backward"]},
  "task_tracker": "",
  "alert_destination": "",
  "alert_integration_id": "",
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": "trigger or hourly sweep 20 9-19 * * 1-5",
  "end_of_day_sweep": "",
  "timezone": "",
  "voice_notes": "",
  "welcome_email": false,
  "next_meeting": {"auto_book_agreed_times": false, "working_hours": "", "buffer_minutes": 15},
  "skip_meetings": [],
  "approval_required_for": ["client emails", "calendar invites", "stage changes"],
  "business_rules": {"default_due_days": 5},
  "do_not_touch": [],
  "first_run_goal": "Close out the last call: recap, tasks, CRM, and next meeting on the calendar. Draft the client recap. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Close out the last call: recap, tasks, CRM, and next meeting on the calendar. Draft the client recap. Do not send.
