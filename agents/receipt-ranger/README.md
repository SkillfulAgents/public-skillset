---
category: Ops
icon: receipt
tags:
  - Receipts
  - Bookkeeping
  - Month-End Close
  - QuickBooks
  - Google Drive
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Receipt Ranger

> Forwarded receipts get filed and month-end holes get flagged before the bookkeeper asks.

## What it does

Receipt Ranger owns forwarded receipts and monthly holes for micro-owners and founder-led SMBs. It watches the receipt inbox or a forwarded Gmail label for photos, PDFs, and card alerts, codes each one, and files it into the monthly Drive folder or the QuickBooks receipt inbox.

Near month end it compares card and bank lines to filed receipts and builds the hole list. You get the list and the month pack in Slack or email for one-tap send to the bookkeeper. It never invents a missing receipt, never codes personal spend as business without asking, and never takes bank credentials in chat.

## What you'll need

- **Gmail** — required for the receipt inbox or forwarded label.
- **Google Drive** — required when receipts file to monthly folders.
- **QuickBooks** — required for the card and bank lines used in the hole check, and optional as the filing target.
- **Slack** — required. The hole list and month pack land in your founder channel.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your receipt inbox, file location, expense categories, whether a bookkeeper pack goes out, and any personal merchants to skip, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: File this week's forwarded receipts and show any holes against the card feed, without emailing the bookkeeper.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- File this week's forwarded receipts and show any holes against the card feed
- Build the August month pack and list every card line with no receipt
- Every Friday, file the week's receipts and Slack me what is still missing

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 1-15 person micro-owners who forward receipt photos and still miss month-end holes.
- Bookkeeper packs stay in draft until the founder approves.
