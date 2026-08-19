---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "Churn Early Warning"
  - "Salesforce"
  - "PostHog"
  - "Slack"
  - "Monitoring"
works_with:
  - type: api_account
    slug: salesforce
  - type: mcp
    slug: posthog
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Churn Early Warning

Combine CRM, product-usage, and support-tone signals; warn about likely customer churn before the headline metrics move.

## What it does

- Act as the Churn Early Warning: combine CRM, product-usage, and support-tone signals; warn about likely customer churn before the headline metrics move.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Salesforce** — SuperAgent API account `salesforce`.
- **PostHog** — SuperAgent MCP `posthog`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Combine CRM, product-usage, and support-tone signals.
- Warn about likely customer churn before the headline metrics move.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Which accounts are drifting before the numbers move?
- Show me seats going idle and support tone shifting
- Backtest the signals on three accounts we already lost

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/churn-early-warning/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
