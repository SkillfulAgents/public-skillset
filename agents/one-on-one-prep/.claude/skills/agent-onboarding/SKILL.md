---
name: agent-onboarding
description: 'First-run setup for One-On-One Prep: connects calendar, mail, notes and a docs home, finds every recurring 1:1, learns each relationship, runs a supervised prep for the next 1:1, then schedules the planning runs.'
---

# One-On-One Prep onboarding

Run this before any other work, including when the user sends the pre-filled setup request from `PROMPT.md`. Reuse anything already in `CLAUDE.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

Explain in two or three sentences: a private running doc per recurring 1:1, updated a couple of hours before each one, with open items carried forward, what the person is waiting on, and an agenda. List the questions you will ask (calendar and sources, which 1:1s, doc home, timing, heads-up channel, reminders, privacy) so the user knows what is coming.

## 2. Find the right connections

For each service call `mcp__user-input__search_connection_options` and check `CONNECTED_ACCOUNTS`, the remote MCP list and `mcp__chat__list_agent_integrations`.

- Calendar: `googlecalendar` or `outlook` connected account. Required.
- Mail: `gmail` or `outlook` connected account. Recommended.
- Notes: ask with `AskUserQuestion`: Granola (remote MCP `granola`), Fireflies (`fireflies-ai`), Otter (`otter-ai`), Fathom (`fathom`), Zoom (`zoom`), "I keep notes in the doc itself", none.
- Slack: `slack` connected account, read-only, for DMs and mentions with each person. Optional.
- Doc home: `AskUserQuestion` with "Google Docs (recommended)" (`googledocs` plus `googledrive`), "Notion" (`notion`), "A Markdown file here in the agent".

## 3. Find the 1:1s

Read the next 14 days of the calendar. List recurring series with exactly one other attendee, plus recurring series with two or three attendees whose titles contain "1:1", "1-1", "one on one", "sync" or "check-in". Show the list and ask the user to confirm which ones count, and to add any that were missed.

## 4. Ask the critical questions, one at a time

1. **Relationship per person**: for each confirmed 1:1, ask with `AskUserQuestion`: Manager, Direct report, Peer, Client, Other. This sets the agenda order.
2. **Timing**: lead time before each 1:1 (1, 2 or 3 hours, or the evening before). Confirm timezone and workday start.
3. **Heads-up channel**: "Here in the app", "DM from this agent's Slack app", "Email from this agent's own inbox to me", "Telegram or iMessage", or "No heads-up, I will just open the doc".
4. **Sources per person**: should Slack DMs and mentions be included? Any person whose mail should be excluded (for example a sensitive HR situation)?
5. **Reminders**: turn on reminders for what the user owes after each 1:1? If Open Loops is installed (`mcp__agents__list_agents`), offer to hand them to it instead.
6. **Sensitive content**: confirm the default that the doc never copies content about this person from other conversations; offer to opt in per person.
7. **Adding topics**: explain the two ways (tell the agent in chat, or type in the "To raise" box at the top of the doc). Ask if they also want to send topics through the agent's Slack or Telegram.
8. **Autonomy**: confirm: update docs and send heads-ups alone; never share, invite, or message the other person.

## 5. Connect

- `mcp__user-input__request_connected_account` for each chosen account, for example "Allow access to Google Calendar to find your recurring 1:1s?" and "Allow access to Google Docs to keep a private prep doc for each 1:1?".
- `mcp__user-input__request_remote_mcp` for the notes server, using the URL from `search_connection_options`.
- Delivery as the agent: `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`; confirm with `mcp__chat__list_agent_integrations` and resolve the user with `mcp__chat__list_chat_users`.

## 6. Supervised dry run

Prep the next upcoming 1:1. Create the doc (private, owned by the user, in a folder named "1:1s (private)") or the Markdown file, write the first section in the `running-doc` format, and show it in chat with the link. Point out what came from where and anything you could not find. Ask what to change, apply it once, and confirm the sharing setting is private.

## 7. Schedule

Read `/opt/gamut/docs/scheduling-and-resuming.md`, then:
- `mcp__user-input__schedule_task` cron planning run `0 6 * * 1-5` (and `0 18 * * 0-4` if any 1:1 starts within two hours of the workday). It creates one-shot `at` tasks per 1:1 and, if reminders are on, per 1:1 end plus 30 minutes.
- Optionally `mcp__user-input__get_available_triggers` on the calendar account; if an event-updated or cancelled trigger exists, offer `mcp__user-input__setup_trigger` for same-day moves.

Each prompt must be self-contained: routine, config path `.claude/skills/agent-onboarding/config.json`, context in `CLAUDE.md`, state paths under `/workspace/state/one-on-one-prep/`, delivery channel, and the rules (skip if cancelled or moved; never share the doc or contact the other person). Verify with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 8. Save

Write a short summary under `## Your context` in `CLAUDE.md` (people and relationships, timing, doc home, channel, reminders) and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "Europe/London",
  "workdayStart": "09:00",
  "leadMinutes": 120,
  "docHome": "googledocs",
  "docFolder": "1:1s (private)",
  "people": [
    {
      "email": "sam@example.com",
      "name": "Sam Rivera",
      "relationship": "report",
      "seriesId": "",
      "docUrl": "",
      "includeSlack": true,
      "includeMail": true,
      "allowCrossConversationContent": false
    }
  ],
  "notesSource": "granola",
  "heads_up": { "channel": "slack", "integrationId": "", "destination": "" },
  "reminders": { "enabled": false, "handTo": null }
}
```

Finish by telling the user which 1:1s are covered, when preps run, where the docs live, and how to add topics during the week.
