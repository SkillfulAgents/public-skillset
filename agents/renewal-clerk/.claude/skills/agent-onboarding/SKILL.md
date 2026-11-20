---
name: agent-onboarding
description: 'Sets up Renewal Clerk: connects the contract folder, mailbox and CRM, builds the customer and vendor tracker, learns lead times and the big-ticket threshold, picks the alert channel, runs a supervised first pass, and schedules sweeps, alerts and the new-contract trigger.'
first_prompt: 'Set up Renewal Clerk for my firm'
---

# Renewal Clerk onboarding

## 1. Welcome

In two or three sentences, say what you will set up: a living tracker of customer and vendor contracts read from the contracts themselves, a watch on the inbox for new contracts and renewal notices, alerts ahead of every notice-period deadline (auto-renewing and big-ticket first), customer renewal drafts, vendor decision cards, and a Monday view. Nothing renews, cancels or gets sent without approval.

Show the planned questions as a short list, then ask them one at a time. Skip anything already answered in `CLAUDE.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected:
- Contracts: Google Drive (`googledrive`), Dropbox (`dropbox`), Box (`box`), OneDrive (`one_drive`).
- Mail: Gmail (`gmail`) or Outlook (`outlook`), for incoming contracts, renewal notices and drafts.
- Tracker: Google Sheets (`googlesheets`) or the state file.
- CRM: HubSpot (`hubspot`), Salesforce (`salesforce`), Attio (`attio`).
- Calendar: `googlecalendar`, if they want act-by holds.
- Alerts: `mcp__chat__list_agent_integrations` for the agent's own Slack app, email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. What is the firm name? Should I track customer contracts, vendor contracts, or both (default both)?
2. Where do contracts live: which Drive folders, the CRM, a sheet, or mostly in the inbox? Any e-signature tool whose completion emails I should watch for?
3. Where should the tracker live: a Google Sheet you can see, or my own state file?
4. Alert lead times before each notice deadline (default 60, 30, 14 and 7 days)? For contracts with no notice period, how long before the renewal date should I raise the decision (default 60 days)?
5. What counts as big-ticket for you (an annual value), so those go first?
6. Customer side: how long before the client's notice deadline should I draft the renewal (default 60 days)? Where does usage or retained hours live, if anywhere? Who owns each relationship?
7. Vendor side: which kinds of contracts matter most (leases, insurance, outsourced services, data, software)? Do you use a broker for insurance renewals? If SaaS Spend Auditor is installed, confirm I leave software subscriptions to it.
8. Paste a renewal note that sounds like you, and point me to the next-term order form template.
9. Should I put a calendar hold on each act-by date?
10. Where should alerts and the weekly view go: in-app, the agent's Slack app (which channel or DM), its email inbox, Telegram or iMessage? Use `AskUserQuestion`.
11. Autonomy: confirm the default (maintain the tracker and send internal alerts on my own; every client or vendor email is a draft; I never renew, cancel or give notice). May I update the renewal date property on the CRM record without asking?
12. Your timezone.

## 4. Connect

- `mcp__user-input__request_connected_account` for the contract store, `gmail` or `outlook`, `googlesheets` if chosen, the CRM, and `googlecalendar` if they want holds.
- `mcp__user-input__request_secret` for a usage source that needs an API key.
- Agent integration: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`. Resolve the exact channel before sending.

## 5. Supervised dry run

On real data:
1. Parse five to ten contracts with the `contract-terms` skill (mix of customer and vendor if both are tracked) and show the tracker rows with cited clauses and parse status. Ask whether the dates and auto-renew flags look right.
2. Search the last 90 days of mail for renewal notices and contract attachments and show what you would add.
3. Show the alert batch you would send today, in priority order, and any data holes.
4. If a customer renewal is inside the drafting window, show the draft in chat.

Iterate once. Then, with their OK, write the full tracker (all reachable contracts), save any drafts, and record which sources were parsed.

## 6. Schedule and triggers

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the firm's timezone: tracker sweep `0 7 * * 1,3,5`, alerts and drafting `30 7 * * 1-5`, weekly view `0 8 * * 1`. Example alert prompt:

  > Renewal Clerk notice-deadline alerts. Read `CLAUDE.md` `## Your context` and `.claude/skills/agent-onboarding/config.json` for the tracker location, sides, lead times, big-ticket threshold and delivery channel. Follow the `contract-terms` skill. For each contract, compare today with its notice deadline; collect any that hit a lead time not yet in `/workspace/state/renewal-clerk/alerts-sent.json`, plus auto-renewing data holes. Draft customer renewals that reached the drafting lead time into the founder's mailbox; never send. Send the batch, auto-renewing and big-ticket first, with `mcp__chat__send_chat_message` to the configured channel and record each alert. If nothing reaches a lead time and nothing changed, send nothing.

- New contracts and renewal notices: `mcp__user-input__get_available_triggers` on the mail account, then `mcp__user-input__setup_trigger` for new incoming messages with a self-contained prompt (ignore mail without a contract, order form or renewal notice; parse the attachment or linked file; update the tracker; alert only on a decision-worthy change). No trigger: a cron sweep every four hours. Optionally discover a Drive new-file trigger the same way.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 7. Save

Write the answers in plain language under `## Your context` in `CLAUDE.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "googledrive",
  "source_system_connected": false,
  "sides": ["customer", "vendor"],
  "contract_sources": { "folders": [], "crm": "hubspot", "sheet_id": null, "esign_senders": [] },
  "tracker": { "location": "googlesheets", "sheet_id": null },
  "mailbox": "gmail",
  "alert_destination": { "channel": "slack", "target": "", "integration_id": "" },
  "workflow_owner": "",
  "escalation_contact": "",
  "relationship_owners": {},
  "cadence": { "sweep_cron": "0 7 * * 1,3,5", "alert_cron": "30 7 * * 1-5", "weekly_cron": "0 8 * * 1" },
  "timezone": "",
  "voice_notes": "",
  "voice_samples": [],
  "order_form_template": "",
  "usage_source": null,
  "approval_required_for": ["every_external_email", "renewal", "cancellation", "notice", "discount", "term_change"],
  "business_rules": {
    "alert_lead_days_before_notice": [60, 30, 14, 7],
    "no_notice_decision_lead_days": 60,
    "unknown_notice_alert_days_before_renewal": 90,
    "customer_draft_lead_days_before_notice": 60,
    "big_ticket_annual_value": null,
    "calendar_holds": false,
    "crm_date_update_without_approval": false,
    "leave_saas_to_saas_spend_auditor": true
  },
  "do_not_touch": [],
  "triggers": {},
  "schedules": {},
  "first_run_goal": "Build the contract tracker, list every notice deadline in the next 120 days with auto-renewing and big-ticket ones first, and draft customer renewals that are due. Do not send."
}
```

Finish with a summary of what runs when, where the tracker, alerts and drafts land, and what always waits for the founder. Suggest the first task:

> Build the contract tracker, list every notice deadline in the next 120 days with auto-renewing and big-ticket ones first, and draft customer renewals that are due. Do not send.
