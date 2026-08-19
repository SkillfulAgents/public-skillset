---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "Tickets To Changelog"
  - "Zendesk"
  - "Notion"
  - "Content Creation"
works_with:
  - type: api_account
    slug: zendesk
  - type: api_account
    slug: notion
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Tickets To Changelog

Turn the week’s Zendesk tickets into changelog notes; draft help-center articles for recurring questions in Notion.

## What it does

- Act as the Tickets To Changelog: turn the week’s Zendesk tickets into changelog notes; draft help-center articles for recurring questions in Notion.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Zendesk** — SuperAgent API account `zendesk`.
- **Notion** — SuperAgent API account `notion`.

## Sample use cases

- Turn the week’s Zendesk tickets into changelog notes.
- Draft help-center articles for recurring questions in Notion.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Turn this week's tickets into changelog notes
- Which questions kept repeating in the queue?
- Draft a help-center article for the top two

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/tickets-to-changelog/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
