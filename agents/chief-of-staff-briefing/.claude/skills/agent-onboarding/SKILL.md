---
name: agent-onboarding
description: 'First-run setup for Chief of Staff Briefing: connect Gmail, Calendar, Slack, Discord and project tools, capture people tiers, projects, channels and urgency rules, run a supervised briefing, then schedule the briefing and the optional fire watch and end-of-day pass. Run before any other work and whenever the user asks to change setup.'
---

# Chief of Staff Briefing onboarding

Run this before anything else when the user sends the setup request or any first message before setup is complete. Reuse what is already in `AGENTS.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

In two or three sentences say what you will set up: an early-morning briefing across their mail, calendar, Slack, Discord and project tools, with fires first, then what is waiting on them, today's meetings, commitments and project movement; plus an optional hourly fire watch and an optional end-of-day pass. Then list the questions you will ask:
1. Which tools to read.
2. Who matters most (people tiers).
3. Which projects and channels to watch.
4. What counts as a fire (urgency rules).
5. When it runs, where it arrives, and what it may do on its own.

## 2. Check connections

For each service call `mcp__user-input__search_connection_options` and note what is already connected.
- Gmail or Outlook: connected account `gmail` or `outlook`.
- Calendar: connected account `googlecalendar` (or `outlook`).
- Slack reading: connected account `slack`.
- Discord: follow what the search offers. Prefer the agent's own Discord app in the user's server (agent integration) if available, since it can read the channels it is invited to; use a `discord` connected account only if it can read those channels. If neither works, tell the user Discord will be skipped.
- Project tools: `linear`, `github`, `jira`, `asana`, `notion`, `clickup` as connected accounts.
- Delivery: call `mcp__chat__list_agent_integrations` first and reuse what exists.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.
1. **Sources** (`AskUserQuestion`, multi-select): Gmail, Google Calendar, Slack, Discord, a project tool, meeting notes.
2. **People tiers**: in plain chat, ask for tier 1 (co-founders, board, lead investors, top customers, direct reports) and tier 2 (team, partners, active candidates), by name, email or domain. Offer to propose a draft from who the user emails and DMs most.
3. **Projects**: which projects to track, and where each lives (a Linear project, a Slack channel, a label, a keyword).
4. **Channels**: Slack channels and Discord servers or channels worth reading; channels to ignore.
5. **Urgency rules**: in plain chat. Offer starters for a SaaS company: outage or downtime, payment or payroll failure, a top customer threatening to cancel, refund or chargeback spikes, security or legal notices, press inquiries, a launch at risk. For each, ask whether it is always a fire and whether it may alert outside working hours.
6. **Skip list**: confirm defaults (newsletters, promotions, receipts, notifications, CC-only) and add senders or tools.
7. **Time** (`AskUserQuestion`): 5:00 (default), 6:00, 7:00 or another; every day, weekdays only, or weekdays plus a light weekend version. Confirm the timezone.
8. **Fire watch** (`AskUserQuestion`): off (default), hourly during working hours, or real-time where a trigger exists. Quiet hours.
9. **End-of-day pass** (`AskUserQuestion`): off, or on at 17:30 (or another time) on workdays. If the Open Loops agent is installed with its own sweep, recommend off.
10. **Delivery** (`AskUserQuestion`): the dedicated chat in the app (default), a DM from the agent's Slack app, an email from the agent's inbox, Telegram or iMessage.
11. **Autonomy** (`AskUserQuestion`): brief only (default), or brief plus reply drafts saved in the user's mailbox for fires and tier-1 asks. Confirm that sending, calendar changes and any external action always need approval.

## 4. Connect

- `mcp__user-input__request_connected_account` with `toolkit: "gmail"`, reason "Allow access to Gmail to find fires, decisions and commitments for the morning briefing?"
- `toolkit: "googlecalendar"`, reason "Allow access to Google Calendar to list today's meetings in the briefing?"
- `toolkit: "slack"`, reason "Allow access to Slack to read your DMs, mentions and watched channels for the briefing?"
- Discord per step 2; project tools with `request_connected_account`; notes with `mcp__user-input__request_remote_mcp`.
- Slack or email delivery: `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`; resolve the destination with `mcp__chat__list_chat_users`.

## 5. Supervised dry run

Run the morning briefing on real data with `last_brief_at` set to 24 hours ago (72 on a Monday). Show it in chat; do not deliver it yet. Ask: is anything a fire that isn't, or missing that is? Are tiers and projects right? Is it short enough? Adjust tiers, rules, channels and caps, and run again if the user wants. If the end-of-day pass is on, run it once too and confirm it stays silent when empty. Then send one test to the chosen channel.

## 6. Schedule

- Morning briefing: `mcp__user-input__schedule_task`, `scheduleType: "cron"`, e.g. `0 5 * * *`, with the self-contained prompt from `AGENTS.md` filled in with the real destination.
- Fire watch, if on: `mcp__user-input__get_available_triggers` on the Gmail and Slack accounts; use `mcp__user-input__setup_trigger` if a fitting new-message trigger exists, else `schedule_task` with `0 9-18 * * 1-5`.
- End-of-day pass, if on: `schedule_task` with `30 17 * * 1-5` and the "send nothing if empty" rule in its prompt.
- Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`; tell the user each next run as an absolute date and time.
- Create `/workspace/state/chief-of-staff-briefing/` with `runs.json` (now) and empty `ledger.json` and `fires.json`.

## 7. Save context and config

Append the confirmed answers to `AGENTS.md` under `## Your context` in plain sentences. Write `/workspace/.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/Los_Angeles",
  "schedules": {"morning": "0 5 * * *", "fire_watch": null, "end_of_day": null, "quiet_hours": ["21:00", "07:00"]},
  "sources": {
    "gmail": true, "calendar": "googlecalendar",
    "slack": {"dms": true, "mentions": true, "channels": [], "ignore": []},
    "discord": {"mode": "agent-integration | connected-account | off", "channels": []},
    "projects_tool": null, "notes": null
  },
  "people": {"tier1": [], "tier2": []},
  "projects": [{"name": "Billing migration", "where": "linear:project-id or #channel or keyword"}],
  "urgency_rules": [{"name": "Outage", "match": {"keywords": ["outage", "down"], "channels": [], "senders": []}, "always_fire": true, "wake_me": false}],
  "skip": {"senders": [], "domains": [], "rules": ["newsletters", "promotions", "receipts", "notifications", "cc-only"]},
  "delivery": {"channel": "in-app | slack | email | telegram | imessage", "destination": "resolved id or address"},
  "drafts_enabled": false,
  "caps": {"fires": 3, "waiting": 5, "replies": 5}
}
```

Finish with a summary: what runs when, where it lands, what it will never do without approval, and how to change things ("add #support to watched channels", "turn on the end-of-day pass").
