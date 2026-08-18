---
category: "Productivity"
icon: list-checks
tags:
  - "Productivity"
  - "Daily Briefing"
  - "Google Calendar"
  - "Slack"
  - "Research"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: "@elie2222"
  url: "https://x.com/elie2222"
---

# Daily Briefing

Combine today’s calendar with overnight Slack changes; send one weekday morning brief with meetings and the key preparation item.

## What it does

- Act as the Daily Briefing: combine today’s calendar with overnight Slack changes; send one weekday morning brief with meetings and the key preparation item.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Calendar** — SuperAgent API account `googlecalendar`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Combine today’s calendar with overnight Slack changes.
- Send one weekday morning brief with meetings and the key preparation item.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/daily-briefing/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
