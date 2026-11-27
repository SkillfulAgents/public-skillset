---
name: agent-onboarding
description: 'First-run setup for Inbox Manager: connects the mailbox, learns the user''s categories and voice from real mail, sets autonomy, runs a supervised sort, and creates the new-mail trigger and schedules.'
first_prompt: 'Set up Inbox Manager for me'
---

# Agent Onboarding

You are setting up Inbox Manager: an agent that sorts the user's mail as it arrives, labels it in their own words, archives noise, pre-drafts replies for threads that clearly need them, and points out patterns. It never sends mail.

Set this up the way the user actually works. Do not impose a generic folder scheme. Learn from their real mail and confirm with them.

## 1. Welcome

Say in two or three sentences what you will set up, then show the plan:

1. Connect your mailbox (and optionally your calendar).
2. I read your recent mail and propose categories in your words.
3. We agree what counts as noise and what must never be touched.
4. I learn your writing voice from your sent mail.
5. We pick how much I do on my own, and where I report to you.
6. A dry run on your real inbox, nothing changed until you approve.
7. I switch on the live sorting and the weekly report.

Tell them this takes about 15 minutes, and they can stop and resume anytime.

## 2. Pick the mechanisms

For each service, call `mcp__user-input__search_connection_options` and check `CONNECTED_ACCOUNTS` and `mcp__chat__list_agent_integrations` before requesting anything.

- **Mailbox.** Ask with `AskUserQuestion`: Gmail, Outlook, or both. Gmail is the primary path with bundled scripts. For Outlook, explain that the work runs through direct Microsoft Graph calls without bundled scripts, so the first week is preview mode. Ask whether they have more than one account to manage. Request each with `mcp__user-input__request_connected_account` (`gmail` or `outlook`) and a plain reason ("so I can label, archive, and leave drafts in your mailbox; I will never send"). Test access by listing labels and the last 10 messages.
- **Calendar** (optional). Offer `googlecalendar` so scheduling drafts can name real free times.
- **Where reports go.** Ask with `AskUserQuestion`: in-app only, a Slack DM from the agent's own Slack app, an email from the agent's own inbox, or Telegram or iMessage. Set up the chosen agent integration with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or hand it to the user with `mcp__user-input__request_integration_setup` when the provider says so. Send a short test message with `mcp__chat__send_chat_message`.

## 3. Learn the inbox (one question at a time)

Before asking, do the homework so the questions are concrete:
- List the user's existing labels and filters.
- Run the `gmail-inbox-screener` skill for the last 72 hours, then pull a sample of 200 to 300 threads from the last 60 to 90 days through the proxy.
- Group senders by domain and frequency, and note which ones the user opens, replies to, or leaves unread.

Then ask, one at a time:

1. **Preset.** `AskUserQuestion`: "Learn my categories from my mail" (default) or "Investor preset (Today's Focus / Action Required / Scheduling / Delegated)". If they choose the investor preset, ask also about LP and fund-admin senders, portfolio company domains, and whether they want reply drafts (off by default). Mention the VC Associate template if they want deal logging too.
2. **Categories.** Show 4 to 8 proposed categories, named in their language, each with three example senders from their mail, and say which existing labels you would reuse. Ask them to rename, merge, drop, or add. For each category, ask: label only, or label and archive?
3. **Always matters.** Show the people and domains you think always matter (frequent two-way correspondents, family, key clients, boss). Ask what to add or remove.
4. **Noise.** Show the top recurring senders they never open. Ask which go on the skip list and whether noise should get a label (for example "Low priority") before archiving.
5. **Never touch.** Confirm the never-archive list (banks, tax, school, medical, legal, contracts and invoices, calendar invites, security codes) and ask what to add.
6. **Read state.** `AskUserQuestion`: never mark as read (default), mark archived noise as read, or mark all archived mail as read.
7. **Drafts.** `AskUserQuestion`: draft replies for threads that clearly need me (default), only for a list of people, or never. Ask what should never get a draft (manager, board, legal, family).
8. **Voice.** Read 30 to 50 recent sent replies. Summarize their voice in three or four bullets (greeting, sign-off, length, tone, phrases they use) and ask if it sounds right. Ask for one example they consider typical if the sample is thin.
9. **Urgent alerts.** Ask if any sender or keyword should ping them immediately.
10. **Cadence and timezone.** Confirm timezone and waking hours, whether they want a daily summary (and when), and the weekly patterns report day and time (default Friday 16:00).
11. **Autonomy.** Confirm the default: "I label and archive on my own within these rules, leave ambiguous mail alone, write drafts, and never send. Unsubscribes need your yes per sender." Offer a preview week instead, where every action is listed before it is applied.

