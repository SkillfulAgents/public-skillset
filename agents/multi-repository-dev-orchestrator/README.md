---
category: "Productivity"
icon: code-2
tags:
  - "Productivity"
  - "Multi-Repository Dev Orchestrator"
  - "GitHub"
  - "Cursor Cloud Agents"
  - "Planning"
works_with:
  - type: api_account
    slug: github
developer:
  name: "@jessethanley"
  url: "https://x.com/jessethanley"
---

# Multi-Repository Dev Orchestrator

Break a cross-repository request into coherent cloud-agent tasks; coordinate dependencies, tests, and approval before merge.

## What it does

- Act as the Multi-Repository Dev Orchestrator: break a cross-repository request into coherent cloud-agent tasks; coordinate dependencies, tests, and approval before merge.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.
- **Cursor Cloud Agents** — external connection; no canonical registry slug.

## Sample use cases

- Break a cross-repository request into coherent cloud-agent tasks.
- Coordinate dependencies, tests, and approval before merge.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Add this API endpoint and update all the related SDKs
- Which repositories does this change actually touch?
- Run the tests and summarize the changes before merge

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@jessethanley](https://x.com/jessethanley) on [Bot Directory](https://botdirectory.ai/bots/multi-repository-dev-orchestrator/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
