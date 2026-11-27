---
name: agent-onboarding
description: 'First-run setup for Daily Briefing: connect mail, calendar and Slack, set the time, workdays, delivery channel and what counts as important, run a supervised brief on real data, then schedule it. Run before any other work and whenever the user asks to change setup.'
---

# Daily Briefing onboarding

Run this before anything else when the user sends the setup request or any first message before setup is complete. Reuse what is already in `AGENTS.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

In two or three sentences say what you will set up: a two-minute brief every workday morning on what needs the user, from mail, Slack, the calendar and open loops, ranked by consequence, and silent about anything already handled. Then list the questions you are about to ask:
1. Which mail, calendar and chat tools to read.
2. Who and what always matters, and what to skip.
3. What time, which days and which timezone.
4. Where the brief should arrive, and whether you want an audio version.
5. What to do on a quiet day.

## 2. Check connections

For each candidate service call `mcp__user-input__search_connection_options` and note what is already connected.
- Mail: connected account `gmail` or `outlook`.
- Calendar: connected account `googlecalendar`, or `outlook` for Outlook calendars.
- Slack reading: connected account `slack` (acts as the user; read-only use).
- Optional: a task tracker (`todoist`, `asana`, `linear`, `notion`, `clickup`, `trello`, `jira`) as a connected account; meeting notes (`granola`, `fireflies-ai`, `otter-ai`) as a remote MCP.
- Delivery: call `mcp__chat__list_agent_integrations` first; reuse an existing Slack app, email inbox, Telegram or iMessage integration.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where the options are discrete.
1. **Sources** (`AskUserQuestion`, multi-select): Gmail or Outlook, Google or Outlook calendar, Slack, a task tracker, meeting notes. Mail and calendar are required.
2. **Slack scope**: DMs and @mentions (default), plus which channels, if any, matter enough to read. Channels to ignore (alerts, social).
3. **Important people and topics**: ask in plain chat for people, companies or domains that always matter (manager, key customers, investors) and topics that are always urgent. Offer a starting list built from the people the user replied to most in the last 60 days.
4. **Always skip**: confirm the default (newsletters, promotions, receipts, automated notifications, mail where the user is only copied) and ask for additions.
5. **Time and workdays** (`AskUserQuestion`): 6:30, 7:00, 7:30 or 8:00, or another time; Monday to Friday or Sunday to Thursday. Confirm the timezone. Ask for any company holidays to skip.
6. **Delivery** (`AskUserQuestion`): in-app, a DM from the agent's Slack app, an email from the agent's own inbox, Telegram or iMessage.
7. **Audio** (`AskUserQuestion`): text only, or text plus audio. If audio, read `/opt/gamut/docs/audio.md`, give an estimated monthly cost from the metering rate (about 2,000 characters a day times the number of workdays), let the user pick a voice, and get an OK.
8. **Quiet days** (`AskUserQuestion`): send the one-line quiet message (default) or send nothing.
9. **Autonomy**: confirm the default: read and send the brief on its own; never reply, respond to invites or change anything.

## 4. Connect

- `mcp__user-input__request_connected_account` with `toolkit: "gmail"`, reason "Allow access to Gmail to find what needs you in each morning brief?"
- `toolkit: "googlecalendar"`, reason "Allow access to Google Calendar to list today's meetings and conflicts in the brief?"
- If Slack: `toolkit: "slack"`, reason "Allow access to Slack to read your DMs and mentions for the morning brief?"
- Optional tracker or notes the same way (`request_connected_account` or `mcp__user-input__request_remote_mcp`).
- Slack delivery with no Slack integration yet: `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration`, or hand it to the user with `mcp__user-input__request_integration_setup`. Resolve the user's Slack user with `mcp__chat__list_chat_users`.
- Email delivery: `add_agent_integration` with provider `platform-email` if the agent has no inbox; ask for the address to send to.

## 5. Supervised dry run

Run routine 1 on real data, with `last_brief_at` set to 24 hours ago (72 hours on a Monday). Show the brief in chat and do not send it to the delivery channel yet. Ask: is anything here that shouldn't be, is anything missing, is the order right, is it short enough? Adjust the important list, skip list and Slack scope, and run once more if the user wants. Then send one test to the chosen channel (and the audio file, if on) and confirm it arrived.

## 6. Schedule

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, e.g. `0 7 * * 1-5` in the user's timezone, with the self-contained prompt from `AGENTS.md` "How this runs on Gamut" filled in with the real channel and destination.
- Confirm with `mcp__user-input__list_scheduled_tasks` and tell the user the next run as an absolute date and time.
- Create `/workspace/state/daily-briefing/` with `runs.json` (`last_brief_at` = now) and an empty `ledger.json`.

## 7. Save context and config

Append the confirmed answers to `AGENTS.md` under `## Your context` in plain sentences. Write `/workspace/.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "schedule": {"cron": "0 7 * * 1-5", "holidays": ["2026-12-25"]},
  "sources": {
    "mail": {"toolkit": "gmail", "account": "work address"},
    "calendar": {"toolkit": "googlecalendar", "calendar_ids": ["primary"]},
    "slack": {"enabled": true, "dms": true, "mentions": true, "channels": [], "ignore_channels": []},
    "tasks": null,
    "notes": null
  },
  "important": {"people": [], "domains": [], "topics": []},
  "skip": {"senders": [], "domains": [], "rules": ["newsletters", "promotions", "receipts", "notifications", "cc-only"]},
  "delivery": {"channel": "in-app | slack | email | telegram | imessage", "destination": "resolved id or address"},
  "audio": {"enabled": false, "voice": "marin"},
  "quiet_day": "one-line | silent",
  "max_top_items": 5
}
```

Finish with a short summary: what runs when, where it arrives, and how to dismiss, snooze or change anything ("drop 2", "move my brief to 7:30").
