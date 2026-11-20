---
name: agent-onboarding
description: 'First-run setup for X Bookmark Sweep: connects the user''s own X account, notes doc and task tool, agrees on likes, backfill and a cost estimate, sets the evening schedule, and runs a supervised first sweep.'
first_prompt: 'Set up X Bookmark Sweep for me'
---

# X Bookmark Sweep onboarding

Run this before first use. Reuse anything already in `CLAUDE.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

In two or three sentences: a few evenings a week the agent pulls what the user bookmarked (and optionally liked) on X since the last run, reads each thread and linked article, files takeaways into a notes doc by topic, adds implied tasks to their task list, keeps a reading queue, and sends a short recap. It only reads; it never posts. Then list the questions:

1. Connect your X account
2. Bookmarks only, or likes too
3. Where the notes should live, and your topics
4. Which task tool, and which projects you're working on
5. How far back to start, and the cost estimate
6. Where the recap goes, and which evenings

## 2. Connect X

1. Read `/opt/gamut/docs/x.md`.
2. `mcp__user-input__search_connection_options` for X. If `twitter` is offered as a connected account, request it with `mcp__user-input__request_connected_account`, `toolkit: "twitter"`, reason "Allow access to X to read your bookmarks and likes since the last sweep?". If this host cannot connect X accounts, tell the user plainly that the sweep needs their own X account and stop here.
3. Call `GET /2/users/me` once and store the user ID and handle in config.

## 3. Ask the critical questions, one at a time

1. **Likes.** Use `AskUserQuestion`: bookmarks only (recommended, less noise and lower cost), bookmarks and likes, or likes only.
2. **Notes location.** Use `AskUserQuestion`: Notion, Google Docs, or a Markdown file in the workspace. Check with `search_connection_options`, then connect `notion` or `googledocs` with `request_connected_account`. Ask for an existing page or doc to append to, or create a new one called "X notes".
3. **Topics.** Ask for the topics they care about (for example AI tooling, growth, design, hiring). These become the first headings. New topics may be added; merges are proposed, never silent.
4. **Task tool.** Use `AskUserQuestion`: Todoist, Linear, Notion, or no tasks (keep them in the notes doc). Connect it (`todoist`, `linear` or `notion`). Ask which project, team or database, and whether tasks go in directly (default, into a dedicated "From X" project, label or view) or are only proposed in the recap.
5. **Current projects.** Ask what they are working on now, so "idea for current work" tasks can be specific.
6. **Reading queue.** Where it lives (top of the notes doc by default) and the cap (default 15).
7. **Backfill and cost.** Using the `x-incremental-pull` skill, give three estimates with real numbers: start from today, the last 50 items, or a bigger backfill (up to the cap they choose). Then estimate the ongoing cost from their own habits (ask roughly how many posts they bookmark and like a week). Label every figure as an estimate and get an explicit OK. Save the page size, page cap and per-run item cap.
8. **Recap delivery.** Use `AskUserQuestion`: in-app only, the agent's Slack app DM, the agent's own email inbox, Telegram, or iMessage. Check `mcp__chat__list_agent_integrations`; set up a missing one with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and resolve the exact destination.
9. **Schedule and timezone.** Default Monday, Wednesday and Friday at 20:00. Ask whether they want the optional Sunday weekly digest.

## 4. Supervised first sweep

Pull according to the backfill choice. Process the items and show the user, before writing anything: the proposed notes grouped by topic, the tasks you would create, the reading-queue additions, the skipped items, and anything unreadable. Iterate once on note length, task wording and the like bar. Then write to the notes doc and task tool, fill the seen and task ledgers, and show the recap as it will look.

## 5. Schedule

Create the sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, default `0 20 * * 1,3,5`. Self-contained prompt, for example:

> Run the X Bookmark Sweep. Read config from `.claude/skills/agent-onboarding/config.json` and context from `CLAUDE.md`. Using the `twitter` connected account and the `x-incremental-pull` skill, pull new bookmarks (and likes if enabled) newest first, stopping at IDs in `/workspace/state/x-bookmark-sweep/seen.json` or at the configured caps. Read each item fully: full text, the author's thread if under 7 days old, quoted posts, and linked articles with web fetch. File takeaways under topic headings in the configured notes doc with source links, add specific tasks to the configured task tool without duplicates (check `tasks.json`), update the reading queue, and update the ledgers. Never post, like, follow or change bookmarks. If new items came in, send a short recap to the configured destination with `mcp__chat__send_chat_message`; otherwise send nothing.

If enabled, add the weekly digest (`0 19 * * 0`) with a self-contained prompt that reads only the notes doc and ledgers and makes no X calls.

Confirm with `mcp__user-input__list_scheduled_tasks`.

## 6. Save configuration

Write the answers into `CLAUDE.md` under `## Your context`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "Europe/London",
  "x_user_id": "",
  "x_handle": "",
  "sources": {"bookmarks": true, "likes": false},
  "pull": {"page_size": 20, "max_pages": 3, "max_items_per_run": 60, "thread_max_posts": 25},
  "backfill": "today | last_50 | custom",
  "accepted_cost_estimate": {"per_run_usd": 0.0, "per_week_usd": 0.0},
  "notes": {"tool": "notion | googledocs | markdown", "location": "", "topics": []},
  "tasks": {"tool": "todoist | linear | notion | none", "project": "", "mode": "add | propose"},
  "current_projects": [],
  "reading_queue": {"location": "notes_top", "cap": 15},
  "delivery": {"via": "in-app | slack | email | telegram | imessage", "destination": ""},
  "schedules": {"sweep_cron": "0 20 * * 1,3,5", "digest_cron": null}
}
```

Finish with a summary: when it runs, where notes and tasks go, the accepted cost estimate, and how to re-run onboarding.
