---
category: "Ops"
icon: flame
tags:
  - "Chief of Staff"
  - "Founder Briefing"
  - "Prioritization"
  - "Gmail"
  - "Slack"
  - "Discord"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
  - type: api_account
    slug: linear
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Chief of Staff Briefing

> A founder's early-morning briefing that puts the fires first, then everything only you can unblock.

## What it does

Every morning, before your day starts, the agent sweeps your Gmail, calendar, Slack, Discord and project tools since the last briefing. It ranks everything against your people tiers, the projects you care about and your own urgency rules.

The briefing leads with fires: what broke, which rule it tripped, who's already on it and what's needed from you. Then come the decisions and approvals waiting on you, today's meetings with what to prepare, commitments you owe and are owed, and one line per watched project that moved, slipped or went quiet. Anything you've handled or dismissed stays gone unless it changes.

Two optional extras: an hourly fire watch during working hours that alerts only on new fires, and an end-of-day pass with three short lists (where you're the blocker, replies people are waiting on, promises about to go stale) that stays silent when there's nothing.

## What you'll need

- **Gmail** — required; read for messages and your own commitments. Outlook works too.
- **Google Calendar** — required; read-only, for today's meetings.
- **Slack** — recommended; your account is read for DMs, mentions and the channels you choose.
- **Discord** — optional; read for the servers and channels you choose, usually through the agent's own Discord app in your server. Skipped if it can't read them.
- **Linear or another project tool** — optional (GitHub, Jira, Asana, Notion, ClickUp), for project movement.
- **A delivery channel** — optional; by default the briefing lands in its own chat in the app. It can also come as a DM from the agent's Slack app, an email from its own inbox, Telegram or iMessage.
- **API keys:** none.

## Getting started

1. Import the template into Gamut. The setup request is pre-filled in the message box from `PROMPT.md`; edit it if you like and send it.
2. Sending it starts the `agent-onboarding` skill. It connects your tools and asks for your people tiers, projects, channels and urgency rules, plus the briefing time, delivery and autonomy.
3. Review the supervised first briefing on real data, tune what counts as a fire, and let it schedule the daily run and any extras you turned on.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Give me this morning's briefing with fires first
- What's waiting on my approval across Gmail and Slack right now?
- Turn on the end-of-day pass at 5:30pm and add an outage rule

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the agent's instructions: morning briefing, fire watch, end-of-day pass, Gamut mechanics and safety rules.
- `.claude/skills/agent-onboarding/` — first-run setup, dry run and scheduling.
- `.claude/skills/fire-rules/` — the fire test, urgency-rule format, ranking and the dismissed-item ledger.

## Notes

- The agent reads and briefs on its own. Sending any message, changing your calendar, or any other external action waits for your approval. Reply drafts in your own mailbox are off unless you turn them on, and are never sent.
- If a source fails to load, the briefing says so at the top.
- For a lighter brief without fire-flagging, use Daily Briefing instead.

## Privacy

The agent reads your accounts through your own connections and keeps only IDs, dates, names and one-line summaries in its state files. The briefing goes only to you.

## Credits

Adapted from the original prompt by [@jessethanley](https://x.com/jessethanley) on [Bot Directory](https://botdirectory.ai/bots/chief-of-staff-briefing/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
