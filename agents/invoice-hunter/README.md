---
category: Ops
icon: badge-dollar-sign
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

Invoice Hunter owns overdue invoices for founder-led home services shops. It pulls open invoices from QuickBooks or your billing system, ages them 1-30, 31-60, 61-90, and 90+, and drafts the next reminder in the shop voice: polite and specific first, then naming the job and the due date.

When a customer replies with a date or a partial, it logs the promise and watches that date rather than dunning through it. At the escalation age you set, or after the last unanswered reminder, it Slacks you the file with a recommended next step: call, pause work, or a collections talk. Reminders stay in draft until you approve.

## What you'll need

- **QuickBooks** — required for open invoices and aging.
- **Gmail** — required for reminder drafts.
- **Slack** — required. Escalations and promise-to-pay dates land in your founder channel.
- **Jobber and an SMS line** — optional, for job context and text reminders. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your billing system, the aging cadence, your reminder voice, the escalation age, and any do-not-chase customers, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Pull overdue invoices, draft the next chase on cadence, and flag anything that needs you, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Pull overdue invoices and draft the next reminder for each one
- Log that the Nguyen job promised to pay Friday and pause their reminders
- Every Monday, chase everything past due and Slack me what hit 60 days

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops with overdue invoices sitting.
- The agent never sends legal, collections, or lien language and never writes off a balance or pauses work without approval.
