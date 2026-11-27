---
name: agent-onboarding
description: 'First-run setup for Voice of Customer: connects the call recorder, calendar, doc tool and CRM, captures the segment list and the existing messaging-doc format, sets the transcript trigger, nightly sweep and weekly idea schedule, and mines a few real calls under supervision.'
first_prompt: 'Set up Voice of Customer for me'
---

# Voice of Customer onboarding

Run this before first use. Reuse anything already in `AGENTS.md` under `## Your context` and in `config.json`; ask only for what is missing.

## 1. Welcome

Explain in two or three sentences: after each customer or prospect call, the agent mines what customers said into a living messaging doc per segment (with a separate product-feedback lane), and every week it sends five to eight content ideas grounded in that signal. Then list the questions you will ask:

1. Where your call recordings or transcripts live
2. Your segment list and how a customer maps to one
3. Your existing messaging doc, so the new one inherits its format
4. Where the docs should live
5. Whether quotes may carry people's names
6. Your content channels and recent topics
7. Where and when to send recaps and the weekly ideas
8. What the agent may do alone vs. ask first

## 2. Discover and connect

Call `mcp__user-input__search_connection_options` for each candidate and note what is already connected.

- **Recorder.** Ask which one they use with `AskUserQuestion`: Granola, Gong, Fathom, Fireflies, Otter, Zoom recordings, or "the agent joins my calls". Connect it: Granola, Fireflies and Otter through `mcp__user-input__request_remote_mcp` (URL from `search_connection_options`); Gong, Fathom and Zoom through `mcp__user-input__request_connected_account` (`gong`, `fathom`, `zoom`). For "the agent joins", explain that it uses `mcp__meetings__join_meeting` in `listen` mode per call and that attendees should know a note-taker is present.
- **Calendar.** `googlecalendar` (or `outlook`), used only to tell external calls from internal ones by attendee domains.
- **Docs.** Google Docs (`googledocs`, with `googledrive` for folders) or Notion (`notion`). Markdown files in `/workspace/voc/` if they want neither.
- **CRM.** `hubspot` or `salesforce`, for segment fields and weekly trends.

## 3. Ask the critical questions, one at a time

1. **Internal domains.** Which email domains are internal? Any partner or reseller domains to treat as external?
2. **Segment list.** Ask for the list and the rule for each (CRM field and value, company size band, industry, persona). If they use a CRM field, read its options and confirm. Ask what to do with calls that fit none (default: "Unsorted").
3. **Existing doc.** Ask for their current messaging or positioning doc (link, or `mcp__user-input__request_file`). Read it and propose how its sections map onto the default in the `messaging-doc-format` skill; their headings win. Ask whether to extend the existing doc in place or start new per-segment docs next to it.
4. **Which calls count.** Default: customers, prospects and churned customers. Ask about partner calls, user research sessions and support escalations. Ask about any account or topic to exclude.
5. **Names in quotes.** Use `AskUserQuestion`: full name and title, title and company only, or company only.
6. **Their messages.** Ask for the three to five core messages or claims they are testing, so "what landed / fell flat" has something to check against.
7. **Content.** Which formats they publish (LinkedIn, blog, email, video, case studies), where recent content can be read (blog RSS, a content calendar doc, pasted list), how far back to skip repeats (default 60 days), and any goals for the quarter.
8. **Delivery.** With `AskUserQuestion`: in-app only, the agent's Slack app DM, the agent's own email inbox, or Telegram. Check `mcp__chat__list_agent_integrations`; set up a missing integration with `mcp__chat__add_agent_integration` or `mcp__user-input__request_integration_setup`, and resolve the exact destination.
9. **Cadence and timezone.** Nightly sweep time (default 22:00), weekly ideas day and time (default Monday 08:00), timezone.
10. **Autonomy.** Confirm: the agent updates the messaging docs alone, and asks before any outside write (CRM persona tags, product-feedback tickets, sharing docs). Ask whether they want CRM tagging proposed at all.

## 4. Supervised dry run

Pick three to five recent external calls from the last two weeks. Mine them, show the user the proposed doc changes (new themes, strengthened themes, quotes with attribution, product-feedback items) and the list of skipped calls with reasons. Iterate once on format and depth, then write the docs. Then build a sample weekly idea list from the same material and adjust the format once.

## 5. Triggers and schedules

1. **Transcript-ready trigger.** For a connected-account recorder, call `mcp__user-input__get_available_triggers` with that toolkit and look for a transcript-ready or recording-completed event. If found, `mcp__user-input__setup_trigger` with a prompt that says: fetch this call's transcript, check the processed ledger, qualify, mine, fold into the segment doc per the `messaging-doc-format` skill, log, and stay silent unless the user asked for per-call recaps. If no trigger exists but the service supports webhooks, offer `mcp__user-input__create_webhook_endpoint` with signature verification. Otherwise rely on the sweep.
2. **Nightly sweep.** `mcp__user-input__schedule_task`, `scheduleType: "cron"`, default `0 22 * * *`. Self-contained prompt, for example:

   > Run the Voice of Customer nightly sweep. Read config from `.claude/skills/agent-onboarding/config.json`. List calls from the configured recorder in the last 48 hours; skip any ID in `/workspace/state/voice-of-customer/processed.json`; skip internal and logistics calls. For each remaining call, assign the segment, extract the messaging signal and product feedback, and fold them into that segment's doc using the `messaging-doc-format` skill. Quotes must be exact and attributed. Do not write to the CRM or any outside system; add proposals to `pending-actions.json`. If anything was added, send a short recap to the configured destination with `mcp__chat__send_chat_message`; otherwise send nothing.

3. **Weekly ideas.** `schedule_task`, `cron`, default `0 8 * * 1`, with a self-contained prompt covering sources, the 5 to 8 limit, the traceability rule, the repeat lookback and the destination.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers`.

## 6. Save configuration

Write the answers into `AGENTS.md` under `## Your context`, and save `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/Chicago",
  "recorder": {"tool": "granola | gong | fathom | fireflies-ai | otter-ai | zoom | join_meeting", "trigger_id": null},
  "calendar": "googlecalendar",
  "internal_domains": ["example.com"],
  "external_partner_domains": [],
  "call_types_included": ["customer", "prospect", "churned"],
  "exclusions": [],
  "segments": [
    {"name": "Mid-market finance teams", "rule": "CRM industry = Financial Services and employees 200-2000", "doc": ""}
  ],
  "unsorted_doc": "",
  "doc_tool": "googledocs | notion | markdown",
  "inherited_format": "",
  "quote_attribution": "name_title_company | title_company | company",
  "core_messages": [],
  "crm": "hubspot | salesforce | none",
  "content": {"formats": ["LinkedIn post", "blog"], "recent_topics_source": "", "repeat_lookback_days": 60, "goals": ""},
  "delivery": {"via": "in-app | slack | email | telegram", "destination": ""},
  "schedules": {"sweep_cron": "0 22 * * *", "ideas_cron": "0 8 * * 1"},
  "ask_before": ["crm_writes", "feedback_tickets", "doc_sharing"]
}
```

Finish with a summary of what runs when, where each doc lives, and how to re-run onboarding.
