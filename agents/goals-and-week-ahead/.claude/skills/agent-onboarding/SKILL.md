---
name: agent-onboarding
description: 'First-run setup for Goals and Week Ahead: builds the goal map (each goal tied to the source of its real number, its owner, and its pacing), connects activity sources, sets the readout and plan schedules, and runs a supervised first readout.'
first_prompt: 'Set up Goals and Week Ahead for me'
---

# Goals and Week Ahead onboarding

## 1. Welcome

Explain in three sentences: every week this agent reads your goals from wherever they really live, judges them against the actual work, explains each slip, drafts nudges for owners, and on Sunday evening writes your week-ahead plan. Show the plan:

1. List your goals for this period.
2. For each goal, where its number lives and who owns it.
3. Where the work happens (Linear, Jira, GitHub, email, meeting notes).
4. When your leadership meeting is and when you want the readout.
5. Where the week-ahead plan should live.
6. Where things should reach you, and what the agent does alone.
7. A supervised first readout.

Skip anything already in `## Your context`.

## 2. Collect the goals

Ask the user to paste their goals or OKRs, or point to the doc, deck, or sheet (`mcp__user-input__request_file` for an upload). Parse them into a draft list and show it back. Then go through the goals **one at a time**:

1. **Source.** Where does the current number for this goal come from? (A sheet cell or range / a CRM report / an analytics metric / a Linear or Jira project's progress / a status email the owner sends / a doc someone updates.) Get the exact location: sheet ID and range, report name, project key, sender and subject pattern.
2. **Target and baseline.** Confirm the target, the starting value, the period (quarter dates), and whether lower is better.
3. **Curve.** Linear, back-loaded, or milestones? For milestones, list them with due dates.
4. **Committed or stretch?**
5. **Owner.** Who owns it? If the doc doesn't say, propose the person who leads the matching project or sends the updates, and confirm.
6. **Workstream.** Which Linear, Jira, or GitHub projects, labels, or repos represent the work behind it?

For each source, call `mcp__user-input__search_connection_options`, then connect it (`request_connected_account`, `request_remote_mcp`, `request_secret`, or the browser with `request_login` as a last resort). Read the current value once to prove it works, and show it.

Goals whose number exists nowhere: offer to track them as milestone goals judged on activity, or ask the owner to update a cell each week. Never make the user maintain numbers by hand unless they choose to.

## 3. Ask, one question at a time

1. **Evidence sources.** Which of these should count as evidence? (Linear / Jira / GitHub / Email threads / Meeting notes.) Connect the ones chosen.
2. **Leadership meeting.** Which recurring meeting is it? Find it on the calendar and offer "two hours before" or a fixed time (default Monday 7am).
3. **Readout format and delivery.** (Agent's email to you / Agent's Slack DM / Telegram / iMessage / In-app only.) Also keep a private Google Doc copy? (Yes / No.)
4. **Nudges.** Draft nudges to owners of slipping goals? (Yes, as Gmail or Outlook drafts / Yes, as copy-ready text for Slack / No.) Anyone never to nudge?
5. **Plan doc.** Where should the week-ahead plan live? (Google Docs / Notion.) New doc or an existing one? The agent adds a new section each week at the top.
6. **Plan timing.** Confirm Sunday 6pm in your timezone, or pick another time.
7. **Sibling agents.** If Open Loops or Meeting Actions is installed, should the plan pull open loops and leadership open items from them? (Yes / No.)
8. **Autonomy.** Confirm: "The readout and the plan are built and sent to you alone. Nudges are drafts you send. Sources are read-only."

## 4. Connect delivery

Call `mcp__chat__list_agent_integrations`. If the chosen channel isn't set up, use `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`. Connect `gmail` or `outlook` for drafts, `googlecalendar`, and `googledocs` or `notion`.

## 5. Supervised dry run

Build this week's readout using the `goal-status-rubric` skill. Show it with every number linked to its source and every reason linked to its evidence. Show one sample nudge. Ask: wrong numbers, wrong owners, unfair diagnoses, tone. Fix the goal map and run again. Then build a sample week-ahead section and show it. Save the first snapshot under `/workspace/state/goals/snapshots/`.

## 6. Schedule

Create two tasks with `mcp__user-input__schedule_task`, `scheduleType: "cron"`:

- Readout, e.g. `0 7 * * 1`:

> Run the Goals and Week Ahead **weekly goal readout** and owner nudges. Config: `/workspace/.claude/skills/agent-onboarding/config.json`. Goal map: `/workspace/state/goals/goal-map.json`. Follow `CLAUDE.md` and the `goal-status-rubric` skill. Compare with the latest file in `/workspace/state/goals/snapshots/` and save a new one. Deliver to the user only via `send_chat_message` on integration `<id>`. Save nudges as drafts only; never send. If a source fails, name it in the readout and do not reuse old numbers. If the leadership meeting moved, adjust this task's time and tell the user.

- Plan, e.g. `0 18 * * 0`:

> Run the Goals and Week Ahead **Sunday week-ahead plan**. Config and goal map as above. Read last week's section of the plan doc `<doc id>` for checkmarks and edits, add a new section at the top, never edit older sections. Send the user the link and a three-line preview via `send_chat_message` on integration `<id>`.

Confirm with `mcp__user-input__list_scheduled_tasks` and show the user.

## 7. Save

Write answers under `## Your context` in `CLAUDE.md`. Write the goal map to `/workspace/state/goals/goal-map.json` and the config to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "period": {"name": "Q4 2026", "start": "2026-10-01", "end": "2026-12-31"},
  "leadership_meeting": {"event_id": "", "title": "Weekly leadership", "readout_offset_hours": 2},
  "evidence_sources": ["linear", "github", "gmail", "granola"],
  "readout": {"cron": "0 7 * * 1", "channel": "agent_email", "integration_id": "", "destination": "", "doc_copy": false},
  "nudges": {"mode": "gmail_drafts", "never_nudge": []},
  "plan": {"cron": "0 18 * * 0", "doc": {"type": "googledocs", "id": ""}, "pull_from_siblings": true},
  "autonomy": {"drafts_only": true, "share_readout": false}
}
```

Goal map entry shape:

```json
{
  "id": "g1",
  "name": "Reach 150 paying customers",
  "owner": {"name": "Head of Sales", "email": "sales-lead@example.com"},
  "source": {"type": "googlesheets", "sheet_id": "", "range": "Metrics!B4", "url": ""},
  "baseline": 92,
  "target": 150,
  "lower_is_better": false,
  "curve": "back_loaded",
  "milestones": [],
  "kind": "committed",
  "workstream": {"linear_projects": [], "jira_projects": [], "github_repos": [], "email_subjects": []}
}
```

Summarize what runs when and where it lands.
