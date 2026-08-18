---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Migration Ramp Watcher"
  - "Datadog"
  - "Slack"
  - "Monitoring"
works_with:
  - type: mcp
    slug: datadog
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Migration Ramp Watcher

Check Datadog logs, metrics, and backfill status at each migration step; post green-to-proceed or stop-and-investigate guidance.

## What it does

- Act as the Migration Ramp Watcher: check Datadog logs, metrics, and backfill status at each migration step; post green-to-proceed or stop-and-investigate guidance.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Datadog** — SuperAgent MCP `datadog`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Check Datadog logs, metrics, and backfill status at each migration step.
- Post green-to-proceed or stop-and-investigate guidance.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/migration-ramp-watcher/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
