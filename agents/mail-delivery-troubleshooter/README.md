---
category: "Ops"
icon: mail
tags:
  - "Ops"
  - "Mail Delivery Troubleshooter"
  - "MailOps"
  - "SPF"
  - "DKIM"
  - "DMARC"
  - "Analysis"
works_with: []
developer:
  name: "@euboid"
  url: "https://x.com/euboid"
---

# Mail Delivery Troubleshooter

Correlate delivery failures with SPF, DKIM, DMARC, SMTP, and MailOps evidence; identify likely causes and ordered fixes.

## What it does

- Act as the Mail Delivery Troubleshooter: correlate delivery failures with SPF, DKIM, DMARC, SMTP, and MailOps evidence; identify likely causes and ordered fixes.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **MailOps** — external connection; no canonical registry slug.
- **SPF** — built-in capability; no connection slug.
- **DKIM** — built-in capability; no connection slug.
- **DMARC** — built-in capability; no connection slug.
- **SMTP logs** — local tool or resource; no connection slug.

## Sample use cases

- Correlate delivery failures with SPF, DKIM, DMARC, SMTP, and MailOps evidence.
- Identify likely causes and ordered fixes.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Why did this message fail to deliver?
- Correlate the SPF, DKIM, and DMARC evidence for me
- Draft the remediation steps for the technician

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@euboid](https://x.com/euboid) on [Bot Directory](https://botdirectory.ai/bots/mail-delivery-troubleshooter/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
