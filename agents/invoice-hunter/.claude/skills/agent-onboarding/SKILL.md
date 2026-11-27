---
name: agent-onboarding
description: 'Sets up Invoice Hunter: connects the books and mailbox, learns aging, cadence, voice and escalation rules, picks the alert channel, runs a supervised first chase, and schedules the collections cycle and reply trigger.'
first_prompt: 'Set up Invoice Hunter for my shop'
---

# Invoice Hunter onboarding

## 1. Welcome

In two or three sentences, say what you will set up: a twice-weekly collections cycle with a living aging log and reminder drafts in the founder's mailbox, a watch on customer replies for promises and payment claims, escalations to the founder channel, and a Monday recap. Nothing goes to a customer without approval.

Show the planned questions as a short list, then ask them one at a time. Skip anything already answered in `AGENTS.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected:
- Billing: QuickBooks (`quickbooks`), Xero (`xero`), Stripe (`stripe`), all connected accounts. Jobber, Housecall Pro or ServiceTitan have no registry connector: an API key via `request_secret`, the browser, or a sheet export.
- Mail: Gmail (`gmail`) or Outlook (`outlook`) connected account, so drafts land in the founder's mailbox.
- Aging log: Google Sheets (`googlesheets`) if they want a sheet; otherwise the state file.
- Alerts: call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. What is the shop name, and where do invoices live (QuickBooks, Xero, Jobber, a sheet)? Do you take card payments through Stripe?
2. Which mailbox should the drafts go to: Gmail or Outlook?
3. Aging buckets: keep current, 1-30, 31-60, 60+ (with 61-90 and 90+ tracked inside 60+)? How many grace days after the due date before the first reminder (default 3)?
4. Chase cycle: how often may one customer get a reminder (default once every 7 days)? Which days should the cycle run (default Tuesday and Thursday morning)?
5. When does a human take over: at 60+, after the third unanswered reminder, or another rule?
6. Paste one or two reminders you have sent that sound like you. Do you want a payment link in every reminder if your billing system has one?
7. Who gets reminders for commercial jobs: the AP contact on the invoice, or someone else? How do you handle financing or home-warranty companies?
8. Any customers we never chase automatically (family, big commercial accounts, anyone with an open callback)? Any accounts already on a payment plan?
9. Do your techs collect cash or checks in the field? Where do they record it, so I don't chase something already paid?
10. How many days do I wait after a "we sent it" reply before checking again (default 5 business days)?
11. Where should escalations, the cycle summary and the Monday recap go: in-app, the agent's own Slack app (which channel or DM), the agent's email inbox, Telegram or iMessage? Use `AskUserQuestion`.
12. Autonomy: confirm the default (track and draft on my own, every customer email waits for you). Should escalations post on their own (default yes)?
13. Your timezone.
14. Optional: a home-screen widget with total overdue and the 60+ count?

## 4. Connect

- `mcp__user-input__request_connected_account` for `quickbooks` or `xero`, `stripe` if used, `gmail` or `outlook`, and `googlesheets` if they want a sheet.
- `mcp__user-input__request_secret` for a field-service API key if they have one (for example `JOBBER_API_KEY`), or `mcp__user-input__request_login` for a browser session.
- Agent's own Slack app or inbox: follow `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or hand the form to the user with `mcp__user-input__request_integration_setup`. Resolve the exact channel with `mcp__chat__list_chat_channels`.
- `slack` as a connected account only if a channel must be read (for example field payments).

## 5. Supervised dry run

On real data, with no drafts saved yet:
1. Pull open invoices and show the bucketed aging log. Ask whether the numbers match what they expect.
2. Show which accounts you would skip and why.
3. Show two or three reminder drafts in chat, one per tone step if possible.
4. Show the worst-offenders summary.

Ask what to change and iterate once. Then, with their OK, save the drafts to the mailbox and write the first aging log and chase ledger.

## 6. Schedule and triggers

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the founder's timezone: the collections cycle (default `0 8 * * 2,4`) and the recap (default `30 7 * * 1`). Example prompt:

  > Invoice Hunter collections cycle. Read `AGENTS.md` `## Your context` and `.claude/skills/agent-onboarding/config.json` for the billing source, buckets, grace days, cycle length, voice and delivery channel. Follow the `collections-playbook` skill. Pull open invoices, update `/workspace/state/invoice-hunter/aging-log.json`, check `chase-ledger.json` and `promises.json`, apply every skip rule, and save one reminder draft per eligible account in the founder's mailbox. Never send. Post the cycle summary with `mcp__chat__send_chat_message` to the configured channel, and escalate accounts past the handoff rule. If nothing is overdue and nothing changed, send nothing.

- Replies: `mcp__user-input__get_available_triggers` on the mail account, then `mcp__user-input__setup_trigger` for new incoming messages with a self-contained prompt (match sender to open invoices, ignore everyone else, classify, update the log, draft any reply, never send). If no trigger exists, schedule a sweep every two hours on weekdays.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`. Build the widget now if they asked for it.

## 7. Save

Write the answers in plain language under `## Your context` in `AGENTS.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "quickbooks",
  "source_system_connected": false,
  "payments_source": "stripe",
  "field_service_tool": null,
  "mailbox": "gmail",
  "aging_log": { "location": "state_file", "sheet_id": null },
  "alert_destination": { "channel": "slack", "target": "", "integration_id": "" },
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": { "cycle_cron": "0 8 * * 2,4", "recap_cron": "30 7 * * 1", "cycle_days": 7 },
  "timezone": "",
  "voice_notes": "",
  "voice_samples": [],
  "approval_required_for": ["every_customer_email", "payment_plan", "pause_work", "write_off"],
  "business_rules": {
    "buckets": ["current", "1-30", "31-60", "60+"],
    "sub_buckets_60_plus": ["61-90", "90+"],
    "grace_days": 3,
    "escalate_at_days": 60,
    "max_unanswered_steps": 3,
    "payment_claim_wait_business_days": 5,
    "include_payment_link": true,
    "commercial_contact_rule": "ap_contact_on_invoice",
    "financing_company_rule": ""
  },
  "do_not_touch": [],
  "payment_plans": [],
  "triggers": {},
  "schedules": {},
  "widget": false,
  "first_run_goal": "Pull overdue invoices, draft the next chase on cadence, and flag anything that needs me. Do not send."
}
```

Finish with a summary: what runs when, where drafts and alerts land, and what always waits for the founder. Suggest the first task:

> Pull overdue invoices, draft the next chase on cadence, and flag anything that needs me. Do not send.
