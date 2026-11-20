---
category: "Productivity"
icon: inbox
tags:
  - "Email"
  - "Gmail"
  - "Outlook"
  - "Inbox Triage"
  - "Labels"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Important Email Triage

> One label you can trust: everything a real person is waiting on you for, tagged within minutes of arriving.

## What it does

The agent watches your inbox as mail arrives (or every 30 minutes) and labels what's genuinely waiting on you: a question, a request, an approval, a deadline from a real person. Everything else goes into a handful of categories learned from your own mail and named the way you'd name them. Newsletters, receipts, notifications and cold outreach, including the fake "Re:" kind, are ignored.

When a message is ambiguous it leaves it alone instead of guessing, and it takes the label off once you've replied. When something new lands it sends you one short list, newest first, with who it is and what they're asking. No new labels means no message.

Investors can switch to a preset with four buckets (Today's Focus, Action Required, Scheduling, Delegated) and a one-line reason for every urgent item; a term sheet or signed document always goes to the top, and fund-admin mail stays out of deal flow.

## What you'll need

- **Gmail or Outlook** — required; the agent reads new mail and adds labels or categories.
- **A delivery channel** — optional; the agent's own Slack app, its own email inbox, Telegram or iMessage. You can also choose labels only.
- **API keys:** none.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill: it connects your mailbox, learns who matters and which categories you use, and picks the delivery channel and hours.
3. Check the read-only dry run on your last two days of mail, then let it switch on the new-mail trigger or the 30-minute check.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Label what's waiting on me in today's unread mail
- What is each person in my waiting label asking me for?
- Switch me to the investor buckets and flag any term sheets

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the agent's instructions: labeling rules, the investor preset, triggers and safety rules.
- `.claude/skills/agent-onboarding/` — first-run setup, read-only dry run and trigger or schedule creation.
- `.claude/skills/triage-labels/` — the skip list, the waiting-on-me test, category learning and the processed-message ledger.

## Notes

- Labels only. It never sends, drafts, archives, deletes, marks read or unsubscribes. For cleanup and unsubscribes, use the Inbox Manager template; for daily reply drafts, use Inbox Reply Digest.
- All labels sit under one `Triage/` parent, so they are easy to find or remove.
- If your account offers no new-mail trigger, the agent checks every 30 minutes, optionally only during working hours.

## Credits

Adapted from the original prompt by [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/important-email-triage/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
