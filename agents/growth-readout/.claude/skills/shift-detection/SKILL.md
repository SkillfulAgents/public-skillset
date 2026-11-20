---
name: shift-detection
description: 'Rules for deciding whether a week-over-week or baseline change in a segment, channel or metric is a real shift worth reporting or ordinary noise. Use in the weekly Growth Readout before writing the what-is-shifting section or calling out a sharp move.'
---

# Shift detection

Use these rules before any change goes into the readout as a "shift" or a "sharp move". The goal is a handful of real changes, not a list of every number that moved.

## Inputs

- This week's count for the segment (signups, pipeline records, pipeline value, conversions).
- The baseline: the mean and spread of the same count over the trailing N complete weeks (default 8), read from `/workspace/state/growth-readout/weekly/`.
- The segment's share of the week's total, and its baseline share.
- Field completeness: the share of this week's records where the segment field is filled.

## A change qualifies when all of these hold

1. **Big enough to matter.** At least 5 records this week (or 5 on average in the baseline, for a drop), or at least 10% of the week's total.
2. **Outside normal variation.** Either the count is more than about 2 standard deviations from the baseline mean, or the segment's share moved by at least 5 percentage points and at least 50% relative.
3. **Not mechanical.** You checked for: CRM field or picklist changes, a new or changed form, an enrichment backfill, a bulk import, a single rep or source creating many records, UTM changes, tracking breaks, holidays and launches. Name what you checked.
4. **Field is trustworthy.** If the segment field is under about 70% complete this week, or its completeness changed by more than 10 points, downgrade the shift to "possible" and say why.

## Special cases

- **New segment.** A segment with zero baseline records that shows 3 or more this week can be reported as "new, early" with the records linked, even below the size bar. Do not call it a trend until it repeats.
- **Going quiet.** A segment averaging 3 or more per week in the baseline with zero for two consecutive weeks qualifies.
- **Persistence.** A change below the variation bar that has moved in the same direction for three consecutive weeks qualifies as a slow shift.
- **Mix shift.** If the total is flat (within about 10%) but two segments moved in opposite directions by the amounts above, report it as one mix shift, not two.
- **Small totals.** If the whole week has fewer than about 30 records, skip statistical language and describe counts plainly; still apply the mechanical checks.

## Writing a shift

One short paragraph each:
- **What changed**: plain sentence, segment named.
- **Evidence**: this week vs. baseline (counts and share), field completeness, records or saved view linked.
- **What it might mean**: one or two interpretations, stated as possibilities.
- **Suggested move**: one concrete next step (a message test, a budget check, a sales follow-up, a tracking fix).

Record each reported shift in `/workspace/state/growth-readout/shifts.json` with the week, segment, direction and status, so next week can say "continuing" or "faded" instead of repeating it as new.
