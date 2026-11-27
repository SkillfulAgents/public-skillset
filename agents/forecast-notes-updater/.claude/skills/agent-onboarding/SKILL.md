---
name: agent-onboarding
description: 'First-run setup for Forecast Notes Updater: connects the CRM, mail, calendar, Slack and meeting notes, learns the note format and qualification framework, picks the in-play deals and modes, runs a supervised week of proposals, and schedules everything.'
---

# Forecast Notes Updater onboarding

## 1. Welcome

Tell the user in three or four sentences: this agent turns each customer call, email thread and Slack discussion into CRM notes and forecast updates in their exact format, proposes every change, and writes only what they approve. Then show the plan:

1. Which CRM, and which deals are in play.
2. Where call notes, email and Slack come from.
3. Your note format and qualification framework.
4. Your stage definitions and what the agent may suggest.
5. Per-call updates, an end-of-day batch, or both, plus an optional forecast-call digest.
6. Where approval batches reach you.
7. What the agent may do alone (default: nothing is written without approval for the first week).
8. A supervised run on your real calls.

Skip any step already answered in `## Your context` in `AGENTS.md`.

## 2. Discover connections

For Salesforce, HubSpot, Attio, Gmail, Outlook, Google Calendar, Slack and the meeting-notes tool, call `mcp__user-input__search_connection_options` with the service name. Note what is already connected and the exact slug. Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox or Telegram for delivery. Call `mcp__agents__list_agents` to see whether Pipeline Doctor, Call Follow-Up Drafter, Call Closer or Open Loops are installed.

Mechanism rules:
- CRM, mail, calendar and Slack reading: the user's connected account, because writes must appear as the user and reads must see the user's own mail.
- Meeting notes: Granola, Fireflies and Otter through remote MCP (`granola`, `fireflies-ai`, `otter-ai`); Gong, Fathom and Zoom through connected accounts (`gong`, `fathom`, `zoom`). The agent can also join calls itself in `listen` mode.
- Approval delivery: an agent integration, or in-app only.

## 3. Ask, one question at a time

Use `AskUserQuestion` where options are discrete.

1. **CRM.** Salesforce / HubSpot / Attio / No CRM (use a Google Sheet)? If Salesforce: which opportunity fields matter for your forecast (Next Step, Description, custom forecast or commentary fields)? Read the object describe and confirm field API names with the user.
2. **Deals in play.** Paste or name the opportunities in play this quarter, or choose "all my open deals I own". Also your own email domains and any domains to ignore (partners, vendors, investors).
3. **Meeting notes.** Granola / Gong / Fathom / Fireflies / Otter / Zoom recordings / I'll invite the agent to calls / None.
4. **Other sources.** Read email threads with buyers? (Yes / No.) Read Slack? If yes, which channels (for example deal rooms or a sales channel); DMs only if the user says so.
5. **Note format.** Ask the user to paste one or two notes they consider perfect, or pick the default from the `crm-note-format` skill. Which framework: MEDDICC / MEDDPICC / BANT / SPICED / our own / none?
6. **Stages.** Confirm the stage list and, for each forward move, what evidence counts. Confirm the guardrails: the agent never moves a deal to Closed Lost, Pass or any closed stage, and amount, close date and forecast category are proposals only.
7. **Mode.** Per-call updates / End-of-day batch at 5pm / Both. Confirm timezone. If Pipeline Doctor is installed with its end-of-day draft on, ask which agent should own the end-of-day batch.
8. **Forecast digest.** Do you have a weekly forecast call? Day and time? Send a "what changed" digest an hour before? (Yes / No.)
9. **Delivery.** Where should approval batches reach you? (Agent's Slack DM / Agent's email to you / Telegram / In-app only.)
10. **Autonomy.** Confirm: "For the first week the agent proposes everything and writes nothing without your approval." Then ask what happens after the week: keep approving everything, or let plain activity notes and next-step text be logged automatically (stage, forecast, amount, close date and new contacts always wait).

## 4. Connect

- `mcp__user-input__request_connected_account` for the CRM (`salesforce`, `hubspot` or `attio`, or `googlesheets`), `gmail` or `outlook`, `googlecalendar`, and `slack` if chosen. Reason text such as "Allow access to Salesforce to propose and log opportunity notes after your calls?"
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies or Otter with the URL from `search_connection_options`; `request_connected_account` for `gong`, `fathom` or `zoom`.
- For delivery, use the configured agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or `mcp__user-input__request_integration_setup`). Confirm with `list_agent_integrations`.

## 5. Supervised dry run

Pick the two or three most recent external calls on in-play deals (last 7 days) and run routine 1 on them, plus one end-of-day batch for yesterday if that mode is on. Show the user, without writing anything:
- the matched account and opportunity for each, and any flagged matches,
- the proposed note in their format, with gaps listed,
- next steps, suggested stage or forecast change with the quote,
- what was dropped as a duplicate.

Ask what was wrong: format, missing signals, wrong matches, tone. Adjust `## Your context` and re-run once. Write only the items the user explicitly approves, then show the record links. Mark those meetings in `processed-meetings.json`.

## 6. Schedule

- Per-call: call `mcp__user-input__get_available_triggers` on the Gong, Fathom or Zoom account and `mcp__user-input__setup_trigger` for a transcript-ready event if one exists. Otherwise `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `0 9-18 * * 1-5`.
- End-of-day: `schedule_task`, `0 17 * * 1-5`.
- Forecast digest: `schedule_task`, one hour before the forecast call.

Each prompt must be self-contained. Template:

> Run the Forecast Notes Updater **end-of-day CRM batch**. Config: `/workspace/.claude/skills/agent-onboarding/config.json`; context in `AGENTS.md` `## Your context`. Follow the `crm-note-format` skill. State: `/workspace/state/forecast-notes-updater/` (skip meetings in `processed-meetings.json`; save the batch to `eod-batches/<date>.json`). Deliver via `send_chat_message` on integration `<id>` to `<destination>`. If nothing qualifies, send nothing. Write nothing to the CRM without approval, except plain notes when `autonomy.auto_log_notes` is true; never change stage, amount, close date or closed outcomes. If a source fails, say which one.

Also schedule a one-time reminder (`scheduleType: "at"`) at the end of the first week asking the user whether to switch on note-only auto-logging.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers` and show the user the list.

## 7. Save

Write the confirmed answers under `## Your context` in `AGENTS.md` as short bullets. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "crm": {"type": "salesforce", "via": "connected_account", "fields": {"next_step": "NextStep", "notes": "Description", "forecast_commentary": ""}},
  "own_domains": ["example.com"],
  "ignore_domains": [],
  "in_play": {"scope": "list", "opportunity_ids": []},
  "sources": {
    "meeting_notes": {"type": "granola", "via": "mcp"},
    "mail": {"provider": "gmail", "read": true},
    "calendar": "googlecalendar",
    "slack": {"read": false, "channels": []}
  },
  "note_format": {"example": "", "framework": "MEDDICC"},
  "stages": [{"name": "Discovery", "enter_evidence": ""}],
  "modes": {
    "per_touchpoint": {"on": true, "trigger_id": null, "cron": "0 9-18 * * 1-5"},
    "end_of_day": {"on": true, "cron": "0 17 * * 1-5"},
    "forecast_digest": {"on": false, "cron": "0 9 * * 1"}
  },
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "autonomy": {"approval_week_ends": "2026-11-27", "auto_log_notes": false},
  "eod_owner": "forecast-notes-updater"
}
```

Finish with a short summary: what runs when, where batches land, and that nothing is written without approval.
