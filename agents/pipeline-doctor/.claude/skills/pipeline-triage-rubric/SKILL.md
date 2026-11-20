---
name: pipeline-triage-rubric
description: 'Rules for flagging stale or sloppy deals, deciding whether a stalled deal deserves a nudge, and scoring closed-lost deals for win-back. Use in every Pipeline Doctor run.'
---

# Pipeline triage rubric

Thresholds below are defaults. Values in `.claude/skills/agent-onboarding/config.json` override them.

## Hygiene flags (routine 1)

Assign one primary group in this order of precedence; list the others as secondary.

| Group | Flag when | Default threshold | Fix to suggest |
|---|---|---|---|
| Past-due close date | close date < today | any | Reset to a date tied to a named buyer event, or close it |
| Past-due close date (pushed) | close date changed 2+ times | 2 pushes | Ask what changed; reset once with a reason in the note |
| Gone quiet | no two-way activity | 14 days (early stage), 7 days (late stage) | Book a next step or draft a nudge |
| Gone quiet | no future next step scheduled | any open deal | Log a dated next step |
| Missing data | amount, close date, stage or primary contact blank | any | Fill the named field |
| Missing data | owner inactive, or duplicate open deal for the same company | any | Reassign or merge |
| Stuck in stage | days in current stage > 1.5x the user's median for that stage | 1.5x | Move forward, back, or close |

"Two-way activity" = an inbound email, a held meeting, or a connected call. Outbound-only touches do not count.

Rank: sum at-risk dollars per group to order the groups; inside a group sort by amount descending, then stage order descending (latest stage first).

## Stalled-deal triage (routine 2)

Ask in order. Stop at the first "yes".
1. Did the contact opt out or ask to stop? -> no draft.
2. Does the user owe the next move? -> flag "you owe this", draft the deliverable cover note.
3. Is there a known waiting reason with a date in the future? -> "waiting, not stalled", recheck after that date.
4. Was the last touch less than the minimum gap ago (default 5 business days)? -> skip, too soon.
5. Two unanswered nudges already? -> draft a polite close-out question.
6. Champion silent but another contact active? -> draft to the other contact.
7. Otherwise -> draft a nudge with one concrete reason and one ask.

Banned phrases in any draft: "circling back", "just checking in", "bumping this", "touching base", "following up on my last email", "any update?".

## Win-back scoring (routine 3)

Loss reason (changeable): timing 3, budget 3, no champion / champion left 3, chose competitor 2, did nothing 2, missing feature now shipped 3. Not changeable: 0, drop.

Trigger (take the strongest one, must be cited and dated):
- new funding round in the last 90 days: 3
- new leader in the buying function in the last 120 days: 3
- competitor stumble (outage, price hike, sunset, acquisition): 3
- feature shipped that fixes the loss reason: 3
- competitor contract likely up for renewal (10-13 months since loss): 2
- relevant expansion, launch or hiring surge: 2
- new fiscal year after a budget loss: 2
- only elapsed time (6+ months): 1

Fit: original amount in the top half of the user's deals +1.

Shortlist at score >= 5 with a trigger of 2 or more. 4, or any uncertainty about opt-out status, goes to borderline. Below 4 is not reported.

## Ledger shape

`/workspace/state/pipeline-doctor/winback-ledger.json`:

```json
{
  "deals": {
    "<crm-deal-id>": {
      "last_considered": "2026-11-15",
      "trigger": "Series B announced 2026-10-30 (source URL)",
      "draft_created": true,
      "outcome": "pending",
      "next_eligible": "2027-02-15"
    }
  }
}
```
