---
category: Productivity
icon: target
tags:
  - OKRs
  - Goal Tracking
  - Weekly Planning
  - Leadership
  - Linear
works_with:
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: linear
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googledocs
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Goals and Week Ahead

> Know which goals are slipping and why before your Monday meeting, and start every week with a plan instead of an inbox.

## What it does

Goals and Week Ahead reads each company goal from wherever its number really lives, whether a sheet, a CRM report, an analytics metric, or a Linear project, and judges it against the actual work behind it. Every Monday, or two hours before your leadership meeting, you get a one-page readout with at-risk goals first: current vs. target, week-over-week movement, owner, blocker, and the reason behind each slip. Reasons are drawn from Linear, Jira, and GitHub activity, email threads, and meeting notes, and each one cites its evidence.

For every slipping goal, it drafts a short, collegial nudge to the owner in your Gmail or Outlook for you to review. On Sunday evening it writes the coming week's plan into a living doc: your top three to five priorities tied to goals, what rolled over from last week, calendar notes such as overloaded days and focus blocks, and the conversations to have.

The readout is for your eyes only, and nothing is sent to anyone without you.

## What you'll need

- **Goal sources** — whatever holds each number: Google Sheets, Google Docs, Notion, HubSpot, Salesforce, Stripe, PostHog, and similar. Onboarding maps each goal to its source.
- **Linear** — recommended for work evidence. Jira, GitHub, or Asana also work.
- **Gmail** — required for owner status emails and nudge drafts. Outlook also works.
- **Google Calendar** — required for leadership meeting timing and the week-ahead calendar notes.
- **Google Docs** — for the week-ahead plan. Notion also works.
- **Meeting notes** — optional: Granola, Fathom, Fireflies, Otter, Gong, or Zoom.
- **API keys:** none for the common sources. A key-only metrics service can be added as a secret.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. You paste or point to your goals, and it walks through them one at a time to tie each to the source of its real number, its owner, its target, and how it should pace. Then it connects your work and calendar tools and picks where things land.
3. It builds this week's readout as a supervised dry run, so you can correct numbers, owners, and diagnoses before the weekly schedule starts.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Map our Q4 goals to where each number actually lives
- Which goals are at risk this week, and why? Draft nudges to the owners
- Every Sunday at 6pm, draft my week-ahead plan in Google Docs

## What's inside

- `CLAUDE.md` — the readout, owner nudges, and week-ahead routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that builds the goal map, connects sources, sets schedules, and writes `config.json`.
- `.claude/skills/goal-status-rubric/` — pacing math, status thresholds for committed and stretch goals, and the named reasons for a slip with the evidence each needs.

## Notes

- A goal is never called off track on the number alone. The work behind it has to agree, and the evidence is linked.
- Stale or missing numbers are labeled as such, never carried forward or estimated.
- Each week's plan is a new section at the top of the doc, so your edits to earlier weeks are never overwritten.
- Pairs with Open Loops and Meeting Actions, which can feed open commitments and leadership decisions into the plan.
