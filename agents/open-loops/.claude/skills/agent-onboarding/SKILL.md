---
name: agent-onboarding
description: 'First-run setup for Open Loops: connects mail, calendar, Slack, and meeting notes, picks which routines run and when, sets the nudge and delivery rules, runs a supervised sweep, and schedules everything.'
first_prompt: 'Set up Open Loops for me'
---

# Open Loops onboarding

## 1. Welcome

Tell the user in three or four sentences: this agent keeps one ledger of what they promised and what they handed off, closes loops only on evidence, and drafts nudges they approve. Then show the plan:

1. Which email and calendar to read.
2. Whether to read Slack and which meeting-notes tool you use.
3. Which routines to turn on (end-of-day sweep, weekly promise sweep, delegation chaser, principal mode).
4. Who matters most (VIPs and clients).
5. Where digests should reach you.
6. What the agent may do alone.
7. A supervised first sweep on your real data.

Skip any step already answered in `## Your context` in `AGENTS.md`.

## 2. Discover connections

For each of Gmail, Outlook, Google Calendar, Slack, and the meeting-notes tool, call `mcp__user-input__search_connection_options` with the service name. Note what is already connected and the exact slug. Also call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram, or iMessage for delivery.

Mechanism rules:
- Mail, calendar, and Slack reading: the user's connected account (it must see the user's own sent mail and DMs).
- Meeting notes: Granola, Fireflies, and Otter through their remote MCP (`granola`, `fireflies-ai`, `otter-ai`); Fathom, Gong, and Zoom through connected accounts (`fathom`, `gong`, `zoom`).
- Digest delivery: an agent integration, or in-app only.

## 3. Ask, one question at a time

Use `AskUserQuestion` where the options are discrete.

1. **Mailbox.** Gmail or Outlook? Which address, if several are connected?
2. **Slack.** Should the agent read your Slack DMs, mentions, and your own messages? (Yes / No.) If yes, any channels to ignore?
3. **Meetings.** Where do your meeting notes or transcripts live? (Granola / Fathom / Fireflies / Otter / Gong / Zoom recordings / I'll invite the agent to calls / None.) If Meeting Actions is installed in this workspace, ask whether it should hand items in instead.
4. **Routines.** Which to turn on? (End-of-day can't-miss sweep / Weekly promise sweep / Delegation chaser / Principal mode.) Default: the first three.
5. **Timing.** Confirm your timezone and workday end. Offer the defaults: EOD sweep 4:30pm weekdays, promise sweep Friday 3pm, delegation chaser Monday 8am with a light 1pm intake.
6. **People who matter.** Paste or name your VIPs (board, investors, key customers, your manager) and your client list with their email domains. These drive ranking and per-client grouping.
7. **Uncertain items.** When the agent isn't sure something is a real commitment: show it in a short "Maybe" section, or drop it? (Principal mode always keeps them.)
8. **Principal mode only.** Who is the principal? Do you have delegated access to their mailbox or calendar? Which of their meetings should be read?
9. **Nudge rules.** Confirm the defaults: first nudge one business day after the due date, or after five business days of silence; at most two nudges, then ask you. Any people never to nudge?
10. **Delivery.** Where should digests reach you? (Agent's Slack DM / Agent's email to you / Telegram / iMessage / In-app only.)
11. **Autonomy.** Confirm: "The agent reads, tracks, and drafts on its own. Every nudge waits in your drafts. Nothing is ever sent as you." Offer only one variation: whether post-call "you're on the hook for" messages should be sent immediately or folded into the next digest.

## 4. Connect

- `mcp__user-input__request_connected_account` with `gmail` or `outlook`, `googlecalendar`, and `slack` if chosen. Reason text such as "Allow access to Gmail to find promises in your sent mail and save nudge drafts?"
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies, or Otter, using the URL from `search_connection_options`.
- For delivery, use the configured agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or hand it over with `mcp__user-input__request_integration_setup`). Confirm with `list_agent_integrations`.

## 5. Supervised dry run

Run the weekly promise sweep and the delegation chaser over the last 14 days of real data. Show the user:
- the open loops by person or client, with the source link for each,
- the "Maybe" items, if any,
- which loops you closed and the evidence for each,
- one or two sample nudge drafts (save them to drafts only after the user approves the wording).

Ask what was wrong: missed promises, false positives, tone of the nudges. Adjust the classification notes in `## Your context` and run once more on the corrected set. Seed `/workspace/state/open-loops/ledger.json` with the confirmed loops.

## 6. Schedule

For each routine turned on, call `mcp__user-input__schedule_task` with `scheduleType: "cron"` and a self-contained prompt. Template:

> Run the Open Loops **weekly promise sweep**. Config: `/workspace/.claude/skills/agent-onboarding/config.json`. Ledger: `/workspace/state/open-loops/ledger.json`. Follow the `commitment-ledger` skill and the routine in `AGENTS.md`. Window: since `runs.json` last_run for this routine. Deliver via `send_chat_message` on integration `<id>` to `<destination>`. If nothing is open, send nothing. Never send email as the user; nudges are saved as drafts only. Update `runs.json` when done. If a source fails, say which one in the digest.

If post-call intake is on and Meeting Actions is not handing items in, check `mcp__user-input__get_available_triggers` on the Fathom, Zoom, or Gong account and use `setup_trigger` for a transcript-ready event. Otherwise schedule an hourly workday sweep (`0 9-18 * * 1-5`) that skips meetings in `processed-meetings.json`.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`, and show the user the list.

## 7. Save

Write the confirmed answers under `## Your context` in `AGENTS.md` as short bullets. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "workday_end": "17:30",
  "mail": {"provider": "gmail", "account": "user@example.com"},
  "calendar": {"provider": "googlecalendar"},
  "slack": {"read": true, "ignore_channels": []},
  "meeting_source": {"type": "granola", "via": "mcp", "handoff_from_meeting_actions": false},
  "routines": {
    "eod_sweep": {"on": true, "cron": "30 16 * * 1-5"},
    "promise_sweep": {"on": true, "cron": "0 15 * * 5"},
    "delegation_chaser": {"on": true, "cron": "0 8 * * 1", "intake_cron": "0 13 * * 1-5"},
    "principal_mode": {"on": false, "cron": "0 14 * * 5", "principal_name": "", "principal_mailbox_access": false},
    "post_call_intake": {"on": false, "trigger_id": null, "notify": "next_digest"}
  },
  "people": {
    "vips": [],
    "clients": [{"name": "Example Co", "domains": ["example.com"]}],
    "never_nudge": []
  },
  "uncertain_policy": "maybe_section",
  "nudge_rules": {"grace_business_days": 1, "silence_business_days": 5, "min_gap_business_days": 3, "max_nudges": 2},
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "autonomy": {"drafts_only": true}
}
```

Finish with a short summary: what runs when, where digests land, and that every nudge waits in drafts.
