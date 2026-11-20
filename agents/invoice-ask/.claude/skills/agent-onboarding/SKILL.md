---
name: agent-onboarding
description: 'Sets up Invoice Ask: connects the invoice source and mailbox, learns cadence, voice and off-book payment habits, picks the alert channel, runs a supervised first ask cycle, and schedules the cycle and reply trigger.'
first_prompt: 'Set up Invoice Ask for me'
---

# Invoice Ask onboarding

## 1. Welcome

In two or three sentences, say what you will set up: a twice-weekly ask cycle that keeps a simple aging log and drafts asks in the owner's mailbox, a watch on customer replies, escalations when a customer needs a call, and a Monday recap. Customer invoices only, never vendor bills. Nothing goes to a customer without approval.

Show the planned questions as a short list, then ask them one at a time. Skip anything already answered in `CLAUDE.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected:
- Invoices: QuickBooks (`quickbooks`), Xero (`xero`), Stripe (`stripe`), or a sheet (`googlesheets`, `excel`), all connected accounts. Square, Wave or FreshBooks: API key via `request_secret`, browser sign-in, or an export.
- Mail: Gmail (`gmail`) or Outlook (`outlook`) connected account.
- Alerts: `mcp__chat__list_agent_integrations` for the agent's own Slack app, email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. What is the business name, and where do customer invoices live?
2. Gmail or Outlook for the drafts?
3. How often may one customer get an ask (default once every 7 days), and which days should the cycle run (default Tuesday and Friday morning)? Grace days after the due date before the first ask (default 3)?
4. When do you take over: after the third unanswered ask, at 60+ days, or something else?
5. Paste an ask that sounds like you.
6. Do customers ever pay you by Venmo, Zelle, cash or a check at the counter? How do I find out, so I don't ask someone who already paid?
7. Any customers we never ask automatically? Anyone on a payment plan?
8. How long do I wait after "I sent it" before checking again (default 5 business days)?
9. Where should the ask queue, escalations and recap go: in-app, the agent's Slack app, the agent's email inbox, Telegram or iMessage? Use `AskUserQuestion`.
10. Autonomy: confirm the default (log and draft on my own; every ask waits for you).
11. Your timezone.

## 4. Connect

- `mcp__user-input__request_connected_account` for the invoice source and `gmail` or `outlook`.
- `mcp__user-input__request_connected_account` for `square` or `freshbooks`; `mcp__user-input__request_login` plus the browser for sources without a connector (such as Wave), or ask for an export.
- Agent integration: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`. Resolve the exact channel or chat before sending anything.

## 5. Supervised dry run

On real data, with no drafts saved:
1. Show the bucketed aging log and confirm the totals look right.
2. Show who you would skip and why.
3. Show two asks in chat, ideally one light and one more direct.
4. Show the ask queue summary.

Iterate once on what they change. With their OK, save the drafts and write the first log and ledger.

## 6. Schedule and triggers

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the owner's timezone: the ask cycle (default `0 9 * * 2,5`) and the recap (default `0 8 * * 1`). Example prompt:

  > Invoice Ask cycle. Read `CLAUDE.md` `## Your context` and `.claude/skills/agent-onboarding/config.json`. Follow the `collections-playbook` skill. Pull open customer invoices only (never vendor bills), update `/workspace/state/invoice-ask/aging-log.json`, check `chase-ledger.json` and `promises.json`, apply every skip rule, and save one ask draft per eligible customer in the owner's mailbox. Never send. Send the ask queue with `mcp__chat__send_chat_message` to the configured channel. If nothing is overdue and nothing changed, send nothing.

- Replies: `mcp__user-input__get_available_triggers` on the mail account, then `mcp__user-input__setup_trigger` for new messages with a self-contained prompt (match to open invoices, ignore other senders, classify, log, draft any reply, never send). No trigger available: a cron sweep every three hours on weekdays.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 7. Save

Write the answers in plain language under `## Your context` in `CLAUDE.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "quickbooks",
  "source_system_connected": false,
  "mailbox": "gmail",
  "aging_log": { "location": "state_file", "sheet_id": null },
  "alert_destination": { "channel": "in_app", "target": "", "integration_id": "" },
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": { "cycle_cron": "0 9 * * 2,5", "recap_cron": "0 8 * * 1", "cycle_days": 7 },
  "timezone": "",
  "voice_notes": "",
  "voice_samples": [],
  "approval_required_for": ["every_customer_email", "payment_plan", "write_off"],
  "business_rules": {
    "buckets": ["current", "1-30", "31-60", "60+"],
    "grace_days": 3,
    "escalate_after_unanswered": 3,
    "escalate_at_days": 60,
    "payment_claim_wait_business_days": 5,
    "off_book_payment_methods": [],
    "off_book_payment_check": ""
  },
  "do_not_touch": [],
  "payment_plans": [],
  "triggers": {},
  "schedules": {},
  "first_run_goal": "List customers who owe us, draft the next asks, and keep vendor bills out of this queue. Do not send."
}
```

Finish with a summary of what runs when, where drafts and alerts land, and what always waits for the owner. Suggest the first task:

> List customers who owe us, draft the next asks, and keep vendor bills out of this queue. Do not send.
