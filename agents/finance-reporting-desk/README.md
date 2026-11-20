---
category: Ops
icon: calculator
tags:
  - Finance
  - Month-End Close
  - Board Reporting
  - Cash Management
  - Variance Analysis
  - QuickBooks
works_with:
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: xero
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: gmail
  - type: api_account
    slug: stripe
  - type: mcp
    slug: mercury
  - type: mcp
    slug: ramp
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Finance Reporting Desk

> The weekly cash note, the close checklist, the variance "why" and the board pack are ready before you sit down to write them.

## What it does

Finance Reporting Desk runs the recurring reporting work for a finance lead, controller, or founder acting as CFO:

- **Weekly cash update draft**: cash on hand, expected collections, upcoming payments, net burn and runway, then a short "what changed and why". It says so when a bank feed or sheet didn't refresh instead of guessing.
- **Month-end close tracker**: a living close-status doc built from your own checklist, covering unbooked invoices, accruals, deferred revenue, prepaids, missing receipts, bank recs and journal entries owed. It cross-checks your inbox for items that are sitting in email, marks something received only when it can see the evidence, ranks what's open by what blocks close and by amount, and drafts chase messages for your approval.
- **Monthly variance commentary**: only the 3-5 lines that matter against budget and forecast, with the "why" found in your email, Slack and notes. When it can't find a reason, it drafts a nudge to the budget owner instead of inventing one. It also flags data errors such as sign flips, missing months and doubled lines.
- **Board and investor reporting pack**: a four-period comparison table, the KPI read your board tracks, the variance narrative, and a "what to flag" section, saved as a dated doc.

It reads from QuickBooks or Xero, Stripe, Mercury, Ramp or Brex, and your budget and forecast sheets. It never posts to the books, moves money, or sends anything to anyone without your OK.

## What you'll need

- **QuickBooks** or **Xero**: your ledger, AR and AP. One of them is required, or regular exports.
- **Google Sheets** (or Excel): budget, forecast, close checklist and cash model.
- **Gmail** (or Outlook): inbox cross-checks during close, the "why" search, and drafts.
- **Stripe**: optional, for revenue, payouts and the clearing-account check.
- **Mercury**: optional, through its MCP server, for bank balances. Other banks work through a CSV drop or a browser session.
- **Ramp** or **Brex**: optional, through their MCP servers, for card balances and missing receipts.
- **Google Drive and Docs, Slack, Carta**: optional, for saved packs, the "why" search, report delivery, and stock comp.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It asks which routines you want, where your numbers live, your close calendar and checklist, materiality, KPI definitions, and where drafts and reports should go. Then it connects your accounts and runs each routine once with you.
3. Ask for a first run: "Draft this week's cash update."

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft this week's cash update from Mercury and QuickBooks
- What's still open for the October close, and who are we waiting on?
- Build the November board pack with variance commentary and what to flag

## What's inside

- `CLAUDE.md`: the four routines with their domain details, connection and scheduling mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup that writes `config.json` and creates one schedule per routine.
- `.claude/skills/finance-checks/`: burn, runway, variance and materiality formulas, plus the data-error checks run before any report.

## Notes

- Read-only on your ledger, bank and cards. It never posts entries, pays bills or reconciles accounts.
- Messages to budget owners and your CEO wait for your approval. Anything to a vendor always waits.
- For spend anomaly scans and COGS audits, see the sibling SaaS CFO Monitor template. For software subscription waste, see SaaS Spend Auditor.

## Privacy

The agent reads financial records, email and Slack threads only to build your reports. Run state (weekly cash snapshots, close items, variance notes) stays in the agent's workspace.
