---
name: agent-onboarding
description: 'First-run setup for Calendar Guardian: picks self or EA mode, connects the calendar and mailbox, captures protected commitments and alert rules, runs a supervised audit, then creates the triggers and schedules.'
first_prompt: 'Set up Calendar Guardian for me'
---

# Calendar Guardian onboarding

## 1. Welcome

Say in two or three sentences what you'll set up: a conflict alarm with drafted reschedule emails, a twice-daily calendar audit, and two optional extras (open-time blocks and a client slip alert to Slack). Make clear that you never move real meetings or send email. Then list the questions you'll ask so the user knows what's coming:

1. Whose calendar is this: yours, or a principal's you manage?
2. Which calendar and mailbox?
3. Working hours, timezone and no-meeting days
4. Protected commitments and VIPs
5. Where alerts should reach you
6. Which optional routines to turn on
7. How quiet the audit should be

## 2. Check connections

For Google Calendar, Outlook, Gmail, Slack and Google Maps, call `mcp__user-input__search_connection_options` and note what's already connected. Also call `mcp__chat__list_agent_integrations` to see whether the agent already has Slack, email, Telegram or iMessage set up. Don't request anything yet.

## 3. Ask, one at a time

Use `AskUserQuestion` for discrete choices and plain chat for open answers. Wait for each answer.

1. **Mode** (`AskUserQuestion`): "My own calendar" or "I'm an EA managing someone else's calendar". In EA mode, ask the principal's name, how drafts should refer to them, and whether drafts go in the EA's or the principal's mailbox.
2. **Calendar provider** (`AskUserQuestion`): Google Calendar or Outlook. In EA mode, confirm the EA has delegate access to the principal's calendar ("make changes to events" if color-coding or open blocks will be used; "see all event details" is enough otherwise).
3. **Working hours and timezone**: start and end time, timezone, no-meeting days, protected lunch, earliest and latest acceptable meeting times, and the holiday calendar (country) to respect.
4. **Protected commitments**: which recurring meetings, people (VIPs, board, investors, key clients) and kinds of events are untouchable. Show the default priority order from the `calendar-checks` skill and ask if it fits.
5. **Travel buffers**: minutes for in-town and across-town in-person meetings (defaults 20 and 45). Offer `google_maps` for live drive estimates as an optional extra.
6. **Alert channel** (`AskUserQuestion`): in-app only, the agent's Slack DM, the agent's own email inbox, Telegram or iMessage. Set up the agent integration if missing (`mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration`, or hand it over with `mcp__user-input__request_integration_setup`).
7. **Audit settings**: lookahead (3 or 5 business days), run times (default 7:30 and 16:30), meeting-hours-per-day ceiling, what to do on a clean day (one line or silence). Ask whether to pull context from Slack, a task tool or notes.
8. **Color-coding** (`AskUserQuestion`): off (default) or on. If on, agree the scheme (for example external, internal, transit, focus, personal) and the color for each.
9. **Open-time blocks** (`AskUserQuestion`): off (default) or on. If on: placeholder title (default "Open"), minimum gap (30 min), horizon (10 business days), whether holds count as busy (default: no, visible but bookable), and whether a scheduling tool such as Calendly reads this calendar.
10. **Slip alert** (`AskUserQuestion`): off (default) or on. If on: which shared inbox, the internal email domains, and the client map (client name, attendee email domains, Slack channel). Offer to draft the map from recent calendar events and Slack channel names for the user to confirm.
11. **Autonomy check**: restate the defaults (alert and draft alone; never send, never move events; post slip alerts on its own once verified; DM when unsure) and ask if anything should be stricter.

## 4. Connect

- `mcp__user-input__request_connected_account` with `googlecalendar` or `outlook`, reason "Allow access to your calendar to watch for conflicts and draft fixes?"
- `gmail` or `outlook` for reschedule drafts.
- For the slip alert: the shared inbox as its own connected account, and the agent's Slack app as an agent integration. Ask the user to invite the Slack app to each client channel, then check with `mcp__chat__list_chat_channels`.
- Optional: `google_maps`, `slack` (read context), and a task tool.

## 5. Supervised dry run

Run the health audit over the next 3 business days on real data and show the briefing. If there is a real conflict, draft one reschedule email and show it (it stays in Drafts). If open-time blocks are on, compute the gaps and show the placeholders you would create, without writing them; write them only after the user says yes. If the slip alert is on, run it over the last 7 days of the shared inbox and show what you would have posted, without posting. Ask what was noise and what was missing, adjust thresholds once, and show the result.

## 6. Schedule and trigger

- Calendar change trigger: `mcp__user-input__get_available_triggers` on the calendar account, then `mcp__user-input__setup_trigger` with the narrowest event-changed trigger. If none exists, `schedule_task` with cron `*/10 7-21 * * *` in the principal's timezone.
- Health audit: `schedule_task` with cron `30 7,16 * * 1-5` (or the agreed times).
- Open-time rebuild, if on: `0 2 * * *`.
- Slip alert, if on: a new-message trigger on the shared-inbox account, or `*/5 8-19 * * 1-5`.

Each prompt must be self-contained: the routine name, the config path `/workspace/.claude/skills/agent-onboarding/config.json`, the state file under `/workspace/state/calendar-guardian/`, the destination, the silence rule, and the hard limits (never create, move, accept, decline or delete real events; never send email). Confirm with `list_scheduled_tasks` and `list_triggers`.

## 7. Save

Write a short human summary under `## Your context` in `CLAUDE.md`, and this config to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "mode": "self",
  "principal": {"name": "", "draft_reference": "", "timezone": "America/New_York"},
  "calendar": {"provider": "googlecalendar", "calendar_id": "primary", "account_id": ""},
  "mailbox": {"provider": "gmail", "account_id": "", "drafts_in": "user"},
  "working_hours": {"start": "09:00", "end": "18:00", "days": [1, 2, 3, 4, 5], "no_meeting_days": [], "protected_lunch": null, "holiday_calendar": "US"},
  "protected": {"recurring_titles": [], "vip_emails": [], "vip_domains": [], "event_types": ["flight", "board", "interview"]},
  "priority_order": ["travel_deadline", "external_vip", "interview", "standing_1on1", "internal_adhoc", "hold_focus"],
  "buffers_minutes": {"in_town": 20, "across_town": 45, "use_google_maps": false},
  "alerts": {"channel": "slack_dm", "integration_id": "", "destination": "", "lookahead_days": 14},
  "audit": {"cron": "30 7,16 * * 1-5", "business_days": 3, "max_meeting_hours": 6, "clean_day": "one_line_morning", "context_sources": []},
  "colors": {"enabled": false, "scheme": {}},
  "availability": {"enabled": false, "title": "Open", "min_gap_minutes": 30, "horizon_business_days": 10, "holds_busy": false},
  "slip_alert": {"enabled": false, "inbox_account_id": "", "internal_domains": [], "clients": [{"name": "", "domains": [], "slack_channel": ""}], "fallback_dm": ""},
  "triggers": [],
  "scheduled_tasks": []
}
```

Finish with a plain summary of what runs when, where alerts land, and what the agent will never do.
