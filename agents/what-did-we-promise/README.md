---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "What Did We Promise"
  - "Slack"
  - "Salesforce"
  - "Google Drive"
  - "Customer Operations"
works_with:
  - type: api_account
    slug: slack
  - type: api_account
    slug: salesforce
  - type: api_account
    slug: googledrive
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# What Did We Promise

Compare a customer contract, Slack channel, and Salesforce record; summarize commitments, implications, and contradictions.

## What it does

- Act as the What Did We Promise: compare a customer contract, Slack channel, and Salesforce record; summarize commitments, implications, and contradictions.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Slack** — SuperAgent API account `slack`.
- **Salesforce** — SuperAgent API account `salesforce`.
- **Google Drive** — SuperAgent API account `googledrive`.

## Sample use cases

- Compare a customer contract, Slack channel, and Salesforce record.
- Summarize commitments, implications, and contradictions.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- What did we actually promise this account?
- Where does the contract contradict what we said?
- Give me one page on commitments and implications

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/what-did-we-promise/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
