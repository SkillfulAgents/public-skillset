---
category: "Sales"
icon: mail
tags:
  - "Sales"
  - "Inbox Reply Digest"
  - "Gmail"
  - "Content Creation"
works_with:
  - type: api_account
    slug: gmail
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Inbox Reply Digest

Find work emails since the last run that plausibly need a reply; send a concise digest only when action is needed.

## What it does

- Act as the Inbox Reply Digest: find work emails since the last run that plausibly need a reply; send a concise digest only when action is needed.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Find work emails since the last run that plausibly need a reply.
- Send a concise digest only when action is needed.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Digest the work emails that need a reply since last run
- Propose a reply in my voice for each one
- Send nothing at all if nothing needs an answer

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/inbox-reply-digest/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
