---
name: agent-onboarding
description: 'First-run setup for Reply Drafter: picks X access, collects the watch list, topics and voice examples, sets the bar, budget and delivery channel, runs one supervised shortlist, and schedules the weekday morning run.'
---

# Reply Drafter onboarding

Run this when the user sends the setup request from `PROMPT.md` or any first message while `## Your context` in `AGENTS.md` is empty. Skip any step already answered there.

## 1. Welcome

Say in two or three sentences: each weekday morning this agent finds the 3 to 5 posts on X worth the user's reply and drafts a starting reply for each in their voice; it never posts anything. Then show the plan:

1. How the agent reads X (your account, or public reads with no account).
2. Your handle, the accounts you are building relationships with, and your topics.
3. A few replies you're proud of, so drafts sound like you.
4. The bar: how many posts a morning, what to skip.
5. Where the shortlist reaches you, and when.
6. A cost estimate and per-run budget.
7. One supervised shortlist on real posts, then the schedule.

## 2. Discover connections

- Call `mcp__user-input__search_connection_options` for "X" (and for Google Docs or Notion only if the user wants the watch list in a doc). Note whether `twitter` is already connected.
- Read `/opt/gamut/docs/x.md` for the allowlisted paths and current prices.
- Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, Telegram, email inbox, or iMessage.

## 3. Ask, one question at a time

Use `AskUserQuestion` where the options are discrete.

1. **X access.** "Connect your X account (best: reads your mentions with your own rate limit, and lets the agent see which posts you already replied to), or use public reads with no account?" If an account is already connected, say it will be used and skip.
2. **Handle.** Your X handle. Look up the user ID once (`/2/users/me` with the account, or `/2/users/by/username/{username}` with built-in reads) and cache it.
3. **Watch list.** Paste the accounts you are building relationships with (start with 5 to 25). Ask whether to keep the list in config (edit by telling the agent) or in a Google Doc or Notion page they can edit.
4. **Topics.** Two or three topics, as keywords or phrases, plus any words to exclude. Ask the language.
5. **Expertise.** In a line or two: what can you answer well, and what should the agent never speak to on your behalf?
6. **Voice.** Paste three to five replies you're proud of (text or links). With the account connected, also offer to read your last 20 replies (about $0.10). Save to `/workspace/state/reply-drafter/voice.md` with short notes on length, casing, emoji, hashtags, and tone.
7. **Bar.** Max items per morning (3 / 4 / 5, default 5). Politics and hot-button topics: skip (default) or include. Prefer replies, quote posts, or let the agent choose?
8. **Delivery.** Where should the shortlist arrive? (Agent's Slack DM / Telegram / Agent's email to you / iMessage / In-app only.)
9. **Timing.** Confirm timezone and run time (default 8:00am, Monday to Friday).
10. **Budget.** Give the estimate from `AGENTS.md` (roughly $0.40 a run, about $8 a month with defaults; more watch-list accounts or topics raise it). Confirm a per-run cap (default $0.75).
11. **Autonomy.** Confirm: "The agent reads, ranks, and drafts. It never posts, replies, likes, reposts, follows, or DMs on X. You send every reply yourself."

## 4. Connect

- X account: `mcp__user-input__request_connected_account` with `toolkit: "twitter"`, reason "Allow access to X to read your mentions and recent replies for the morning shortlist?"
- Watch-list doc, if chosen: `request_connected_account` with `googledocs` or `notion`.
- Delivery: use the existing agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or hand it to the user with `mcp__user-input__request_integration_setup`). Confirm with `list_agent_integrations`, and resolve the exact destination (the user's Slack user ID, Telegram chat, or email address).

## 5. Supervised dry run

Run the weekday shortlist now, over the last 24 hours (48 for mentions), following the `reply-bar` skill. Show it in chat, not on the delivery channel, along with the cost of the run and what was dropped and why (a short list). Ask:
- Did any item not deserve your time? Did something obvious get missed?
- Which draft sounded least like you, and how would you change it?

Adjust the watch list, topics, bar, and `voice.md`, and redo the drafts once. Do not seed `shortlisted.json` with posts the user rejected as off-target; do seed it with the ones shown, so they don't reappear tomorrow. Save the `since_id` values to `runs.json`.

## 6. Schedule

Create the run with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, default `0 8 * * 1-5` in the user's timezone, with a self-contained prompt:

> Run the Reply Drafter weekday shortlist. Config: `/workspace/.claude/skills/agent-onboarding/config.json`. State: `/workspace/state/reply-drafter/` (`runs.json`, `shortlisted.json`, `users.json`, `voice.md`). Follow the `reply-bar` skill and `AGENTS.md`. Read X via `<connected account twitter | built-in public reads>`, only paths in `/opt/gamut/docs/x.md`, using `since_id` from `runs.json`, and stop at the $`<cap>` per-run budget. Shortlist at most `<N>` posts that clear the bar, with a one-line reason and a draft in the user's voice. Deliver one message via `send_chat_message` on integration `<id>` to `<destination>`. If nothing clears the bar, send nothing. Never post, reply, like, repost, follow, or DM on X. Update `runs.json` and `shortlisted.json`. If a source fails, say which in the footer.

Confirm with `mcp__user-input__list_scheduled_tasks` and show the user the entry.

## 7. Save

Write short bullets under `## Your context` in `AGENTS.md`. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "run_cron": "0 8 * * 1-5",
  "schedule_task_id": "",
  "x": {
    "access": "connected_account",
    "handle": "examplehandle",
    "user_id": "",
    "language": "en"
  },
  "watch_list": {
    "location": "config",
    "doc_url": "",
    "accounts": ["examplefounder", "exampleinvestor"]
  },
  "topics": [
    {"query": "\"customer onboarding\" OR \"activation rate\"", "exclude": ["hiring", "giveaway"]}
  ],
  "expertise": "B2B SaaS onboarding and pricing",
  "never_speak_to": ["company financials"],
  "bar": {
    "max_items": 5,
    "max_age_hours": 48,
    "topic_max_age_hours": 24,
    "politics_opt_in": false,
    "format_preference": "agent_choice"
  },
  "budget_usd_per_run": 0.75,
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "autonomy": {"never_act_on_x": true}
}
```

Finish with a short summary: when the shortlist runs, where it arrives, the expected cost, and that the agent never posts.
