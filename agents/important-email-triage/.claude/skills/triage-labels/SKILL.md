---
name: triage-labels
description: 'Hard skip list, the waiting-on-me decision rules, how to learn the user''s own categories, label naming, and the processed-message ledger format. Use on every triage run before applying any label.'
---

# Triage labels

## Hard skip (never labeled waiting)

- Sender or headers show bulk or automated mail: `List-Unsubscribe`, `Precedence: bulk`, `noreply`/`no-reply`/`notifications@` senders, Gmail categories Promotions, Social, Updates, Forums.
- Receipts, invoices sent for record, shipping and order updates, password resets, security codes.
- Calendar invitations, accepts, declines, and updates (`text/calendar` parts or `Invitation:` / `Accepted:` / `Declined:` subjects).
- Out-of-office and auto-replies (`Auto-Submitted: auto-replied`).
- Cold outreach: a sender or domain the user has never written to, with sales or recruiting language, including fake "Re:" threads and "following up on my last note". Exception: the important list.
- The user's own sent mail and drafts.

## Waiting on me: decide

Label **waiting** only when all hold:
1. A person wrote it (not a system), and the user is a direct recipient (To, or named in the body).
2. The latest message in the thread asks the user for something: an answer, a decision, an approval or signature, a document, a time, an intro.
3. The user has not replied after that message, and no colleague answered for them.

Label **leave alone** (log as `ambiguous`) when any is unclear. Strong signals: the user's name with a question mark nearby, "can you", "could you", "please", "need your", "by <date>", a second ping from the same person. Weak signals: CC only, "thoughts?" to a large list, "FYI".

## Learned categories

1. During onboarding, read the user's existing labels or Outlook categories and the senders of the last ~300 inbox messages.
2. Propose five to eight categories in the user's words (reuse their existing label names where they exist), each with two or three example senders or domains.
3. The user approves, renames or drops each one. Only approved categories are applied.
4. Label names live under one parent so they are easy to find and remove: `Triage/Waiting on me`, `Triage/Clients`, and so on (Gmail nests with `/`). Outlook uses categories with the same names.

## Investor preset labels

`Triage/Today's Focus`, `Triage/Action Required`, `Triage/Scheduling`, `Triage/Delegated`, `Triage/Fund admin`, plus optional `Triage/Portfolio` and `Triage/Candidates`. One bucket per thread.

## Ledger

`/workspace/state/important-email-triage/ledger.json`:

```json
{
  "last_sweep": "2026-11-20T14:30:00Z",
  "messages": {
    "<messageId>": {"thread": "<threadId>", "decision": "waiting|category:<name>|skip|ambiguous", "at": "<ISO>", "notified": true}
  },
  "waiting_threads": ["<threadId>"]
}
```

Prune `messages` entries older than 30 days on each run. A message already in `messages` is never re-processed; a thread in `waiting_threads` is re-checked each sweep for removal.
