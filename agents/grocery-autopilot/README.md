---
category: "Personal"
icon: house
tags:
  - "Personal"
  - "Grocery Autopilot"
  - "Amazon"
  - "Costco"
  - "Google Calendar"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: googlecalendar
developer:
  name: "@RhysSullivan"
  url: "https://x.com/RhysSullivan"
---

# Grocery Autopilot

Plan weekly meals across Amazon and Costco; prepare grocery orders and a cooking calendar while remembering household preferences.

## What it does

- Act as the Grocery Autopilot: plan weekly meals across Amazon and Costco; prepare grocery orders and a cooking calendar while remembering household preferences.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Amazon** — browser session; no registry slug.
- **Costco** — browser session; no registry slug.
- **Google Calendar** — SuperAgent API account `googlecalendar`.

## Sample use cases

- Plan weekly meals across Amazon and Costco.
- Prepare grocery orders and a cooking calendar while remembering household preferences.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Plan this week's meals and split the order by store
- Remember that we never want olives in anything
- Put what to cook and when on my calendar

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@RhysSullivan](https://x.com/RhysSullivan) on [Bot Directory](https://botdirectory.ai/bots/grocery-autopilot/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
