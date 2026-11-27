---
category: Ops
icon: calculator
avatar:
  color: tonal-brown
  shape: circle
tags:
  - Invoicing
  - Overdue Chase
  - Accounts Receivable
  - QuickBooks
  - Professional Services
works_with:
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: xero
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Ledger Hawk

> Completed work gets invoiced and overdue invoices get chased, in your voice, until they are paid or you step in.

## What it does

Ledger Hawk owns invoices out and overdue chased for founder-led consulting, accounting, insurance, staffing and law firms. Each week it finds completed work, approved time, retainer periods and placements with no invoice yet, and drafts the invoice in QuickBooks or Xero with the right terms, PO number and billing contact. Clients who only pay through an AP portal are flagged on the draft.

Twice a week it buckets open invoices as current, 1-30, 31-60 and 60+ days past due, keeps a living aging log, and drafts one chase per client per cycle, firmer as it ages, naming the invoice number, amount and due date. Paid accounts and payment plans are skipped, and an invoice counts as paid only once the money has cleared. "Payment is scheduled" is logged as a claim, not a payment.

Client replies and bounces are read as they arrive. Accounts past your handoff age reach you from the agent's own Slack app with the file, a recommended next step, and a worst-offenders summary. Invoices and chases stay in draft until you approve them.

Unlike Invoice Hunter (trades jobs) and Invoice Ask (simple chasing, no vertical), it also gets completed work billed; unlike Billing Chaser (agencies), it does not reconstruct time or manage retainer burn.

## What you'll need

- **QuickBooks or Xero** — one is required for unbilled work, open invoices, payments and invoice drafts.
- **HubSpot** — recommended for completed deals and billing contacts. Salesforce or Attio work as alternatives.
- **Gmail or Outlook** — required. Invoice covers and chases land as drafts in your mailbox.
- **Slack** — the agent posts escalations from its own Slack app, set up during onboarding. Your own Slack account is only needed if it should read a billing channel.
- **Stripe** — optional, if clients pay by card or ACH there.
- **Harvest, Toggl or a timesheet** — optional, for hourly billing. Harvest and Toggl connect with an API key.
- **API keys:** only for Harvest or Toggl, if you use them.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your books, CRM and mailbox, asks for your terms, PO and portal clients, aging, chase cycle, voice and handoff rule, runs a supervised first pass, and schedules billing, collections and the reply watch.
3. Ask for the first run: draft invoices for completed unbilled work and the next overdue chases, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft invoices for completed unbilled work and the next overdue chases
- Show me everything over 45 days and draft a firmer chase for each
- Which clients said payment is scheduled but nothing has cleared?

## What's inside

- `AGENTS.md` — the routines (ready to bill, collections cycle, replies and promises, escalation and recap), the Gamut mechanics, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run setup: connections, questions, supervised dry run, schedules and triggers, and `config.json`.
- `.claude/skills/collections-playbook/` — aging buckets, the aging log format, the tone ladder, the cleared-payment test, skip rules and the one-chase-per-cycle ledger.

## Notes

- Built for 2-200 person founder-led professional firms with completed work unbilled and overdue sitting.
- Invoices and chases stay in draft until the founder sends. The agent never touches client trust funds, never logs into client AP portals, and never writes legal or collections language.
