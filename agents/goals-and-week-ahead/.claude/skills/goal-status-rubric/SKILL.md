---
name: goal-status-rubric
description: 'How to compute pacing and assign on track, at risk, off track, or no fresh data to a goal, and how to name and evidence the reason for a slip. Use on every weekly goal readout.'
---

# Goal status rubric

## Pacing

Let `elapsed = (today - period_start) / (period_end - period_start)`, between 0 and 1.

| Curve in goal map | Expected value now |
|---|---|
| `linear` | `baseline + (target - baseline) × elapsed` |
| `back_loaded` | `baseline + (target - baseline) × elapsed²` |
| `milestone` | no value; compare each milestone's due date with its actual state |

For a "lower is better" goal (churn, cost, cycle time), flip the comparison. `pace = progress_made / progress_expected`, where progress is measured from the baseline.

## Status

| Status | Numeric goals | Milestone goals |
|---|---|---|
| On track | pace ≥ 0.9, or target already hit | every milestone due so far is done |
| At risk | 0.7 ≤ pace < 0.9, or pace ≥ 0.9 but the workstream shows no activity for 10+ days | one milestone late by under two weeks |
| Off track | pace < 0.7, **and** activity evidence agrees | a milestone late by two weeks or more, or the final date is no longer reachable on current evidence |
| No fresh data | source unchanged since last snapshot, or unreadable | no tracker activity and no update |

Stretch goals: shift the thresholds down by 0.2 (on track at 0.7, at risk from 0.5).

Never call a goal off track on the number alone. If the number says off track but activity is strong (many issues closing, a big deal in late stage), mark it at risk and say why the number may lag. If the number says on track but the work has gone silent, mark at risk ("number fine, work stalled").

Before the first ten percent of a period has elapsed, report movement only, no status.

## Reasons (pick one primary, optionally one secondary)

| Reason | Typical evidence |
|---|---|
| Blocked on dependency or person | issue marked blocked or has a blocking relation; "waiting on" in a thread |
| Waiting on the user's decision | open question addressed to the user in mail, notes, or a comment |
| Deprioritized | owner's recent activity is concentrated in other projects; issues moved out of the cycle |
| Capacity | owner out of office, team member left, cycle over-committed |
| Scope grew | many issues added to the project since last week |
| External | customer, vendor, or regulator delay named in mail or notes |
| Measurement | metric definition or source changed; numbers jumped without matching activity |
| Unknown | not enough evidence; say so and suggest asking the owner |

Cite one or two concrete pieces of evidence, each with a link. Never assert a reason without one; use "Unknown" instead.

## Week-over-week

`delta = current - last_snapshot_value`. Show it with direction ("+12 to 148", "flat", "-3"). If last week had no value, show "new".
