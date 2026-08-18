---
category: "Ops"
icon: shield-check
tags:
  - "Ops"
  - "Security Questionnaire"
  - "Google Drive"
  - "Notion"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: notion
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Security Questionnaire

Draft security-questionnaire answers from public docs and past responses; cite evidence and flag questions needing a human.

## What it does

- Act as the Security Questionnaire: draft security-questionnaire answers from public docs and past responses; cite evidence and flag questions needing a human.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Drive** — SuperAgent API account `googledrive`.
- **Notion** — SuperAgent API account `notion`.

## Sample use cases

- Draft security-questionnaire answers from public docs and past responses.
- Cite evidence and flag questions needing a human.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/security-questionnaire/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
