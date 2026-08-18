---
category: Email & Communication
icon: inbox
tags:
  - email-management
  - inbox-zero
  - email-triage
  - unsubscribe
  - automation
works_with:
  - type: api_account
    slug: gmail
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Inbox Manager

> Turn a noisy Gmail inbox into a short, useful queue of messages that deserve your attention.

## What it does

Inbox Manager screens recent Gmail messages and separates important conversations from marketing and low-value mail. It can summarize what needs attention, mark processed messages as read, and prepare or send replies through the connected Gmail account.

For recurring clutter, it extracts unsubscribe options from message headers and bodies so unwanted lists can be removed safely. Its onboarding flow learns which senders and message patterns matter to you, how often it should screen the inbox, and whether useful notifications should also go to Slack.

## What you'll need

- **Gmail:** Required for the shipped screening, action, and unsubscribe tools.
- **Slack:** Optional, for inbox notifications configured during onboarding.
- **API keys:** None.

## Getting started

1. Import the template into Gamut.
2. Run the onboarding conversation and connect the Gmail inbox you want it to manage.
3. Describe what “important” means for you and choose a screening schedule.
4. Optionally connect Slack for notifications.
5. Ask it to screen the inbox or unsubscribe you from a mailing list.

## What's inside

- `CLAUDE.md` — the agent's durable workspace instructions.
- `.claude/skills/agent-onboarding/` — account connection, preferences, and schedule setup.
- `.claude/skills/gmail-inbox-screener/` — Gmail retrieval, categorization, mark-read, and reply actions.
- `.claude/skills/gmail-unsubscribe/` — unsubscribe-link extraction and guided cleanup.

## Notes

The current implementation is Gmail-specific. Onboarding may discuss other mail providers, but the included screening and unsubscribe scripts require a connected Gmail account.
