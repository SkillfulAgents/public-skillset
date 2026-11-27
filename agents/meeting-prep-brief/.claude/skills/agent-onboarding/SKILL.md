---
name: agent-onboarding
description: 'First-run setup for Meeting Prep Brief: connects calendar, mail and optional notes or CRM sources, learns which meetings deserve a brief and when to deliver it, runs a supervised brief on a real meeting, then schedules the planning runs.'
---

# Meeting Prep Brief onboarding

Run this before any other work, including when the user sends the pre-filled setup request from `PROMPT.md`. Reuse anything already in `AGENTS.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

Say in two or three sentences what will be set up: a short brief before each external, first-time or high-stakes meeting, built from the calendar, the user's email history, web research and any notes or CRM they connect, delivered where and when they choose. Then list the questions you will ask (sources, own domains, which meetings, timing, delivery, deck agent, autonomy) so they know it takes about five minutes.

## 2. Find the right connections

For each service call `mcp__user-input__search_connection_options` with the service name, and check `CONNECTED_ACCOUNTS`, the remote MCP list and `mcp__chat__list_agent_integrations` for what already exists.

- Calendar: connected account `googlecalendar` or `outlook`. Required.
- Mail: connected account `gmail` or `outlook`. Required.
- Notes (optional): ask with `AskUserQuestion` which they use: Granola (remote MCP `granola`), Fireflies (`fireflies-ai`), Otter (`otter-ai`), Fathom (`fathom`), Gong (`gong`), none.
- CRM (optional): Salesforce, HubSpot, Attio (connected accounts `salesforce`, `hubspot`, `attio`), Pipedrive or Close (remote MCP), none.
- Slack (optional): connected account `slack`, only if they want internal chatter about the account included. Ask which channels.
- Web research and built-in lead enrichment need no connection.

## 3. Ask the critical questions, one at a time

Use `AskUserQuestion` where the options are discrete.

1. **Own domains**: "Which email domains are internal?" Propose the domain of the connected mailbox and ask for others (subsidiaries, contractors, partner domains to treat as internal).
2. **Which meetings**: options "External meetings only (recommended)", "External plus internal meetings I flag", "Everything with at least one other person". Ask whether recurring 1:1s should be left to One-On-One Prep (default yes) and for any skip-list titles.
3. **High-stakes rules**: accounts to always treat as high-stakes, a deal size threshold if a CRM is connected, and any keywords of their own.
4. **Timing**: options "The evening before, one message for the next day", "Shortly before each call", "Both". If shortly before, ask the lead time (30, 45, 60, 90 minutes). Confirm workdays and timezone.
5. **Delivery**: options "Here in the app", "DM from this agent's Slack app", "Email from this agent's own inbox to me", "Telegram or iMessage". If an agent integration is missing, set it up (see step 4).
6. **Length and shape**: show the format from the `meeting-triage` skill and ask what to cut or add ("what does a good brief look like to you?").
7. **Deck agent**: call `mcp__agents__list_agents`. If a slides or deck agent exists, ask: "Never", "Ask me each time (recommended)", "Automatically for first-time and high-stakes calls".
8. **Autonomy**: confirm the default: research and brief alone; never contact attendees, never touch the calendar, never send as the user.

## 4. Connect

- `mcp__user-input__request_connected_account` for each chosen account, for example reason "Allow access to Google Calendar to find which meetings need a brief?" and "Allow access to Gmail to read past threads with meeting attendees?".
- `mcp__user-input__request_remote_mcp` for notes or CRM MCP servers, with the URL from `search_connection_options`.
- For delivery as the agent: follow `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration` (or `mcp__user-input__request_integration_setup` to let the user do it). Confirm with `mcp__chat__list_agent_integrations` and resolve the user's DM or address with `mcp__chat__list_chat_users`.
- If a connection is declined, carry on without it and note it under "Not checked" in briefs.

## 5. Supervised dry run

Pick the next real qualifying meeting (or tomorrow's, as the original setup asked). Show the triage result for the whole day first (briefed, skipped and why), then the full brief in chat. Ask what to change, apply it once, and show the revised brief. Do not send it to the delivery channel unless the user asks for a test send.

## 6. Schedule

Read `/opt/gamut/docs/scheduling-and-resuming.md`, then create with `mcp__user-input__schedule_task`:
- Day ahead: cron `0 18 * * 0-4` (adjusted to their workdays and time).
- Shortly before: planning cron `0 6 * * 1-5`, plus optional midday sweep `0 12 * * 1-5`. The planning run creates one-shot `at` tasks per meeting.
- Optional: `mcp__user-input__get_available_triggers` on the calendar account; if an event-created or event-updated trigger exists, offer it via `mcp__user-input__setup_trigger` so late bookings are caught.

Each prompt must be self-contained: routine name, config path `.claude/skills/agent-onboarding/config.json`, context in `AGENTS.md`, ledger path `/workspace/state/meeting-prep-brief/briefed.json`, delivery channel and destination, and the rules (skip internal and already-briefed meetings, send nothing if cancelled or nothing qualifies, never contact attendees or edit the calendar). Verify with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 7. Save

Write a short summary under `## Your context` in `AGENTS.md` (domains, which meetings, timing, delivery, sources, deck setting) and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "workdays": [1, 2, 3, 4, 5],
  "ownDomains": ["example.com"],
  "internalDomains": ["example-subsidiary.com"],
  "calendars": ["primary"],
  "scope": "external",
  "skipRecurringOneOnOnes": true,
  "skipList": ["Standup", "All hands"],
  "flaggedAccounts": ["acme.com"],
  "highStakesDealAmount": 50000,
  "highStakesKeywords": ["pricing", "renewal", "contract"],
  "timing": { "mode": "before", "leadMinutes": 45, "dayAheadTime": "18:00" },
  "delivery": { "channel": "slack", "integrationId": "", "destination": "" },
  "sources": { "mail": "gmail", "calendar": "googlecalendar", "notes": "granola", "crm": null, "slackChannels": [] },
  "deckAgent": { "slug": null, "mode": "ask" }
}
```

Finish by telling the user what runs when, where briefs arrive, and that they can say "re-run onboarding" anytime.
