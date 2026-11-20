---
name: agent-onboarding
description: 'First-run setup for Investor Update Drafter: who sends the update, the artifact and cadence, where past updates and metrics live, output destination, and the schedule.'
first_prompt: 'Set up Investor Update Drafter for me'
---

# Onboarding: Investor Update Drafter

## 1. Welcome

Tell the user, in two or three sentences: this agent drafts the recurring update from the last one plus what actually changed, marks every missing number instead of guessing, and never sends. Then show the questions you will ask:

1. Are you the sender, or drafting for a principal?
2. What kind of update, how often, and when is it due?
3. Where do past updates live?
4. Where do the numbers and the "what shipped" come from?
5. Where should the draft and the summary land?
6. Anything that must never appear in an update?

Check `## Your context` in `CLAUDE.md` first and skip anything already answered.

## 2. Ask, one at a time

Use `AskUserQuestion` for discrete choices; ask open questions in plain chat.

1. **Role** (`AskUserQuestion`): "I send it myself" / "I draft it for a principal (EA or chief of staff)". If principal, ask the principal's name as it appears in sign-offs, and whether the draft goes to the user's or the principal's mailbox.
2. **Artifact** (`AskUserQuestion`): startup monthly investor update / quarterly investor update / LP update / partner-meeting recap / other.
3. **Cadence and due date**: e.g. "monthly, by the 5th". How many days ahead to draft (default 3). Timezone. Calendar or fiscal periods.
4. **Past updates**: "Where can I find the last one: sent Gmail (what does the subject usually look like?), a Google Doc folder, or somewhere else?" If it lives in a tool with no connector (Visible, DocSend), ask them to forward or upload the last one (`mcp__user-input__request_file`).
5. **Metric list and definitions**: read the last update and propose the metric list back to the user; confirm each definition (e.g. "ARR = active subscription MRR x 12, excluding trials") and where each value comes from.
6. **Sources for the rest**: shipped work (GitHub, Linear, or a changelog), pipeline and customers (CRM or email), hires (email, ATS, or tell me), cash and runway (finance sheet, Finance Reporting Desk, or tell me).
7. **Output destination** (`AskUserQuestion`): Gmail draft / Google Doc in a folder / both. Recipients: leave empty (default) or pre-fill a list.
8. **Summary channel** (`AskUserQuestion`): in-app only / the agent's Slack bot DM / the agent's own email / Telegram or iMessage.
9. **Sensitive topics**: customers under NDA, topics that always need the user's call.
10. **Autonomy** confirm: "I'll draft and save, never send. OK?"

## 3. Connect

For each service the user named, call `mcp__user-input__search_connection_options` and see what's already connected. Then:

- Gmail / Outlook, Google Drive, Google Docs, Google Sheets, Excel, Stripe, GitHub, Linear, HubSpot, Salesforce, Attio: `mcp__user-input__request_connected_account` with the slug (e.g. reason "Allow access to Gmail to find your last investor update and save the new draft?").
- PostHog, Amplitude, Mixpanel, Carta: `mcp__user-input__request_remote_mcp` with the URL from `search_connection_options`.
- Summary channel: `mcp__chat__list_agent_integrations`; if the chosen one isn't set up, `mcp__chat__list_available_integration_providers` then `mcp__chat__add_agent_integration`, or hand it to the user with `mcp__user-input__request_integration_setup`.

Skip anything the user declined and note the gap in config.

## 4. Supervised dry run

Run routine 1 for the most recent period with real data. Show the user: the last update you anchored on, the commitments list with statuses, the draft, and the placeholder list. Ask what to change (tone, length, sections, metric sources). Apply the changes once and save them to config. Save the draft only if the user wants it.

## 5. Schedule

Create the recurring run with `mcp__user-input__schedule_task` (`scheduleType: "cron"`), e.g. `0 9 1 * *` for an update due on the 5th, in the user's timezone. Use the self-contained prompt from `CLAUDE.md` > How this runs on Gamut, filled with the real config path, destination and channel. Confirm with `mcp__user-input__list_scheduled_tasks`.

## 6. Save

Write the answers to `CLAUDE.md` under `## Your context` (plain bullets), and this file to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "role": "founder | drafting_for_principal",
  "principal_name": "",
  "artifact": "startup_monthly | quarterly | lp_update | partner_recap | other",
  "cadence": { "frequency": "monthly", "due_day": 5, "draft_days_ahead": 3, "period_basis": "calendar", "timezone": "America/New_York" },
  "past_updates": { "gmail_subject_pattern": "", "drive_folder_id": "" },
  "metrics": [ { "name": "MRR", "definition": "", "source": "stripe | sheet | manual", "sheet_range": "" } ],
  "sources": { "shipped": ["github", "linear"], "pipeline": "", "hires": "", "cash_runway": "" },
  "output": { "destination": "gmail_draft | google_doc | both", "drive_folder_id": "", "recipients": [] },
  "summary_channel": { "type": "in_app | slack | email | telegram | imessage", "integration_id": "", "target": "" },
  "sensitive_topics": [],
  "schedule": { "cron": "0 9 1 * *", "task_id": "" }
}
```

Finish with a short summary: what runs when, where the draft lands, where the summary arrives, and which sources are missing.
