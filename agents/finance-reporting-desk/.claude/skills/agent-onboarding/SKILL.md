---
name: agent-onboarding
description: 'First-run setup for Finance Reporting Desk: which routines to run, where the numbers live, close calendar and checklist, materiality, KPI definitions, delivery and approval rules.'
first_prompt: 'Set up Finance Reporting Desk for me'
---

# Onboarding: Finance Reporting Desk

## 1. Welcome

Say in two or three sentences: this agent drafts the weekly cash update, tracks month-end close, writes variance commentary and assembles the board pack, using only your real numbers. It never posts to your books, never moves money, and never sends anything without your OK. Show the planned questions:

1. Which of the four routines do you want?
2. Where do the numbers live (ledger, bank, cards, budget, KPIs)?
3. For the close: your checklist, close deadline, and owners?
4. For variances: materiality and budget vs. forecast?
5. For the board pack: period format, KPIs and their definitions?
6. Where do drafts and reports go, and what waits for approval?

Check `## Your context` in `CLAUDE.md` first and skip anything already answered.

## 2. Ask, one at a time

Use `AskUserQuestion` for discrete choices; plain chat for open answers.

1. **Role and company**: finance lead, controller, or founder acting as CFO; company name; fiscal year start; timezone; reporting currency.
2. **Routines** (`AskUserQuestion`, multi-select): weekly cash update / month-end close tracker / variance commentary / board pack.
3. **Ledger** (`AskUserQuestion`): QuickBooks / Xero / exports in a folder / other. Then **bank** (Mercury / bank feed in the ledger / CSV drop / browser-only bank) and **cards** (Ramp / Brex / none).
4. **Cash update** (if chosen): who receives it, the day and time of the check-in, the format they read (email, doc, Slack), book vs. bank balance, restricted cash, payroll schedule, runway window (default 3-month average).
5. **Close tracker** (if chosen): where the close checklist lives (ask them to share the sheet or upload it with `mcp__user-input__request_file`), close deadline (e.g. business day 5), owner per area, whether to read an AP inbox, chase tone, and who can be chased (internal only, or vendors with approval).
6. **Variance commentary** (if chosen): where budget and forecast live, materiality (amount and percent), whether leadership manages to budget or forecast, owner per department, where the "why" lives (Gmail, Slack channels, meeting notes).
7. **Board pack** (if chosen): monthly or quarterly, meeting date pattern, audience (board, investors, LPs), KPI list with definitions (copy them from the last pack if the user shares it), Drive folder for packs.
8. **Delivery** (`AskUserQuestion`): in-app / the agent's Slack bot DM / the agent's own email / Telegram or iMessage. Optional team channel for close status.
9. **Autonomy** confirm: drafts and docs on its own; any message to another person waits for approval; vendors always wait; never touches the ledger.

## 3. Connect

For each service, call `mcp__user-input__search_connection_options` and check what's already connected. Then:

- QuickBooks, Xero, Stripe, Google Sheets, Excel, Google Drive, Google Docs, Gmail, Outlook, Slack (to read threads): `mcp__user-input__request_connected_account` with the slug, e.g. "Allow access to QuickBooks to read the ledger for the close tracker and variance commentary?"
- Mercury, Ramp, Brex, Carta: `mcp__user-input__request_remote_mcp` with the URL from `search_connection_options`.
- A bank with no API: offer a weekly CSV drop (`request_file`) or a browser session (`mcp__browser__browser_open`, then `mcp__user-input__request_login`; 2FA via `request_browser_input`).
- Delivery: `mcp__chat__list_agent_integrations`; set up a missing one with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`.

## 4. Supervised dry run

Run each chosen routine once on real data, most useful first (usually the cash update or the close tracker for the current or last month). Show the output, the data issues found, and the sources used. Ask what to change (format, thresholds, wording). Apply once and save to config.

## 5. Schedule

Create one `mcp__user-input__schedule_task` per chosen routine (`scheduleType: "cron"`, user's timezone), using the expressions and self-contained prompt rules in `CLAUDE.md` > How this runs on Gamut. Fill in real config paths, destinations and integration IDs. Confirm with `mcp__user-input__list_scheduled_tasks`. Optionally, use `get_available_triggers` on Gmail to react to new invoices during the close window; if no suitable trigger exists, the daily sweep covers it.

## 6. Save

Write the answers to `CLAUDE.md` under `## Your context`, and this to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "role": "finance_lead | controller | founder_cfo",
  "company": "",
  "timezone": "",
  "currency": "USD",
  "fiscal_year_start_month": 1,
  "routines": ["cash_update", "close_tracker", "variance", "board_pack"],
  "sources": { "ledger": "quickbooks | xero | export", "bank": "mercury | ledger_feed | csv | browser", "cards": "ramp | brex | none", "stripe": true, "budget_sheet": "", "forecast_sheet": "", "kpi_sheet": "" },
  "cash_update": { "recipient": "", "format": "gmail_draft | google_doc | slack_draft", "cron": "0 7 * * 1", "balance_basis": "bank | book", "restricted_accounts": [], "payroll": "biweekly", "runway_window_months": 3 },
  "close": { "checklist_location": "", "status_doc_id": "", "deadline_business_day": 5, "window_start_business_days_before_month_end": 3, "owners": {}, "ap_inbox": "", "external_chase_allowed": false },
  "variance": { "threshold_amount": 10000, "threshold_pct": 0.1, "lead_with": "budget | forecast", "department_owners": {}, "why_sources": ["gmail", "slack"] },
  "board_pack": { "frequency": "monthly | quarterly", "periods": 4, "audience": "board", "kpis": [ { "name": "", "definition": "", "source": "" } ], "drive_folder_id": "" },
  "delivery": { "type": "in_app | slack | email | telegram | imessage", "integration_id": "", "target": "", "team_channel": "" },
  "approval_required_for": ["any message to another person", "vendor contact"],
  "schedules": {}
}
```

End with a short summary: which routine runs when, where each output lands, and which sources are missing or manual.
