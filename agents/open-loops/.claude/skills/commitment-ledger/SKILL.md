---
name: commitment-ledger
description: 'Rules and file format for the open-loops ledger: how to tell a real commitment from talk, how to dedupe, estimate due dates, rank, and record closure evidence. Use on every Open Loops run that reads or writes /workspace/state/open-loops/ledger.json.'
---

# Commitment ledger

## Classify a candidate

Score each candidate sentence or action item on four signals:

| Signal | Example that passes | Example that fails |
|---|---|---|
| Owner is a specific person | "I'll send", "Dana will draft" | "we should", "someone needs to" |
| Future action, not a wish | "I'll send it Friday" | "would be great to", "maybe we could" |
| Concrete deliverable | "the pricing deck", "an intro to their CFO" | "think about it", "stay in touch" |
| Directed at someone | to a named person, team, or client | to nobody in particular |

- All four: **commitment** (confidence high).
- Three, missing the recipient or the deliverable is slightly vague: **commitment** (confidence medium).
- Contains "if/once/assuming…": **conditional**. It stays dormant until the condition is visibly met.
- Two or fewer: **talk**. Do not log it.

Always log "I'll circle back", "let me check and get back to you", and "I'll look into it" as medium-confidence commitments with an estimated date. Never log scheduling chatter, pleasantries, quoted or forwarded text, signatures, or auto-replies.

Direction tags: `by_user`, `to_user` (a delegation, owed to the user), `by_principal`, `to_principal`.

## Estimate due dates

Resolve relative to the message's timestamp in the user's timezone. Label every estimate.

| Said | Due |
|---|---|
| "today", "EOD" | end of that workday |
| "tomorrow" | next business day, end of day |
| "this week", "by end of week" | that Friday |
| "next week" | the following Friday |
| "ASAP", "shortly", "right away" | +2 business days (est.) |
| a named day or date | that day |
| nothing | +5 business days (est.) |

## Dedupe

Fingerprint = direction + counterparty (normalized email, or Slack user ID) + deliverable (lowercased, stopwords removed, key nouns kept).

- Same fingerprint already open: append the new source to `sources`, keep the earliest `made_at`, and take the newest stated due date (a restated deadline replaces an old one).
- Same fingerprint already closed: log a new loop only if the new source is dated after the closure and clearly restarts the work.
- Hand-offs from another agent carry an `external_id`. Never create a second loop with the same `external_id`.

## Rank

`priority = relationship_weight × (1 + days_overdue / 5)`, with weights from config: VIP or board 3, external customer, investor, or partner 2, internal 1. Ties go to the oldest loop. Never print the score; it only orders the list.

## Close

Set `status` to `closed`, `dropped`, or `closed_by_user`, and fill `evidence` with a URL or message ID and a one-line description of what proved it. See "What counts as closed" in `AGENTS.md`. An acknowledgement is never evidence.

## File format

`/workspace/state/open-loops/ledger.json`:

```json
{
  "version": 1,
  "loops": [
    {
      "id": "ol_2026-11-18_7f3a",
      "direction": "by_user",
      "owner": "user",
      "counterparty": {"name": "Client contact", "email": "contact@example.com", "org": "Example Co"},
      "deliverable": "Send revised SOW with phase 2 pricing",
      "quote": "I'll get you the revised SOW by Thursday",
      "confidence": "high",
      "conditional_on": null,
      "made_at": "2026-11-18T15:04:00Z",
      "due": "2026-11-20",
      "due_is_estimate": false,
      "sources": [{"kind": "gmail", "id": "<threadId>", "url": "https://mail.google.com/mail/u/0/#all/<threadId>"}],
      "external_id": null,
      "status": "open",
      "evidence": null,
      "closed_at": null,
      "nudges": [],
      "last_flagged": null
    }
  ]
}
```

Keep `quote` to the single sentence that made the promise. Never store whole message bodies. Write the file atomically: write to `ledger.json.tmp`, then rename it over `ledger.json`.
