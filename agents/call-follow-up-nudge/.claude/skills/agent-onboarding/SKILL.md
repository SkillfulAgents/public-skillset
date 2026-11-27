---
name: agent-onboarding
description: 'First-run setup for Call Follow-Up Nudge: connects calendar, mailbox, and meeting notes, sets the skip list, delivery channel and voice, runs a shadow day on real calls, then creates the transcript trigger or hourly sweep.'
---

# Call Follow-Up Nudge onboarding

## 1. Welcome

Tell the user in two or three sentences: after each call this agent lists what they personally committed to, drafts the follow-ups they promised in their own mailbox, and sends them one short message. Nothing is ever sent as them. Then show the plan:

1. Which calendar and mailbox to use.
2. Where your call notes or transcripts come from.
3. Which calls to skip.
4. Where the post-call message should reach you, and whether to stay silent after calls with nothing owed.
5. How your follow-ups should sound.
6. Whether to hand open items to Open Loops.
7. A shadow day on your real calls before anything is scheduled.

Skip any step already answered in `## Your context` in `AGENTS.md`.

## 2. Discover connections

For Google Calendar, Gmail, Outlook, Slack, and the user's notes tool, call `mcp__user-input__search_connection_options` with the service name. Note what is already connected and the exact slug. Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram, or iMessage. Call `mcp__agents__list_agents` to see whether Open Loops, Call Follow-Up Drafter, or Meeting Actions is installed.

Mechanism rules:
- Calendar, mailbox, and Slack reading: the user's connected account.
- Notes: Granola, Fireflies, Otter through remote MCP (`granola`, `fireflies-ai`, `otter-ai`); Fathom, Gong, Zoom through connected accounts (`fathom`, `gong`, `zoom`); or the agent joining calls in `listen` mode.
- Post-call message: an agent integration, or in-app only.

## 3. Ask, one question at a time

Use `AskUserQuestion` where options are discrete.

1. **Calendar and mailbox.** Google (Calendar + Gmail) or Microsoft (Outlook)? Which account if several are connected? What are your own company email domains?
2. **Notes source.** Where do transcripts come from? (Granola / Fathom / Fireflies / Otter / Gong / Zoom recordings / I'll invite the agent to calls.)
3. **Which calls.** All calls with notes, or only calls with someone outside your domains? Anything to always skip (standups, 1:1s, interviews, personal)?
4. **Timing.** Confirm timezone and working hours. Default: process each call about 30 minutes after it ends, with an hourly sweep 9am to 6pm on weekdays as the safety net.
5. **Delivery.** Where should the post-call message reach you? (The agent's Slack DM / The agent's email to you / Telegram / iMessage / In-app only.)
6. **Silence.** After a call with nothing owed: send nothing, or a one-line "nothing owed"?
7. **Slack follow-ups.** Should the agent read your Slack to address promised Slack messages to the right person and check whether you sent them? (Yes / No.)
8. **Voice.** May the agent read your last 30 sent emails to learn your tone? Paste one follow-up you were happy with, and any phrases you never use.
9. **Edge cases.** Should "I'll think about it" or "let me see what I can do" count as yours, go to Maybe, or be ignored?
10. **Hand-off.** If Open Loops is installed: hand your open items to it after each call? (Yes / No.) If not: turn on the daily 8am open-commitments check? (Yes / No.)
11. **Autonomy.** Confirm: "The agent captures, drafts, and messages you on its own. Email follow-ups wait in your drafts; Slack follow-ups arrive as text for you to send. Nothing goes to anyone else."

## 4. Connect

- `mcp__user-input__request_connected_account` for `googlecalendar` and `gmail`, or `outlook`; `slack` if chosen. Example reason: "Allow access to Gmail to save follow-up drafts in the right threads after your calls?"
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies, or Otter with the URL from `search_connection_options`; `request_connected_account` for `fathom`, `gong`, or `zoom`.
- Delivery: use the existing agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or `mcp__user-input__request_integration_setup` to hand it to the user). Confirm with `list_agent_integrations`.

## 5. Shadow day (supervised dry run)

Run routine 2 from `AGENTS.md` on the most recent day with recorded calls. Follow the `commitment-capture` skill. Show in this session, per call: YOU OWE, CIRCLE BACK, THEY OWE YOU, MAYBE, and the draft texts. Save no drafts yet.

Ask: what did I miss, what did I wrongly count as yours, do the drafts sound like you? Apply the corrections, rerun one call, and once the user approves, save the approved drafts to their mailbox. Seed `processed-meetings.json` with the shadow-day meetings so they are not processed again.

## 6. Schedule and trigger

- Fathom, Zoom, or Gong: `mcp__user-input__get_available_triggers` on that account; if a recording- or transcript-ready event exists, `mcp__user-input__setup_trigger` with a self-contained prompt.
- Always add the hourly safety-net sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `0 9-18 * * 1-5` in the user's timezone (the only path for Granola, Fireflies, and Otter).
- If chosen, the daily check at `0 8 * * 1-5`.

Prompt template:

> Run Call Follow-Up Nudge **routine 1, post-call commitment capture**. Read `AGENTS.md` and `/workspace/.claude/skills/agent-onboarding/config.json`. Follow the `commitment-capture` skill. State: `/workspace/state/call-follow-up-nudge/`. Process only calls that ended at least 20 minutes ago and are not in `processed-meetings.json`. Save email follow-ups as drafts in the user's mailbox in the right thread; never send; never post to Slack as the user. Deliver one message per call with `send_chat_message` on integration `<id>` to `<destination>`. If a call has nothing owed, follow the silence setting. If a source fails, say which one.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`, and show the user the list.

## 7. Save

Write the confirmed answers under `## Your context` in `AGENTS.md` as short bullets, including the classification corrections from the shadow day. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "workday": {"start": "09:00", "end": "18:00", "days": [1, 2, 3, 4, 5]},
  "calendar": {"provider": "googlecalendar", "account": "user@example.com"},
  "mail": {"provider": "gmail", "account": "user@example.com"},
  "own_domains": ["example.com"],
  "notes_source": {"type": "granola", "via": "mcp", "trigger_id": null},
  "scope": {"external_only": true, "skip_title_keywords": ["standup", "1:1", "focus"]},
  "delay_minutes": 30,
  "schedules": {"sweep_cron": "0 9-18 * * 1-5", "daily_check": {"on": false, "cron": "0 8 * * 1-5"}},
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "silence": "nothing",
  "slack_read": false,
  "voice": {"learn_from_sent": true, "sample": "", "avoid_phrases": []},
  "edge_cases": {"ill_think_about_it": "maybe"},
  "handoff": {"open_loops": false, "slug": "open-loops"},
  "autonomy": {"drafts_only": true}
}
```

Finish with a short summary: what runs when, where the post-call message lands, and that every follow-up waits for the user.
