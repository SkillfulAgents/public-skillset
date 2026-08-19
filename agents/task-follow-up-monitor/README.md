---
category: "Productivity"
icon: list-checks
tags:
  - "Productivity"
  - "Task Follow-Up Monitor"
  - "Google Calendar"
  - "Slack"
  - "Email"
  - "Monitoring"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: "@techdevnotes"
  url: "https://x.com/techdevnotes"
---

# Task Follow-Up Monitor

Track a task through its current step across calendar, Slack, and email; alert only when progress stalls or follow-up is due.

## What it does

- Act as the Task Follow-Up Monitor: track a task through its current step across calendar, Slack, and email; alert only when progress stalls or follow-up is due.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Calendar** — SuperAgent API account `googlecalendar`.
- **Slack** — SuperAgent API account `slack`.
- **Email** — external connection; no canonical registry slug.

## Sample use cases

- Track a task through its current step across calendar, Slack, and email.
- Alert only when progress stalls or follow-up is due.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Track this task and tell me when it stalls
- Where is this piece of work right now?
- Check in every ten minutes until it is done or blocked

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@techdevnotes](https://x.com/techdevnotes) on [Bot Directory](https://botdirectory.ai/bots/task-follow-up-monitor/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
