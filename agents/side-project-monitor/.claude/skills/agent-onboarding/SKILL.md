---
name: agent-onboarding
description: 'First-run setup for Side Project Monitor: connects analytics, the GitHub repo and optional Stripe and infra sources, proposes the watchlist, seeds the baseline, sets the daily brief schedule and delivery, and runs a supervised first brief.'
first_prompt: 'Set up Side Project Monitor for my project'
---

# Side Project Monitor onboarding

Run this before first use. Reuse anything already in `AGENTS.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

In two or three sentences: every morning the agent reads the project's analytics, repo and (optionally) payments and hosting costs, and sends a short brief on what needs a decision. It picks the metrics worth watching itself and never changes code or settings. Then list the questions:

1. What the project is and where it lives (URL, repo)
2. Which analytics you use
3. Whether it takes payments, and where it is hosted
4. Any budget or plan limits to protect
5. Where and when the brief should arrive
6. Your sign-off on the watchlist the agent proposes

## 2. Discover and connect

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected.

1. **Project basics.** Ask for the project name, its URL and the GitHub repo (owner/name).
2. **GitHub.** `mcp__user-input__request_connected_account`, `toolkit: "github"`, reason "Allow access to GitHub to read commits, deploys and issues for the project?". Read only.
3. **Analytics.** Use `AskUserQuestion`: PostHog, Google Analytics, both, or none yet. PostHog via `mcp__user-input__request_remote_mcp` (URL from `search_connection_options`), GA4 via connected account `google_analytics`. Ask which project or property. If none, say the brief will lean on GitHub, payments and costs, and suggest adding analytics.
4. **Payments.** Ask whether the project takes payments with Stripe. If yes, connected account `stripe` (read only).
5. **Hosting, database, errors, AI APIs.** Ask which services the project runs on. Also read the repo for clues (`vercel.json`, `netlify.toml`, `fly.toml`, `supabase/`, Sentry or AI SDK dependencies) and confirm. For each, check `search_connection_options`. Use a connected account or MCP if offered. If not, offer an API token via `mcp__user-input__request_secret` with a clear name (`VERCEL_TOKEN`, `SUPABASE_ACCESS_TOKEN`, `SENTRY_AUTH_TOKEN`, an AI provider usage key), asking for the narrowest read-only scope that service allows. Skipping is fine; the brief marks those costs as not covered.

## 3. Ask the critical questions, one at a time

1. **What success looks like now.** Use `AskUserQuestion`: getting first users, growing signups, converting to paid, keeping costs near zero, or keeping it alive with little effort. This weights the watchlist.
2. **Key action.** What is the one thing a user does that shows they got value (the activation event)? Offer event names found in analytics.
3. **Budget.** Monthly spend they are comfortable with, and the daily cost floor below which spikes are not worth a message (default $5).
4. **Plan limits.** Which plans they are on (free or paid tiers), so the agent can warn before limits.
5. **Quiet days.** Use `AskUserQuestion`: a one-line "all steady" message, or nothing at all on quiet days.
6. **Delivery.** Use `AskUserQuestion`: in-app only, the agent's Slack app DM, the agent's own email inbox, Telegram, or iMessage. Check `mcp__chat__list_agent_integrations`; set up a missing one with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and resolve the exact destination.
7. **Time and timezone.** Default 08:00. Ask whether they want the optional every-2-hours cost and outage watch.

## 4. Propose the watchlist

Follow routine 1 in `AGENTS.md` and the menu in the `metrics-baseline` skill. Present 6 to 10 metrics as a short table: metric, why it matters for this project, source, alert rule, and "measurable now?" with the smallest fix if not. Let the user add, drop or adjust, then confirm.

Seed the baseline: pull the last 28 days for each metric where the source allows, write daily files under `/workspace/state/side-project-monitor/daily/`, and compute `baseline.json`. Say which metrics have no history yet and need a couple of weeks before alerts are reliable.

## 5. Supervised first brief

Run the daily brief on yesterday's data and show it in chat. Check with the user: is it short enough, are the priorities right, are any alerts noise? Adjust once. Then send it to the chosen destination so they see how it arrives.

## 6. Schedule

Create the daily brief with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, default `0 8 * * *`. Self-contained prompt, for example:

> Run the Side Project Monitor daily brief for the project in `.claude/skills/agent-onboarding/config.json`. For each watchlist metric, pull yesterday's value and the 7-day rolling value from its configured source; pull the last 48 hours of commits, merged PRs, deploys, failing CI, security alerts and new issues from GitHub. Compare with `/workspace/state/side-project-monitor/baseline.json` using the `metrics-baseline` skill, check regressions against deploy times, classify findings as Act now, Look this week or Good news, and add at most two data-grounded ideas. Report missing sources as missing, never zero. Save today's values, update the baseline and `alerts.json`, then send the brief to the configured destination with `mcp__chat__send_chat_message`, following the quiet-day setting. Read only: never change code or settings.

If enabled, add the cost and outage watch (`0 */2 * * *`) that alerts only on threshold breaches with a 12-hour cooldown, and the monthly watchlist review (`0 9 1 * *`) that messages only if it has a change to propose.

Confirm with `mcp__user-input__list_scheduled_tasks`.

## 7. Save configuration

Write the answers and the confirmed watchlist into `AGENTS.md` under `## Your context`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "project": {"name": "", "url": "", "repo": "owner/name", "default_branch": "main"},
  "timezone": "America/Los_Angeles",
  "goal": "first_users | grow_signups | convert_paid | low_cost | low_effort",
  "sources": {
    "analytics": {"tool": "posthog | google_analytics | none", "project": "", "activation_event": ""},
    "github": true,
    "stripe": false,
    "infra": [{"service": "vercel", "via": "connected_account | mcp | secret", "secret_name": "VERCEL_TOKEN", "plan": "free"}]
  },
  "budget": {"monthly_usd": 0, "daily_cost_floor_usd": 5},
  "plan_limits": [{"service": "", "meter": "", "limit": 0, "unit": ""}],
  "watchlist": [
    {"id": "activation_rate_7d", "definition": "", "source": "posthog", "rule": "look_this_week if outside typical range 2 days running", "measurable": true}
  ],
  "quiet_day": "one_line | silent",
  "delivery": {"via": "in-app | slack | email | telegram | imessage", "destination": ""},
  "schedules": {"brief_cron": "0 8 * * *", "watch_cron": null, "review_cron": "0 9 1 * *"},
  "widget": false
}
```

Finish with a summary of what runs when, what is covered and what is not, and mention the optional home-screen widget for one key number, which can be added later.
