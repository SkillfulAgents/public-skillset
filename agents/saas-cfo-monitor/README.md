---
category: "Ops"
icon: calculator
tags:
  - "Ops"
  - "SaaS CFO Monitor"
  - "Stripe"
  - "Xero"
  - "QuickBooks"
  - "Gmail"
  - "Monitoring"
works_with:
  - type: api_account
    slug: stripe
  - type: api_account
    slug: xero
  - type: api_account
    slug: quickbooks
  - type: api_account
    slug: gmail
developer:
  name: "@jessethanley"
  url: "https://x.com/jessethanley"
---

# SaaS CFO Monitor

Scan SaaS spending for missed or unusual charges and audit COGS; produce weekly findings and a monthly CFO report.

## What it does

- Act as the SaaS CFO Monitor: scan SaaS spending for missed or unusual charges and audit COGS; produce weekly findings and a monthly CFO report.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Stripe** — SuperAgent API account `stripe`.
- **Xero** — SuperAgent API account `xero`.
- **QuickBooks** — SuperAgent API account `quickbooks`.
- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Scan SaaS spending for missed or unusual charges and audit COGS.
- Produce weekly findings and a monthly CFO report.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@jessethanley](https://x.com/jessethanley) on [Bot Directory](https://botdirectory.ai/bots/saas-cfo-monitor/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
