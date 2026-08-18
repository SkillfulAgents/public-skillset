---
category: "Personal"
icon: sparkles
tags:
  - "Personal"
  - "School Form Filler"
  - "Google Drive"
  - "Gmail"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# School Form Filler

Reuse last year’s PDFs to prefill current school forms; ask only for changed fields and signatures, never submitting automatically.

## What it does

- Act as the School Form Filler: reuse last year’s PDFs to prefill current school forms; ask only for changed fields and signatures, never submitting automatically.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Drive** — SuperAgent API account `googledrive`.
- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Reuse last year’s PDFs to prefill current school forms.
- Ask only for changed fields and signatures, never submitting automatically.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/school-form-filler/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
