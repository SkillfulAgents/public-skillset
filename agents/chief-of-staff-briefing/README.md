---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Chief of Staff Briefing"
  - "Gmail"
  - "Google Calendar"
  - "Slack"
  - "Discord"
  - "Research"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
  - type: api_account
    slug: discord
developer:
  name: "@jessethanley"
  url: "https://x.com/jessethanley"
---

# Chief of Staff Briefing

Combine important messages, meetings, commitments, and open work; deliver an early daily briefing that highlights urgent fires.

## What it does

- Act as the Chief of Staff Briefing: combine important messages, meetings, commitments, and open work; deliver an early daily briefing that highlights urgent fires.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Gmail** — SuperAgent API account `gmail`.
- **Google Calendar** — SuperAgent API account `googlecalendar`.
- **Slack** — SuperAgent API account `slack`.
- **Discord** — SuperAgent API account `discord`.

## Sample use cases

- Combine important messages, meetings, commitments, and open work.
- Deliver an early daily briefing that highlights urgent fires.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Give me this morning's briefing across mail and calendar
- What are today's fires that need putting out?
- Run the briefing at 5am daily and flag anything urgent

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@jessethanley](https://x.com/jessethanley) on [Bot Directory](https://botdirectory.ai/bots/chief-of-staff-briefing/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
