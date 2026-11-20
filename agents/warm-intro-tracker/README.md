---
category: Sales
icon: handshake
tags:
  - Warm Intros
  - Networking
  - Follow-ups
  - Relationship Management
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: googlesheets
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Warm Intro Tracker

> The intros you make stop dying in someone's inbox, and you finally see which ones turn into conversations.

## What it does

Warm Intro Tracker is for anyone who makes a lot of double-opt-in introductions: founders, investors and community leads. Twice a day it looks through the intros you sent and finds the ones where the other side hasn't replied. Once a thread has been quiet past your window (3 business days by default), it drafts a short nudge in the original thread, in the tone of that thread, addressed to whoever owes the reply.

It spaces the bumps out and stops after two, never starts a new thread or adds anyone, and leaves alone any thread where a reply is in motion: an out-of-office, a "will get back to you next week", or a scheduling link. Each week it sends a scoreboard of sent, replied, open and dormant intros, with the reply rate by intro type or campaign and how many replies came after a nudge.

Every nudge is a draft in your Gmail or Outlook. You review it and send it yourself.

## What you'll need

- **Gmail or Outlook** — required. The agent reads your intro threads and saves drafts in your mailbox.
- **Google Sheets** — optional, for a running intro log and scoreboard.
- **Google Calendar** — optional, to count meetings booked from an intro.
- **Slack, email or Telegram** — optional, to get the "drafts ready" note and weekly scoreboard from the agent instead of in the app.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs automatically. It connects your mailbox, learns how you write intros from a few examples, and asks for your intro types, nudge window, nudge limit, exclusions and where the scoreboard should go. It then shows you the intros it found and drafts up to three nudges for you to approve before scheduling anything.
3. Ask for your first check: which intros from the last two months are still waiting on a reply.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Show me every intro I sent this month that's still waiting on a reply
- Draft nudges in the original threads for intros quiet for three days
- Every Monday, send me my intro reply rate split by fundraising and hiring

## What's inside

- `CLAUDE.md` — the nudge and scoreboard routines, how they run on Gamut, and the safe operating rules.
- `.claude/skills/agent-onboarding/` — mailbox connection, intro detection, timing, voice, dry run and schedules.
- `.claude/skills/intro-ledger/` — how intros are detected, the per-intro record, nudge timing and the scoreboard definitions.

## Notes

- Nudges are never sent automatically. If you delete a draft, the agent takes that as "don't nudge this one" and won't recreate it.
- Reply rates only count intros old enough to have had a chance to reply, and groups with fewer than five intros show counts without a percentage.
- Sibling templates: Referral Scout asks people for intros, and VC Associate thanks whoever introduced a founder to you.
