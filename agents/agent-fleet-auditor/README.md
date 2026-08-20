---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Agent Fleet Auditor"
  - "Slack"
  - "Analysis"
works_with:
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Agent Fleet Auditor

Review every active agent’s cost and weekly output; make evidence-based keep, change, or kill recommendations.

## What it does

- Act as the Agent Fleet Auditor: review every active agent’s cost and weekly output; make evidence-based keep, change, or kill recommendations.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Review every active agent’s cost and weekly output.
- Make evidence-based keep, change, or kill recommendations.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Tally what each bot cost and produced this week
- Flag the wasteful bots with a keep or kill recommendation
- Post the fleet ledger to Slack every Friday

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/bot-fleet-auditor/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
