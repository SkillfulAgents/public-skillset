---
category: "Sales"
icon: mail
avatar:
  color: tonal-teal
  shape: hexagon
tags:
  - "Client Follow-Up"
  - "Meeting Notes"
  - "Email Drafts"
  - "Account Management"
  - "Gmail"
  - "Granola"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: granola
  - type: api_account
    slug: gong
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Call Follow-Up Drafter

> Every client call ends with a follow-up already waiting in your drafts, in your voice, on the right thread.

## What it does

After each external call, Call Follow-Up Drafter reads the transcript, works out which client, engagement and email thread the call belongs to, and writes the follow-up you would have written: what you covered, the next steps you agreed (split into your side and theirs), and everything you asked the client for. The draft lands in your own Gmail or Outlook as a reply in the right conversation, addressed to the people who were on the call.

Getting the client right is the core rule. If a call mixes two clients, the client has more than one engagement, or the right thread isn't obvious, the agent asks you instead of guessing, and it never carries a name, number or detail from one client's call into another's email.

- **Per-call follow-up draft** — recap, next steps with owners and dates, and your asks, with numbers and dates quoted exactly as said.
- **Debrief to you** — action items grouped by person, plus the transcript spots that were unclear, so you can check before you send.
- **Welcome emails for kickoffs** — optional: fills your onboarding template from the kickoff call and marks anything it couldn't confirm.
- **Learns your voice** — from your sent mail and from the edits you make to its drafts.

It never sends anything. Every email waits in your drafts for you.

## What you'll need

- **Gmail or Outlook** — required. Reads your client threads and sent mail, and saves drafts in your mailbox.
- **Google Calendar** — required for Gmail users, to find calls that just ended and who attended. Outlook covers calendar for Microsoft users.
- **A call-notes source** — one of Granola, Gong, Fathom, Fireflies, Otter or Zoom recordings, or invite the agent to listen in on your calls.
- **A debrief channel** — the agent's own Slack app, its own email inbox, Telegram or iMessage, set up during onboarding. In-app only also works.
- **Optional:** Google Docs for a welcome template, and read-only HubSpot, Salesforce or Attio to confirm which client a contact belongs to.
- **API keys:** none.

## Getting started

1. Import the template into Gamut and send the setup message that appears in your message box.
2. The `agent-onboarding` skill connects your mailbox, calendar and notes tool, then asks for your company domains, your client list, how your follow-ups should read and where debriefs should reach you.
3. It drafts one follow-up from your most recent client call for you to correct, then sets up a transcript-ready trigger or an hourly workday sweep that never handles a call twice.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft the follow-up from my most recent client call
- Draft the Northwind kickoff welcome email from this morning's call
- Check my calls every workday hour and draft follow-ups as notes land

## What's inside

- `PROMPT.md` — the starter message you send to set the agent up; edit it before sending if you like.
- `AGENTS.md` — the follow-up, welcome and debrief routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, runs a supervised draft, schedules the sweep and writes `config.json`.
- `.claude/skills/follow-up-playbook/` — the client attribution check, the default email structure, welcome-template rules, and how the agent learns your voice.

## Notes

- Run state lives under `state/call-follow-up-drafter/` in the agent's workspace and holds meeting IDs, statuses and draft IDs, not transcripts or email bodies.
- Pairs with Call Follow-Up Nudge (tracks what you personally promised), Deck Updater (deck and covering email after demos) and Open Loops (chases the asks you made).

## Credits

Adapted from the original prompt by [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/call-follow-up-drafter/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
