---
category: "Personal"
icon: mail
tags:
  - "Personal"
  - "Mail Cleanup Assistant"
  - "Gmail"
  - "Outlook"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
developer:
  name: "@APompliano"
  url: "https://x.com/APompliano"
---

# Mail Cleanup Assistant

Classify Gmail and Outlook messages by priority; propose safe unsubscribe and filing actions while protecting sacred mail.

## What it does

- Act as the Mail Cleanup Assistant: classify Gmail and Outlook messages by priority; propose safe unsubscribe and filing actions while protecting sacred mail.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.
- **Outlook** — SuperAgent API account `outlook`.

## Sample use cases

- Classify Gmail and Outlook messages by priority.
- Propose safe unsubscribe and filing actions while protecting sacred mail.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Do a dry run cleanout across my Gmail and Outlook
- Which recurring senders do I never actually read?
- Show me every unsubscribe before you touch anything

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@APompliano](https://x.com/APompliano) on [Bot Directory](https://botdirectory.ai/bots/mail-cleanup-assistant/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
