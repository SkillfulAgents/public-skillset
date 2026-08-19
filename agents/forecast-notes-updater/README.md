---
category: "Sales"
icon: badge-dollar-sign
tags:
  - "Sales"
  - "Forecast Notes Updater"
  - "Salesforce"
  - "Granola"
  - "Gong"
  - "Slack"
  - "Revenue Operations"
works_with:
  - type: api_account
    slug: salesforce
  - type: mcp
    slug: granola
  - type: api_account
    slug: slack
  - type: api_account
    slug: gmail
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Forecast Notes Updater

Combine call notes, Slack threads, and email after each customer touchpoint; draft updated Salesforce forecast fields for approval.

## What it does

- Act as the Forecast Notes Updater: combine call notes, Slack threads, and email after each customer touchpoint; draft updated Salesforce forecast fields for approval.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Salesforce** — SuperAgent API account `salesforce`.
- **Granola** — SuperAgent MCP `granola`.
- **Gong** — direct API, feed, or required credentials; no canonical registry slug.
- **Slack** — SuperAgent API account `slack`.
- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Combine call notes, Slack threads, and email after each customer touchpoint.
- Draft updated Salesforce forecast fields for approval.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Update my opportunity notes from this week's touchpoints
- Show me the proposed Salesforce updates before writing
- What changed on my in-play deals since the last forecast?

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/forecast-notes-updater/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
