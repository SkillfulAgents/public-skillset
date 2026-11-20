---
name: agent-onboarding
description: 'Sets up Pipeline Doctor: connects the CRM, mailbox and calendar, learns stage norms and thresholds, picks the delivery channel and autonomy, runs a supervised first pass, and schedules the four routines.'
first_prompt: 'Set up Pipeline Doctor for me'
---

# Pipeline Doctor onboarding

## 1. Welcome

Say in two or three sentences what you will set up: a weekly pipeline hygiene digest, weekly nudges for stalled deals, a biweekly closed-lost win-back pass, and an end-of-day CRM update draft. Everything outbound is a draft and every CRM change waits for approval unless they say otherwise.

Show the planned questions up front as a short list, then ask them one at a time. Skip any already answered in `CLAUDE.md` `## Your context`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for each candidate: the CRM (HubSpot, Salesforce, Attio, Pipedrive, Close), Gmail or Outlook, Google Calendar, and any meeting-notes tool. Note what is already connected.

- CRM: HubSpot, Salesforce and Attio as connected accounts (`hubspot`, `salesforce`, `attio`); Pipedrive and Close as remote MCP (`pipedrive`, `close`).
- Mail and calendar: always the user's own connected account, so drafts land in their mailbox.
- Notes: Granola, Fireflies, Otter via MCP; Gong, Fathom, Zoom via connected account. Optional.
- Delivery: call `mcp__chat__list_agent_integrations` to see whether the agent already has a Slack app, its own email inbox, Telegram or iMessage.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.

1. Which CRM do you use, and should I look at only your deals or the whole team's?
2. Gmail or Outlook for drafts? Which calendar?
3. Do you use a call recorder or notes tool I should read for the end-of-day draft?
4. What are your stage names, and what has to be true for a deal to enter each one? (Offer to read the pipeline settings from the CRM and confirm.)
5. Forecast day and time, so the hygiene digest lands before your forecast call.
6. How many days of no buyer reply counts as "gone quiet" for early and late stages? (Defaults 14 and 7.)
7. Which fields must every deal have? Which fields does your team ignore?
8. Minimum gap before a nudge after your last touch? (Default 5 business days.)
9. How far back should win-back look (default 24 months), and which loss reasons do you consider dead for good?
10. Anyone or any company I must never contact (opt-outs, legal, partners)?
11. Your own email domains and any domains to ignore (vendors, investors, recruiters).
12. Where should digests and approval batches go: in-app, the agent's Slack DM, the agent's own email inbox, Telegram, or iMessage?
13. Autonomy, per routine: drafts only (default), or may I log routine activity notes without asking? Stage changes and new records always wait.
14. Paste two or three emails you have sent to prospects so I can match your voice.
15. Your timezone.
16. Would you like a pipeline health dashboard? (Optional.)

## 4. Connect

- `mcp__user-input__request_connected_account` for `hubspot` / `salesforce` / `attio`, `gmail` or `outlook`, `googlecalendar`, and any notes tool with an account.
- `mcp__user-input__request_remote_mcp` for `pipedrive`, `close`, `granola`, `fireflies-ai`, `otter-ai` as needed.
- For delivery through the agent's own identity, follow `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or hand the form to the user with `mcp__user-input__request_integration_setup`.

## 5. Supervised dry run

Run on real data with no writes and no drafts saved yet:
1. Compute stage norms and show them. Ask whether they look right.
2. Produce the hygiene digest and show it.
3. Pick the top two stalled deals and show the reconstruction and draft text in chat.
4. Show one win-back candidate if any qualify.
5. Draft today's CRM updates (or yesterday's, if it is morning).

Ask what to change. Iterate once. Then, with the user's OK, save the stalled and win-back drafts to their mailbox.

## 6. Schedule

Create four `mcp__user-input__schedule_task` cron tasks in the user's timezone (defaults `30 7 * * 1`, `0 8 * * 1`, `0 9 1,15 * *`, `0 17 * * 1-5`; adjust to their forecast day). Each prompt must be self-contained, for example:

> Pipeline Doctor, weekly hygiene digest. Read `CLAUDE.md` `## Your context` and `.claude/skills/agent-onboarding/config.json` for the CRM, thresholds, deal scope and delivery channel. Apply the `pipeline-triage-rubric` skill to all open deals. Compare with `/workspace/state/pipeline-doctor/hygiene-last.json` and mark repeat offenders. Send the digest with `mcp__chat__send_chat_message` to the configured channel. Do not write to the CRM. If nothing is flagged, send one line saying the pipeline is clean and how many deals were checked. Update the state file.

Write similar prompts for the other three. Confirm with `mcp__user-input__list_scheduled_tasks`.

If the user wants the dashboard, build it now with the `dashboards` skill.

## 7. Save

Write the answers in plain language under `## Your context` in `CLAUDE.md`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "crm": { "system": "hubspot", "mechanism": "connected_account", "scope": "mine" },
  "mailbox": "gmail",
  "calendar": "googlecalendar",
  "notes_source": null,
  "timezone": "America/New_York",
  "stages": [ { "name": "Discovery", "entry_criteria": "", "median_days": null } ],
  "thresholds": {
    "quiet_days_early": 14,
    "quiet_days_late": 7,
    "close_date_pushes": 2,
    "stuck_multiplier": 1.5,
    "min_nudge_gap_business_days": 5,
    "winback_lookback_months": 24
  },
  "required_fields": ["amount", "closedate", "dealstage", "primary_contact"],
  "dead_loss_reasons": [],
  "suppression": { "emails": [], "domains": [] },
  "own_domains": [],
  "ignore_domains": [],
  "delivery": { "channel": "slack_dm", "integration_id": "" },
  "autonomy": {
    "hygiene": "report_and_draft_corrections",
    "nudges": "draft_only",
    "winback": "draft_only",
    "eod_notes": "approval_required"
  },
  "voice_samples": [],
  "dashboard": false,
  "schedules": {}
}
```

Finish with a summary: what runs when, where each output lands, and what will always wait for approval.
