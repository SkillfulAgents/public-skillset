---
name: agent-onboarding
description: 'First-run setup for Deck Updater: connects slides, Drive, mail, calendar and meeting notes, captures the master deck, proof-point library, voice and sharing rules, runs a supervised build on one real call, and sets up the trigger or sweep.'
---

# Deck Updater onboarding

## 1. Welcome

Tell the user in three or four sentences: after each demo or discovery call, this agent copies their master deck, tailors the copy to what the prospect said, marks what it inferred, and leaves a covering email in their drafts. It never sends or shares anything externally. Then show the plan:

1. Which tools to connect (slides, Drive, email, calendar, meeting notes).
2. Your master deck and where approved proof points live.
3. Which calls count as sales calls.
4. How the tailored decks are named, filed and shared.
5. How your follow-up emails sound.
6. Where the "deck ready" notice reaches you.
7. What the agent does alone.
8. A supervised build on one of your recorded calls.

Skip anything already answered in `## Your context` in `CLAUDE.md`.

## 2. Discover connections

For each of Google Slides, Google Drive, Gmail, Outlook, Google Calendar, the meeting-notes tool and the CRM, call `mcp__user-input__search_connection_options` with the service name. Note what is connected and the exact slug. Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram or iMessage.

Mechanism rules:
- Slides, Drive, mail, calendar, CRM: the user's connected account (decks and drafts must be the user's).
- Meeting notes: Granola, Fireflies, Otter via remote MCP (`granola`, `fireflies-ai`, `otter-ai`); Gong, Fathom, Zoom via connected account (`gong`, `fathom`, `zoom`); or the agent joins calls in `listen` mode.
- Notice to the user: an agent integration, or in-app only.

## 3. Ask, one question at a time

Use `AskUserQuestion` where options are discrete.

1. **Mail and calendar.** Gmail with Google Calendar, or Outlook? Which address if several?
2. **Meeting notes.** Where do your call notes or transcripts live? (Granola / Gong / Fathom / Fireflies / Otter / Zoom recordings / I'll invite the agent to calls.)
3. **Your domains.** Which email domains are your own company? (Anyone else on an invite is external.)
4. **Which calls.** Which calls get a deck? Offer: all external calls with a sales keyword in the title (demo, discovery, intro, walkthrough) / only calls on open CRM opportunities / only when I ask. Ask for extra keywords and an ignore list (investors, vendors, recruiting).
5. **Master deck.** Paste the link to the master Google Slides deck. Read it, list its slides back, and ask which are always kept, which are pricing, and which are optional by pain, use case or industry. Offer to write the `#library` tags into the master's speaker notes only with explicit permission; otherwise keep the mapping in config.
6. **Proof points.** Where do approved case studies, metrics, logos and quotes live (tagged slides, a doc or a sheet)? Which customers are cleared to be named externally?
7. **Pricing.** When pricing came up on a call, may the deck show your standard list price, only what was said, or never pricing (you add it)?
8. **Filing.** Parent Drive folder for account folders, and the naming pattern (default `<Account> – Follow-up – <YYYY-MM-DD>`). Target slide count (default 8–12).
9. **Sharing.** Keep new decks private to you, or shared with your company domain? (External sharing always waits for you.)
10. **Voice.** Read 10–20 of your recent sent follow-ups to prospects and summarize your voice; ask the user to confirm or paste one they like. Ask for the usual sign-off.
11. **Timing.** Timezone, and how long before the next meeting the deck must be ready (default 24 hours).
12. **Email ownership.** If Call Follow-Up Drafter is installed (check `mcp__agents__list_agents`): who drafts the email after demo calls? (This agent with the deck link / Call Follow-Up Drafter, given the link / Ask each time.)
13. **Delivery.** Where should the "deck ready" notice reach you? (Agent's Slack DM / Agent's email to you / Telegram / iMessage / In-app only.)
14. **Autonomy.** Confirm: "The agent builds deck copies and saves email drafts on its own. It never sends email, never shares a deck outside your company, and never edits the master." Ask whether the pre-meeting refresh may update decks it built, or only propose changes.

## 4. Connect

- `mcp__user-input__request_connected_account` for `googleslides`, `googledrive`, `gmail` or `outlook`, `googlecalendar`, and `gong` / `fathom` / `zoom` or the CRM if chosen. Reason text such as "Allow access to Google Slides to build tailored copies of your master deck?"
- `mcp__user-input__request_remote_mcp` for Granola, Fireflies or Otter, using the URL from `search_connection_options`.
- Delivery: use the configured agent integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or `mcp__user-input__request_integration_setup`). Confirm with `list_agent_integrations`.

