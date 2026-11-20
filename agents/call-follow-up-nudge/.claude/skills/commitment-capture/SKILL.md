---
name: commitment-capture
description: 'Rubric for pulling the user''s own commitments out of a call transcript: what counts as theirs, mine-vs-theirs separation, circle-back items, exact quoting, date inference with (est.) labels, and the commitments.json record. Use on every call before drafting anything.'
---

# Commitment capture

## 1. Identify the user's lines

Map transcript speakers to calendar attendees. Use the user's name, their known voice in the notes tool, and context ("as I said in my email..."). If a line cannot be attributed with confidence, it can only ever be a **Maybe**.

## 2. Classify each candidate

| Class | Counts when | Examples |
|---|---|---|
| **Mine** | The user agreed to do a specific thing for someone | "I'll send the deck tonight", "Yes, I can get you references by Friday", "Let me intro you to our CTO" |
| **Circle back** | The user promised to check, find out, or return to something, with no concrete deliverable | "Let me check with legal", "I'll look into the SSO question", "I'll come back to you on pricing" |
| **Theirs** | Someone else agreed to do something (for the user or for the group) | "We'll get you the security questionnaire", "I'll loop in procurement" (said by the client) |
| **Maybe** | Ambiguous owner, hedged language, or unclear speaker | "I can probably...", "We could send...", a "sure" whose question is unclear |
| **Not a commitment** | Ideas and intentions with no owner | "We should revisit this", "It'd be worth exploring", "Someone could...", questions |

Rules:
- "We'll" from the user counts as **Mine** only if nobody else on the call took it.
- A request to the user answered with a clear yes is **Mine**, even if the user never said "I'll".
- If a commitment was made and then explicitly reversed later in the call ("actually, let Sam send that"), use the final state.
- Apply the user's corrections recorded in `## Your context` before these defaults.

## 3. Fields for each Mine / Circle back item

- **deliverable**: the concrete thing, in the user's terms ("revised SOW with the 3-seat option").
- **for**: the person (name and email from the invite) or company.
- **due**: the spoken deadline, or an inferred one with `due_estimated: true`.
- **quote**: the exact words, up to about 25 words, with timestamp.
- **channel**: email, Slack, or other, based on how the user normally talks to that person (existing thread first).

## 4. Exactness

Copy numbers, prices, percentages, quantities, names of documents, and dates exactly as spoken. If the transcript is clearly mis-heard ("fifteen" vs. "fifty"), quote it as written and flag it: `(transcript unclear: 15 or 50?)`. Never fix it silently.

## 5. Date inference (only when no exact date was said)

| Said | Due | Label |
|---|---|---|
| "tonight", "right after this", "today" | call date | |
| "tomorrow" | next calendar day | |
| "this week", "by end of week" | Friday of the call week | (est.) |
| "next week" | Friday of the following week | (est.) |
| "early next week" | Tuesday of the following week | (est.) |
| nothing | two business days after the call | (est.) |

Keep the spoken words next to every computed date in the output.

## 6. Record format (`/workspace/state/call-follow-up-nudge/commitments.json`)

```json
{
  "id": "cfn-2026-11-20-001",
  "meeting_id": "evt_abc123",
  "meeting_title": "Example Co pricing review",
  "direction": "mine",
  "deliverable": "Revised SOW with the 3-seat option",
  "for": {"name": "Client contact", "email": "contact@example.com"},
  "due": "2026-11-21",
  "due_estimated": false,
  "quote": "I'll get you the revised SOW with three seats by tomorrow",
  "timestamp": "14:32",
  "channel": "email",
  "draft_id": "r-123456",
  "status": "open",
  "evidence": null
}
```

`direction` is one of `mine`, `circle-back`, `theirs`, `maybe`. `status` is `open`, `done`, `dropped`, or `handed-off`. Store only the short quote, never longer transcript text.
