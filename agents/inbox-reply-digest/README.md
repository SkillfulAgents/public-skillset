---
category: "Sales"
icon: mail
tags:
  - "Email"
  - "Slack"
  - "Inbox Zero"
  - "Reply Drafts"
  - "Daily Digest"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Inbox Reply Digest

> One list each morning of every email and Slack thread someone is waiting on you for, with the replies already drafted.

## What it does

Once a day, at a time you pick, the agent reads your work email and your Slack DMs and mentions and keeps only the threads where a person is genuinely waiting on you: a direct question, a customer or prospect thread, a pricing or renewal question, an intro, a promise you haven't closed. It drops newsletters, notifications, receipts, calendar replies and internal noise, and skips threads where you replied last or someone else owns the next step.

Each item comes with a one-line reason, how long they've waited and a link, ordered by what's most time-sensitive or oldest. For email it saves a reply in your voice as a draft in your own mailbox; for Slack it gives you paste-ready text. On a day with nothing owed, it sends nothing.

It learns how you write from your sent mail, remembers what you've already handled so the same thread doesn't come back every morning, and never invents prices, dates or promises in a draft.

## What you'll need

- **Gmail or Outlook** — required; the agent reads your inbox and saves reply drafts there.
- **Slack** — recommended; your account is used read-only to find DMs and mentions that need a reply.
- **A delivery channel** — optional; the agent's own Slack app, its own email inbox, Telegram or iMessage. Otherwise the digest appears in the app.
- **API keys:** none.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill: it connects your mailbox and Slack, learns your voice, asks who always matters and what to skip, and sets the time and delivery channel.
3. Review the supervised dry run on your last week of mail, adjust, and let it schedule the daily digest.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- What do I owe replies to from the last three days?
- Draft a reply to the pricing question from the Acme thread
- Run the digest every weekday at 8am and DM it to me on Slack

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the agent's instructions: the daily digest, the voice refresh, Gamut mechanics and safety rules.
- `.claude/skills/agent-onboarding/` — first-run setup, dry run and scheduling.
- `.claude/skills/voice-profile/` — how the agent learns and applies your writing style.

## Notes

- The agent never sends a reply or posts in Slack as you. Email drafts wait in your mailbox; Slack suggestions are text in the digest, because Slack has no way to save a draft for you.
- It does not archive, label or mark anything read.
- Links point to the original message so you can clear the list in one pass.

## Privacy

The agent reads your mail and Slack messages through your own connected accounts. It keeps only thread IDs, dates and one-line reasons in its state files, plus a short style profile with no message bodies.

## Credits

Adapted from the original prompt by [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/inbox-reply-digest/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
