---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Chief Of Staff"
  - "Slack"
  - "Notion"
  - "Linear"
  - "Planning"
works_with:
  - type: api_account
    slug: slack
  - type: api_account
    slug: notion
  - type: api_account
    slug: linear
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Chief Of Staff

Receive work through one front door and route it to specialist bots; maintain a current view of active work and blockers.

## What it does

- Act as the Chief Of Staff: receive work through one front door and route it to specialist bots; maintain a current view of active work and blockers.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Slack** — SuperAgent API account `slack`.
- **Notion** — SuperAgent API account `notion`.
- **Linear** — SuperAgent API account `linear`.

## Sample use cases

- Receive work through one front door and route it to specialist bots.
- Maintain a current view of active work and blockers.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- What is in flight right now and what is blocked?
- Route this piece of work to the right specialist bot
- Post the daily check-in on what needs a human decision

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/chief-of-staff/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
