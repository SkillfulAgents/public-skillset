---
category: "Sales"
icon: presentation
tags:
  - "Sales Decks"
  - "Demo Follow-Up"
  - "Google Slides"
  - "Meeting Notes"
  - "Sales Enablement"
works_with:
  - type: api_account
    slug: googleslides
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: granola
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Deck Updater

> Every demo ends with a deck about the prospect's problem, not your generic pitch, waiting in your Drive with the email already drafted.

## What it does

After each external demo or discovery call, Deck Updater reads the transcript and pulls out the prospect's goals, their pains in their own words, the use cases they cared about, the objections they raised, who was in the room, and the agreed next steps. It then copies your master Google Slides deck into a folder for that account and tailors the copy: a recap of the call, how you map to their top pains, proof points from your approved library, answers to their objections, pricing only if it came up, the agreed next steps, and one clear call to action. Slides that don't apply are cut; your theme, fonts and layouts are left alone.

Every tailored line is tagged in the speaker notes as said on the call or inferred, and you get a short review list of what to double-check. A covering email in your voice, linking the deck and naming the next step, waits in your Gmail drafts on the existing thread. If your next meeting with that account is already booked, the deck is ready before it, and a morning refresh picks up anything new from the thread.

Deck Updater never edits your master deck, never invents customer names, logos or numbers, never sends the email, and never shares the deck outside your company without your approval.

## What you'll need

- **Google Slides and Google Drive** — required. The master deck, the tailored copies and the per-account folders.
- **Gmail** — required for the covering-email drafts. Outlook works instead.
- **Google Calendar** — required, to find which sales calls ended and when the next one is.
- **Granola** — or another notes source: Gong, Fathom, Fireflies, Otter, Zoom recordings, or inviting the agent to listen in on calls.
- **HubSpot or Salesforce** — optional, read-only, for account context when picking calls.
- **A delivery channel** — the agent's own Slack app, its own email inbox, Telegram or iMessage for the "deck ready" notice. In-app only also works.
- **API keys:** none.

## Getting started

1. Import the template into Gamut and send the setup message that is already in the message box.
2. The `agent-onboarding` skill connects your tools, reads your master deck, maps your standard and proof-point slides, learns your email voice from sent mail, and asks how decks are named, shared and delivered.
3. It builds one supervised deck from a real recorded call so you can correct it, then sets up the transcript trigger or an hourly workday sweep.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Build a follow-up deck from my last discovery call notes
- Tailor the master deck to the pains the Acme team raised and draft the email
- Refresh the deck before tomorrow's call with anything new from the thread

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the post-call deck and pre-meeting refresh routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, maps the master deck, runs a supervised build, and schedules the work.
- `.claude/skills/slides-tailoring/` — how to copy and tailor the deck with the Slides API, the slide-library tags, the default outline, and the said-versus-inferred tagging.

## Notes

- Proof points come only from slides or a doc you mark as approved; anything missing shows up as a placeholder for you to fill.
- Decks stay private (or company-wide, if you choose). You decide when to share the link with the prospect.
- Pairs with Call Follow-Up Drafter (so the prospect gets one email, not two) and Forecast Notes Updater (the CRM note for the same call).

## Credits

Adapted from the original prompt by [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/deck-updater/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