## 4. Supervised dry run

Run routine 1 on the last 48 hours of mail without changing anything. Show a table: thread, sender, proposed label, archive yes or no, draft yes or no, reason. Then show two sample drafts.

Ask what is wrong. Fix the rules, rerun once on the same mail, and show what changed. When the user approves, apply the labels and archives from the dry run, and save the drafts.

Offer an unsubscribe pass: list the top 10 commercial senders they never open, and unsubscribe only from the ones they approve, using the `gmail-unsubscribe` skill.

## 5. Switch it on

1. Call `mcp__user-input__get_available_triggers` on each mailbox account and pick the new-message trigger. Do not guess slugs. Create it with `mcp__user-input__setup_trigger` and the self-contained prompt from `AGENTS.md` ("Triggers and schedule"), filled in with the account.
2. If no trigger exists, create a sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `*/15 <waking hours> * * *`, using the same prompt.
3. Create the daily catch-up sweep, the weekly patterns report, and the daily summary if enabled, each with a self-contained prompt that names the config path, state path, destination channel and integration ID, and the "send nothing if nothing to say" rule.
4. Verify with `mcp__user-input__list_triggers` and `mcp__user-input__list_scheduled_tasks`, and show the user what will run when.
5. Initialize `/workspace/state/inbox-manager/` with the current history ID per account.

## 6. Save

Write a readable summary into `AGENTS.md` under `## Your context` (categories, lists, voice notes, autonomy, channels, schedule, timezone). Save machine-readable config to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "accounts": [{"provider": "gmail", "address": "", "account_id": ""}],
  "preset": "learned",
  "timezone": "",
  "waking_hours": "07-22",
  "categories": [
    {"label": "", "match": {"senders": [], "domains": [], "keywords": []}, "archive": false, "mark_read": false}
  ],
  "always_matters": {"senders": [], "domains": []},
  "skip_list": {"senders": [], "domains": [], "patterns": []},
  "noise_label": "",
  "never_archive": ["security codes", "calendar invites", "contracts", "invoices", "banks", "tax", "school", "medical", "legal"],
  "mark_read": "never",
  "drafts": {"mode": "clearly_needs_reply", "never_draft": []},
  "voice_notes": [],
  "urgent_alert": {"senders": [], "keywords": []},
  "investor_preset": {"lp_domains": [], "portfolio_domains": [], "candidate_label": "", "drafts": false},
  "delivery": {"channel": "in-app", "integration_id": "", "destination": ""},
  "schedule": {"trigger": "", "sweep_cron": "", "catchup_cron": "0 22 * * *", "summary_cron": "", "patterns_cron": "0 16 * * 5"},
  "autonomy": "label_archive_draft_never_send",
  "preview_mode_until": ""
}
```

Close with a short summary: what runs on each new email, what runs daily and weekly, where reports go, and how to change anything ("tell me, or ask me to run the `agent-onboarding` skill again").

## Ongoing feedback

When the user says a message was misfiled, fix the rule, say what changed, and update `config.json` and `## Your context`. If they say "stop doing X", remove the rule rather than stacking a new one on top.
