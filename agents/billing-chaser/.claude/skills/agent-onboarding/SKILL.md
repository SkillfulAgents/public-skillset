---
name: agent-onboarding
description: 'Sets up Billing Chaser: connects books, time source, calendar, docs and mailbox, learns the client map, retainers, aging and voice, picks the alert channel, runs a supervised hours recap and chase, and schedules every routine.'
first_prompt: 'Set up Billing Chaser for my agency'
---

# Billing Chaser onboarding

## 1. Welcome

In two or three sentences, say what you will set up: a Friday billable-hours recap rebuilt from calendar, email and docs (estimates, read-only), invoice drafts for confirmed time, a twice-weekly collections cycle with an aging log and chase drafts, low-retainer warnings, renewal drafts, and a Monday recap. Nothing goes to a client without approval.

Show the planned questions as a short list, then ask them one at a time. Skip anything already answered in `AGENTS.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected:
- Books: QuickBooks (`quickbooks`) or Xero (`xero`); Stripe (`stripe`) if used.
- Time: Harvest or Toggl (API key via `request_secret`), or a sheet (`googlesheets`, `excel`).
- Recap evidence: Google Calendar (`googlecalendar`), Google Drive and Docs (`googledrive`, `googledocs`), or Outlook and OneDrive (`outlook`, `one_drive`).
- Mail: Gmail (`gmail`) or Outlook (`outlook`).
- Retainer records: HubSpot (`hubspot`) or a sheet.
- Alerts: `mcp__chat__list_agent_integrations` for the agent's own Slack app, email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. What is the agency name, and where do time, invoices and retainers live?
2. Client map: which email domains, calendar keywords and Drive folders belong to which client? (Offer to propose one from the last month of calendar and folders, then confirm.)
3. Whose time should the recap cover: only yours, or named team members who have connected their own calendars?
4. Billing increment (0.25 h default, or 0.1 h) and how many unlogged hours are worth flagging (default 0.5 h or 25%)? Do internal meetings ever count as billable?
5. Which day do you invoice (default the 1st), and are retainers billed in advance or in arrears?
6. Low-retainer warning at what remaining percent (default 20%)? How many days before a retainer ends should I draft the renewal (default 30)? Do any retainers auto-renew with a client notice period?
7. Aging: keep current, 1-30, 31-60, 60+? Grace days (default 3)? How often may one client be chased (default every 7 days)? When does the founder take over (default 60+ or third unanswered chase)?
8. Paste one billing note, one overdue note and one renewal note that sound like you.
9. Clients we never auto-draft for, payment plans in place, anyone in a dispute right now?
10. Where should the hours recap, summaries and warnings go: in-app, the agent's Slack app, its email inbox, Telegram or iMessage? Should the recap also be written to a sheet? Use `AskUserQuestion`.
11. Autonomy: confirm the default (reconstruct, track and draft on my own; no invoice or client email without you).
12. Your timezone and the end of your work week.
13. Optional: a retainer burn dashboard?

## 4. Connect

- `mcp__user-input__request_connected_account` for `quickbooks` or `xero`, `stripe` if used, `googlecalendar`, `googledrive`, `googledocs`, `gmail` (or the Microsoft equivalents), `hubspot` or `googlesheets` if retainers live there.
- Harvest: `mcp__user-input__request_connected_account` with toolkit `harvest`. Toggl Track has no connector: `mcp__user-input__request_secret` for `TOGGL_API_TOKEN`.
- Agent integration: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`. Resolve the exact channel before sending.

## 5. Supervised dry run

On real data, with nothing saved:
1. Rebuild last week's hours for two clients using the `time-reconstruction` skill and show the evidence tables. Ask whether the client map and estimates look right.
2. Show the bucketed aging log, who you would skip and why, and two chase drafts at different tone steps.
3. Show retainer burn for each retainer and any low-retainer or renewal draft due.

Iterate once. With their OK, save drafts and write the first state files.

## 6. Schedule and triggers

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the agency's timezone: recap `0 15 * * 5`, invoicing `0 9 1 * *`, collections plus retainer check `0 9 * * 2,4`, renewal check `0 8 * * 1-5`, weekly recap `0 8 * * 1`. Example recap prompt:

  > Billing Chaser, billable hours recap. Read `AGENTS.md` `## Your context` and `.claude/skills/agent-onboarding/config.json` for the client map, increment and delivery channel. Follow the `time-reconstruction` skill for Monday to Friday of this week. Read-only: do not create time entries, invoices or emails. Compare with the time source, flag possibly unlogged time, label every number "est.", save `/workspace/state/billing-chaser/hours-recap/<week>.json`, and send the per-client recap with `mcp__chat__send_chat_message` to the configured channel. If there was no client activity, send one line saying so.

  Write similar self-contained prompts for the others; the collections one follows the `collections-playbook` skill and ends with "if nothing is overdue and nothing changed, send nothing".
- Replies: `mcp__user-input__get_available_triggers` on the mail account, then `mcp__user-input__setup_trigger` for new incoming messages. No trigger: a cron sweep every two hours on weekdays.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`. Build the dashboard if requested.

## 7. Save

Write the answers in plain language under `## Your context` in `AGENTS.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "quickbooks",
  "source_system_connected": false,
  "time_source": "harvest",
  "evidence_sources": { "calendar": "googlecalendar", "mail": "gmail", "docs": "googledrive" },
  "mailbox": "gmail",
  "alert_destination": { "channel": "slack", "target": "", "integration_id": "", "recap_sheet_id": null },
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": {
    "recap_cron": "0 15 * * 5",
    "invoice_cron": "0 9 1 * *",
    "cycle_cron": "0 9 * * 2,4",
    "renewal_cron": "0 8 * * 1-5",
    "weekly_recap_cron": "0 8 * * 1",
    "cycle_days": 7
  },
  "timezone": "",
  "voice_notes": "",
  "voice_samples": { "billing": "", "overdue": "", "renewal": "" },
  "approval_required_for": ["every_invoice", "every_client_email", "write_off_hours", "retainer_discount"],
  "business_rules": {
    "client_map": [ { "client": "", "domains": [], "keywords": [], "folders": [] } ],
    "recap_people": [],
    "rounding_increment_hours": 0.25,
    "unlogged_flag": { "hours": 0.5, "percent": 25 },
    "internal_meetings_billable": false,
    "retainer_billing": "in_advance",
    "low_retainer_percent": 20,
    "renewal_window_days": 30,
    "buckets": ["current", "1-30", "31-60", "60+"],
    "grace_days": 3,
    "escalate_at_days": 60,
    "max_unanswered_steps": 3,
    "payment_claim_wait_business_days": 5
  },
  "retainers": [ { "client": "", "budget": null, "unit": "hours", "end_date": "", "auto_renews": null, "notice_days": null } ],
  "do_not_touch": [],
  "payment_plans": [],
  "triggers": {},
  "schedules": {},
  "dashboard": false,
  "first_run_goal": "Pull unbilled time, overdue invoices, and retainers running low, and draft any renewals due. Do not send."
}
```

Finish with a summary of what runs when, where drafts and alerts land, and what always waits for the founder. Suggest the first task:

> Pull unbilled time, overdue invoices, and retainers running low, and draft any renewals due. Do not send.
