---
category: Productivity
icon: bookmark
avatar:
  color: tonal-white
  shape: bloom
tags:
  - X
  - Bookmarks
  - Knowledge Management
  - Reading List
  - Notion
  - Todoist
works_with:
  - type: api_account
    slug: twitter
  - type: api_account
    slug: notion
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: todoist
  - type: api_account
    slug: linear
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# X Bookmark Sweep

> Stop letting saved threads pile up unread: every few evenings they become notes, tasks and a short reading list.

## What it does

A few evenings a week, X Bookmark Sweep pulls everything you bookmarked on X since the last run, and your likes too if you want them. It reads each one in full: the whole thread, any quoted post and the linked article, not just the first line.

From that it keeps three things up to date:

- **A notes doc grouped by topic**, in Notion, Google Docs or a Markdown file. Each takeaway links back to the original post and article.
- **Tasks in your task list**, in Todoist, Linear or Notion. These are specific actions such as a tool to try, a person to contact or an idea for a project you're working on, each with its source link and never added twice.
- **A short reading queue** for the long pieces that deserve focused time.

You get a short recap after each sweep, and nothing at all when nothing new came in.

It only reads your own saved items. It never posts, replies, likes or follows, and never changes your bookmarks.

## What you'll need

- **X**: required. Your own X account, connected so the agent can read your bookmarks and likes.
- **Notion or Google Docs**: where the notes live. A Markdown file in the workspace works if you prefer neither.
- **Todoist, Linear or Notion**: recommended, for the tasks. Without one, tasks stay in the notes doc.
- **Slack, email, Telegram or iMessage**: optional. The agent's own account delivers the recap; otherwise it stays in the app.
- **API keys:** none. X reads are billed per post to your Gamut workspace; onboarding gives you an estimate first.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It connects X, your notes doc and your task tool, asks whether likes count, collects your topics and current projects, and quotes the X cost before the first pull.
3. Run a supervised first sweep, review the notes and tasks, then let the evening schedule take over.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Sweep my X bookmarks from this week into my notes
- What tools did I bookmark this month that I haven't tried yet?
- Every Mon, Wed and Fri evening, sweep my bookmarks and send me a recap

## What's inside

- `AGENTS.md`: the evening sweep and optional weekly digest, the reading and filing rules, connections, schedule, state and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup for X, notes, tasks, cost estimate, delivery and schedule.
- `.claude/skills/x-incremental-pull/`: how to pull only new items, read threads cheaply, handle errors and estimate cost.

## Notes

- X bills per post returned. A typical run with a couple dozen new items costs well under a dollar; onboarding gives you an estimate based on your own habits before anything is pulled.
- Threads older than a week can only be read in part, because X's search only reaches back seven days. Those entries are marked as partial.
- Paywalled or login-only articles are marked unread rather than guessed at.
