---
category: Marketing
icon: activity
tags:
  - Paid Ads
  - Meta Ads
  - Google Ads
  - Spend Monitoring
  - Agency Ops
works_with:
  - type: mcp
    slug: meta-ads
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Ad Anomaly Watch

> Catch the spend and CPA spike on a live campaign before the client sees it on the invoice.

## What it does

Ad Anomaly Watch is a spend-and-CPA anomaly owner for founder-led marketing, creative, and web shops. On the cadence you set it pulls spend, clicks, conversions, and CPA or ROAS for every live campaign in Google Ads and Meta Ads, then flags pacing that will blow the cap, CPA above your threshold, conversion tracking sitting at zero while spend runs, and broken landing pages when a URL check is configured.

It never stops at an alert. Every anomaly comes with exactly one recommendation: pause this ad set or campaign, cut budget to a named number, or wait and watch with a reason. The default is to Slack you the rec and wait. Live spend only gets paused when you have configured that exact kill switch, and this agent never launches a campaign, ad, or keyword.

## What you'll need

- **Meta Ads** — required for Meta campaign pulls, through the Meta Ads MCP.
- **Google Ads** — required for Google campaign pulls. Connected during onboarding; no registry connector, so the agent uses the account access you grant.
- **Slack** — required. Every rec, tracking break, and kill-switch fire lands in your founder channel.
- **Client tracker** — optional. A sheet or tracker that maps accounts to clients and caps.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your ad accounts, CPA and cap targets per client, what counts as a spike, whether a kill switch exists, and which Slack channel gets the recs, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Check live campaigns for spend and CPA spikes and draft pause-or-rec notes without pausing anything.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Check every live campaign for spend and CPA spikes right now
- Which ad sets should we pause or cut today, and why
- Every two hours during business hours, watch live spend and Slack me any spike

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led agencies that need live spend watched, not another campaign brief.
- The agent never launches a campaign, rewrites the media plan, or hides a tracking break while spend continues.
- No pause or budget change happens without founder approval unless a kill switch you configured has fired.
