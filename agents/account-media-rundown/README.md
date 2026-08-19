---
category: "Sales"
icon: badge-dollar-sign
tags:
  - "Sales"
  - "Account Media Rundown"
  - "X"
  - "Slack"
  - "Revenue Operations"
works_with:
  - type: api_account
    slug: slack
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Account Media Rundown

Find new talks and posts from people at a strategic account; summarize category mentions, notable quotes, and buying signals.

## What it does

- Act as the Account Media Rundown: find new talks and posts from people at a strategic account; summarize category mentions, notable quotes, and buying signals.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **X** — external connection; no canonical registry slug.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Find new talks and posts from people at a strategic account.
- Summarize category mentions, notable quotes, and buying signals.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Find new talks and podcasts from people at my target account
- Summarize the category mentions and buying signals this week
- Post the account media rundown to Slack every Monday

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/account-media-rundown/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
