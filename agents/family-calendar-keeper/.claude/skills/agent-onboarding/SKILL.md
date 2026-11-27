---
name: agent-onboarding
description: 'First-run setup for Family Calendar Keeper: learns the kids and their schools and teams, agrees the sender allowlist, connects mail, calendar and docs, builds the shared doc from this week''s mail, then schedules the sweeps and the pickup check.'
first_prompt: 'Set up Family Calendar Keeper for our family'
---

# Family Calendar Keeper onboarding

## 1. Welcome

In two or three sentences, explain what you'll set up: one shared family doc built from school and activity mail, a family calendar kept in sync with it, a daily pickup check, and optional weekly activity ideas. Say that you only read mail from senders the family approves and never message anyone else. Then list the questions you'll ask:

1. The kids: names, ages, schools, activities
2. Which senders count as school and family mail
3. Which mailbox and calendars
4. Who should see the shared doc
5. How to reach you for urgent changes
6. Who usually covers pickups
7. Whether you want weekly activity ideas

## 2. Check connections

Call `mcp__user-input__search_connection_options` for Gmail, Outlook, Google Calendar, Google Docs, Google Drive and Google Maps. Call `mcp__chat__list_agent_integrations` to see whether Telegram, iMessage, Slack or an agent email inbox is already set up.

## 3. Ask, one at a time

1. **Kids**: for each kid, first name, age or grade, school, teacher, and regular activities (team, club, lessons) with their usual days and places.
2. **Mailbox** (`AskUserQuestion`): Gmail or Outlook, and which address gets the school mail. Ask whether a partner's mailbox also gets school mail; if so, the simplest path is a forwarding rule from the partner's mailbox to this one for the allowlisted senders.
3. **Sender allowlist**: offer to propose one. Search the last 60 days of mail for likely school, team and club senders (school domains, the platforms listed in `AGENTS.md`, coaches) and show the list with message counts. The user ticks what's in and adds anyone missing. Store domains and addresses separately.
4. **Calendars** (`AskUserQuestion`): which calendar is the family calendar (or a new "Kids" calendar created now with the user's OK), and which personal calendars to read for the pickup check, and whose each one is.
5. **Shared doc**: use an existing doc or create a new one. Who to share it with (partner, sitter, grandparents) and at what level (default: partner can edit, others can comment or view). Confirm each email address before sharing.
6. **Urgent channel** (`AskUserQuestion`): Telegram, iMessage, the agent's Slack app or the agent's own email. Set it up if missing (`mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`). Ask about quiet hours (default 21:00 to 06:30).
7. **Pickups**: the standing weekly pattern (who does which pickup on which day), carpool partners, sitter, any co-parenting schedule, and typical drive times between home, schools and venues (or use `google_maps`).
8. **Calendar sync autonomy** (`AskUserQuestion`): the default is to ask before every calendar change for 7 days, then sync with undo. Offer "always ask" as an alternative.
9. **Activity ideas** (`AskUserQuestion`): on or off. If on: the day and time, which teacher updates to read, a household items list (offer a starter list to edit: paper, tape, crayons, cups, spoons, socks, cardboard boxes, a ball, string), and anything to avoid (allergies, mess level, screen time).

## 4. Connect

- `mcp__user-input__request_connected_account` with `gmail` (or `outlook`): "Allow access to Gmail to read school and activity mail from the senders you approved?"
- `googlecalendar`: "Allow access to Google Calendar to keep the family calendar in sync?"
- `googledocs` and `googledrive`: for the doc and sharing it.
- Optional: `google_maps` for drive times.

## 5. Supervised dry run

Sweep this week's and next week's allowlisted mail. Build the doc and show it. List the calendar changes you would make, without making them, plus any clashes. Run the pickup check for tomorrow and show the result, even if it's clean. If activity ideas are on, produce this week's ten ideas and the PDF. Ask what's wrong or missing, fix it once, then apply the calendar changes the user approves.

## 6. Schedule and trigger

- Sweeps: `schedule_task`, cron `0 7,12,17 * * *` in the family's timezone.
- Urgent catch: `get_available_triggers` on the mailbox account, then `setup_trigger` on new messages. If there's no trigger, use a `*/20 6-21 * * *` sweep for urgent same-day items.
- Pickup check: `schedule_task`, cron `0 13 * * *`.
- Activity ideas: `schedule_task` at the chosen time.
- A one-time `schedule_task` (`scheduleType: "at"`) on day 7 to ask whether to switch calendar sync from "ask first" to "sync with undo".

Each prompt names the routine, the config path `/workspace/.claude/skills/agent-onboarding/config.json`, the state directory `/workspace/state/family-calendar-keeper/`, the delivery channel, the silence rule and the limits (allowlist only, draft never send, never delete a human-made event). Confirm with `list_scheduled_tasks` and `list_triggers`.

## 7. Save

Summarize in `AGENTS.md` under `## Your context` and write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/Chicago",
  "kids": [{"name": "", "age": 0, "grade": "", "school": "", "teacher": "", "activities": [{"name": "", "days": [], "location": ""}]}],
  "mailbox": {"provider": "gmail", "account_id": ""},
  "allowlist": {"domains": [], "addresses": []},
  "calendars": {"family": "", "read_for_pickups": [{"id": "", "owner": ""}]},
  "doc": {"id": "", "title": "Family Week", "shared_with": [{"email": "", "role": "writer"}]},
  "urgent": {"channel": "telegram", "integration_id": "", "destination": "", "quiet_hours": ["21:00", "06:30"]},
  "pickups": {"pattern": [{"day": "Mon", "kid": "", "event": "school pickup", "driver": ""}], "carpool": [], "sitter": "", "co_parenting": null, "drive_minutes": {}},
  "calendar_sync": {"mode": "ask_first", "first_week_until": "2026-11-27"},
  "activities": {"enabled": false, "cron": "0 16 * * 5", "sources": [], "household_items": [], "avoid": []},
  "scheduled_tasks": [],
  "triggers": []
}
```

End with a plain summary: what runs when, where urgent pings go, who can see the doc, and what the agent will never do.
