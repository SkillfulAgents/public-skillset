---
name: agent-onboarding
description: 'Configures Proposal Pilot for the firm: notes source, template and rate card, mailbox, CRM or Sheet, stage mapping, follow-up cadence and speed window, approvers, then a supervised draft and the trigger and schedules.'
first_prompt: 'Set up Proposal Pilot for me'
---

# Agent Onboarding

Welcome. This onboarding configures your Proposal Pilot workspace so the agent can run against your own tools and process. Tell the founder up front what you will cover: where call notes, the proposal template, and the rate card live; your mailbox and CRM; how your deal stages map to proposal milestones; the follow-up cadence and how fast proposals should go out; who approves; and where the daily digest goes. Then one supervised proposal from real notes before anything runs on its own.

Ask one question at a time and wait for each answer. Use `AskUserQuestion` when the options are discrete.

## 1. Connect the systems

For each service, call `mcp__user-input__search_connection_options` first, and check `CONNECTED_ACCOUNTS`, the remote MCP list, and `mcp__chat__list_agent_integrations` so you never ask twice.

1. **Firm, template, and rate card.** What is the firm name, and where are the proposal template and rate card? Connect `googledrive` and `googledocs` with `mcp__user-input__request_connected_account`, or ask for the files with `mcp__user-input__request_file`.
2. **Call notes.** `AskUserQuestion`: Granola, Fathom, Fireflies, Otter, Gong, Zoom, CRM notes, or a paste. Connect with `mcp__user-input__request_remote_mcp` (`granola`, `fireflies-ai`, `otter-ai`) or `request_connected_account` (`fathom`, `gong`, `zoom`).
3. **Mailbox and calendar.** Request `gmail` and `googlecalendar`, or `outlook`. Explain: "Proposals and follow-ups land as drafts in your mailbox. I never send."
4. **CRM.** `AskUserQuestion`: HubSpot, Salesforce, Attio, Pipedrive, Close, or no CRM (I create a pipeline Sheet with `googlesheets`).
5. **Digest channel.** `AskUserQuestion`: in-app, the agent's own Slack app (channel or DM), an email from the agent's own inbox, or Telegram. Set it up with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and send a test with `mcp__chat__send_chat_message`.

## 2. Rules of the job

6. **Stages.** Show the CRM pipeline and map its stages to: discovery done, proposal sent, client replied, contract out, signed. Which forward moves may the agent make on evidence without asking? Lost and parked are always the founder's call.
7. **Speed window.** How many business days from discovery call to proposal sent is your target? (Default 3.)
8. **Cadence.** Show the default: proposal follow-ups on days 2, 5, and 10, contract follow-ups on days 3 and 7, then a founder call. `AskUserQuestion`: keep it, adjust the days, or business days versus calendar days.
9. **Contract and signature.** What do you send after a yes (engagement letter, MSA and SOW), and which e-signature tool?
10. Who must approve price, and which work types always need a lawyer or partner pass (spicy)?
11. **Voice.** Paste a proposal intro and one follow-up that sound like you, or let me read recent ones from your sent mail.
12. Timezone, and which clients or contacts are do-not-contact.

## 3. Supervised dry run

Take the latest discovery call notes and draft the proposal Doc and the send email, with the gap list. Then load the open proposals you can find in sent mail and the CRM, show each one's stage, days since sent, and the next touch with its date, and draft one follow-up. Ask what to change, fix the config, and rerun once. Write nothing to the CRM and send nothing.

## 4. Schedule

1. Call `mcp__user-input__get_available_triggers` on the mailbox account and pick the new-message trigger (never guess the slug). Create it with `mcp__user-input__setup_trigger` and the self-contained prompt from `AGENTS.md`. If none exists, the daily check also sweeps mail.
2. Discovery calls: a transcript-ready trigger on the notes source if offered; otherwise `mcp__user-input__schedule_task` with cron `40 9-18 * * 1-5`.
3. Daily cadence check `0 8 * * 1-5` and weekly view `0 8 * * 1`, in the founder's timezone.
4. Verify with `mcp__user-input__list_triggers` and `mcp__user-input__list_scheduled_tasks`, and seed `/workspace/state/proposal-pilot/deals.json` with the open proposals from the dry run.

## Configuration to save

Write the answers into `AGENTS.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json` with this structure:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "",
  "source_system_connected": false,
  "proposal_template": "",
  "rate_card": "",
  "proposal_folder": "",
  "crm": {"system": "", "sheet_url": "", "stage_map": {"discovery_done": "", "proposal_sent": "", "client_replied": "", "contract_out": "", "signed": ""}, "auto_forward_moves": []},
  "speed_window_business_days": 3,
  "cadence": {"proposal_days": [2, 5, 10], "contract_days": [3, 7], "day_type": "business", "after_last_touch": "founder_call"},
  "esignature_tool": "",
  "alert_destination": "",
  "alert_integration_id": "",
  "workflow_owner": "",
  "escalation_contact": "",
  "timezone": "",
  "voice_notes": "",
  "approval_required_for": ["price", "proposal send", "follow-up send", "stage changes"],
  "business_rules": {"spicy": []},
  "do_not_touch": [],
  "first_run_goal": "Turn the latest call notes into a sendable proposal. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Turn the latest call notes into a sendable proposal. Do not send.
