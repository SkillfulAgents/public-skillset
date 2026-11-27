---
name: meeting-triage
description: 'Decide whether a calendar event gets a brief, which type it is (first-time, high-stakes, external recurring, routine), how deep to research it, and the fixed brief format. Use on every planning run and before writing any brief.'
---

# Meeting triage and brief format

## 1. Does it get a brief?

Skip the event when any of these is true:
- The user declined it, it is marked free, it is all-day, or it has no attendees besides the user.
- Every attendee's email domain is in `ownDomains` (plus `internalDomains`) from config. Ignore room resources (`resource.calendar.google.com`), group aliases and the user's assistant when deciding.
- It is a recurring event with exactly one other attendee from the user's own domains (a 1:1; One-On-One Prep owns it), unless the user opted in.
- Its title or organizer matches `skipList` in config (for example "Standup", "All hands", "Lunch").

Always brief when the user explicitly asked for it, even if internal.

## 2. Which type?

Check in this order; the first match wins.

| Type | Test |
|---|---|
| High-stakes | Title or description mentions pricing, contract, renewal, proposal, term sheet, board, legal, security review, negotiation or decision; or a C-level or VP external attendee; or a CRM deal at or above `highStakesDealAmount` or in a late stage; or the company is on `flaggedAccounts` |
| First-time | No prior email thread or meeting with any external attendee or their domain in the last 12 months |
| External recurring | Recurring series with external attendees and prior history |
| Routine | Anything else that still qualifies |

## 3. How deep?

| Section | First-time | High-stakes | External recurring | Routine |
|---|---|---|---|---|
| The one thing | yes | yes | yes | yes |
| Who is in the room | full profile, every external attendee | full for new faces, one line for known | one line each, new faces in full | names and roles only |
| Email history | first contact and how they found us | last 3 exchanges, who wrote last | last exchange, who wrote last | last exchange only |
| Promises from last time | n/a (say "first meeting") | all, open first | all, open first | open only |
| What is new | company and people changes | full | full | only if something changed |
| Company news | 3 to 4 items | 2 to 4 items | 1 to 2 items | only if notable |
| CRM / call notes (if connected) | record exists? | full stage, amount, risks | stage and next step | skip |
| Word budget | 500 | 500 | 300 | 150 |

## 4. Brief format

```
<Meeting title> · <day, time, timezone> · <type>
The one thing: <say or ask this>, because <one-line reason with source>.

Who is in the room
- <Name>, <title> at <company> (<since when, if known>). <one notable line>. [link]

Where we left it
- Last contact: <date>, <who wrote last>, <topic>. [link]
- Open: <you|they> promised "<quoted promise>" on <date>. Not seen done. [link]
- Done: "<quoted promise>". [evidence link]

What is new since <last contact date>
- <change>, <date>. [link]

Company news
- <headline>, <date>. [link]

Deal / call notes (optional)
- <stage, amount, close date, last call highlight> [link]

Not checked: <sources that failed or were unavailable>
```

Rules: no tables in the brief itself, every fact with a link or a named source, uncertain matches stated plainly, dates absolute.
