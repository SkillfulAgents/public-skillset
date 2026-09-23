---
category: Marketing
icon: presentation
tags:
  - Client Reporting
  - Monthly Recaps
  - Meta Ads
  - Google Ads
  - Agency Ops
works_with:
  - type: mcp
    slug: meta-ads
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Report Runner

> Every client's monthly recap written from ads, analytics, and the sheet, with what moved flagged, ready for one-tap send.

## What it does

Report Runner owns the monthly client recap for founder-led marketing, creative, and web shops. For each client on the roster it pulls the reporting month from Google Ads, Meta Ads, GA4, and the client tracker sheet, then drafts a short founder-voice recap: what we spent, what it did, what changed versus last month, and the one thing to do next.

It calls out spend or CPA spikes, tracking breaks, and campaigns that died mid-month instead of hiding them. Each recap lands in a Google Doc or an email draft, and you get the pack in Slack for one-tap send. The agent never invents metrics or changes bids, budgets, or campaigns.

## What you'll need

- **Meta Ads** — required for Meta campaign data, through the Meta Ads MCP.
- **Google Drive** — required for the recap Docs.
- **Gmail** — required for recap email drafts.
- **Slack** — required. The monthly pack lands in your founder channel.
- **Google Ads and GA4** — required for Google campaign and analytics data. Connected during onboarding; no registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your client roster, ad accounts, the reporting month, your recap voice, and the founder Slack channel, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Build this month's client recaps from ads, analytics, and the sheet, as drafts only.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Build this month's client recaps from ads, analytics, and the sheet
- Draft the Lumen recap and flag anything that spiked or broke in August
- On the 2nd of every month, build all recaps and Slack me the pack to send

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led marketing, creative, and web shops that still assemble monthly recaps by hand.
- Recaps stay in draft until the founder sends.
