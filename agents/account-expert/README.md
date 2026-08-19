---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "Account Expert"
  - "Slack"
  - "Gmail"
  - "Gong"
  - "Granola"
  - "Research"
works_with:
  - type: api_account
    slug: slack
  - type: api_account
    slug: gmail
  - type: mcp
    slug: granola
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Account Expert

Monitor one strategic account across Slack, email, and calls; track feature requests, support tickets, and relevant product updates.

## What it does

- Act as the Account Expert: monitor one strategic account across Slack, email, and calls; track feature requests, support tickets, and relevant product updates.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Slack** — SuperAgent API account `slack`.
- **Gmail** — SuperAgent API account `gmail`.
- **Gong** — direct API, feed, or required credentials; no canonical registry slug.
- **Granola** — SuperAgent MCP `granola`.

## Sample use cases

- Monitor one strategic account across Slack, email, and calls.
- Track feature requests, support tickets, and relevant product updates.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Catch me up on the last month for the account you track
- What feature requests has this customer raised on calls?
- Ping me in Slack when we ship something relevant to them

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/account-expert/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
