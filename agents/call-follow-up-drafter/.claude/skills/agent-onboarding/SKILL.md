---
name: agent-onboarding
description: 'First-run setup for Call Follow-Up Drafter: connects mail, calendar and the meeting-notes source, learns the client list, company domains and the user''s voice, picks the debrief channel, drafts one supervised follow-up, then sets the transcript trigger or hourly sweep.'
---

# Call Follow-Up Drafter onboarding

## 1. Welcome

Tell the user in three or four sentences: after each external call this agent drafts the client follow-up in their voice, saves it in their own drafts in the right thread, and sends them a short debrief. It never sends anything to a client, and it asks when it isn't sure which client a call belongs to. Then show the plan:

1. Which mailbox and calendar to use.
2. Where your call notes or transcripts come from.
3. Your company domains and your clients.
4. How your follow-ups should read.
5. An optional welcome template for kickoff calls.
6. Where your debriefs should reach you.
7. One supervised draft from your most recent client call.
8. Scheduling.

Skip any step already answered in `## Your context` in `AGENTS.md`.

## 2. Discover connections

Call `mcp__user-input__search_connection_options` for Gmail, Outlook, Google Calendar, and the likely notes tools (Granola, Fathom, Fireflies, Otter, Gong, Zoom). Note what is already connected and the exact slug. Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram or iMessage for debriefs.

Mechanism rules:
- Mailbox and calendar: the user's connected account. Drafts must land in the user's own mailbox.
- Notes: Granola, Fireflies, Otter through their remote MCP (`granola`, `fireflies-ai`, `otter-ai`); Gong, Fathom, Zoom through connected accounts (`gong`, `fathom`, `zoom`); or the agent joining calls in `listen` mode.
- Debrief: an agent integration, or in-app only.

## 3. Ask, one question at a time

Use `AskUserQuestion` where the options are discrete. Ask open questions in plain chat.

1. **Mailbox.** Gmail or Outlook? Which address, if several are connected?
2. **Notes source.** Where do your call notes or transcripts live? (Granola / Gong / Fathom / Fireflies / Otter / Zoom recordings / I'll invite the agent to my calls.)
3. **Company domains.** Which email domains are yours (including old or subsidiary domains)? Anything outside them counts as external.
4. **Clients.** List your active clients with their email domains and, where a client has more than one, the engagement or project names. Offer to pre-fill from recent calendar attendees and, if a CRM is connected, from its companies; the user confirms.
5. **Skip list.** Which external meetings should never get a follow-up? (Recruiters, vendors, investors, personal, specific series.)
6. **Voice.** Offer: "I'll learn from your recent sent mail to clients." Ask for one or two follow-ups they were happy with, and any must-haves (greeting, sign-off, bullets or prose, length).
7. **Recipients.** Address the draft to: external attendees only / external attendees and CC internal colleagues who attended / ask me each time.
8. **Welcome template.** Do you run onboarding or kickoff calls that need a standard welcome email? If yes, paste the template or point to the Google Doc, and give the title keywords that mark those calls.
9. **Debrief channel.** Where should debriefs and "which client is this?" questions reach you? (Agent's Slack DM / Agent's email to you / Telegram / iMessage / In-app only.) Each call, or one end-of-day digest?
10. **Timing.** Confirm your timezone and workday hours (default sweep hourly 9am to 6pm on weekdays).
11. **Siblings.** If `mcp__agents__list_agents` shows Deck Updater, Call Follow-Up Nudge or Open Loops, ask: who drafts the email after sales demos (Deck Updater by default)? Should your action items and asks be handed to Open Loops?
12. **Autonomy.** Confirm: "The agent drafts and holds every email and asks when the client is unclear. It sends you debriefs on its own. It never sends anything to a client."

## 4. Connect

- `mcp__user-input__request_connected_account` with `gmail` or `outlook` ("Allow access to Gmail to read your client threads and save follow-up drafts?"), and `googlecalendar` for Gmail users.
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies or Otter with the URL from `search_connection_options`; or `request_connected_account` for `gong`, `fathom` or `zoom`.
- `googledocs` only if the welcome template is a Doc.
- For the debrief, use the configured agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or hand it over with `mcp__user-input__request_integration_setup`). Confirm with `mcp__chat__list_agent_integrations`.

## 5. Supervised dry run

1. Read 10–20 recent sent client emails and write first observations to `/workspace/state/call-follow-up-drafter/voice-notes.md`.
2. Pick the most recent external call with a transcript. Show the attribution you reached (client, engagement, thread) and the evidence. If it is uncertain, ask, as the live agent would.
3. Show the full draft (To, CC, Subject, thread, body) and the debrief in chat. Do not save it yet.
4. Ask what to change: tone, length, structure, recipients, anything wrong. Apply the corrections to `## Your context` and `voice-notes.md`, redraft once, and with the user's OK save it to their drafts. Confirm it appears in the right thread.
5. If a welcome template was given and a recent kickoff call exists, fill it once the same way.

Seed `processed-meetings.json` with the calls from the last 24 hours so the first sweep does not redraft them.

## 6. Schedule

1. If the notes source is Fathom, Zoom or Gong, call `mcp__user-input__get_available_triggers` for that account. If a transcript-ready or recording-ready event exists, call `mcp__user-input__setup_trigger` with the self-contained prompt below.
2. Unless a trigger covers every call reliably, also create the sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `0 9-18 * * 1-5` in the user's timezone.
3. If debriefs are batched, add `0 17 * * 1-5` for the digest.

Prompt template:

> Run Call Follow-Up Drafter routine 1. Config: `.claude/skills/agent-onboarding/config.json`. State: `/workspace/state/call-follow-up-drafter/`. Follow the `follow-up-playbook` skill and `AGENTS.md`. Find external calls that ended since `runs.json` last_run and are not in `processed-meetings.json`. If client, engagement or thread is uncertain, ask the user instead of drafting. Save drafts in the user's mailbox only; never send. Deliver the debrief with `send_chat_message` on integration `<id>` to `<destination>`. Send nothing for skipped calls. If a source fails, say which one. Update state when done.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers` and show the user what will run.

## 7. Save

Write the confirmed answers as short bullets under `## Your context` in `AGENTS.md`. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "workday": {"start": "09:00", "end": "18:00", "days": [1, 2, 3, 4, 5]},
  "mailbox": {"provider": "gmail", "account": "user@example.com"},
  "calendar": {"provider": "googlecalendar"},
  "notes_source": {"type": "granola", "via": "mcp", "trigger_id": null},
  "company_domains": ["example.com"],
  "clients": [
    {"name": "Example Co", "domains": ["example.org"], "engagements": ["Q1 audit"], "status": "active"}
  ],
  "skip": {"title_keywords": [], "domains": []},
  "recipients": "external_only",
  "voice": {"samples_provided": 2, "must_haves": ["first-name greeting", "bulleted next steps"]},
  "welcome": {"enabled": false, "template_source": "", "title_keywords": ["kickoff", "onboarding"]},
  "debrief": {"channel": "slack_dm", "integration_id": "", "destination": "", "batch": false},
  "schedule": {"sweep_cron": "0 9-18 * * 1-5", "digest_cron": null},
  "siblings": {"demo_email_owner": "deck-updater", "handoff_open_loops": false},
  "autonomy": {"drafts_only": true, "ask_when_attribution_uncertain": true}
}
```

Finish with a short summary: what runs when, where drafts and debriefs land, and that nothing is ever sent to a client.
