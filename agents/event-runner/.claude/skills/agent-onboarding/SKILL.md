---
name: agent-onboarding
description: 'Sets up Event Runner for one event: captures the event plan, connects the registration platform, mailbox and calendar, sets lead times, segments and autonomy, runs a first readiness check, and schedules the run-up and post-event runs.'
first_prompt: 'Set up Event Runner for my next event'
---

# Event Runner onboarding

## 1. Welcome

Explain in two or three sentences: you will track this event's readiness every morning until event day, draft the next promo or reminder when it is due, and within a day of the event pull attendance, split people into hand-raisers, attendees and no-shows, and draft a follow-up for each. Every outbound message waits for approval. The daily check stops by itself after the follow-up wave.

List the planned questions up front, then ask one at a time. Skip anything already in `CLAUDE.md` `## Your context` or `/workspace/state/event-runner/events.json`.

## 2. Find the connections

Call `mcp__user-input__search_connection_options` for Gmail or Outlook, Google Calendar, Eventbrite, Zoom, Luma, Google Sheets or Docs, the CRM, and Typeform. Note what is connected. Call `mcp__chat__list_agent_integrations` for delivery channels.

## 3. Questions, one at a time

1. What is the event: name, date, start and end time with timezone, webinar or in person, and the goal (pipeline, signups, community, education)?
2. Where do people register and where will attendance come from? (`AskUserQuestion`: Eventbrite, Zoom webinar, Luma, a form or sheet, the CRM, other.) For Luma, ask whether the calendar has API access; otherwise plan for a CSV export.
3. Registration link, and a registration goal if they have one.
4. Speakers: who, and how do you reach them? (Use roles, not guesses, if the user is unsure.)
5. Do you have a checklist or plan doc? If not, offer the default timeline from the `event-playbook` skill and adjust its lead times together.
6. Which promo channels are you using (email list, CRM marketing emails, LinkedIn, X, partners)? Which ones can I see, and which should I just ask you about?
7. Reminder sequence: keep the default T-7 days, T-1 day and T-1 hour, or use yours?
8. Post-event: what is the CTA? Where will the recording live? What counts as attended (default 10+ minutes) and what counts as a hand-raise for you?
9. Consent rules: may registrants get a follow-up? Anyone to exclude?
10. Gmail or Outlook for drafts? Paste one follow-up email you liked, for voice.
11. Should attendance and engagement be logged to the CRM or a sheet after approval?
12. Where should readouts go: in-app, the agent's Slack DM, a team Slack channel through the agent's Slack app, the agent's own email inbox, Telegram or iMessage? What time each morning?
13. Autonomy: confirm that every outbound message is a held draft (default). Anything you want me to do without asking, such as updating the internal checklist sheet?

## 4. Connect

- `mcp__user-input__request_connected_account`: `gmail` or `outlook`, `googlecalendar`, and as needed `eventbrite`, `zoom`, `googlesheets`, `googledocs`, `hubspot` / `salesforce` / `attio`, `typeform`.
- `mcp__user-input__request_remote_mcp` for `pipedrive` or `close` if that is the CRM.
- Luma: `mcp__user-input__request_secret` with `LUMA_API_KEY` if available; otherwise `mcp__user-input__request_login` for the browser, or `mcp__user-input__request_file` for the guest CSV after the event.
- Delivery: `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`.

## 5. Supervised dry run

1. Run the readiness check now. Fetch the registration page, check speaker emails and invites, pull the current registration count, and build the at-risk list split by owner. Show it.
2. If a beat is due soon, draft it and show it before saving to the mailbox.
3. Draft template versions of the three follow-ups (hand-raiser, attendee, no-show) and agree on them now, so the post-event wave only needs the names and signals filled in.
4. Iterate once.

## 6. Schedule

Using `mcp__user-input__schedule_task`, in the user's timezone:
- Run-up: `scheduleType: "cron"`, `0 8 * * *` (or the chosen time).
- Post-event: `scheduleType: "at"`, about two hours after the scheduled end, for example `at 2026-12-03 13:00`.
- Next-morning check: `scheduleType: "at"`, 9:00 the day after the event.

Example self-contained post-event prompt:

> Event Runner, post-event follow-up wave for event "<name from events.json>". Read `CLAUDE.md` `## Your context`, `.claude/skills/agent-onboarding/config.json` and `/workspace/state/event-runner/events.json`. Pull registrants and attendees from the configured source. Segment with the `event-playbook` rules. Draft hand-raiser follow-ups first, then attendees, then no-shows (only if the recording link works). Save the drafts in the user's mailbox and never send. Send the report to the configured channel with `mcp__chat__send_chat_message`. Then list scheduled tasks and cancel this event's run-up cron, unless another event is active. Update the state files.

Write the run-up prompt the same way. Its silence rule: send a one-line on-track note when nothing changed. Save the task ids in `events.json` and confirm with `mcp__user-input__list_scheduled_tasks`.

## 7. Save

Write a plain-language summary under `## Your context` in `CLAUDE.md` and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "mailbox": "gmail",
  "calendar": "googlecalendar",
  "crm": null,
  "delivery": { "channel": "slack_dm", "integration_id": "", "time": "08:00" },
  "lead_times": { "announce_days": 28, "reminders": ["T-7d", "T-1d", "T-1h"], "final_headcount_days": 3 },
  "attended_min_minutes": 10,
  "hand_raise_signals": ["question", "poll_intent", "cta_click", "booked_meeting"],
  "consent_rule": "",
  "exclude": [],
  "log_attendance_to": null,
  "autonomy": { "outbound": "draft_only", "internal_checklist_updates": false },
  "voice_samples": []
}
```

And add the event to `/workspace/state/event-runner/events.json`:

```json
{
  "events": [
    {
      "id": "",
      "name": "",
      "format": "webinar",
      "start": "2026-12-03T11:00:00",
      "end": "2026-12-03T12:00:00",
      "timezone": "America/New_York",
      "source": { "type": "zoom", "ref": "" },
      "registration_url": "",
      "goal": { "registrations": null },
      "speakers": [],
      "checklist_ref": "",
      "cta": "",
      "recording_url": null,
      "tasks": { "runup": "", "post_event": "", "next_morning": "" },
      "phase": "run-up"
    }
  ]
}
```

Finish with a summary: daily readout time, the post-event run time, when the schedule stops, and that every message waits for approval.
