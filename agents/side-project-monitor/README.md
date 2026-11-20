---
category: Productivity
icon: activity
tags:
  - Side Projects
  - Product Analytics
  - Cost Monitoring
  - Daily Brief
  - GitHub
  - PostHog
works_with:
  - type: mcp
    slug: posthog
  - type: api_account
    slug: google_analytics
  - type: api_account
    slug: github
  - type: api_account
    slug: stripe
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Side Project Monitor

> Production-grade monitoring for the project you build on weekends, in one short morning brief that tells you what to do and what can wait.

## What it does

Side Project Monitor watches a side project you don't have time to check. Every morning it reads your product analytics, the GitHub repo and, if you connect them, Stripe and your hosting, database, error-tracking and AI API costs. It then sends a brief that opens with a one-line verdict, then lists what needs action now, what to look at this week, and what went well.

You don't have to tell it what to watch. It proposes the 6 to 10 signals that matter for your project, such as activation, retention, failed payments, cost per active user and error rate after each deploy, and you confirm the list. It keeps a rolling baseline, so it can tell a real cost spike, drop-off or regression from the normal ups and downs of small numbers. When a metric breaks right after a deploy, it links the commit.

Each brief ends with up to two improvement ideas drawn from the data: a feature new users try and then abandon, a busy page people leave, a request that keeps coming up in issues. It only reads and reports. It never changes code, settings or billing.

## What you'll need

- **PostHog or Google Analytics**: one is strongly recommended, for traffic, activation, funnels and retention.
- **GitHub**: required, read only, for commits, deploys, CI status, security alerts and issues.
- **Stripe**: optional, for MRR, failed payments, cancellations and disputes.
- **Hosting, database and error tracking**: optional. Vercel, Supabase, Sentry and similar services connect through whatever the app offers, or a read-only token you create.
- **Slack, email, Telegram or iMessage**: optional. The agent's own account delivers the brief; otherwise it stays in the app.
- **API keys:** only for infra services with no other connection option, for example `VERCEL_TOKEN`, `SUPABASE_ACCESS_TOKEN` or `SENTRY_AUTH_TOKEN`, with read-only scopes.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It connects the repo and analytics, detects your hosting from the repo, asks about payments, budget and plan limits, proposes a watchlist for you to confirm, and fills in 28 days of baseline history.
3. Review a first brief on yesterday's data, then let the daily schedule run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- How did my project do yesterday, and does anything need me?
- What metrics should I be watching that I'm not, and why?
- Every morning at 8, send me the brief and alert me on any cost spike

## What's inside

- `CLAUDE.md`: the watchlist, daily brief and optional cost-watch routines, connection table, schedules, state files and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup for sources, budget, watchlist, baseline, delivery and schedule.
- `.claude/skills/metrics-baseline/`: the metric menu, baseline format and flag rules for cost, revenue, funnels and regressions.

## Notes

- Read only. It never opens pull requests, deploys, changes hosting or billing settings, refunds or rotates keys.
- Small projects have small numbers, so traffic and funnel alerts need a minimum volume. Cost and payment alerts are the most sensitive and can go out between briefs if you enable the cost watch.
- An optional home-screen widget can show one key number, such as weekly active users or MRR, with its trend.
