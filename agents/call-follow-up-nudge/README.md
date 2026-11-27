---
category: "Productivity"
icon: list-checks
avatar:
  color: tonal-cobalt
  shape: circle
tags:
  - "Commitments"
  - "Follow-Ups"
  - "Meeting Notes"
  - "Gmail"
  - "Google Calendar"
  - "Granola"
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: mcp
    slug: granola
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Call Follow-Up Nudge

> Walk out of every call knowing exactly what you promised, with the follow-ups already drafted.

## What it does

About thirty minutes after each call, Call Follow-Up Nudge reads the transcript and pulls out only what you personally agreed to: the deliverable, who it is for, and the deadline, with your exact words quoted. A passing "we should look at that" is not counted as yours, and what the other side took on goes in its own list.

It then drafts the follow-ups you promised as replies in the right thread in your own Gmail or Outlook, writes any promised Slack messages as copy-ready text, and sends you one message: your commitments at the top, the drafts below, and every "let me check and circle back" flagged so it does not quietly disappear.

- Numbers, prices, and dates are quoted exactly as said; any date it had to infer is marked as an estimate.
- Silent after calls where you promised nothing.
- Never processes the same call twice, whether the transcript arrives on time or an hour late.
- Optional daily check of what is due or overdue, or a hand-off to the Open Loops agent for long-running tracking.

Nothing is ever sent or posted as you.

## What you'll need

- **Google Calendar** — required (or Outlook), to find your calls and attendees.
- **Gmail or Outlook** — required, to save follow-up drafts in your mailbox and learn your tone from sent mail.
- **Granola** — or another notes source: Fathom, Fireflies, Otter, Gong, Zoom recordings, or inviting the agent to listen in on calls.
- **Slack** — optional, to address promised Slack messages to the right person and check whether you sent them.
- **A delivery channel** — the agent's own Slack app, its own email inbox, Telegram, iMessage, or in-app only, set up during onboarding.
- **API keys:** none.

## Getting started

1. Import the template into Gamut and send the setup message that appears in the message box.
2. The `agent-onboarding` skill connects your calendar, mailbox, and notes tool, and asks which calls to skip, where the post-call message should reach you, and how your follow-ups should sound.
3. It shadows one day of your real calls so you can correct what it caught before it runs on its own.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- What did I commit to on my last call with the Acme team?
- Draft the follow-ups I promised today as replies in Gmail
- After every external call, message me what I owe within 30 minutes

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `AGENTS.md` — the post-call capture, shadow day, and daily check routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, runs the shadow day, creates the trigger or sweep, and writes `config.json`.
- `.claude/skills/commitment-capture/` — the rubric for what counts as your commitment, exact quoting, date estimates, and the record format.

## Notes

- Slack has no draft feature for your account, so promised Slack messages arrive as text for you to send.
- If Call Follow-Up Drafter is also installed, it writes the full recap email and this agent drafts only the specific things you promised.
- State lives under `state/call-follow-up-nudge/` in the agent's workspace and holds short quotes, IDs, and links, not full transcripts.

## Credits

Adapted from the original prompt by [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/call-follow-up-nudge/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
