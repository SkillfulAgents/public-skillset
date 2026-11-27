---
name: agent-onboarding
description: 'First-run setup for Team Progress Digest: connects GitHub and Linear or Jira, sets the repos, teams, and people in scope, the grouping, stuck thresholds and decision labels, delivery and timing, then runs a supervised digest and schedules it.'
first_prompt: 'Set up Team Progress Digest for me'
---

# Team Progress Digest onboarding

## 1. Welcome

Explain in two sentences: every weekday morning this agent tells you what your team shipped, what is in progress, and what is stuck, from GitHub and Linear or Jira, with every item linked and the items that need you first. It only reads; it never touches a PR or issue. Show the plan:

1. Connect GitHub and your tracker.
2. Pick the repos, teams, and people in scope.
3. Group by project or by person.
4. What counts as stuck, and how a "needs a decision" item is marked.
5. When and where the digest arrives, and whether you want a Friday weekly.
6. A supervised first digest.

Skip anything already in `## Your context`.

## 2. Discover connections

Call `mcp__user-input__search_connection_options` for GitHub, Linear, and Jira, and `mcp__chat__list_agent_integrations` for delivery. Ask with `AskUserQuestion`: read GitHub and Linear as you (connected account; sees everything you see, simplest) or through the agent's own GitHub or Linear app (scoped to what you install it on; better for larger orgs)? Default: as you.

## 3. Ask, one question at a time

1. **Tracker.** Linear, Jira, or GitHub Issues only?
2. **Scope.** Which GitHub org and repos? Which Linear teams or projects, or Jira project keys? Offer the list you can see and let the user pick.
3. **People.** Who is on the team? Pre-fill from recent PR authors and issue assignees; the user removes anyone out of scope and marks any automation accounts.
4. **Grouping.** By project or by person? (Default: project.)
5. **Your identity.** Confirm the user's GitHub login and tracker user, so "Needs you" works.
6. **Decision labels.** Which labels or statuses mean "waiting on a decision"? Offer the defaults from the `stuck-signals` skill and any matching labels found in the tracker.
7. **Stuck thresholds.** Accept the defaults (review waiting 2 business days, in-progress silent 5, and so on) or adjust?
8. **Time off.** Is there a shared out-of-office calendar the agent can read? (Optional.)
9. **Delivery.** (Agent's Slack DM / A team Slack channel / Agent's email to you / Telegram / iMessage / In-app only.) If a team channel: confirm that stuck items will be visible to the team.
10. **Timing.** Daily at 8am weekdays in your timezone? Also a fuller Friday 4pm weekly? (Yes / No.)
11. **Quiet days.** When nothing moved: send one line, or nothing?

## 4. Connect

- `mcp__user-input__request_connected_account` with `github`, `linear`, or `jira`; reason text such as "Allow access to GitHub to read pull requests for the daily team digest?"
- Or set up the agent's own GitHub or Linear app: `mcp__chat__list_available_integration_providers`, then `mcp__user-input__request_integration_setup` (these providers usually hand setup to the user), and confirm with `mcp__chat__list_agent_integrations`.
- Delivery: an existing agent integration, or `mcp__chat__add_agent_integration`. For a team channel, confirm the agent's Slack app is in it with `mcp__chat__list_chat_channels`.

## 5. Supervised dry run

Build a digest for the last two business days with the `stuck-signals` rules and show it in chat. Ask: missing repos or projects, wrong "stuck" calls, noise to collapse, too long or too short. Adjust config and rebuild once. Save the high-water marks to `/workspace/state/team-progress/runs.json`.

## 6. Schedule

`mcp__user-input__schedule_task`, `scheduleType: "cron"`:

- Daily, e.g. `0 8 * * 1-5`:

> Run the Team Progress Digest **daily digest**. Config: `/workspace/.claude/skills/agent-onboarding/config.json`. High-water marks: `/workspace/state/team-progress/runs.json`; stuck ages: `stuck.json`. Follow `AGENTS.md` and the `stuck-signals` skill. Group by `<project|person>`. Order: Needs you, Stuck, Shipped, In progress; link every item. Deliver via `send_chat_message` on integration `<id>` to `<destination>`. Read-only: never write to GitHub, Linear, or Jira. Quiet day: `<one line|nothing>`. If a source fails, name it at the top. Update `runs.json` when done.

- Weekly (if chosen), e.g. `0 16 * * 5`, with the same rules plus the weekly section of `AGENTS.md`.

Confirm with `mcp__user-input__list_scheduled_tasks` and show the user.

## 7. Save

Write answers under `## Your context` in `AGENTS.md`, and create `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "read_as": "user",
  "github": {"org": "example-org", "repos": ["example-org/app"], "default_branch_only": true},
  "tracker": {"type": "linear", "teams": ["ENG"], "projects": [], "jira_projects": []},
  "team": [{"name": "Teammate", "github": "teammate", "tracker_user": "teammate@example.com"}],
  "automation_authors": [],
  "me": {"github": "", "tracker_user": ""},
  "grouping": "project",
  "decision_labels": ["needs decision", "needs-decision", "blocked: decision", "question"],
  "stuck_thresholds": {"review_wait": 2, "changes_requested_idle": 3, "failing_checks": 1, "conflicts": 2, "draft_idle": 5, "in_progress_idle": 5, "in_review": 3},
  "ooo_calendar_id": null,
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "daily": {"cron": "0 8 * * 1-5", "quiet_day": "one_line"},
  "weekly": {"on": true, "cron": "0 16 * * 5"}
}
```

Summarize what runs when, where it lands, and that the agent is read-only.
