---
category: Productivity
icon: list-checks
avatar:
  color: tonal-blue
  shape: diamond
tags:
  - Commitments
  - Delegation
  - Follow-Ups
  - Executive Assistant
  - Gmail
  - Meeting Notes
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
  - type: mcp
    slug: granola
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Open Loops

> Every promise you make and every task you hand off stays on one list until there is proof it got done.

## What it does

Open Loops keeps a single ledger of what you owe people and what people owe you, harvested from your sent mail, your Slack messages, and your meeting notes. It tells a real commitment ("I'll send the revised SOW Thursday") from passing talk ("we should revisit pricing"), and it closes a loop only when it finds evidence: the email with the attachment, the intro with both people on it, the calendar invite.

It runs as four routines you can switch on separately:

- **End-of-day can't-miss sweep** — before you log off: where you are the blocker, replies you owe, and promises due by tomorrow morning. Silent when there is nothing.
- **Weekly promise sweep** — every open promise from the week, grouped by person or client, with the source linked.
- **Delegation chaser** — what you handed off and never got back, split into "their court" and "waiting on you", with a polite nudge drafted in the original thread for each overdue item.
- **Principal mode** — for executive assistants and chiefs of staff: commitments made by you, by your executive, and to your executive, ranked by who they are owed to.

Nudges are saved as drafts in your own Gmail or Outlook. Nothing is ever sent in your name.

## What you'll need

- **Gmail or Outlook** — required. Reads sent and received mail and saves nudge drafts in your mailbox.
- **Google Calendar** — recommended, to confirm "I'll set up a call" promises and respect out-of-office time.
- **Slack** — optional. Reads your own messages, DMs, and mentions for promises and asks.
- **Granola** — optional, for spoken commitments. Fathom, Fireflies, Otter, Gong, Zoom recordings, or inviting the agent to listen in on calls also work.
- **A delivery channel** — the agent's own Slack app, its own email inbox, Telegram, or iMessage, set up during onboarding. In-app only also works.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your mail, calendar, Slack, and notes, asks who your VIPs and clients are, which routines to turn on and when, and where digests should reach you.
3. It then runs a supervised sweep over your last two weeks so you can correct what it caught before anything is scheduled.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Show me every promise I made in email in the last two weeks
- What have I delegated that went quiet? Draft the nudges in Gmail
- Every weekday at 4:30pm, tell me only what can't wait until tomorrow

## What's inside

- `AGENTS.md` — the four routines, the evidence rules for closing a loop, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, sets schedules, and writes `config.json`.
- `.claude/skills/commitment-ledger/` — how to classify, dedupe, date, rank, and close loops, and the ledger file format.

## Notes

- The ledger lives in the agent's workspace under `state/open-loops/` and stores one-line summaries and links, not message bodies.
- Slack has no draft API for your account, so Slack nudges arrive as copy-ready text in the digest.
- Pairs with Meeting Actions, which can hand each meeting's delegations straight into the ledger.

## Privacy

Open Loops reads your mailbox, calendar, Slack, and meeting notes through your own connected accounts. Digests go only to you. In principal mode, your executive's mail is read only if you already have delegated access, and only summaries and links are kept.
