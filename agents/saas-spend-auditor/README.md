---
category: Ops
icon: receipt
avatar:
  color: tonal-white
  shape: circle
tags:
  - SaaS Spend
  - Cost Savings
  - Subscriptions
  - Renewals
  - Ramp
  - Brex
works_with:
  - type: mcp
    slug: ramp
  - type: mcp
    slug: brex
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: googlecalendar
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# SaaS Spend Auditor

> Find the software your team pays for and doesn't use, and catch every renewal while you can still say no.

## What it does

Once a month, SaaS Spend Auditor pulls recurring charges from Ramp or Brex, or from your accounting system or a card export, and looks back 13 months so annual plans don't hide. It rolls spend up by vendor with amount, cadence and change against prior months, and cleans up messy card descriptors along the way.

Then it looks for usage evidence: paid seats against active users where admin data is reachable, activity from admin exports you share, and softer signals such as mentions in email, Slack and the calendar. It flags tools with no use in 30 days, excess seats, renewals and price increases, duplicate tools, trials that turned into paid plans, and the same vendor paid on several cards. The digest is ranked by potential savings and split into "probably cancel" and "worth a closer look". Each item says how strong the evidence is and when the saving can actually be realized.

It also tracks renewal notice deadlines, which usually fall 30-90 days before the renewal itself, and warns you while there's still time to act. It never cancels, downgrades, changes seats or contacts a vendor.

## What you'll need

- **Ramp** or **Brex**: one spend source, through their MCP servers. QuickBooks, Xero or a card export work instead.
- **Gmail**: recommended, for renewal and signup emails and usage signals.
- **Slack**: optional, for tool mentions and, if you're an admin, inactive members.
- **Google Sheets**: optional, for a shared subscription inventory.
- **Google Calendar**: optional, for meeting-tool usage and notice-deadline reminders.
- **Admin access or exports** for tools like GitHub, Zoom, HubSpot or Notion: optional, for the strongest seat-usage evidence.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It asks where software gets paid for, where usage can be seen, your thresholds and keep-list, how early to warn about notice deadlines, and where the digest goes. Then it connects your accounts and runs a supervised first review.
3. Ask for your first review: "Find software we're paying for but not using."

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Find software we're paying for in Ramp but nobody has used in 30 days
- Which SaaS renewals have notice deadlines in the next 60 days?
- On the 1st of every month, email me the ranked subscription savings digest

## What's inside

- `AGENTS.md`: the monthly waste review and the renewal notice watch, with their domain details, connection and scheduling mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup that writes `config.json` and creates both schedules.
- `.claude/skills/spend-rollup/`: vendor normalization, cadence detection, usage-evidence grades, savings math and notice-deadline rules.

## Notes

- Report only. Cancelling, downgrading and vendor contact are always your call. Check-ins to tool owners are drafted and held for approval.
- "No usage signal found" is not the same as "unused", and the digest always says which one it means.
- For personal subscriptions found in Gmail receipts, see the sibling Subscription Pruner template.

## Privacy

The agent reads card transactions, email, Slack and calendar metadata only to judge whether a tool is used. The subscription inventory stays in the agent's workspace, or in your sheet if you choose one.
