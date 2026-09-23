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
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Invoice Ask

> Ask the customers who owe you, on cadence and in your voice, until they pay or you step in.

## What it does

Invoice Ask owns customers who owe you for micro-owners and founder-led SMBs. It pulls open customer invoices from QuickBooks or your invoice sheet and writes a short founder-voice ask that names the invoice and the due date. Every ask is queued for one-tap send on the cadence you set.

After the last unanswered ask it Slacks you to escalate, with no legal or collections language anywhere. Vendor bills stay out of this queue entirely; that is Vendor Nudge's job. The agent never writes off a balance and never stops at an AR list without drafting the ask.

## What you'll need

- **QuickBooks** — required for open customer invoices and payment status.
- **Gmail** — required for the ask drafts.
- **Slack** — required. Escalations after the last ask land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your invoice source, the ask cadence, your ask voice, and any do-not-ask customers, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: List customers who owe you, draft the next asks, and keep vendor bills out of the queue, all without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List who owes us and draft the next ask for each open invoice
- Draft a second ask for the Bell Plumbing invoice that is 20 days late
- Every Tuesday, send me the ask queue and flag anyone past the last ask

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners who know who owes them and still have not asked.
- Asks stay in draft until the founder sends. This agent is the opposite of Vendor Nudge and never chases vendors or pays bills.
