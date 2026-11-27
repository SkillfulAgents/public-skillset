---
category: Productivity
icon: list-checks
avatar:
  color: tonal-white
  shape: arch
tags:
  - Engineering Management
  - Team Updates
  - Pull Requests
  - GitHub
  - Linear
  - Jira
works_with:
  - type: api_account
    slug: github
  - type: api_account
    slug: linear
  - type: api_account
    slug: jira
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Team Progress Digest

> See what your team shipped and where they are stuck every morning, without asking anyone for a status update.

## What it does

Team Progress Digest reads your team's pull requests in GitHub and issues in Linear or Jira, and every weekday morning sends you one short digest:

- **Needs you** — questions addressed to you, items labeled as waiting on a decision, reviews requested from you, and anything blocked on you.
- **Stuck** — PRs waiting on review, failing checks, conflicts, and issues that have sat in progress or review past your thresholds, each with how long it has been stuck.
- **Shipped** — merged to the default branch or completed, with the PR and its issue shown together.
- **In progress** — what is actively moving.

Items are grouped by project or by person, and every line links to the PR or issue. Dependency-update PRs collapse to one line. An optional Friday digest adds the week's synthesis, a few computed measures such as review wait time, and up to three evidence-backed signals worth watching.

It is strictly read-only and is not a performance tool: it never ranks people by output. For a summary of what AI agents did, use Swarm Daily Summarizer instead.

## What you'll need

- **GitHub** — required if your team uses GitHub. Read as you, or through the agent's own GitHub app scoped to the repos you choose.
- **Linear** — or **Jira**, for issues, projects, and blocked relations. GitHub Issues alone also works.
- **A delivery channel** — the agent's own Slack app (a DM to you or a team channel), its own email inbox, Telegram, or iMessage. In-app only also works.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects GitHub and your tracker, picks the repos, teams, and people in scope, sets what counts as stuck and how decisions are labeled, and chooses when and where the digest arrives.
3. It builds a digest for the last two business days as a supervised dry run, then schedules the daily run and the optional Friday digest.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- What did the team ship yesterday, and what is stuck right now?
- Show me every PR waiting on review for more than two days
- Every Friday at 4pm, send me the weekly digest with what to watch

## What's inside

- `AGENTS.md` — the daily and weekly digests, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects sources, sets scope and thresholds, schedules the digests, and writes `config.json`.
- `.claude/skills/stuck-signals/` — stuck and waiting-on-decision rules, plus the GitHub, Linear, and Jira queries and PR-to-issue linking.

## Notes

- Monday's digest covers Friday through Monday morning. If a source cannot be read, the digest says so instead of reporting a quiet day.
- Stuck items go to you privately by default. Posting to a team channel is opt-in.
