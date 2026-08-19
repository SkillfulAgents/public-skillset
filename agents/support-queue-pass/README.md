---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "Support Queue Pass"
  - "Zendesk"
  - "Slack"
  - "Customer Operations"
works_with:
  - type: api_account
    slug: zendesk
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Support Queue Pass

Review the Zendesk queue hourly and draft confident replies; alert in Slack only when a ticket genuinely needs a human.

## What it does

- Act as the Support Queue Pass: review the Zendesk queue hourly and draft confident replies; alert in Slack only when a ticket genuinely needs a human.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Zendesk** — SuperAgent API account `zendesk`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Review the Zendesk queue hourly and draft confident replies.
- Alert in Slack only when a ticket genuinely needs a human.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Do a pass on the support queue and draft what you can
- Which tickets did you hold back and why?
- Ping me in Slack only when a human is really needed

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/support-queue-pass/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
