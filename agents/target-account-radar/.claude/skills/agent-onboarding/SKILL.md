---
name: agent-onboarding
description: 'Sets up Target Account Radar: builds the editable watchlist, picks X and web sources, sets the signal bar, cadence, budget and delivery channel, runs a supervised first digest, and schedules the digest and X watch.'
first_prompt: 'Set up Target Account Radar for me'
---

# Target Account Radar onboarding

## 1. Welcome

Explain in two or three sentences: you will keep an editable watchlist of accounts, contacts, competitors and topics. You will send a cited digest grouped by account, each item with an outreach angle, and run a high-bar X watch that messages the user only when something real happens. You never contact anyone.

List the planned questions up front, then ask one at a time. Skip anything already in `CLAUDE.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for Google Sheets, Google Docs, the user's CRM (HubSpot, Salesforce, Attio, Pipedrive, Close) and X (`twitter`). Note what is already connected. Call `mcp__chat__list_agent_integrations` to see existing delivery channels.

X decision (read `/opt/gamut/docs/x.md`): if a `twitter` connected account exists, use it. Otherwise use the built-in public reads and do not ask the user to connect.

## 3. Questions, one at a time

1. What do you sell, and to whom? One or two sentences. This drives every outreach angle.
2. Where is your target account list today: a sheet, a doc, a CRM list or view, or should I start a new sheet? (Offer to create a Google Sheet with columns: Account, Domain, Tier, Key contacts, Competitors, Topics, X handles, Angle, Last signal.)
3. Which competitors and industry topics should I watch beyond the accounts?
4. Which people's X accounts matter (founders, executives, analysts)? Any keyword topics for X?
5. Digest cadence: weekly (default) or daily? What day and time? How far back should each digest look?
6. X watch: how many checks a day (default two) and quiet hours? With built-in reads, give a rough monthly cost estimate from the list size, labeled as an estimate, and ask for a monthly ceiling.
7. Which signals matter most to you? (Use `AskUserQuestion` with multi-select: funding, leadership change, M&A, launches, earnings, hiring or layoffs, press, social posts, regulation.)
8. Where should the digest and alerts go: in-app, the agent's Slack DM, a team Slack channel through the agent's Slack app, the agent's own email inbox, Telegram or iMessage?
9. If nothing clears the bar: send a one-line "nothing new" note, or stay silent? (X alerts always stay silent.)
10. May I update the "Last signal" column in the watchlist sheet? (Default no.)
11. Timezone.

## 4. Connect

- `mcp__user-input__request_connected_account` for `googlesheets` or `googledocs`, the CRM (`hubspot`, `salesforce`, `attio`) if the list lives there, and `twitter` only if the user wants to use their own X account.
- `mcp__user-input__request_remote_mcp` for `pipedrive` or `close` if needed.
- Delivery: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup` to hand the form to the user.

## 5. Supervised dry run

1. Read the watchlist and show how you resolved each account (domain, industry). Fix any mismatches with the user.
2. Run a digest for the top 5 accounts with a 30-day lookback so there is something to show. Show it.
3. Run one X check with tight queries. Show any alert you would have sent and the number of posts it read.
4. Ask what to tighten or loosen. Iterate once. Seed `seen.json` and `x-cursors.json` from this run so the first scheduled run does not repeat it.

## 6. Schedule

Create with `mcp__user-input__schedule_task` (`scheduleType: "cron"`, user's timezone):
- Digest: `0 7 * * 1` by default.
- X watch: `0 9,15 * * 1-5` by default.

Example self-contained prompt for the X watch:

> Target Account Radar, X watch. Read `CLAUDE.md` `## Your context`, `.claude/skills/agent-onboarding/config.json` and `/opt/gamut/docs/x.md`. Load the X handles and queries from the watchlist. Use `/workspace/state/target-account-radar/x-cursors.json` for `since_id`. Apply the `signal-bar` skill; only High signals qualify. For each one, send a direct message with `mcp__chat__send_chat_message` to the configured channel: what happened, who, why it matters, link. If nothing qualifies, send nothing. Never post or reply on X. Update the cursors, baselines and `seen.json`, and the monthly read count.

Confirm with `mcp__user-input__list_scheduled_tasks`.

## 7. Save

Write a plain-language summary under `## Your context` in `CLAUDE.md` and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "offer": "",
  "ideal_customer": "",
  "watchlist": { "type": "googlesheets", "id": "", "tab": "Accounts" },
  "crm_list": null,
  "competitors": [],
  "topics": [],
  "signal_priorities": ["leadership_change", "funding", "launch"],
  "digest": { "cron": "0 7 * * 1", "lookback_days": 14, "silent_when_empty": false },
  "x": {
    "mechanism": "builtin",
    "cron": "0 9,15 * * 1-5",
    "handles": [],
    "queries": [],
    "monthly_budget_usd": 0,
    "quiet_hours": "20:00-07:00"
  },
  "delivery": { "digest": { "channel": "email", "integration_id": "" }, "alerts": { "channel": "slack_dm", "integration_id": "" } },
  "may_update_sheet": false,
  "timezone": "America/New_York"
}
```

Finish with a summary: what runs when, where it lands, the X budget, and that nothing is ever sent to accounts.
