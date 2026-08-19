---
category: "Customer Success"
icon: life-buoy
tags:
  - "Customer Success"
  - "Support Autopilot"
  - "Bento Chat"
  - "HelpSpot"
  - "Help Scout"
  - "Intercom"
  - "Customer Operations"
works_with:
  - type: api_account
    slug: intercom
developer:
  name: "@jessethanley"
  url: "https://x.com/jessethanley"
---

# Support Autopilot

Pull support tickets on a schedule and draft answers from approved documentation; organize uncertain cases for human attention.

## What it does

- Act as the Support Autopilot: pull support tickets on a schedule and draft answers from approved documentation; organize uncertain cases for human attention.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Bento Chat** — external connection; no canonical registry slug.
- **HelpSpot** — direct API, feed, or required credentials; no canonical registry slug.
- **Help Scout** — direct API, feed, or required credentials; no canonical registry slug.
- **Intercom** — SuperAgent API account `intercom`.

## Sample use cases

- Pull support tickets on a schedule and draft answers from approved documentation.
- Organize uncertain cases for human attention.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Pull the new tickets and draft answers from our docs
- Which tickets need a human and why?
- Hold every response for my approval before sending

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@jessethanley](https://x.com/jessethanley) on [Bot Directory](https://botdirectory.ai/bots/support-autopilot/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
