---
category: "Marketing"
icon: messages-square
tags:
  - "Marketing"
  - "Release To Social Campaign"
  - "GitHub"
  - "Postiz"
  - "Slack"
  - "Content Creation"
works_with:
  - type: api_account
    slug: github
  - type: api_account
    slug: slack
developer:
  name: "@elie2222"
  url: "https://x.com/elie2222"
---

# Release To Social Campaign

Turn verified GitHub release changes into platform-specific Postiz drafts; route approval in Slack and summarize later performance.

## What it does

- Act as the Release To Social Campaign: turn verified GitHub release changes into platform-specific Postiz drafts; route approval in Slack and summarize later performance.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.
- **Postiz** — direct API, feed, or required credentials; no canonical registry slug.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Turn verified GitHub release changes into platform-specific Postiz drafts.
- Route approval in Slack and summarize later performance.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Turn this release into platform-specific drafts
- Show me the drafts and schedule in Slack for approval
- Summarize how the posts performed after 72 hours

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/release-to-social-campaign/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
