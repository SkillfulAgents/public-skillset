---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Contractor Quote Negotiator"
  - "Gmail"
  - "Contractor websites"
  - "Google Sheets"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlesheets
developer:
  name: "@benln"
  url: "https://x.com/benln"
---

# Contractor Quote Negotiator

Collect contractor quotes and scope details; compare price, timing, exclusions, and warranties before drafting negotiation replies.

## What it does

- Act as the Contractor Quote Negotiator: collect contractor quotes and scope details; compare price, timing, exclusions, and warranties before drafting negotiation replies.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.
- **Contractor websites** — browser session; no registry slug.
- **Google Sheets** — SuperAgent API account `googlesheets`.

## Sample use cases

- Collect contractor quotes and scope details.
- Compare price, timing, exclusions, and warranties before drafting negotiation replies.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Collect the contractor quotes from my inbox and compare them
- Where are the negotiation opportunities in these bids?
- Draft a counteroffer that holds my must-have scope

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@benln](https://x.com/benln) on [Bot Directory](https://botdirectory.ai/bots/contractor-quote-negotiator/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
