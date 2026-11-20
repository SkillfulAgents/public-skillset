---
name: finance-checks
description: 'Formulas (net burn, runway, burn multiple, variance, materiality) and the data-error checks to run before any cash update, variance commentary or board pack.'
---

# Finance formulas and data checks

Always state the method next to the number in the user's output the first time it appears.

## Formulas

- **Net burn (period)** = beginning cash - ending cash, excluding financing inflows (equity, debt draws) and adding back debt repayments only if the user's convention says so. Positive means cash went down.
- **Average net burn** = mean of the last 3 months of net burn. Use for runway unless the user picks another window.
- **Runway (months)** = unrestricted cash / average net burn. If average net burn is zero or negative, report "cash-flow positive", not a runway.
- **Gross burn** = total cash out in the period (operating), before receipts.
- **Variance** = actual - budget (or forecast). **Variance %** = variance / |budget|. If budget is zero, report "unbudgeted" instead of a percent.
- **Favorable / unfavorable**: revenue and other income, actual above plan is F. Costs, actual above plan is U.
- **Material** if |variance| >= threshold_amount AND |variance %| >= threshold_pct (from config), OR the line is new, unbudgeted, or flagged by a data check.
- **Burn multiple** = net burn / net new ARR for the same period. Undefined if net new ARR <= 0.
- **MRR from Stripe**: active subscriptions normalized to monthly (annual / 12, quarterly / 3), after discounts, excluding trials, one-time items and tax. State currency handling.

## Data-error checks (run first, report in a "data issues" section)

| Check | Rule of thumb |
|---|---|
| Sign flip | A line whose sign is opposite to its usual sign (negative revenue, negative rent). |
| Missing month | A recurring line that is zero or blank this month but non-zero in each of the prior 3. |
| Doubled line | This month is 1.9-2.1x the trailing average, or two bills share vendor, amount and invoice number. |
| Miscoding | One account or department up and another down by about the same amount. |
| Stale source | Bank feed or sheet last updated more than 2 business days ago; forecast tab unchanged since last month. |
| Truncated export | Row count or totals don't match the source's own total. |
| Doesn't tie | Ending cash vs. bank, revenue vs. Stripe (beyond known timing), last pack's ending figure vs. this pack's starting figure. |

A failed check never gets silently corrected. Report it, keep the original value, and say what you think the right value is only if a source proves it.
