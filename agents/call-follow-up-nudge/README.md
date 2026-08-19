---
category: "Productivity"
icon: list-checks
tags:
  - "Productivity"
  - "Call Follow-Up Nudge"
  - "Google Calendar"
  - "Slack"
  - "Monitoring"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Call Follow-Up Nudge

Check completed calendar calls for promised follow-ups; send a timely Slack nudge with who, what, and why.

## What it does

- Act as the Call Follow-Up Nudge: check completed calendar calls for promised follow-ups; send a timely Slack nudge with who, what, and why.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Calendar** — SuperAgent API account `googlecalendar`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Check completed calendar calls for promised follow-ups.
- Send a timely Slack nudge with who, what, and why.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- What did I commit to on today's calls?
- Nudge me in Slack thirty minutes after each call ends
- Shadow one day of calls before you start posting

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/call-follow-up-nudge/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
