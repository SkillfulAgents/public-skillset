---
category: Ops
icon: badge-dollar-sign
tags:
  - Agency Billing
  - Unbilled Time
  - Retainers
  - Accounts Receivable
  - QuickBooks
works_with:
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Billing Chaser

> Get unbilled hours out the door, overdue invoices chased, and the retainer renewal drafted before it quietly expires.

## What it does

Billing Chaser owns agency money in for founder-led marketing, creative and web shops. Every Friday it rebuilds your week's billable time by client from your calendar, sent email and the documents you edited, shows the meeting, thread or file behind each block, labels every number as an estimate, and flags work that looks billable but is not logged in Harvest, Toggl or your time sheet. The recap is read-only; it never creates time entries or invoices on its own.

Once hours are confirmed it drafts the invoice in QuickBooks or Xero. Twice a week it buckets open invoices as current, 1-30, 31-60 and 60+ days past due, keeps a living aging log, and drafts one chase per client per cycle, firmer as it ages, naming the invoice number, amount and due date. Paid accounts and payment plans are skipped, and an invoice counts as paid only once the money has cleared.

It watches hours or dollars left on every retainer and warns at the remaining percent you set (default 20%). When a retainer end date or the client's notice deadline lands inside the renewal window, it drafts the renewal inside this same job. Invoices, chases and renewals all stay in draft until you approve the exact text.

Unlike Invoice Hunter (trades jobs), Invoice Ask (simple chasing) and Ledger Hawk (professional firms), it is built around agency time and retainers.

## What you'll need

- **QuickBooks or Xero** — one is required for open invoices, aging and invoice drafts.
- **Google Calendar and Google Drive** — required for the billable hours recap. Outlook and OneDrive work too.
- **Gmail or Outlook** — required. Sent mail feeds the recap and drafts land in your mailbox.
- **Slack** — the agent posts warnings and escalations from its own Slack app, set up during onboarding. Your own Slack account is only needed if it should read a billing channel.
- **Harvest, Toggl or a time sheet** — recommended, to compare against logged time. Harvest and Toggl connect with an API key.
- **Stripe or HubSpot** — optional, for card payments or retainer records.
- **API keys:** only for Harvest or Toggl, if you use them.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your books, time source, calendar, docs and mailbox, builds a client map with you, asks for your rounding, low-retainer percent, renewal window, chase cycle and voice, runs a supervised hours recap and chase, and schedules every routine.
3. Ask for the first run: pull unbilled time, overdue invoices and retainers running low, and draft any renewals due, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Rebuild this week's billable hours by client and show me what's unlogged
- Which retainers are under 20% left, and draft the renewals for any ending soon
- Draft the next chase for every overdue invoice and list the worst offenders

## What's inside

- `CLAUDE.md` — the routines (hours recap, unbilled time to invoice, collections, retainer running low, renewal, replies and recap), the Gamut mechanics, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run setup: connections, client map, questions, supervised dry run, schedules and triggers, and `config.json`.
- `.claude/skills/time-reconstruction/` — how to rebuild billable time from calendar, email and docs with evidence per block and estimate labels.
- `.claude/skills/collections-playbook/` — aging buckets, the aging log format, the tone ladder, the cleared-payment test, skip rules and the one-chase-per-cycle ledger.

## Notes

- Built for 2-200 person founder-led agencies with time sitting unbilled and retainers that expire quietly.
- Recap hours are estimates for your review and are never invoiced as-is. The agent never writes off hours, discounts a retainer, or sends legal collections language.
