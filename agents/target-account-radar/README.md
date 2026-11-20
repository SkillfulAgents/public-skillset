---
category: Sales
icon: target
tags:
  - Account-Based Selling
  - Buying Signals
  - Sales Intelligence
  - X Monitoring
  - Outreach Angles
works_with:
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: salesforce
  - type: api_account
    slug: twitter
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Target Account Radar

> Always have a timely, specific reason to reach out to the accounts you care about most.

## What it does

Target Account Radar watches a list you can edit: target accounts, their key people, competitors and industry topics. It watches the web and X for real buying signals: funding, acquisitions, leadership changes, launches, earnings, hiring surges or layoffs, press, and notable posts. It also watches for sub-industry trends that create urgency for what you sell.

- **Account digest.** Weekly by default, or daily. Grouped by account, with account news first and industry signals after. Each item has a source link and date, why it matters, and a suggested outreach angle or opening line. Stale, repeated and unsourced items are dropped.
- **X watch.** A couple of times a day it checks the people and topics you track on X. It messages you only when something clears a high bar, such as a launch, a funding announcement, a new executive, or a pointed critique of a competitor. If nothing does, you hear nothing.

It researches and suggests. It never sends outreach and never posts on X.

## What you'll need

- **Google Sheets or Google Docs:** required for the editable watchlist, unless the list lives in your CRM.
- **HubSpot or Salesforce:** optional, to read target accounts from a CRM list. Attio, Pipedrive and Close also work.
- **X:** built-in public X reads work with no account. They are billed per post read, so queries stay narrow. Connect your own X account (`twitter`) if you prefer to use it.
- **Delivery channel:** in-app, or the agent's own Slack app, email inbox, Telegram or iMessage.
- **API keys:** none. Web search, Exa and lead enrichment are built in.

## Getting started

1. Import the template into Gamut. The `agent-onboarding` skill starts automatically.
2. Onboarding builds or connects your watchlist and learns what you sell. It sets the signal bar, the digest cadence, the X check times and a monthly X budget, then picks where alerts go and runs a first digest on your top accounts.
3. Review the first digest, tighten the list, and let the schedules run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Start a watchlist sheet from these ten accounts and their CEOs
- What happened at my target accounts this week, and how should I open?
- Watch these founders on X twice a day and ping me only on big news

## What's inside

- `CLAUDE.md`: the digest and X watch routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup, dry run, schedules and config.
- `.claude/skills/signal-bar/`: the freshness gate, signal strength table, outreach-angle formula and X query hygiene.

## Notes

- X recent search only reaches back about seven days. The watch checks steadily and cannot catch up after a long pause.
- Built-in X reads cost money per post. Onboarding gives a rough monthly estimate and sets a ceiling.
- For a deep weekly rundown on a single account, pair with `account-media-rundown`. For LinkedIn leaders, pair with `linkedin-signal-watch`.

## Privacy

Target Account Radar reads only public web and X content, plus the watchlist you give it. It keeps a ledger of links and post ids it has already reported, so nothing is reported twice. It never contacts anyone.
