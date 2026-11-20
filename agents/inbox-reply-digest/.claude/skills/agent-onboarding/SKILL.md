---
name: agent-onboarding
description: 'First-run setup for Inbox Reply Digest: connect the mailbox and Slack, learn the voice, set the bar, pick delivery and time, do a supervised dry run, then schedule the daily digest. Run before any other work and whenever the user asks to change setup.'
---

# Inbox Reply Digest onboarding

Run this before doing anything else when the user sends the setup request or any first message before setup is complete. Reuse anything already in `CLAUDE.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

Say in two or three sentences what you will set up: a once-a-day list of the email and Slack threads the user owes a reply to, with drafts in their voice saved in their own mailbox, silent on days with nothing. Then show the questions you are about to ask:
1. Which mailbox (Gmail or Outlook), and should Slack be included?
2. Who always counts as important, and what should always be skipped?
3. Where should the digest arrive?
4. What time, which days, which timezone?
5. How far back should open threads be carried, and how should drafts behave?

## 2. Check and choose connections

For each service call `mcp__user-input__search_connection_options` and note what is already connected.
- Mailbox: connected account `gmail` or `outlook` (the drafts must live in the user's own mailbox).
- Slack reading: connected account `slack` (acts as the user, read-only use).
- Delivery: call `mcp__chat__list_agent_integrations` first. An existing Slack app, email inbox, Telegram or iMessage integration can be reused.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where options are discrete.
1. **Mailbox**: Gmail or Outlook. If several accounts are connected, which one is work.
2. **Slack**: include DMs and @mentions (recommended), DMs only, or email only. Any channels whose mentions should be ignored (alerts, social).
3. **Important senders**: ask in plain chat for people, companies or domains that always count (key customers, the user's manager, investors). Offer to suggest a starting list from the people the user replied to most in the last 60 days.
4. **Always skip**: confirm the default skip list (newsletters, automated notifications, receipts, calendar RSVPs, internal broadcast mail) and ask for additions (a vendor, a noisy tool, an internal list).
5. **Delivery channel** (`AskUserQuestion`): DM from the agent's Slack app, email from the agent's own inbox, Telegram or iMessage, or in-app only.
6. **Time and days** (`AskUserQuestion`): 7:30, 8:00 or 9:00, or another time; weekdays only or every day. Confirm the timezone.
7. **Look-back** (`AskUserQuestion`): carry open threads for 3, 7 (default) or 14 days.
8. **Drafts** (`AskUserQuestion`): draft every item (default), only for external threads, or list only with no drafts.
9. **Autonomy**: confirm the default: read, draft and send the digest on its own; never send a reply, never touch mail beyond drafts.

## 4. Connect

- `mcp__user-input__request_connected_account` with `toolkit: "gmail"` or `"outlook"`, reason like "Allow access to Gmail to find threads waiting on your reply and save draft replies?"
- If Slack is included: `request_connected_account` with `toolkit: "slack"`, reason "Allow access to Slack to read your DMs and mentions for replies you owe?"
- For Slack delivery with no Slack agent integration yet: `mcp__chat__list_available_integration_providers`, then set it up with `mcp__chat__add_agent_integration` or hand it to the user with `mcp__user-input__request_integration_setup`. Resolve the user's Slack user ID with `mcp__chat__list_chat_users`.
- For email delivery: `add_agent_integration` with provider `platform-email` if no inbox exists.

## 5. Learn the voice

Run the `voice-profile` skill. Show the user the short profile and ask if anything is off.

## 6. Supervised dry run

Run routine 1 over the real last 7 days but **save no drafts yet**: show the digest in chat with the proposed reply text under each item. Ask: anything listed that shouldn't be, anything missing, does the voice sound right? Adjust the config (skip list, important senders, length) and run once more if needed. Then, with the user's OK, save the drafts for the current items so they can see them in their mailbox.

## 7. Schedule

- `mcp__user-input__schedule_task`, `scheduleType: "cron"`, e.g. `0 8 * * 1-5` in the user's timezone, with the self-contained prompt from CLAUDE.md "How this runs on Gamut" filled in with the real channel and destination.
- Monthly voice refresh: `0 7 1 * *`.
- Confirm with `mcp__user-input__list_scheduled_tasks` and tell the user the next run time with an absolute date.
- Create `/workspace/state/inbox-reply-digest/` with `last_run.json` set to now and an empty `ledger.json`.

## 8. Save

Append confirmed answers to `CLAUDE.md` under `## Your context` in plain sentences. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "mailbox": {"provider": "gmail", "account": "work@example.com"},
  "slack": {"enabled": true, "scope": "dms_and_mentions", "ignore_channels": ["#alerts"]},
  "important_senders": ["@keycustomer.com", "manager@example.com"],
  "skip": {"defaults": true, "extra_senders": ["noreply@vendor.example"], "extra_domains": []},
  "lookback_days": 7,
  "drafts": "all",
  "delivery": {"channel": "slack_app_dm", "integration_id": "<id>", "destination": "<slack user id>"},
  "schedule": {"cron": "0 8 * * 1-5", "timezone": "America/New_York", "task_id": "<id>"},
  "voice_refresh": {"cron": "0 7 1 * *", "task_id": "<id>"}
}
```

Finish with a three-line summary: what runs when, where it lands, and what it will never do.
