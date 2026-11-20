---
name: agent-onboarding
description: 'First-run setup for Recruiter Desk: picks which of the six routines to switch on, connects mailbox, calendar, sheets, ATS and enrichment, captures scorecards, stages and voice, runs a supervised dry run, and schedules the routines.'
first_prompt: 'Set up Recruiter Desk for me'
---

# Recruiter Desk onboarding

Goal: a working desk with only the routines the user wants, connected to their real tools, with every candidate-facing message landing as a draft.

## 1. Welcome

Open with two or three sentences: you'll set up a recruiting desk that sources candidates, reads candidate replies, writes post-interview follow-ups and scorecards, drafts weekly hiring-manager updates and nudges stalled candidates, and that nothing ever goes to a candidate or client without them sending it. Then show the plan in one short list:

1. Which routines to switch on
2. Your mailbox, calendar and ATS
3. Your searches, scorecards and stage names
4. Your voice and where alerts go
5. A dry run on real data
6. Schedules

Then start asking. One question per turn. Use `AskUserQuestion` for discrete choices, plain chat for open answers.

## 2. Questions (one at a time; skip any already answered in `## Your context`)

1. **Your setup** (`AskUserQuestion`): agency or contract recruiter working for clients / in-house recruiter / both. Then, in chat: your name, company, timezone.
2. **Routines** (`AskUserQuestion`, multi-select): Candidate Sourcing Run, Candidate Reply Assessment, Post-Interview Candidate Follow-Up, Post-Interview Pipeline Update, Hiring Manager Weekly Update, Stalled Candidate Re-Engagement. Default all on.
3. **Mailbox and calendar** (`AskUserQuestion`): Gmail + Google Calendar / Outlook. Which address do you send outreach from? (Needed for the reply gates.)
4. **ATS or tracker** (`AskUserQuestion`): Greenhouse / Ashby / Lever / Google Sheet tracker / other. Then:
   - Pipeline update: should scorecards be **submitted** or saved as **drafts / copy-paste blocks** for you?
   - Your stage names, in order. Which stage moves may be automatic and which are held? (Rejections are always held. Warn that some ATS stage moves send candidate emails automatically.)
   - The scorecard: attributes or focus areas, rating scale, overall recommendation options. Ask for it per role or a default; offer to read it from the ATS job if connected.
   - Greenhouse only: your Greenhouse user ID for write attribution.
5. **Interview detection** (pipeline and follow-up routines): how interview events look on your calendar (title keywords, scheduling tool, ATS invites). Where notes or transcripts live: Granola / Fathom / Fireflies / Otter / Zoom / my own notes doc / none. Do you want an internal hiring-manager read, and where should it go (ATS private note, email draft to you, Slack)?
6. **Active searches**: for each, role, client or company, hiring manager name and email, cc's, ATS job ID or JD link. Agency: each client's off-limits companies. Also: may candidate names appear in client updates, or initials only?
7. **Sourcing** (if enabled) (`AskUserQuestion`): Clay (if they have it) / Gamut built-in enrichment. Your teammates (or a team page link) for warm-referral matching. Countries you source in (for the privacy notice reminder).
8. **Voice**: paste two or three outreach or follow-up emails you've written. Note sign-off, length, greeting, formality.
9. **Stalled threshold and cap** (`AskUserQuestion`): 3 / 5 / 7 business days of silence; max nudges per run (default 8).
10. **Alerts to you** (`AskUserQuestion`): in-app only / the agent's Slack DM / the agent's own email inbox / Telegram. For which events: 80+ replies, do-not-contact flags, at-risk searches, drafts ready.
11. **Cadence** (`AskUserQuestion`): weekly update on Friday 8am / Monday 8am / other; stalled sweep Tue and Thu 9am / other.
12. **Autonomy confirmation**: read back the default: research, scoring and drafting run alone; nothing is sent to candidates or clients; stage changes wait unless marked automatic; rejections always wait. Ask if they want anything stricter.

## 3. Connect

For every service the enabled routines need, call `mcp__user-input__search_connection_options` first and reuse anything already connected. Then:

- Gmail / Outlook, Google Calendar, Google Sheets, Google Drive, Slack (user's), Greenhouse, Fathom, Zoom: `mcp__user-input__request_connected_account` with the slug from the search (`gmail`, `outlook`, `googlecalendar`, `googlesheets`, `googledrive`, `slack`, `greenhouse`, `fathom`, `zoom`).
- Clay, Granola, Fireflies, Otter: `mcp__user-input__request_remote_mcp` (`clay`, `granola`, `fireflies-ai`, `otter-ai`).
- Built-in enrichment: no connection; read `/opt/gamut/docs/lead-enrichment.md` and confirm it's available.
- Ashby / Lever: `mcp__user-input__request_secret` for `ASHBY_API_KEY` or `LEVER_API_KEY`. If the user has no key, plan the browser path and test a sign-in with `mcp__user-input__request_login`.
- Alerts: `mcp__chat__list_agent_integrations`; if the chosen channel isn't set up, add it with `mcp__chat__add_agent_integration` or hand it to the user with `mcp__user-input__request_integration_setup`. Resolve the exact user or DM; don't guess.

Make one cheap read call per connection to prove it works (list one label, one calendar event, one ATS job).

## 4. Dry run (supervised, on real data, nothing sent)

Pick the most useful enabled routine and run it once:
- Reply assessment: find the most recent candidate reply in the last 14 days on the user's outreach and write the internal draft. Show it.
- Pipeline update: take the last finished interview with notes and fill the scorecard as a copy-paste block. Show it next to the user's real scorecard.
- Sourcing: ask for one live role and produce the plan only; run the search only if the user approves.
- Weekly update: draft one search's update.

Ask what to change, apply it once, and save the correction to `## Your context`.

## 5. Schedule

Create only the enabled ones, with self-contained prompts (fresh sessions do not see this conversation). Each prompt states: the routine name and "follow it as written in CLAUDE.md"; read `config.json` and `## Your context` first; the state files to read and update; drafts only, never send; the alert channel; "if nothing qualifies, send nothing."

- Reply assessment: `mcp__user-input__get_available_triggers` on the `gmail` or `outlook` account, then `mcp__user-input__setup_trigger` for new incoming messages. If none is available: `schedule_task`, `cron`, `*/15 7-20 * * 1-5`.
- Post-interview (follow-up and/or pipeline): `schedule_task`, `cron`, `*/30 8-20 * * 1-5`, sweeping interview events that ended 30–120 minutes ago and skipping event IDs in `processed-interviews.json`.
- Weekly update: `0 8 * * 5` (or chosen).
- Stalled sweep: `0 9 * * 2,4` (or chosen).

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`, and show the user the list.

## 6. Save

Write the confirmed answers to `CLAUDE.md` under `## Your context` (no candidate personal data). Create `/workspace/state/` files as empty JSON (`[]` or `{}`). Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "user": { "name": "", "company": "", "mode": "agency|in-house|both", "timezone": "", "outreach_addresses": [] },
  "routines": {
    "sourcing_run": true,
    "reply_assessment": true,
    "post_interview_follow_up": true,
    "post_interview_pipeline_update": true,
    "hiring_manager_weekly_update": true,
    "stalled_re_engagement": true
  },
  "mail": { "provider": "gmail|outlook" },
  "calendar": { "provider": "googlecalendar|outlook", "interview_match": { "title_keywords": [], "organizers": [] } },
  "transcripts": { "source": "granola|fathom|fireflies-ai|otter-ai|zoom|notes_doc|none" },
  "ats": {
    "system": "greenhouse|ashby|lever|sheet|other",
    "access": "connected_account|secret|browser|sheet",
    "scorecard_mode": "submit|draft|copy_paste",
    "greenhouse_user_id": "",
    "stages": [],
    "automatic_stage_moves": [],
    "held_stage_moves": ["Rejected"],
    "default_scorecard": { "attributes": [], "scale": [], "overall_options": [] },
    "hiring_manager_read": { "enabled": false, "destination": "" }
  },
  "searches": [
    { "id": "", "role": "", "client": "", "hiring_manager": { "name": "", "email": "" }, "cc": [], "ats_job_id": "", "jd_ref": "", "off_limits_companies": [], "scorecard_override": null, "sheet_id": "" }
  ],
  "sourcing": { "enrichment": "clay|builtin", "teammates": [], "regions": [], "default_count": 30 },
  "updates": { "candidate_names_in_client_updates": "full|initials", "skip_quiet_searches": true },
  "stalled": { "threshold_business_days": 5, "max_per_run": 8, "max_nudges_per_stall": 2 },
  "alerts": { "channel": "in_app|slack_dm|agent_email|telegram", "target": "", "events": [] },
  "schedules": { "post_interview": "*/30 8-20 * * 1-5", "weekly_update": "0 8 * * 5", "stalled": "0 9 * * 2,4", "reply_fallback": "*/15 7-20 * * 1-5" },
  "voice_notes": ""
}
```

Finish with a short summary: which routines are on, what runs when (in the user's timezone), where drafts and alerts land, and three things to try now (for example "Source for the senior data engineer role", "Assess the last reply from my outreach", "Draft this week's update for each search").