## 5. Supervised dry run

Ask the user to pick one recent recorded sales call. Run routine 1 end to end following the `slides-tailoring` skill:
- show the extracted brief (goals, pains with quotes, people, objections, pricing, next steps);
- build the tailored copy and share its link with the user only;
- show the review list of `[INFERRED]` and `[CHECK]` items;
- show the covering email text, and save it to drafts only after the user approves the wording.

Ask what was wrong: slides kept or cut, emphasis, tone, missing proof points. Update the library mapping and voice notes, rebuild once, and mark that meeting `done` in `/workspace/state/deck-updater/processed-meetings.json`.

## 6. Schedule

- If the meeting source is Gong, Fathom or Zoom: call `mcp__user-input__get_available_triggers` on that connected account and `mcp__user-input__setup_trigger` for a recording- or transcript-ready event if one exists. Otherwise, and for Granola, Fireflies and Otter, create an hourly workday sweep with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, `0 9-18 * * 1-5`.
- If the refresh is on, schedule `0 7 * * 1-5`.

Scheduled prompt template (self-contained):

> Run the Deck Updater **post-call follow-up deck** routine. Config: `/workspace/.claude/skills/agent-onboarding/config.json`; context in `CLAUDE.md` `## Your context`. Follow the `slides-tailoring` skill. Consider calendar events that ended since `runs.json` last_run; skip meetings already `done` in `/workspace/state/deck-updater/processed-meetings.json`; mark missing notes `pending_notes`. Copy the master deck, never edit it. Save the covering email as a draft only; never send; never change sharing. Notify via `send_chat_message` on integration `<id>` to `<destination>`. If no qualifying call, send nothing. If a source fails, say which.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers` and show the user what is set.

## 7. Save

Write confirmed answers under `## Your context` in `CLAUDE.md` as short bullets. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "own_domains": ["example.com"],
  "mail": {"provider": "gmail", "account": "user@example.com"},
  "calendar": {"provider": "googlecalendar"},
  "meeting_source": {"type": "granola", "via": "mcp", "trigger_id": null},
  "call_filter": {"mode": "keywords", "keywords": ["demo", "discovery", "intro", "walkthrough"], "ignore": ["investor", "interview"]},
  "master_deck_id": "",
  "library": {
    "source": "tagged_slides",
    "doc_id": null,
    "slide_map": [{"slide_id": "", "tags": ["fixed"]}],
    "cleared_customers": []
  },
  "pricing_policy": "only_what_was_said",
  "list_price_note": "",
  "filing": {"parent_folder_id": "", "name_pattern": "<Account> – Follow-up – <YYYY-MM-DD>", "slide_target": [8, 12]},
  "sharing": "private",
  "ready_lead_hours": 24,
  "voice": {"notes": "", "sign_off": ""},
  "email_owner": "deck-updater",
  "crm": {"provider": null},
  "refresh": {"on": true, "cron": "0 7 * * 1-5", "may_write": true},
  "sweep_cron": "0 9-18 * * 1-5",
  "delivery": {"channel": "slack_dm", "integration_id": "", "destination": ""},
  "autonomy": {"drafts_only": true, "external_sharing": "never_without_approval"}
}
```

Finish with a short summary: what triggers a build, where decks and drafts land, where the notice arrives, and that nothing is sent or shared without the user.
