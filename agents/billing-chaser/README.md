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

Billing Chaser owns agency money in for founder-led marketing, creative, and web shops. It pulls unbilled hours from Harvest, Toggl, or your time sheet against each retainer or project, drafts the invoice, and chases overdue agency invoices on cadence in your voice.

It watches hours or dollars left on every retainer and warns at the remaining percent you set (default 20%). When a retainer end date lands inside the renewal window, it drafts the renewal inside this same job instead of spinning up a separate agent. Invoices, chases, and renewals all stay in draft until you approve the exact text.

## What you'll need

- **QuickBooks** — required for open invoices, aging, and invoice drafts.
- **Gmail** — required for chase and renewal drafts.
- **Slack** — required. Low-retainer warnings and renewal drafts land in your founder channel.
- **Harvest or Toggl** — one is needed for unbilled time. No registry connector; connect the account or point the agent at your time sheet during onboarding.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your time system, the low-retainer percent, the renewal window, your chase voice, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Pull unbilled time, overdue invoices, and retainers running low, and draft any renewals due without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Pull unbilled time and overdue invoices and draft what should go out today
- Which retainers are under 20% left, and draft the renewals for any ending soon
- Every Monday, chase overdue invoices on cadence and Slack me the drafts

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led agencies with time sitting unbilled and retainers that expire quietly.
- The agent never writes off hours, discounts a retainer, or sends legal collections language.
