---
name: intro-ledger
description: 'How to detect intro threads the user made, the per-intro ledger record and its states, nudge timing rules, and the scoreboard definitions. Use on every nudge sweep and scoreboard run.'
---

# Intro ledger

## Detecting an intro thread

A thread is an intro the user made when all of these hold:
- The user sent the first message (or the first message in the connection stage).
- At least two people other than the user are on To or Cc, from different domains or clearly different people (opt-in requests have one recipient; see below).
- The subject or opening matches the user's intro style. Defaults: "Intro:", "Introduction", "Connecting", "meet", "<>", " / ", " x ", or phrases like "I wanted to introduce", "you two should meet", "looping in". Onboarding adds the user's own patterns.

**Opt-in request:** one external recipient, asking permission to introduce someone ("would you be open to an intro to…"). Tracked with `stage: "opt_in"`. When the user later sends the actual intro, link it with `parent`.

Exclude: threads where the user was only cc'd, internal-only threads (all recipients on the user's own domain, unless the user wants them), and anything on the exclusion list.

Gmail search to start from (adjust to the user's patterns): `in:sent newer_than:60d (subject:intro OR subject:introduction OR subject:connecting OR "<>")`. Then confirm each candidate with the rules above.

## Record

```json
{
  "thread_id": "",
  "provider": "gmail|outlook",
  "subject": "",
  "stage": "opt_in|connection",
  "parent": null,
  "type": "fundraising|hiring|customer|advisor|portfolio|community|other",
  "campaign": "",
  "parties": [{"name": "", "email": "", "role": "owes_reply|requester"}],
  "sent_at": "",
  "state": "open|replied|meeting_booked|dormant|excluded",
  "replied_at": null,
  "replied_after_nudge": false,
  "nudges": [{"draft_id": "", "created_at": "", "status": "draft|sent|discarded"}],
  "hold_until": null,
  "notes": ""
}
```

`type` comes from the intro's content or the user's label; ask the user once when it's unclear and remember the answer. `campaign` is optional and set by the user (for example "Q4 customer intros for portfolio").

## Each sweep

1. For every open record, re-read the thread.
2. Reply from an `owes_reply` party, or a "moved to bcc" message: `state = replied`, record `replied_at` and whether any nudge had been sent.
3. Out-of-office with a return date: set `hold_until` to one business day after it.
4. Reply-in-motion signals (a promise to reply later, a scheduling link, a calendar invite, a user reply): skip this sweep; re-check next sweep.
5. Previous draft still in Drafts: leave it. Draft gone and a matching message in Sent: `status = sent`. Draft gone with nothing sent: `status = discarded` and stop nudging this stage.
6. Otherwise, if business days since the later of `sent_at` and the last sent nudge are at least the window (3 for the first nudge, 5 for the second by default), the number of sent nudges is below the cap (2), and `hold_until` has passed: draft a nudge.
7. Sent nudges at the cap and the window passed again: `state = dormant`.

## Scoreboard definitions

- **Sent**: connection-stage intros in the period (opt-in requests reported separately).
- **Mature**: sent at least one first-nudge window ago.
- **Replied**: `state` in replied or meeting_booked.
- **Reply rate** = replied ÷ mature. Show the denominator. Fewer than 5 mature in a group: show counts only.
- **Open**: open and not dormant. **Dormant**: cap reached, no reply.
- **Replied after a nudge**: replied with at least one sent nudge before `replied_at`.
- **Median days to first reply**: over replied intros.
- **Meeting booked**: only with evidence in the thread or on the user's calendar.

Sheet columns, if the user keeps a sheet: `Sent | Subject | Type | Campaign | Parties | State | Nudges sent | Replied on | Replied after nudge | Thread link`.
