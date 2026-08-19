---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "PR Conflict Flagger"
  - "GitHub"
  - "Slack"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: github
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# PR Conflict Flagger

Scan open GitHub pull requests for overlapping code changes; notify the right people in Slack before merge conflicts land.

## What it does

- Act as the PR Conflict Flagger: scan open GitHub pull requests for overlapping code changes; notify the right people in Slack before merge conflicts land.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Scan open GitHub pull requests for overlapping code changes.
- Notify the right people in Slack before merge conflicts land.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Scan the open pull requests for overlapping changes
- Which PRs will conflict and who should talk to whom?
- Post the conflict warning to Slack before merge

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/pr-conflict-flagger/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
