---
name: agent-onboarding
description: 'First-run setup for Growth Readout: connects the user''s analytics, ad, search and CRM sources, captures metric definitions, segments and voice, sets the Monday schedule and delivery, and runs a supervised first readout.'
first_prompt: 'Set up Growth Readout for me'
---

# Growth Readout onboarding

Run this before first use. Reuse anything already in `CLAUDE.md` under `## Your context` and in `.claude/skills/agent-onboarding/config.json`; ask only for what is missing.

## 1. Welcome

Say in two or three sentences what will be set up: a Monday readout with a leadership update draft, a website conversion section and a "what's shifting" analysis, posted as a short team summary plus a full doc. Then show the questions you plan to ask, as a short list, so the user knows how long this takes:

1. Which sources you use (analytics, ads, search, product analytics, CRM)
2. What counts as a signup, a lead or MQL, and pipeline
3. The segments you care about
4. Where the summary and the full doc should go
5. When leadership needs the update, and your timezone
6. A past update so the draft sounds like you

## 2. Discover and connect sources

For each candidate service, call `mcp__user-input__search_connection_options` and note what is already connected. Then ask which ones the user actually uses, with `AskUserQuestion` (multi-select): Google Analytics 4, Google Search Console, Google Ads, Meta Ads, LinkedIn Ads, PostHog, Amplitude, Mixpanel, HubSpot, Salesforce.

Connect each chosen source:
- GA4: `mcp__user-input__request_connected_account` with `toolkit: "google_analytics"`, reason "Allow access to Google Analytics to read last week's traffic and conversions?". Then list the account's properties and ask which property to use if there is more than one.
- Search Console: `google_search_console`; ask which site property (domain vs. URL-prefix).
- Google Ads: `googleads`; ask which customer account(s), and whether a manager account is involved.
- Meta Ads or LinkedIn Ads: use whatever `search_connection_options` returns. If nothing fits, offer a weekly CSV export (the user uploads via `mcp__user-input__request_file`) or a Google Sheet they already maintain. If neither, record the channel as "not covered" so every readout says so.
- PostHog, Amplitude, Mixpanel: `mcp__user-input__request_remote_mcp` with the URL from `search_connection_options`. Ask which project.
- HubSpot or Salesforce: connected account (`hubspot` or `salesforce`).
- Google Docs and Drive (`googledocs`, `googledrive`) for the full breakdown and the draft, unless the user prefers Markdown files.

If the user connects nothing in a category, continue: the readout works with any subset and states what is missing.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete; otherwise ask in plain chat and wait for each answer.

1. **Signup definition.** Which GA4 key event or PostHog/Amplitude/Mixpanel event is a signup? Offer the event names you found.
2. **Funnel definitions.** In the CRM, what is a lead, an MQL or SQL, and "pipeline created" (deal stage, opportunity created, amount field)? Which currency?
3. **Segments to watch.** Which fields define segments (industry, company size, persona or job title, region, source, use case, plan)? Read the CRM properties first and offer the real field names.
4. **Baseline.** Default trailing 8 weeks. Ask whether any recent weeks should be excluded (launch, holiday, outage).
5. **Reporting week and timezone.** Monday to Sunday by default.
6. **Leadership deadline.** When does the update go out? Set the run a couple of hours before.
7. **Draft format.** Ask for a past update (paste or `mcp__user-input__request_file`). Note section names, length, tone and abbreviations. Ask whether the draft should live in a Google Doc or a Gmail draft with no recipients.
8. **Team summary destination.** Use `AskUserQuestion`: the agent's Slack app in a team channel, a Slack DM to the user, the agent's own email inbox, or in-app only. For Slack, check `mcp__chat__list_agent_integrations`; if no Slack integration exists, set one up with `mcp__chat__add_agent_integration` or hand it to the user with `mcp__user-input__request_integration_setup`, then resolve the exact channel with `mcp__chat__list_chat_channels`. Remind the user to invite the agent to a private channel.
9. **Full doc location.** Which Drive folder, and who can view.
10. **Privacy.** May the team summary name customers or companies, or should it link to records only?
11. **Autonomy.** Confirm the default: read only everywhere, draft only for leadership, posts only the internal summary. Ask whether they also want the optional Thursday "only if something broke" check.

## 4. Supervised dry run

Run the full routine on the last complete week with real data. Show the user, in the chat: the team summary as it would be posted, the leadership draft, and the website and shifting sections. Point out every source marked missing or provisional. Ask what to change (tone, length, metrics, segments, thresholds), apply it once, and confirm. Do not post to Slack or create the shared doc until the user approves the format; then create the first doc and post the first summary if they want it.

Backfill the baseline: if the sources allow, compute the trailing 8 weeks now and write them to `/workspace/state/growth-readout/weekly/` so the first scheduled run has a baseline.

## 5. Schedule

Create the recurring task with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, default `0 7 * * 1` adjusted to the deadline and timezone. The prompt must be self-contained, for example:

> Run the Growth Readout weekly routine. Read config from `.claude/skills/agent-onboarding/config.json` and context from `CLAUDE.md`. Window: the last complete reporting week in the configured timezone, compared with the prior week and the trailing baseline in `/workspace/state/growth-readout/weekly/`. Produce: (1) the leadership update draft (draft only, never send or address it), (2) the website section, (3) the what's-shifting section using the `shift-detection` skill; write "No meaningful shifts this week" if none qualify. Report any missing, failed or partial source as missing, never as zero. Create the full breakdown doc in the configured folder, save this week's metrics to state, then post the short summary to the configured destination with `mcp__chat__send_chat_message`.

If the user opted in, add the Thursday check (`0 12 * * 4`) with a prompt that posts only when a tracking break or a sharp swing is found and otherwise sends nothing.

Confirm with `mcp__user-input__list_scheduled_tasks`.

## 6. Save configuration

Write the answers into `CLAUDE.md` under `## Your context` as short plain bullets, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "reporting_week": "mon-sun",
  "run_cron": "0 7 * * 1",
  "midweek_check": false,
  "sources": {
    "google_analytics": {"connected": true, "property_id": ""},
    "google_search_console": {"connected": false, "site": ""},
    "googleads": {"connected": false, "customer_ids": []},
    "meta_ads": {"mode": "none | connection | csv | sheet", "location": ""},
    "linkedin_ads": {"mode": "none | connection | csv | sheet", "location": ""},
    "product_analytics": {"tool": "posthog | amplitude | mixpanel | none", "project": ""},
    "crm": {"tool": "hubspot | salesforce | none"}
  },
  "definitions": {
    "signup_event": "",
    "lead": "",
    "mql": "",
    "pipeline_created": "",
    "currency": "USD"
  },
  "segments": ["industry", "company_size", "persona", "source", "use_case"],
  "baseline_weeks": 8,
  "excluded_weeks": [],
  "delivery": {
    "summary": {"via": "slack | email | in-app", "destination": ""},
    "full_doc": {"via": "googledocs | markdown", "folder": ""},
    "leadership_draft": {"via": "googledocs | gmail_draft"}
  },
  "summary_may_name_customers": false,
  "voice_notes": ""
}
```

Finish with a short summary: what runs when, where each output lands, which sources are connected and which are missing, and how to re-run onboarding.
