---
name: agent-onboarding
description: 'Sets up Ledger Hawk: connects the books, CRM and mailbox, learns terms, PO and portal clients, aging, cadence and voice, picks the alert channel, runs a supervised first pass, and schedules billing, collections and the reply trigger.'
first_prompt: 'Set up Ledger Hawk for my firm'
---

# Ledger Hawk onboarding

## 1. Welcome

In two or three sentences, say what you will set up: a weekly ready-to-bill pass that drafts invoices for completed work, a twice-weekly collections cycle with a living aging log and chase drafts, a watch on client replies and bounces, escalations to the founder, and a Monday recap. No invoice or client email goes out without approval.

Show the planned questions as a short list, then ask them one at a time. Skip anything already answered in `CLAUDE.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected:
- Books: QuickBooks (`quickbooks`) or Xero (`xero`); Stripe (`stripe`) if clients pay there. All connected accounts.
- CRM: HubSpot (`hubspot`), Salesforce (`salesforce`) or Attio (`attio`), connected accounts.
- Time: a sheet (`googlesheets`, `excel`) or Harvest/Toggl by API key.
- Mail: Gmail (`gmail`) or Outlook (`outlook`).
- Alerts: `mcp__chat__list_agent_integrations` for the agent's own Slack app, email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. What is the firm name, and where do invoices, engagements and time live?
2. What counts as "ready to bill" for you: closed deal, completed milestone, approved timesheet, retainer period start, placement start?
3. Standard payment terms, and which clients have different ones?
4. Which clients need a PO number on every invoice, and which pay only through an AP portal?
5. Do you send invoices from QuickBooks or Xero, or as an email with a PDF? Paste one invoice cover note and one overdue note that sound like you.
6. Aging: keep current, 1-30, 31-60, 60+? Grace days before the first chase (default 3)? How often may one client be chased (default every 7 days)?
7. Who should chases go to: the billing or AP contact only, or copy the relationship owner? At what point should the relationship owner call instead?
8. When does the founder take over (default 60+ days or the third unanswered chase)?
9. Clients we never auto-draft for or never chase? Any payment plans in place? (Law firms: confirm I never touch trust or retainer funds.)
10. Wait after "payment is scheduled" before checking again (default 5 business days)?
11. Where should the ready-to-bill list, summaries and escalations go: in-app, the agent's Slack app (which channel), its email inbox, Telegram or iMessage? Use `AskUserQuestion`.
12. Autonomy: confirm the default (find, log and draft on my own; every invoice and client email waits for you). May I log a "chase drafted" note on the CRM record without asking?
13. Your timezone, and the day your payment runs or month-end close happen.
14. Optional: a receivables dashboard?

## 4. Connect

- `mcp__user-input__request_connected_account` for `quickbooks` or `xero`, `stripe` if used, `hubspot` / `salesforce` / `attio`, `gmail` or `outlook`, and `googlesheets` or `excel` if time lives in a sheet.
- Harvest, if used: `mcp__user-input__request_connected_account` with toolkit `harvest`. Toggl, if used: `mcp__user-input__request_secret` for `TOGGL_API_TOKEN`.
- Agent integration: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`. Resolve the exact channel with `mcp__chat__list_chat_channels`.

## 5. Supervised dry run

On real data, with nothing saved:
1. Show the ready-to-bill list and one invoice draft in chat, with its source records.
2. Show the bucketed aging log and confirm totals.
3. Show who you would skip and why, then two chase drafts at different tone steps.
4. Show the cycle summary with worst offenders.

Iterate once. With their OK, save the invoice drafts in the books, the chase drafts in the mailbox, and write the first state files.

## 6. Schedule and triggers

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the firm's timezone: ready to bill (`0 15 * * 5` and `0 9 1 * *`), collections (`30 8 * * 2,4`), recap (`0 8 * * 1`). Example collections prompt:

  > Ledger Hawk collections cycle. Read `CLAUDE.md` `## Your context` and `.claude/skills/agent-onboarding/config.json`. Follow the `collections-playbook` skill. Pull open invoices and payments, update `/workspace/state/ledger-hawk/aging-log.json`, check `chase-ledger.json` and `promises.json`, apply every skip rule, and save one chase draft per eligible client in the founder's mailbox. Never send. Also list anything in `unbilled.json` still without a draft. Send the summary with `mcp__chat__send_chat_message` to the configured channel and escalate per the handoff rule. If nothing is overdue, nothing is unbilled and nothing changed, send nothing.

- Replies and bounces: `mcp__user-input__get_available_triggers` on the mail account, then `mcp__user-input__setup_trigger` for new incoming messages with a self-contained prompt. No trigger: a cron sweep every two hours on weekdays. Optionally discover a HubSpot deal trigger the same way.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`. Build the dashboard if requested.

## 7. Save

Write the answers in plain language under `## Your context` in `CLAUDE.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "quickbooks",
  "source_system_connected": false,
  "crm": "hubspot",
  "time_source": null,
  "payments_source": null,
  "mailbox": "gmail",
  "aging_log": { "location": "state_file", "sheet_id": null },
  "alert_destination": { "channel": "slack", "target": "", "integration_id": "" },
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": { "bill_crons": ["0 15 * * 5", "0 9 1 * *"], "cycle_cron": "30 8 * * 2,4", "recap_cron": "0 8 * * 1", "cycle_days": 7 },
  "timezone": "",
  "voice_notes": "",
  "voice_samples": { "invoice_cover": "", "overdue": "" },
  "approval_required_for": ["every_invoice", "every_client_email", "payment_plan", "write_off", "credit"],
  "business_rules": {
    "ready_to_bill_signals": [],
    "default_terms": "Net 30",
    "client_terms": {},
    "po_required_clients": [],
    "portal_clients": [],
    "buckets": ["current", "1-30", "31-60", "60+"],
    "grace_days": 3,
    "escalate_at_days": 60,
    "max_unanswered_steps": 3,
    "copy_relationship_owner": false,
    "payment_claim_wait_business_days": 5,
    "crm_note_without_approval": false
  },
  "do_not_touch": [],
  "payment_plans": [],
  "triggers": {},
  "schedules": {},
  "dashboard": false,
  "first_run_goal": "Draft invoices for completed unbilled work and the next overdue chases. Do not send."
}
```

Finish with a summary of what runs when, where drafts and alerts land, and what always waits for the founder. Suggest the first task:

> Draft invoices for completed unbilled work and the next overdue chases. Do not send.
