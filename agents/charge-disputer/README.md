---
category: "Personal"
icon: sparkles
tags:
  - "Personal"
  - "Charge Disputer"
  - "Gmail"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: gmail
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Charge Disputer

Match a disputed charge to its receipt and statement line; draft a complete dispute letter for your review.

## What it does

- Act as the Charge Disputer: match a disputed charge to its receipt and statement line; draft a complete dispute letter for your review.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Match a disputed charge to its receipt and statement line.
- Draft a complete dispute letter for your review.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Pull the receipt and statement line for this wrong charge
- Draft the dispute letter with the details laid out properly
- Track the case number and deadlines now that I have sent it

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/charge-disputer/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
