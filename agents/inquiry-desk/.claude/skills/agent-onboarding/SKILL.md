---
name: agent-onboarding
description: 'Configures Inquiry Desk for the firm: mailbox, calendar, CRM, inquiry sources, fit rules, voice learned from sent mail, booking rules and alert channel, then a supervised drafting run and the new-mail trigger.'
first_prompt: 'Set up Inquiry Desk for me'
---

# Agent Onboarding

Welcome. This onboarding configures your Inquiry Desk workspace so the agent can run against your own tools and process. Tell the founder up front what you will cover: your mailbox and calendar, where inquiries come from, your CRM, what a qualified call means for you, how you write, when calls can be booked, and where alerts go. Then a supervised run on real recent inquiries and prospect replies before anything runs on its own.

Ask one question at a time and wait for each answer. Use `AskUserQuestion` when the options are discrete.

## 1. Connect the systems

For each service, call `mcp__user-input__search_connection_options` first, and check `CONNECTED_ACCOUNTS`, the remote MCP list, and `mcp__chat__list_agent_integrations` so you never ask twice.

1. **Firm.** What is the firm name, and who takes the first call?
2. **Mailbox and calendar.** Request `gmail` and `googlecalendar`, or `outlook`, with `mcp__user-input__request_connected_account`. Explain: "Replies land as drafts in your mailbox. I never send."
3. **Inquiry sources.** `AskUserQuestion` (multi-select): contact form emails, a Typeform, another form tool, a shared inbox address, referral intros, replies to my outbound emails. For Typeform request `typeform`; for other form tools, offer a webhook endpoint or rely on the notification email.
4. **CRM.** `AskUserQuestion`: HubSpot, Salesforce, Attio, Pipedrive, Close, or none.
5. **Alert channel.** `AskUserQuestion`: in-app, the agent's own Slack app (channel or DM), an email from the agent's own inbox, or Telegram. Set it up with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and send a test with `mcp__chat__send_chat_message`.

## 2. Rules of the job

6. **Qualified call.** What is a qualified call for you: size, problem, geography, budget signal, exclusions, conflicts?
7. **Outbound replies.** How do I recognize your outbound threads (a sequence tool, a label, any thread you started with someone not yet a client)?
8. **Voice.** Read 30 to 50 recent replies from sent mail and summarize the voice in three or four bullets. Ask if it is right, and paste one booking note that sounds like you if the sample is thin.
9. **Times.** Call length, working hours, buffers, minimum notice, which calendar, and whether you use a booking link (`calendly` if so).
10. **Rates and materials.** Any published rate I may quote, and links I may share (case studies, a one-pager)? Otherwise I never quote fees.
11. **Booking autonomy.** `AskUserQuestion`: every reply and invite is one-tap (default), or after a trial, qualified bookings may be created when the prospect picks one of the offered times.
12. **Spicy.** Which inquiries always come to you unsent (enterprise procurement, existing clients, conflicts, press)?
13. Timezone.

## 3. Supervised dry run

Find the last five inquiries and prospect replies from the past two weeks. For each, show the classification, fit score and reasoning, and a reply draft with real times. Ask what to change in tone, length, or qualification, fix the config, and redraft one. Save the approved drafts to the mailbox only if the founder says so; send nothing.

## 4. Schedule

1. Call `mcp__user-input__get_available_triggers` on the mailbox account and pick the new-message trigger (never guess the slug). Create it with `mcp__user-input__setup_trigger` and the self-contained prompt from `AGENTS.md`. If none exists, create the sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `*/15 7-19 * * 1-5`.
2. Web form: `setup_trigger` on Typeform's new-response event if offered, or `mcp__user-input__create_webhook_endpoint` with signature verification for another tool.
3. Stale check: `0 12,16 * * 1-5`.
4. Verify with `mcp__user-input__list_triggers` and `mcp__user-input__list_scheduled_tasks`, and record the current mailbox history ID in `/workspace/state/inquiry-desk/history.json`.

## Configuration to save

Write the answers into `AGENTS.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json` with this structure:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "",
  "source_system_connected": false,
  "inquiry_sources": [],
  "outbound_thread_rule": "",
  "crm": "",
  "calendar": {"id": "", "call_minutes": 30, "working_hours": "", "buffer_minutes": 15, "min_notice_hours": 24, "booking_link": ""},
  "fit_rules": {"size": "", "problems": [], "geography": [], "exclusions": []},
  "published_rates": "",
  "approved_materials": [],
  "alert_destination": "",
  "alert_integration_id": "",
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": "new-mail trigger or */15 7-19 * * 1-5",
  "timezone": "",
  "voice_notes": "",
  "approval_required_for": ["every reply", "calendar invites"],
  "preauthorized_bookings": false,
  "business_rules": {"spicy": [], "stale_after_business_hours": 4},
  "do_not_touch": [],
  "first_run_goal": "Work today's inbound inquiries through a qualified call on the calendar. Draft invites. Do not send until I approve."
}
```

## First task prompt

After onboarding, suggest this first task:

> Work today's inbound inquiries through a qualified call on the calendar. Draft invites. Do not send until I approve.
