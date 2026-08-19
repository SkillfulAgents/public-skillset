---
category: "Productivity"
icon: code-2
tags:
  - "Productivity"
  - "Linear Development Orchestrator"
  - "Linear"
  - "GitHub"
  - "Cursor Background Agents"
  - "Planning"
works_with:
  - type: api_account
    slug: linear
  - type: api_account
    slug: github
developer:
  name: "@iannuttall"
  url: "https://x.com/iannuttall"
---

# Linear Development Orchestrator

Turn selected Linear tickets into independent agent tasks; coordinate GitHub branches, tests, results, and approval gates.

## What it does

- Act as the Linear Development Orchestrator: turn selected Linear tickets into independent agent tasks; coordinate GitHub branches, tests, results, and approval gates.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Linear** — SuperAgent API account `linear`.
- **GitHub** — SuperAgent API account `github`.
- **Cursor Background Agents** — external connection; no canonical registry slug.

## Sample use cases

- Turn selected Linear tickets into independent agent tasks.
- Coordinate GitHub branches, tests, results, and approval gates.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Turn these Linear tickets into parallel agent tasks
- Open a pull request for each completed ticket
- Where do the acceptance criteria overlap or conflict?

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@iannuttall](https://x.com/iannuttall) on [Bot Directory](https://botdirectory.ai/bots/linear-development-orchestrator/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
