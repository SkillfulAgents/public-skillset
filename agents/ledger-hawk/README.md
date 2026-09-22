---
category: Ops
icon: calculator
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

Ledger Hawk owns invoices out and overdue chased for founder-led consulting, accounting, insurance, and staffing firms. It pulls completed work, time, or retainers with no invoice yet from QuickBooks, the CRM, or your sheet, and queues each new invoice for one-tap send by email or through QuickBooks.

It ages open invoices and drafts the next chase in the firm voice, then Slacks you the file at the escalation age you set. No legal language, no write-offs without approval, and no run that stops after creating invoices and skips the overdue chase.

## What you'll need

- **QuickBooks** — required for unbilled work, open invoices, and invoice drafts.
- **HubSpot** — the supported CRM connector for completed-work signals. Another CRM or a sheet can be configured during onboarding.
- **Gmail** — required for invoice and chase drafts.
- **Slack** — required. Escalations land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your billing system, payment terms, aging buckets, chase voice, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Draft invoices for completed unbilled work and the next overdue chases, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft invoices for completed unbilled work and the next overdue chases
- Show me everything over 45 days and draft a firmer chase for each
- Every Friday, invoice the week's completed work and Slack me the drafts

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led professional firms with completed work unbilled and overdue sitting.
- Invoices and chases stay in draft until the founder sends.
