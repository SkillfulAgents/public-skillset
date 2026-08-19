---
category: "Personal"
icon: plane
tags:
  - "Personal"
  - "Trip Concierge"
  - "Gmail"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: gmail
developer:
  name: "@petergyang"
  url: "https://x.com/petergyang"
---

# Trip Concierge

Research flights and stays that fit a trip; surface cheaper alternatives and prepare options from relevant Gmail context.

## What it does

- Act as the Trip Concierge: research flights and stays that fit a trip; surface cheaper alternatives and prepare options from relevant Gmail context.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.

## Sample use cases

- Research flights and stays that fit a trip.
- Surface cheaper alternatives and prepare options from relevant Gmail context.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Research flights and stays for this trip
- Find cheaper dates or airports I would have missed
- Did any fare drop on what I already booked?

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@petergyang](https://x.com/petergyang) on [Bot Directory](https://botdirectory.ai/bots/trip-concierge/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
