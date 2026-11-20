---
category: Customer Success
icon: refresh-cw
tags:
  - Contract Renewals
  - Notice Deadlines
  - Vendor Contracts
  - Professional Services
  - Google Drive
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Renewal Clerk

> Every contract end date is tracked and every renewal is drafted before the term quietly dies.

## What it does

Renewal Clerk owns contract renewals for founder-led consulting, accounting, insurance, staffing and law firms, on both sides: the contracts clients pay you for and the contracts you pay vendors for. It keeps a living tracker with counterparty, annual value, renewal date, an auto-renew yes/no flag, and the notice-period deadline, which is the real date you have to act by and often falls 30 to 90 days before the renewal date.

When a new contract, order form or renewal notice lands in your inbox, it reads the attachment itself, not just the email, and adds or updates the tracker. A contract whose terms it could not read is flagged as a data hole, never guessed.

It alerts you ahead of every notice deadline with enough lead time to decide, with big-ticket and auto-renewing contracts first. For clients it pulls the usage picture where one is connected and drafts the renewal note and next-term order form from your template and current price. For vendors it shows a decision card and drafts the non-renewal or renegotiation email you ask for. Nothing auto-renews, nothing is cancelled, and no email goes out without your approval.

## What you'll need

- **Google Drive** — required for the contract folder and the order form template. Dropbox, Box or OneDrive work too.
- **Gmail or Outlook** — required. New contracts and renewal notices are read from your inbox and drafts land there.
- **Google Sheets** — recommended, if you want the tracker as a sheet you can see.
- **HubSpot** — optional, for customer contract records and renewal logging. Salesforce or Attio work too.
- **Slack** — the agent posts alerts from its own Slack app, set up during onboarding. Your own Slack account is only needed if it should read a channel.
- **Google Calendar** — optional, for a hold on each act-by date.
- **Usage or billing system** — optional, for the client usage picture. Connected during onboarding; no registry connector.
- **API keys:** none required.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your contract folder and mailbox, asks which sides to track, your alert lead times, big-ticket threshold, usage source and renewal voice, parses a first batch of contracts with you, and schedules the sweeps, alerts and the new-contract watch.
3. Ask for the first run: build the tracker, list notice deadlines in the next 120 days, and draft customer renewals that are due, without sending.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- List every notice deadline in the next 90 days, auto-renewing ones first
- Draft the Beacon renewal with their usage this term and the current price
- Which vendor contracts auto-renew this quarter and what does each cost?

## What's inside

- `CLAUDE.md` — the routines (contract tracker, new contract or notice, notice-deadline alerts, customer renewals, vendor decisions, weekly view), the Gamut mechanics, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run setup: connections, questions, supervised first parse, schedules and triggers, and `config.json`.
- `.claude/skills/contract-terms/` — what to read in a contract, how to compute the notice deadline and set the auto-renew flag, parse status, the tracker row, and alert order.

## Notes

- Built for 2-200 person founder-led professional firms whose terms die, or auto-renew, because nobody watched the notice window.
- Software subscriptions found in card spend belong to SaaS Spend Auditor; if both are installed, this agent tracks only signed contracts.
- Renewals and notices stay in draft until the founder sends. The agent flags a missing or unreadable date rather than guessing.
