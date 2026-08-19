---
category: "Sales"
icon: calendar-check
tags:
  - "Sales"
  - "Meeting Prep Brief"
  - "Salesforce"
  - "Gmail"
  - "Slack"
  - "Granola"
  - "Research"
works_with:
  - type: api_account
    slug: salesforce
  - type: api_account
    slug: gmail
  - type: api_account
    slug: slack
  - type: mcp
    slug: granola
  - type: api_account
    slug: googlecalendar
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Meeting Prep Brief

Combine calendar, CRM, email, Slack, call notes, and research for each meeting; deliver a focused preparation brief.

## What it does

- Act as the Meeting Prep Brief: combine calendar, CRM, email, Slack, call notes, and research for each meeting; deliver a focused preparation brief.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Salesforce** — SuperAgent API account `salesforce`.
- **Gmail** — SuperAgent API account `gmail`.
- **Slack** — SuperAgent API account `slack`.
- **Granola** — SuperAgent MCP `granola`.
- **Gong** — direct API, feed, or required credentials; no canonical registry slug.
- **Google Calendar** — SuperAgent API account `googlecalendar`.

## Sample use cases

- Combine calendar, CRM, email, Slack, call notes, and research for each meeting.
- Deliver a focused preparation brief.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Prep me for tomorrow's meetings in one short brief
- What do we already know about this new account?
- Send the brief before my first meeting every day

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/meeting-prep-brief/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
