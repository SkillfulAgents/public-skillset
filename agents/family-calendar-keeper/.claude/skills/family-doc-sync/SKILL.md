---
name: family-doc-sync
description: 'Layout of the shared family doc, the item record, and the rules for reconciling the doc with the family calendar, including approval mode and undo.'
---

# Family doc and calendar sync

## Doc layout

One Google Doc, title set in onboarding (default "Family Week"). Top to bottom:

1. **This week at a glance**: a 7-day table (day, kid, what, time, who's driving). Rebuilt each sweep.
2. **Clashes and open questions**: anything flagged and not yet resolved.
3. One section per kid (`## Maya (Grade 3, Lincoln Elementary)`), each with three sub-headings:
   - **Upcoming**: events, newest-added first.
   - **Need-to-knows**: forms, payments, RSVPs, bring-items, dress-up days, half-days.
   - **What's due**: deadlines in date order.
4. **Whole family**: items for every kid (school closures, district notices).

Each line: `Fri Dec 5, 3:15-4:30 pm. Winter concert, school gym. Wear white top. (Ms. Rivera, "Concert details", Nov 18)`. Changed items add `Changed Nov 20: was 3:00`. Cancelled items are struck through for 7 days, then removed.

Edit the doc with the Google Docs API `batchUpdate`. Keep a named range per item, using the item ID, so updates hit the right line.

## Item record (`/workspace/state/family-calendar-keeper/items.json`)

```json
{
  "id": "itm-2026-11-18-concert-maya",
  "kid": "Maya",
  "type": "event",
  "title": "Winter concert",
  "start": "2026-12-05T15:15:00-05:00",
  "end": "2026-12-05T16:30:00-05:00",
  "location": "Lincoln Elementary gym",
  "bring": "white top",
  "due": null,
  "status": "active",
  "source": {"message_id": "", "from": "", "subject": "", "date": "2026-11-18"},
  "calendar_event_id": null,
  "history": []
}
```

`type` is one of `event`, `form`, `payment`, `rsvp`, `bring`, `theme_day`, `half_day`, `no_school`, `deadline`.

## Reconcile rules

| Doc item | Calendar | Action |
|---|---|---|
| active event, no `calendar_event_id` | none | create (tagged `managedBy=family-calendar-keeper`) |
| active event, time or place differs | ours | update |
| cancelled | ours | delete ours |
| any | event made by a person that overlaps or duplicates | flag in "Clashes and open questions"; never edit |
| half-day / no-school | none | create an all-day event on the kids' calendar |

Need-to-knows get a calendar event only if the user asked for that (for example a 7:30 pm reminder the night before "bring X").

## Approval mode

While today is before `first_week_until` in config, gather the planned writes into one numbered list, send it, and apply only the numbers the user approves. After that date, apply them and include a "Calendar changes" section in the digest.

## Undo

Each write appends to `sync-log.json`:

```json
{"ts": "", "action": "update", "event_id": "", "item_id": "", "before": {}, "after": {}}
```

"Undo last sync" reverses every entry from the latest sweep in reverse order. "Undo <item>" reverses that item's latest entry. Then mark the item `user_override: true` so the next sweep doesn't redo it.
