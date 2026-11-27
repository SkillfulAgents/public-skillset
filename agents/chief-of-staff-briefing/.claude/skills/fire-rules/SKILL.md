---
name: fire-rules
description: 'The fire test, the urgency-rule format, people tiers, the consequence ranking and the ledger that stops handled or dismissed items resurfacing. Use on every briefing, fire watch and end-of-day pass before writing anything.'
---

# Fire rules

## 1. The fire test

An item is a **fire** only if all three hold:
1. **Consequence**: money, a customer, a hire, security, legal exposure, reputation, or a same-day launch or deadline is at stake.
2. **Gets worse with time**: waiting until tomorrow makes it materially worse.
3. **No clear owner**: nobody credible has said they are handling it, or the owner is blocked on the user.

It also counts as a fire if it matches a user urgency rule marked `always_fire`.

Strong signals: several different people reporting the same thing; a tier-1 person writing outside their usual pattern; words like "down", "outage", "can't log in", "refund", "chargeback", "cancel", "lawyer", "breach", "press", "deadline today"; a payment or payroll failure notice from a real provider (check the sender domain).

Not fires on their own: one angry message, a noisy channel, an automated alert that auto-resolved, marketing urgency ("last chance").

If it is close but not certain, list it under **Watching** with the reason.

## 2. Urgency rules format (config)

```json
{"name": "Outage", "match": {"keywords": ["outage", "down", "502"], "channels": ["#incidents"], "senders": []}, "always_fire": true, "wake_me": false}
```

Rules match on keywords (case-insensitive, whole words), channels, senders or domains. Quote the line that matched in the briefing.

## 3. Ranking inside each section

Score 0 to 3 on each factor and sum:

| Factor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| People tier | unknown or automated | tier 3 | tier 2 | tier 1 |
| Deadline | none | this week | tomorrow | today or overdue |
| Blocking | FYI | helpful | someone waiting | someone stuck until the user acts |
| Cost of delay | none | awkward | money, deal or hire slips | legal, security, contractual, reputational |

Add 1 for a repeat follow-up. Subtract 2 when the user is only copied. Ties go to the oldest item.

## 4. Ledger

`/workspace/state/chief-of-staff-briefing/ledger.json`, one entry per item:

```json
{"key": "gmail:<threadId> | slack:<channel>:<ts> | discord:<channel>:<messageId> | cal:<eventId>:<start> | issue:<id>",
 "summary": "one line", "section": "fire | waiting | reply | commitment | project | watching",
 "first_shown": "2026-11-18", "last_shown": "2026-11-20", "times_shown": 2,
 "status": "open | handled | dismissed | snoozed", "snoozed_until": null, "last_change": "<ISO>"}
```

- **Handled**: evidence the user acted (replied, approved, the issue closed) or the user said "done". Never shown again.
- **Dismissed**: shown again only after a material change (a new person, a closer deadline, an escalation), prefixed "(back: <what changed>)".
- **Fires**: also logged in `fires.json` with the time first flagged; the fire watch never alerts the same fire twice, and the next morning's briefing shows it once more only if it is still open.
- Prune handled and dismissed entries after 60 days.
