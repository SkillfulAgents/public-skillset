---
name: rank-and-remember
description: 'Consequence scoring for brief candidates, the cut to a top handful, and the ledger that keeps handled, dismissed and snoozed items from resurfacing. Use on every brief before writing it.'
---

# Rank and remember

## 1. Score each candidate

Ask "what happens if the user does nothing today?" and score 0 to 3 on each line. Sum them.

| Factor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Who | automated or unknown | colleague | important sender from config | key customer, investor, board, the user's manager |
| Deadline | none | this week | tomorrow | today or overdue |
| Blocking | FYI | would help someone | someone is waiting | someone is stuck until the user acts |
| Cost of delay | none | awkward | money, a deal or a hire slips | contractual, legal, security or reputational |

Add 1 if the person has followed up. Subtract 2 if the user is only copied.

## 2. Cut

- Score 7 or more: "Needs you today", highest first, at most five. Ties go to the oldest.
- Score 4 to 6: counted in the footer, with the single best example if there is room.
- Below 4: dropped.
- If more than five score 7 or more, keep five and add "+N more urgent items" with links in the footer. Never silently drop a 9 or above.

## 3. Ledger

`/workspace/state/daily-briefing/ledger.json`, one entry per item:

```json
{
  "key": "gmail:<threadId> | slack:<channel>:<thread_ts> | cal:<eventId>:<start> | task:<id> | loop:<id>",
  "summary": "Acme asked for the signed order form",
  "first_shown": "2026-11-18",
  "last_shown": "2026-11-20",
  "times_shown": 3,
  "status": "open | handled | dismissed | snoozed",
  "snoozed_until": null,
  "last_change": "<ISO time of the newest message or edit seen>"
}
```

Rules:
- **Handled**: the user replied after the item arrived, the task closed, the event passed, or the user said "done". Never show it again.
- **Dismissed**: shown again only if `last_change` moved and the change is material: a different person wrote, a deadline moved to today, or a stated escalation. Prefix "(back: <what changed>)".
- **Snoozed**: hidden until `snoozed_until`, then shown once and set back to `open`.
- **Repeats**: an open item shown three days running is marked "(day 3)". After five days, ask once: "Still relevant, or drop it?"
- Prune entries older than 60 days that are handled or dismissed.
