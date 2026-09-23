---
category: Ops
icon: wallet
tags:
  - Accounts Payable
  - Vendor Follow-Up
  - Bills Due
  - QuickBooks
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

# Vendor Nudge

> Late suppliers get a nudge and this week's bills get a pay list, without the agent ever touching your money.

## What it does

Vendor Nudge owns late suppliers and bills you owe for micro-owners and founder-led SMBs. It watches open POs and promised dates from email, your sheet, or QuickBooks and, when a delivery is late, drafts a short supplier nudge in your voice instead of stopping at a late list.

It pulls unpaid bills and upcoming due dates, groups what is due this week versus what can wait, and flags late fees and shutoff risk. For each item it recommends pay, nudge, or dispute with the amount and due date, and queues nudges for one-tap send. It never pays a bill or moves money, and customer AR stays with Invoice Ask.

## What you'll need

- **QuickBooks** — required for bills, due dates, and open POs.
- **Gmail** — required for supplier threads and nudge drafts.
- **Slack** — required. The pay list and vendor disputes land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for where POs and bills live, your regular suppliers, which Slack channel gets the pay list, and any never-nudge vendors, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: List late suppliers and bills due this week, draft nudges, and build a pay list, without sending or paying.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List late suppliers and bills due this week and draft the nudges
- Build the pay list for this week and flag anything with a late fee
- Every Monday morning, Slack me the pay list and the late POs

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners juggling late POs and bills due this week.
- Vendor nudges stay in draft until the founder sends. This agent is the opposite of Invoice Ask and never chases customers.
