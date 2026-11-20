---
name: agent-onboarding
description: 'First-run setup for Important Email Triage: connect the mailbox, learn the user''s categories and important senders, choose the default or investor preset, pick delivery, dry-run read-only, then set up the new-mail trigger or a 30-minute sweep. Run before any other work and whenever the user asks to change setup.'
---

# Important Email Triage onboarding

Run this before anything else when the user sends the setup request or any first message before setup is complete. Reuse what is already in `CLAUDE.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

Explain in two sentences: the agent will label mail that's genuinely waiting on the user, in their own categories, and only message them when something new lands. It never sends, drafts or archives. Show the planned questions:
1. Gmail or Outlook?
2. Who always counts as important?
3. Your own categories, or the investor preset?
4. Where should updates go, and how often?
5. Anything else to always skip?

## 2. Check connections

Call `mcp__user-input__search_connection_options` for Gmail or Outlook, and `mcp__chat__list_agent_integrations` for delivery channels already set up.

## 3. Ask, one at a time

1. **Mailbox** (`AskUserQuestion`): Gmail or Outlook; which account if several.
2. **Important senders**: plain chat. Offer a suggested list from the people the user replied to most in the last 60 days.
3. **Mode** (`AskUserQuestion`): learned categories (default), investor preset (Today's Focus / Action Required / Scheduling / Delegated), or waiting label only.
4. **Delivery** (`AskUserQuestion`): DM from the agent's Slack app, email from the agent's own inbox, Telegram or iMessage, in-app only, or labels only with no messages.
5. **Hours** (`AskUserQuestion`): around the clock, or working hours only (default 7:00 to 19:00 weekdays). Confirm the timezone.
6. **Extra skips**: senders, domains or tools to always ignore.
7. **Autonomy**: confirm labels only; nothing is sent, drafted, archived or deleted.

## 4. Connect

- `mcp__user-input__request_connected_account` with `toolkit: "gmail"` or `"outlook"`, reason like "Allow access to Gmail to label the messages waiting on your reply?"
- Delivery integration if chosen and missing: `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`; resolve the destination with `mcp__chat__list_chat_users` or `list_chat_channels`. Email: provider `platform-email`.

## 5. Learn categories

Follow "Learned categories" in the `triage-labels` skill (skip in investor or waiting-only mode). Get approval for each name.

## 6. Supervised dry run (read-only)

Run routine 1 on the last 48 hours **without applying labels**. Show: what would be labeled waiting (newest first, with what each person asks), the category assignments, what was left alone as ambiguous, and what was skipped as noise (counts plus a few examples). Ask what's wrong; adjust important senders, skips and categories. With the user's OK, apply the labels for real.

## 7. Trigger or schedule

1. `mcp__user-input__get_available_triggers` for the mailbox account. If a new-message trigger exists, `mcp__user-input__setup_trigger` with the self-contained prompt from CLAUDE.md, then add a safety sweep `0 */2 * * *` with `schedule_task`.
2. Otherwise `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `*/30 * * * *` or `*/30 7-19 * * 1-5`, with the self-contained sweep prompt.
3. Verify with `mcp__user-input__list_triggers` and `mcp__user-input__list_scheduled_tasks`. Create `/workspace/state/important-email-triage/ledger.json` with `last_sweep` set to now.

## 8. Save

Append confirmed answers to `CLAUDE.md` under `## Your context`. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "mailbox": {"provider": "gmail", "account": "work@example.com"},
  "mode": "learned",
  "categories": [{"label": "Triage/Clients", "examples": ["@client.example"]}],
  "waiting_label": "Triage/Waiting on me",
  "important_senders": ["@keycustomer.example", "manager@example.com"],
  "extra_skip": ["@vendor.example"],
  "delivery": {"channel": "slack_app_dm", "integration_id": "<id>", "destination": "<slack user id>", "batch_minutes": 15},
  "hours": {"cron": "*/30 7-19 * * 1-5", "timezone": "Europe/London"},
  "trigger_id": "<id or null>",
  "task_ids": ["<id>"]
}
```

End with a short summary: how it watches (trigger or sweep), what the labels are, where updates go, and that it never sends, drafts or archives.
