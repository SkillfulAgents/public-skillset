---
category: "Productivity"
icon: list-checks
tags:
  - "1:1 Meetings"
  - "Management"
  - "Meeting Prep"
  - "Google Calendar"
  - "Granola"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: gmail
  - type: mcp
    slug: granola
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# One-On-One Prep

> Walk into every standing 1:1 with last week's open items, their pending asks, and your agenda already on the page.

## What it does

One-On-One Prep keeps a private running doc for each recurring 1:1, whether with your manager, your reports, peers or clients. A couple of hours before each one, it adds a new dated section on top: what each of you still owes from last time (carried forward until there is evidence it was done), what the person has emailed or messaged you about since, the decisions or approvals they are waiting on from you, the topics you flagged during the week, a short suggested agenda, and space for your own talking points.

- **Every recurring 1:1**: found from your calendar and confirmed by you, with the agenda order tuned to the relationship.
- **Running thread, not a blank page**: items that keep slipping are marked by week and pushed up the agenda.
- **Topics on the fly**: tell the agent "for my 1:1 with Sam, raise the hiring plan", or type into the box at the top of the doc.
- **Optional reminders**: for what you promised, after each 1:1.
- **Private by design**: the doc is never shared with the other person and nothing is posted where they can see it.

## What you'll need

- **Google Calendar or Outlook** — required, to find your recurring 1:1s.
- **Gmail or Outlook mail** — recommended, for recent asks and proof that items were done.
- **Granola** — recommended, for what was said last time; Fireflies, Otter, Fathom or Zoom notes also work.
- **Slack** — optional, to include your DMs and mentions with each person; also an optional heads-up channel through the agent's own Slack app.
- **Google Docs** — optional home for the running docs; Notion or a Markdown file in the agent also work.
- **API keys:** none.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill: it connects your calendar and notes, lists your recurring 1:1s for you to confirm, asks the relationship for each, and preps your next 1:1 with you watching.
3. Once you approve the first doc, it schedules the daily planning run and preps land on their own.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Prep my next 1:1 from Google Calendar and show me the doc
- For my 1:1 with my manager, raise the Q1 hiring plan
- Before every recurring 1:1, carry forward what Granola says is open

## What's inside

- `PROMPT.md` — the editable setup request placed in your message box after import.
- `CLAUDE.md` — the agent's routines, carry-forward rules, Gamut mechanics and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup, 1:1 discovery, dry run and scheduling.
- `.claude/skills/running-doc/` — the running doc layout, carry-forward and evidence rules, and agenda order by relationship.

## Notes

- An item is only marked done when there is evidence, such as a sent email, a shared doc or a closed ticket; anything you tick yourself in the doc wins.
- Cancelled 1:1s are skipped and their open items roll to the next one; moved 1:1s are prepped at the new time.
- External and first-time meetings are left to the Meeting Prep Brief template.

## Privacy

The docs are created in your own account, unshared, in a private folder. The agent never invites, messages or posts to the other person, and by default it does not copy what others said about that person into their doc.

## Credits

Adapted from the original prompt by [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/one-on-one-prep/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
