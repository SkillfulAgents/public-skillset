---
category: Ops
icon: badge-dollar-sign
tags:
  - Accounts Receivable
  - Invoice Reminders
  - QuickBooks
  - Cash Flow
  - Small Business
works_with:
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: xero
  - type: api_account
    slug: stripe
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlesheets
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Invoice Ask

> Ask the customers who owe you, on cadence and in your voice, until they pay or you step in.

## What it does

Invoice Ask owns customers who owe you for micro-owners and founder-led SMBs. Twice a week it pulls open customer invoices from QuickBooks, Xero, Stripe or your invoice sheet, buckets them as current, 1-30, 31-60 and 60+ days past due, and keeps a simple aging log of who owes what and when you last asked.

For each overdue customer it drafts one short ask per cycle in your voice, light at first and more direct as it ages, naming the invoice number, amount and due date. It skips anyone paid, on a payment plan or inside a promise date, and it only counts an invoice as paid once the money has cleared. "I sent it" is logged as a claim, and Venmo, Zelle or cash payments you took off the books are checked with you before anyone gets asked.

Replies are read as they arrive, promises are watched, and after the last unanswered ask you get a message from the agent with a suggested next step and a worst-offenders summary. Vendor bills stay out of this queue entirely; that is Vendor Nudge's job.

It is the simplest of the receivables agents: Invoice Hunter is tuned for trades jobs, Ledger Hawk for professional firms that also need invoices drafted, and Billing Chaser for agencies with unbilled time and retainers.

## What you'll need

- **QuickBooks, Xero, Stripe or a Google Sheet** — one is required for open customer invoices.
- **Gmail or Outlook** — required. Asks are drafts in your own mailbox and replies are watched there.
- **Slack, email, Telegram or iMessage** — the agent messages you from its own account, set up during onboarding. In-app works too.
- **Square, Wave or FreshBooks** — optional. No registry connector; an API key, a browser sign-in, or an export.
- **API keys:** none required.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your invoice source and mailbox, asks for your cadence, voice, off-book payment habits and do-not-ask customers, runs a supervised first ask cycle, and schedules the cycle and the reply watch.
3. Ask for the first run: list customers who owe you and draft the next asks, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List who owes us and draft the next ask for each open invoice
- Draft a second ask for the Bell Plumbing invoice that is 20 days late
- Who has said they paid but nothing has cleared yet?

## What's inside

- `CLAUDE.md` — the routines (ask cycle, promises and replies, escalation and recap), the Gamut mechanics, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run setup: connections, questions, supervised dry run, schedules and triggers, and `config.json`.
- `.claude/skills/collections-playbook/` — aging buckets, the aging log format, the tone ladder, the cleared-payment test, skip rules and the one-ask-per-cycle ledger.

## Notes

- Built for 1-15 person micro-owners who know who owes them and still have not asked.
- Asks stay in draft until you send them. This agent is the opposite of Vendor Nudge and never chases vendors or pays bills.
