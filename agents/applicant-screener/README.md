---
category: "Ops"
icon: user-search
tags:
  - "Ops"
  - "Applicant Screener"
  - "Airtable"
  - "Gmail"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: airtable
  - type: api_account
    slug: gmail
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Applicant Screener

Read and score applications against the hiring profile; batch strong fits and prepare appropriate Gmail follow-ups.

## What it does

- Act as the Applicant Screener: read and score applications against the hiring profile; batch strong fits and prepare appropriate Gmail follow-ups.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Airtable** — SuperAgent API account `airtable`.
- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Read and score applications against the hiring profile.
- Batch strong fits and prepare appropriate Gmail follow-ups.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Score this week's applications against our hiring profile
- Show me the clear fits with a one-line reason for each
- Draft the Gmail follow-ups for everyone I just advanced

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/applicant-screener/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
