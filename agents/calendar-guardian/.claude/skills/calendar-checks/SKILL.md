---
name: calendar-checks
description: 'Rubric for Calendar Guardian: which calendar problems deserve an alert, how to rank and fingerprint them, how to find three reschedule slots, and how to recognize the agent''s own placeholder blocks.'
---

# Calendar checks

Use this whenever you evaluate calendar changes, run the health audit, propose slots or touch availability placeholders. Read the principal's settings from `/workspace/.claude/skills/agent-onboarding/config.json` first.

## 1. Is it a problem?

Score each candidate on two axes and alert (Routine 1) only when severity is high and it's in the next 14 days. Everything else goes to the next audit.

| Problem | Severity | Alert now when |
|---|---|---|
| Overlap with a protected commitment | High | both events accepted or tentative, overlap of 5 min or more |
| Key meeting cancelled or declined by the other side | High | external or VIP attendee, or organizer cancelled |
| Proposed new time from the other side (`METHOD:COUNTER`) | High | for a key meeting |
| In-person with no travel time | High | gap shorter than the buffer, within 3 business days |
| Over PTO / out-of-office | High | any accepted event |
| Missing location and conferencing | Medium | external meeting within 2 business days |
| Outside hours or on a no-meeting day | Medium | new or moved in the last change |
| Missing agenda | Low | audit only |
| Overlap between two internal ad hoc meetings | Low | audit only |

Ignore: declined events, events marked free, all-day informational events, cancelled events you've already reported, and anything carrying the `managedBy=calendar-guardian` marker.

## 2. Who wins a collision

Default order, highest first (the user can override in config `priority_order`):
1. Flights, travel and hard external deadlines
2. External, client, investor, board and VIP meetings
3. Interviews
4. Standing 1:1s and recurring team rituals
5. Internal ad hoc meetings
6. Holds and focus blocks (unless marked protected)

Ties: the older booking wins; the one the principal organizes yields more easily, because the principal controls it.

## 3. Fingerprint and dedup

`fingerprint = "<event_id>|<problem_type>|<event_start_iso>|<other_event_id or ->"`

Store in `/workspace/state/calendar-guardian/alerts.json`:

```json
{
  "fingerprints": {
    "abc123|overlap|2026-12-02T15:00:00-05:00|def456": {
      "first_seen": "2026-11-30T14:03:00Z",
      "status": "open",
      "draft_id": "r-1234"
    }
  }
}
```

Status is `open`, `dismissed` (user said ignore) or `resolved` (the problem is gone at the next check). Remove entries once the event is in the past.

## 4. Three slots

1. Query free/busy for the principal (Google `freeBusy`, Outlook `getSchedule`) over the next 10 business days, plus the other attendees if their calendars are visible.
2. Candidate windows: inside working hours, not on no-meeting days, not within the configured buffer of another event, not over protected lunch, same duration as the original.
3. Prefer: the same time of day as the original; at least two different days; nothing in the first or last 30 minutes of the day unless allowed.
4. Show each slot in the principal's timezone and, when different, the recipient's.
5. Say in the draft that the times are proposed, not held.

## 5. Placeholder blocks

A placeholder is yours only if all three hold:
- it carries the marker (Google: `extendedProperties.private.managedBy == "calendar-guardian"`; Outlook: the configured category or extended property),
- its ID is in `/workspace/state/calendar-guardian/availability-log.json`,
- it has no attendees.

If any check fails, it is a real event. Leave it alone. Create placeholders as free/transparent, with no reminders and the configured title (default "Open").
