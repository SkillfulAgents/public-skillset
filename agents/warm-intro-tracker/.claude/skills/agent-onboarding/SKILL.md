---
name: agent-onboarding
description: 'First-run setup for Warm Intro Tracker: connect the mailbox, learn how the user writes intros, set intro types, nudge window and cap, pick where the scoreboard goes, do a supervised dry run, then schedule the sweeps.'
first_prompt: 'Set up Warm Intro Tracker for me'
---

# Warm Intro Tracker onboarding

Goal: the agent can find the user's intros, draft nudges that sound like them, and report a scoreboard on a schedule. Ask one question at a time. Use `AskUserQuestion` for discrete choices. Skip anything already in `AGENTS.md` `## Your context`.

## 1. Welcome

Explain in a few lines: the agent finds intros you made that went quiet, drafts a short bump in the original thread for you to send, stops after a couple of tries, and keeps a reply-rate scoreboard. Nothing is ever sent for you. Then list the questions you'll ask: mailbox, how you write intros, intro types, timing, scoreboard and delivery, and autonomy.

## 2. Connections

For each service, call `mcp__user-input__search_connection_options`, check `CONNECTED_ACCOUNTS` and `mcp__chat__list_agent_integrations`, and request only what's missing.

- **Mailbox (required):** Gmail or Outlook? `request_connected_account` with `gmail` or `outlook`, reason "Allow access to Gmail to find your intro threads and save nudge drafts for your review?".
- **Google Sheets (optional):** `googlesheets`, if they want the intro log and scoreboard in a sheet. Ask for an existing sheet or create a new one.
- **Google Calendar (optional):** `googlecalendar`, to count meetings booked from intros.
- **Delivery channel:** `AskUserQuestion`: in-app only, the agent's Slack DM, the agent's own email inbox, or Telegram. Set up the chosen agent integration and resolve the exact destination.

## 3. Questions

1. How do your intro emails usually start or what do the subjects look like? Ask for two or three examples (subjects are enough). Turn them into detection patterns.
2. Do you do double opt-in (ask permission first), or connect people directly, or both?
3. Which intro types or campaigns should the scoreboard split by? `AskUserQuestion` multi-select: fundraising, hiring, customer, advisor, portfolio support, community, plus their own.
4. Nudge window: `AskUserQuestion` with 2, 3 (default) or 5 business days before the first nudge.
5. Nudge cap and spacing: 1 or 2 (default) nudges, second at least 5 business days after the first.
6. Lookback: how far back to pick up intros (default 60 days).
7. Exclusions: people, domains or kinds of intro never to nudge (for example a board member, a VIP, internal intros).
8. Voice: paste one or two follow-ups they've sent, or describe their style (sign-off, emoji or not, formality).
9. Scoreboard: weekly on Monday at 8am (default) or another time, and in a sheet, a message, or both. Mention an optional dashboard for a living view.
10. Timezone and any holidays to skip.
11. Autonomy: confirm the defaults with `AskUserQuestion`: tracking, scoreboard and drafts on their own; every nudge waits for the user to send.

## 4. Supervised dry run

Scan the lookback window. Show the user the intros found (subject, parties, type, state) and ask them to correct any misses or false matches; update the detection patterns. Then draft nudges for up to three quiet threads and show the text in chat. After they approve the wording, save those drafts in the original threads and give them the links. Show a first scoreboard. Iterate once on tone or detection if needed.

## 5. Schedules

Read `/opt/gamut/docs/scheduling-and-resuming.md`. Create with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, in the user's timezone:

- Nudge sweep: `0 9,15 * * 1-5`. Prompt: "Run Warm Intro Tracker routine 1. Read AGENTS.md Your context and .claude/skills/agent-onboarding/config.json, follow the intro-ledger skill, update /workspace/state/intro-ledger.json. Save nudge drafts in the original threads only; never send, never add recipients. Send the list of new drafts with mcp__chat__send_chat_message to <integration and destination>. If there are no new drafts, send nothing."
- Scoreboard: `0 8 * * 1`. Prompt: "Run Warm Intro Tracker routine 2. Read AGENTS.md Your context and config.json, refresh /workspace/state/intro-ledger.json per the intro-ledger skill, compute the scoreboard by type, write it to <sheet if configured>, and send it with mcp__chat__send_chat_message to <integration and destination>."

Confirm with `list_scheduled_tasks` and show the user.

## 6. Save

Write the answers in plain sentences under `## Your context` in `AGENTS.md`, and the config to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "",
  "holidays": [],
  "mailbox": {"provider": "gmail|outlook", "account": ""},
  "detection": {"subject_patterns": [], "body_phrases": [], "double_opt_in": true, "include_internal": false},
  "intro_types": ["fundraising", "hiring", "customer"],
  "campaigns": [],
  "nudge": {"window_business_days": 3, "second_gap_business_days": 5, "cap": 2, "lookback_days": 60},
  "exclusions": {"people": [], "domains": []},
  "voice_samples": [],
  "scoreboard": {"cron": "0 8 * * 1", "sheet_id": "", "dashboard": false},
  "delivery": {"channel": "in_app|slack|email|telegram", "integration_id": "", "destination": ""},
  "schedules": []
}
```

Create `/workspace/state/intro-ledger.json` from the dry-run scan. Finish with a summary: what runs when, where drafts and the scoreboard appear, and that nothing is ever sent for them.
