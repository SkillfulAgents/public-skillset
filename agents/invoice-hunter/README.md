---
category: Ops
icon: badge-dollar-sign
avatar:
  color: tonal-cobalt
  shape: circle
tags:
  - Overdue Invoices
  - Accounts Receivable
  - Home Services
  - QuickBooks
  - Promise to Pay
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
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Invoice Hunter

> Chase every overdue invoice through reminder, promise-to-pay, and human handoff instead of watching an aging report grow.

## What it does

Invoice Hunter owns overdue job invoices for founder-led home services shops. Twice a week it pulls open invoices from QuickBooks or Xero, buckets them as current, 1-30, 31-60 and 60+ days past due, and keeps a living aging log of who owes what, how overdue, and when you last reached out.

For each overdue account it drafts one reminder per cycle in your shop voice, firmer as the invoice ages, naming the invoice number, job, amount and due date. It skips anyone paid, on a payment plan, inside a promise date, or with an open callback, and it only counts an invoice as paid once the money has cleared. "Check's in the mail" is logged as a claim, not a payment.

Customer replies are read as they arrive: promises are logged and watched, disputes go to you. Accounts past your handoff age reach your founder channel from the agent's own Slack app with the file and a recommended next step, plus a worst-offenders summary each cycle. Every reminder stays a draft in your mailbox until you approve it.

It differs from Invoice Ask (micro-owners, no vertical), Ledger Hawk (professional firms, also invoices completed work) and Billing Chaser (agencies, also unbilled time and retainers) by focusing on trades jobs: homeowners, property managers, GCs and callbacks.

## What you'll need

- **QuickBooks or Xero** — one is required for open invoices and payment status.
- **Stripe** — optional, for card payments and hosted payment links.
- **Gmail or Outlook** — required. Reminder drafts land in your own mailbox and customer replies are watched there.
- **Slack** — the agent posts escalations from its own Slack app, set up during onboarding. Your own Slack account is only needed if it should read a payments channel.
- **Jobber, Housecall Pro or ServiceTitan** — optional, for job context. No registry connector; an API key, a browser sign-in, or a sheet export.
- **Google Sheets** — optional, if you want the aging log as a sheet.
- **API keys:** none required.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your books and mailbox, asks for your aging buckets, grace days, chase cycle, voice, handoff rule and do-not-chase customers, runs a supervised first chase on real data, and schedules the cycle and the reply watch.
3. Ask for the first run: pull overdue invoices, draft the next chase, and flag anything that needs you, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Pull overdue invoices and draft the next reminder for each one
- Log that the Nguyen job promised to pay Friday and pause their reminders
- Show me the worst offenders over 60 days and what you recommend for each

## What's inside

- `AGENTS.md` — the routines (collections cycle, promises and replies, escalation and recap), the Gamut mechanics, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run setup: connections, questions, supervised dry run, schedules and triggers, and `config.json`.
- `.claude/skills/collections-playbook/` — aging buckets, the aging log format, the tone ladder, the cleared-payment test, skip rules and the one-chase-per-cycle ledger.

## Notes

- Built for 2-200 person founder-led home services shops with overdue invoices sitting.
- The agent never sends anything to a customer, never writes lien, legal or collections language, and never writes off a balance or pauses work without approval.
