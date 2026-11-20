---
name: metrics-baseline
description: 'Menu of metrics worth watching on a small product, the baseline file format, and the rules that separate a real cost spike, drop-off or regression from small-number noise. Use when proposing the watchlist and on every daily brief or cost check.'
---

# Metrics baseline

## Watchlist menu

Pick 6 to 10 that fit the project. Always include at least one from cost and one from reliability if a source exists.

| Area | Metric | Typical source |
|---|---|---|
| Acquisition | Visitors, signups, visitor-to-signup rate, top sources by signups | PostHog, GA4 |
| Activation | Share of new signups reaching the key first action within 24 hours or 7 days | PostHog events |
| Engagement | Daily and weekly active users, DAU/WAU ratio | PostHog |
| Retention | Share of a signup week still active 1 and 4 weeks later | PostHog |
| Funnel | Conversion of each step in the main flow (signup → setup → first value → upgrade) | PostHog funnels |
| Revenue | MRR, new and cancelled subscriptions, failed payments, past due, refunds, disputes | Stripe |
| Cost | Hosting usage and spend, function invocations and duration, bandwidth, database size and egress, AI API spend, cost per active user | Hosting, database, AI provider |
| Plan limits | Each usage meter as a share of its plan limit | Hosting, database |
| Reliability | Error events per 1,000 sessions or requests, new error types, failed deploys | Sentry, hosting, PostHog |
| Performance | Page load or web vitals on key pages, slow endpoints | PostHog, hosting |
| Code health | Failing CI on the default branch, open security alerts, PRs open more than 14 days | GitHub |
| Feedback | New issues from users, top requested features | GitHub issues |

## Baseline

- Keep each day's values in `/workspace/state/side-project-monitor/daily/<date>.json`:

```json
{"date": "2026-11-19", "metrics": {"signups": {"value": 14, "source": "posthog", "status": "ok"}, "vercel_bandwidth_gb": {"value": 3.2, "source": "vercel", "status": "provisional"}}}
```

- Recompute `/workspace/state/side-project-monitor/baseline.json` each run: for each metric, the median and the typical range (roughly the 10th to 90th percentile) over the last 28 days, the median for each weekday, and the last 7-day rolling value.
- Exclude days marked `missing` and days the user flagged as unusual (a launch, an outage) from the baseline.

## Flag rules

**Cost (most sensitive).**
- Act now: yesterday's cost or usage is more than 2x the 28-day median and more than a small absolute floor (default $5 a day or the user's own floor), or any meter passes 80% of a plan limit, or the projected month-end spend exceeds the user's budget.
- Projected month-end spend = spend so far this month ÷ days elapsed × days in month. Label it a projection.

**Revenue.**
- Act now: any new dispute (give the response deadline), a failed payment on an annual or large plan, or more than one failed payment in a day on a small base.
- Look this week: cancellations above the 28-day typical range; read and quote cancellation reasons if present.

**Traffic and funnel (least sensitive, because numbers are small).**
- Only judge rates when the base has at least about 50 events in the window; otherwise report counts and say "too small to call".
- Look this week: the 7-day rolling value is outside the typical range for the second day in a row, or a funnel step conversion fell by more than 25% relative on at least about 50 entrants.
- Same-weekday comparison beats day-over-day for anything with a weekly rhythm.

**Reliability and regressions.**
- Act now: error rate more than 3x baseline, a new error type affecting more than a handful of users, site or key endpoint failing, failing deploys on the default branch, a critical or high security alert.
- Regression check: compare the 24 hours after each deploy with the same hours on prior days. If a metric breaks its range right after a deploy, link the commit or PR as "lines up with".

**Tracking breaks.**
- An event that drops more than 80% in a day, or to zero, is first a suspected tracking break. Check recent commits for renamed or removed events before reporting a business drop.

## Cooldown

Do not repeat the same alert within 12 hours (cost and reliability) or 3 days (traffic and funnel) unless it gets worse. Record each in `alerts.json` and say when it resolves.
