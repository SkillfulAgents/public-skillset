---
name: agent-onboarding
description: 'Configures Quote Chaser for the shop: estimate source, mailbox, follow-up cadence and speed window, quiet hours, voice, digest channel and approval rules, then a supervised chase and the daily schedule.'
first_prompt: 'Set up Quote Chaser for me'
---

# Agent Onboarding

Welcome. This onboarding configures your Quote Chaser workspace so the agent can run against your own tools and process. Tell the founder up front what you will cover: where estimates live, your mailbox and texting setup, the follow-up cadence, how your nudges sound, where the daily digest goes, and what always needs you. Then one supervised chase on your real estimates before anything runs on its own.

Ask one question at a time and wait for each answer. Use `AskUserQuestion` when the options are discrete.

## 1. Connect the systems

For each service, call `mcp__user-input__search_connection_options` first, and check `CONNECTED_ACCOUNTS` and `mcp__chat__list_agent_integrations` so you never ask twice.

1. **Shop and estimate source.** What is the shop name? `AskUserQuestion`: Jobber, Housecall Pro, ServiceTitan, a Google Sheet, or other. If the tool has a connector, request it. If not, ask whether they can create an API key (save it with `mcp__user-input__request_secret`, UPPER_SNAKE_CASE, never echo it back), or use the browser with `mcp__user-input__request_login`, or a sheet export (`googlesheets`).
2. **Mailbox.** Request `gmail` or `outlook` with `mcp__user-input__request_connected_account`. Explain: "Email nudges land as drafts in your mailbox. I never send."
3. **Texts.** Do customers mostly text? Does your field-service tool send texts? If not, text drafts appear in the approval message for the office to send from the shop phone.
4. **Digest channel.** `AskUserQuestion`: in-app, the agent's own Slack app (channel or DM), an email from the agent's own inbox, or Telegram. Set it up with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and send a test with `mcp__chat__send_chat_message`.

## 2. Rules of the job

5. **Cadence.** Show the default: nudges on days 2, 5, and 10 after the estimate is sent, days 3 and 7 after approval paperwork or a deposit request, then a founder call. `AskUserQuestion`: keep, adjust, or business versus calendar days.
6. **Speed window.** How soon after a site visit should the estimate be out? (Default 2 business days.)
7. **Expiring estimates.** Do your estimates expire, and after how many days?
8. **Voice.** Paste one follow-up that sounds like you, or let me read a few from your sent mail.
9. **Approvals.** Who approves sends? Any customers, job types, or dollar amounts that always need a founder call first?
10. **Quiet hours and do-not-contact.** Confirm text quiet hours (default 8am to 7pm customer time) and anyone never to contact.
11. Timezone, and the time for the daily chase (default 7am weekdays).

## 3. Supervised dry run

Pull the open estimates. Show each one's stage, days since sent, the next touch and its date, and which are parked for missing info or spicy. Draft three nudges (a first touch, a second touch, an expiring one). Ask what to change, fix the config, and rerun once. Send nothing and write nothing back to the source system.

## 4. Schedule

1. Create the daily chase with `mcp__user-input__schedule_task` (`scheduleType: "cron"`, `0 7 * * 1-5`, shop timezone) and the self-contained prompt from `CLAUDE.md`.
2. Create the weekly scoreboard (`0 7 * * 1`).
3. Optional: call `mcp__user-input__get_available_triggers` on the mailbox and set up the new-message trigger with `mcp__user-input__setup_trigger` so replies pause the cadence the same day. Never guess the slug.
4. Verify with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`, and seed `/workspace/state/quote-chaser/estimates.json` from the dry run.

## Configuration to save

Write the answers into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json` with this structure:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "",
  "source_system_connected": false,
  "source_access": "connector | api_key | browser | sheet",
  "mailbox": "",
  "sms": {"via": "field_service_tool | manual", "quiet_hours": "08:00-19:00"},
  "alert_destination": "",
  "alert_integration_id": "",
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": {"estimate_days": [2, 5, 10], "paperwork_days": [3, 7], "day_type": "business", "after_last_touch": "founder_call", "expiring_touch_days_before": 3},
  "speed_window_business_days": 2,
  "daily_chase_cron": "0 7 * * 1-5",
  "timezone": "",
  "voice_notes": "",
  "approval_required_for": ["every send", "discounts", "start dates", "won or lost"],
  "business_rules": {"spicy_amount_over": null, "spicy_job_types": []},
  "do_not_touch": [],
  "first_run_goal": "Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends. Do not send.
