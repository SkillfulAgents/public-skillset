---
name: agent-onboarding
description: 'First-run setup for Time and Mileage Log: captures the start address, trip rules, client map and billing conventions, connects calendar, maps, sheets, mail and drive, runs supervised reconstructions on real data, then schedules the monthly and weekly runs.'
first_prompt: 'Set up Time and Mileage Log for me'
---

# Time and Mileage Log onboarding

## 1. Welcome

In two sentences: you'll rebuild the monthly mileage report from the calendar at the current IRS rate, and the weekly billable hours by client from calendar, email and documents, always as estimates with evidence. You never invoice or submit anything. Ask whether they want both routines or just one, then list the questions for the chosen ones:

1. Where your drives start, and your home state
2. Trip rules: airport runs, personal places to skip
3. Your clients and how to recognize them
4. How you bill: rounding, what's billable
5. Where you log time today
6. Where the sheets live and where summaries go

## 2. Check connections

Call `mcp__user-input__search_connection_options` for Google Calendar, Outlook, Google Maps, Google Sheets, Gmail, Google Drive, QuickBooks and Harvest. Call `mcp__chat__list_agent_integrations` for existing delivery channels.

## 3. Ask, one at a time

Mileage (if enabled):
1. **Start point** (`AskUserQuestion`): home, office or depends on the day. Get the address(es). Ask whether home is their principal place of business. Record the answer and don't give tax advice.
2. **Home state and radius**: trips outside the state, or beyond N miles, are skipped.
3. **Airport runs**: fixed round-trip miles per airport they use.
4. **Personal exclusions**: places that are never business (gym, kids' school, doctor), by name or address.
5. **Multi-stop days** (`AskUserQuestion`): chain stops into one route (default) or count each as its own round trip.
6. **Client reimbursement rates**: any client that pays a contract rate instead of the IRS rate.

Billable hours (if enabled):
7. **Clients**: names, email domains, name keywords, Drive folders, project codes. Offer to draft the map from the last 30 days of calendar attendees and sent-mail domains for the user to confirm.
8. **What's billable**: internal meetings (default no), prospect calls (default no), travel time (per client), email time estimates (defaults 0.1 h short, 0.2 h long), rounding increment (0.1 h default, or 0.25 h), and any monthly caps or retainers.
9. **Where time is logged today** (`AskUserQuestion`): nowhere, a spreadsheet, QuickBooks time, Harvest or another tool. Then ask whether they want confirmed entries pushed there (default no).

Both:
10. **Output** (`AskUserQuestion`): Google Sheet (default, one tab per month or week) or Google Doc. Use an existing sheet or create new ones.
11. **Delivery** (`AskUserQuestion`): in-app, the agent's own email inbox, Slack or Telegram. Set it up if missing (`mcp__chat__list_available_integration_providers`, `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`).
12. **Timing**: the mileage run time on the last business day (default 16:00), the weekly recap day and time (default Friday 16:00), timezone, and holidays to treat as non-business days.

## 4. Connect

- `googlecalendar` (or `outlook`): "Allow access to Google Calendar to find in-person meetings and billable time?"
- `google_maps`: "Allow access to Google Maps to measure driving distance to client meetings?" If declined, use web lookups and label each trip that way.
- `googlesheets` (and `googledocs` if a doc was chosen).
- `gmail` and `googledrive` for the hours recap.
- Optional: `quickbooks` or `harvest` via `mcp__user-input__request_connected_account` ("Allow access to Harvest to compare your logged hours with the weekly recap?").

## 5. Supervised dry run

- Mileage: run last month end to end. Look up the IRS rate per the `mileage-math` skill and show the citation. Walk through the "Skipped" and "Needs your input" lists with the user, and save their resolutions to the distance cache and exclusions.
- Hours: run last week. Show the per-client summary and three sample blocks with their evidence. Ask what's wrong (client mismatches, too generous or too stingy estimates) and adjust once.

## 6. Schedule

- Mileage: `schedule_task`, cron `0 16 26-31 * *`. The prompt exits unless today is the last business day of the month.
- Hours: `schedule_task`, cron `0 16 * * 5` (or the chosen time).

Each prompt is self-contained: the routine, config path `/workspace/.claude/skills/agent-onboarding/config.json`, state directory `/workspace/state/time-and-mileage-log/`, the instruction to look up and cite the IRS rate fresh, the sheet ID, the delivery channel, and the limits (estimates only; never invoice or submit; push entries only if opted in and confirmed). Confirm with `list_scheduled_tasks`.

## 7. Save

Summarize under `## Your context` in `AGENTS.md` and write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/Denver",
  "holidays": "US",
  "mileage": {
    "enabled": true,
    "start_point": "home",
    "addresses": {"home": "", "office": ""},
    "home_is_principal_place_of_business": null,
    "home_state": "CO",
    "max_radius_miles": 150,
    "airport_round_trip_miles": {"DEN": 0},
    "personal_exclusions": [],
    "multi_stop": "chain",
    "client_rates": {},
    "calendars": ["primary"],
    "output": {"type": "sheet", "id": ""},
    "cron": "0 16 26-31 * *"
  },
  "hours": {
    "enabled": true,
    "clients": [{"name": "", "domains": [], "keywords": [], "drive_folders": [], "travel_billable": false, "monthly_cap_hours": null}],
    "internal_domains": [],
    "billable_internal_meetings": false,
    "email_estimate_hours": {"short": 0.1, "long": 0.2},
    "doc_session_gap_minutes": 30,
    "doc_min_session_minutes": 15,
    "rounding_hours": 0.1,
    "timesheet_source": "none",
    "push_time_entries": false,
    "output": {"type": "sheet", "id": ""},
    "cron": "0 16 * * 5"
  },
  "delivery": {"channel": "in_app", "integration_id": "", "destination": ""},
  "scheduled_tasks": []
}
```

End with what runs when, where the sheets are, and a reminder that every number is an estimate the user confirms.
