---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Feature Ask Finder"
  - "Slack"
  - "Research"
works_with:
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Feature Ask Finder

Search Slack for every customer mention of a requested feature; return one linked list with customers and original wording.

## What it does

- Act as the Feature Ask Finder: search Slack for every customer mention of a requested feature; return one linked list with customers and original wording.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Search Slack for every customer mention of a requested feature.
- Return one linked list with customers and original wording.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/feature-ask-finder/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
