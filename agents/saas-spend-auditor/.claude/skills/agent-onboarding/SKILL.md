---
name: agent-onboarding
description: 'First-run setup for SaaS Spend Auditor: spend source, usage evidence, thresholds, renewal notice lead time, delivery channel and schedules.'
first_prompt: 'Set up SaaS Spend Auditor for me'
---

# Onboarding: SaaS Spend Auditor

## 1. Welcome

Say in two or three sentences: this agent reviews company software spend monthly against real usage, ranks what could be saved, and warns before renewal notice deadlines. It never cancels, downgrades or contacts vendors. Show the planned questions:

1. Where does software get paid for?
2. Where can usage be seen?
3. What counts as worth flagging?
4. How early should notice-deadline alerts come?
5. Where should the digest go?
6. Anything already known to keep?

Check `## Your context` in `CLAUDE.md` first and skip anything already answered.

## 2. Ask, one at a time

Use `AskUserQuestion` for discrete choices; plain chat for open answers.

1. **Spend source** (`AskUserQuestion`): Ramp / Brex / QuickBooks / Xero / card export file. Ask whether software is also paid on personal cards and expensed, or through other entities.
2. **Usage evidence**: which tools the user (or an admin) can connect as an admin (Slack, GitHub, Zoom, HubSpot, Salesforce, Notion, Google Workspace). For the rest, offer monthly admin exports (seat lists with last-active dates) via `mcp__user-input__request_file`. Ask whether email, Slack and calendar can be read for soft signals.
3. **Thresholds**: inactivity days (default 30), seat gap worth flagging (default 20% or 3 seats), minimum annual cost to report (default $500), seat headroom to keep for hiring (default 10% or 2 seats).
4. **Contracts and notice periods**: where order forms live (Drive folder), and the notice-deadline alert lead time (default 21 days).
5. **Keep-list**: tools that must not be flagged (e.g. the customer-required video tool) and the owner of each major tool.
6. **Delivery** (`AskUserQuestion`): in-app / the agent's own email inbox / the agent's Slack bot DM / Telegram or iMessage. Optional inventory Google Sheet. Optional Google Calendar reminders for notice deadlines.
7. **Autonomy** confirm: report only; owner check-ins drafted and held; never cancel or contact vendors.

## 3. Connect

For each service, call `mcp__user-input__search_connection_options` and check what's already connected. Then:

- Ramp, Brex: `mcp__user-input__request_remote_mcp` with the URL from `search_connection_options`, e.g. "Allow access to Ramp to find recurring software charges?"
- QuickBooks, Xero, Gmail, Slack, Google Calendar, Google Sheets, Google Drive, and admin-level tools: `mcp__user-input__request_connected_account` with the slug.
- Delivery: `mcp__chat__list_agent_integrations`; set up a missing one with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`.

## 4. Supervised dry run

Run the monthly review on real data. Show the vendor rollup first and ask the user to correct vendor names, owners and keep-list items. Then show the ranked digest and the renewals list with notice deadlines and their sources. Iterate once and save corrections to the inventory and config.

## 5. Schedule

Create two `mcp__user-input__schedule_task` jobs (`scheduleType: "cron"`, user's timezone): monthly review `0 8 1 * *`, notice watch `0 8 * * 1`, each with a self-contained prompt as in `CLAUDE.md` > How this runs on Gamut. Confirm with `mcp__user-input__list_scheduled_tasks`.

## 6. Save

Write the answers to `CLAUDE.md` under `## Your context`, and this to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company": "",
  "timezone": "",
  "spend_sources": ["ramp | brex | quickbooks | xero | export"],
  "usage_sources": { "admin_connected": ["slack", "github"], "admin_exports": ["zoom"], "soft_signals": ["gmail", "slack", "googlecalendar"] },
  "thresholds": { "inactive_days": 30, "seat_gap_pct": 0.2, "seat_gap_min": 3, "min_annual_cost": 500, "seat_headroom_pct": 0.1, "seat_headroom_min": 2 },
  "renewals": { "contracts_folder_id": "", "notice_alert_lead_days": 21, "calendar_reminders": false },
  "keep_list": [],
  "owners": {},
  "delivery": { "type": "in_app | email | slack | telegram | imessage", "integration_id": "", "target": "", "inventory_sheet_id": "", "quiet_month": "short_note | nothing" },
  "schedules": { "monthly_review": "0 8 1 * *", "notice_watch": "0 8 * * 1" }
}
```

End with a short summary: when each job runs, where the digest arrives, which usage sources are connected vs. export-only, and the next notice deadline found.
