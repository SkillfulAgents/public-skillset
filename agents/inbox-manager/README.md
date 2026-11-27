---
category: Email & Communication
icon: inbox
avatar:
  color: tonal-black
  shape: arch
tags:
  - Email Management
  - Inbox Zero
  - Email Triage
  - Reply Drafts
  - Unsubscribe
  - Automation
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

Inbox Manager sorts your mail in the background as it arrives. It learns your categories from your real mail and labels in your own words instead of a generic folder scheme, archives the noise you confirmed against a skip list, and leaves anything ambiguous exactly where it is. Each thread gets at most one label, and it never overrides a label you set yourself.

For threads that clearly need an answer from you, it writes a reply in your voice, learned from your sent mail, and leaves it in your Gmail drafts. It never sends. Once a week it tells you what you might not notice: senders you always ignore, threads you keep leaving hanging, and rules that keep misfiring. It proposes unsubscribes, and acts on one only after you approve that sender.

An optional investor preset swaps learned categories for four fixed buckets (Today's Focus, Action Required, Scheduling, Delegated), keeps LP and fund-admin mail out of deal flow, and sends a morning digest with a one-line reason for each urgent item.

## What you'll need

- **Gmail:** Required. Labels, archiving, drafts, and the bundled screening and unsubscribe tools all run through your connected Gmail account.
- **Outlook:** Optional alternative. The same work runs through Microsoft Graph, without the bundled Gmail scripts, so the first week runs in preview mode.
- **Google Calendar:** Optional, so scheduling drafts can offer real free times.
- **Slack, email, Telegram, or iMessage:** Optional, for summaries and the weekly report, sent from the agent's own account. In-app works too.
- **API keys:** None.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It connects your mailbox, reads your recent mail to propose categories in your words, agrees the skip list and never-touch list with you, learns your voice from sent mail, and asks how much to do on its own.
3. Review the dry run on the last 48 hours of mail, nothing changed until you approve. Then it switches on sorting for new mail and the weekly patterns report.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Sort today's unread and show me what you labeled, archived, and left alone
- Which senders do I always ignore, and which threads am I leaving hanging?
- Draft replies for the threads that need me today and leave them in Gmail

## What's inside

- `AGENTS.md` — the sorting, drafting, and patterns routines, the investor preset, Gamut setup, and safe operating rules.
- `.claude/skills/agent-onboarding/` — mailbox connection, category and voice learning, dry run, and trigger and schedule setup.
- `.claude/skills/gmail-inbox-screener/` — Gmail retrieval, first-pass marketing screening, and mark-read actions.
- `.claude/skills/gmail-unsubscribe/` — unsubscribe-link extraction for approved senders.

## Notes

- Default autonomy: it labels and archives on its own within your confirmed rules and writes drafts. It never sends, deletes, or marks mail as spam, and unsubscribes need your yes per sender.
- It runs on each new email through a new-mail trigger when your account offers one, otherwise as a sweep every 15 minutes during your waking hours.
- Gmail-first: the bundled scripts are Gmail-specific.
