---
category: "Productivity"
icon: sunrise
avatar:
  color: tonal-amber
  shape: bloom
tags:
  - "Morning Brief"
  - "Prioritization"
  - "Gmail"
  - "Google Calendar"
  - "Slack"
  - "Open Loops"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Daily Briefing

> Start every workday knowing the five things that actually need you, in a message you can read in two minutes.

## What it does

Each workday morning, at the time you pick, the agent looks back at everything since your last brief (email, Slack, and any task tracker or meeting notes you connect) and ahead at today's calendar. It also checks your open loops: promises you made that are coming due, and things you're still waiting on from other people.

It ranks everything by consequence rather than arrival time, keeps a top handful under "Needs you today", and folds the rest into a count. Each meeting gets one line on who and why, with conflicts, unanswered invites and anything to prepare flagged. Monday's brief covers the weekend, and holidays and out-of-office days are skipped.

It remembers what you've handled or dismissed, so the same thread doesn't come back every morning unless something about it changed. On a quiet day you get one line instead of filler. If you like, it also makes a short audio version with the platform's built-in speech.

## What you'll need

- **Gmail or Outlook** — required; read-only, to find what needs you.
- **Google Calendar or Outlook Calendar** — required; read-only, for today's meetings and conflicts.
- **Slack** — recommended; your account is read for DMs, mentions and any channels you choose.
- **A task tracker or meeting notes** — optional (Todoist, Asana, Linear, Notion, Granola and others).
- **A delivery channel** — optional; a DM from the agent's own Slack app, an email from its own inbox, Telegram or iMessage. Otherwise the brief appears in the app.
- **API keys:** none. Audio uses built-in speech, metered per character; onboarding gives an estimate first.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill. It connects your mail, calendar and Slack, asks who always matters and what to skip, and sets your time, workdays, delivery channel and audio preference.
3. Review the supervised first brief on real data, adjust, and let it schedule the daily run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Brief me now on what came in since yesterday morning
- What's due from me today, and who am I still waiting on?
- Move my brief to 7:30 on weekdays and add an audio version

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `AGENTS.md` — the agent's instructions: the morning brief, dismissals, audio, Gamut mechanics and safety rules.
- `.claude/skills/agent-onboarding/` — first-run setup, dry run and scheduling.
- `.claude/skills/rank-and-remember/` — the consequence scoring and the ledger that stops handled items from resurfacing.

## Notes

- The agent is read-only. It never replies, accepts or declines invites, or changes anything in your mail, calendar or Slack.
- Reply "done 2", "drop 3" or "snooze the Acme one till Thursday" to tidy the brief.
- If a source fails to load, the brief says so instead of pretending it was a quiet day.
- Founders who want more sources, fire-flagging and an end-of-day pass should look at Chief of Staff Briefing instead.

## Privacy

The agent reads your mail, calendar and Slack through your own connected accounts. Its state files hold only IDs, dates, senders and one-line summaries, never message bodies.

## Credits

Adapted from the original prompt by [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/daily-briefing/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
