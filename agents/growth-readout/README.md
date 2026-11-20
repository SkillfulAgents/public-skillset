---
category: Marketing
icon: trending-up
tags:
  - Marketing Reporting
  - Web Analytics
  - Pipeline Analysis
  - Google Analytics
  - HubSpot
  - Weekly Digest
works_with:
  - type: api_account
    slug: google_analytics
  - type: api_account
    slug: google_search_console
  - type: api_account
    slug: googleads
  - type: api_account
    slug: hubspot
  - type: mcp
    slug: posthog
  - type: api_account
    slug: googledocs
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Growth Readout

> Start every Monday with the leadership update already drafted and a clear read on what your website and pipeline are really telling you.

## What it does

Every Monday morning Growth Readout pulls last week's numbers from whatever you have connected: Google Analytics, Search Console, Google Ads, product analytics, and your CRM. It compares them with the week before and with your recent baseline, then writes three things:

- **A leadership update draft**: headline takeaways, a compact numbers table with week-over-week changes, what changed and what it means, and your asks. It matches the format of a past update you share, and it always stays a draft.
- **A website section**: which pages and calls to action drive signups, which button copy is winning (and when it is too early to tell), where visitors stop scrolling on the homepage, and which traffic sources send people who convert, not just people who visit.
- **A "what's shifting" readout**: real changes in who is signing up and entering pipeline, such as a new industry or persona gaining traction, a channel bringing a different kind of lead, a use case catching on, or a segment going quiet. Each one comes with the evidence, what it might mean and a suggested next move. Normal weekly noise is filtered out.

A short summary goes to your team channel from the agent's own Slack app, and the full breakdown, with every table, lands in a shareable doc. Missing or broken data is called out by name, never reported as zero.

## What you'll need

- **Google Analytics 4**: recommended, for traffic, conversions, landing pages and scroll depth.
- **Google Search Console**: optional, for organic queries and pages.
- **Google Ads**: optional, for paid spend and conversions. Meta and LinkedIn ads are covered through a connection if one is offered, or a weekly export or sheet.
- **PostHog**: optional, for product events, experiments and heatmaps. Amplitude or Mixpanel work the same way.
- **HubSpot**: recommended, for leads and pipeline. Salesforce works too.
- **Google Docs**: recommended, for the full breakdown and the leadership draft. Markdown files are the fallback.
- **Slack**: optional, the agent's own Slack app posts the team summary. Email or in-app delivery work too.
- **API keys:** none.

The readout works with any subset of these sources and states clearly what is missing.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It connects your sources, asks what counts as a signup, lead and pipeline, which segments matter, where the summary and doc should go, and when leadership needs the update. It also reads a past update to match your voice.
3. Ask for a dry run on last week's data, review it, then let the Monday schedule take over.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft last week's marketing update from what's connected
- Which traffic sources actually converted to signups last week?
- What's shifting in our signups and pipeline versus the last two months?

## What's inside

- `CLAUDE.md`: the three weekly routines, the data-honesty rules, the Gamut connections and schedule, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/`: first-run setup for sources, definitions, segments, delivery and the Monday schedule.
- `.claude/skills/shift-detection/`: the rules that separate a real signup or pipeline shift from weekly noise.

## Notes

- The agent reads only. It never changes ad accounts, analytics settings, experiments or CRM records, and never sends the leadership update.
- Ad-platform conversions are reported per platform and never added together, since each platform claims credit differently. The last few days of paid data are marked provisional.
- The first run backfills a baseline from your recent history when the sources allow it. Until then, shifts are described with less confidence.
