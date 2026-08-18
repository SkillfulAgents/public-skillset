---
category: "Productivity"
icon: list-checks
tags:
  - "Productivity"
  - "Nexus Coordinator"
  - "Gmail"
  - "Google Calendar"
  - "Slack"
  - "Planning"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: "@Voxyz_ai"
  url: "https://x.com/Voxyz_ai"
---

# Nexus Coordinator

Maintain TEAM_ALIGNMENT as the shared source of truth; collect commitments and changes from email, calendar, and Slack.

## What it does

- Act as the Nexus Coordinator: maintain TEAM_ALIGNMENT as the shared source of truth; collect commitments and changes from email, calendar, and Slack.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.
- **Google Calendar** — SuperAgent API account `googlecalendar`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Maintain TEAM_ALIGNMENT as the shared source of truth.
- Collect commitments and changes from email, calendar, and Slack.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@Voxyz_ai](https://x.com/Voxyz_ai) on [Bot Directory](https://botdirectory.ai/bots/nexus-coordinator/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
