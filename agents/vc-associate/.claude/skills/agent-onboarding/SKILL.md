---
name: agent-onboarding
description: 'First-run setup for VC Associate: pick which of the seven routines to turn on, connect the mailbox, calendar, Drive, notes and CRM, capture the investment thesis and rules, do a supervised dry run, then create each routine trigger and schedule.'
first_prompt: 'Set up VC Associate for me'
---

# VC Associate onboarding

Goal: the user picks the routines they want, each one is connected, tested on real data, and scheduled. Ask one question at a time. Use `AskUserQuestion` whenever the options are discrete. Skip anything already answered in `CLAUDE.md` `## Your context`.

## 1. Welcome

Say in a few lines what this agent does, then list the seven routines with one line each:

1. Investor Inbox Triage: labels every email into four buckets and sends a morning digest.
2. Deal Flow to Pipeline: logs intros, decks and data rooms to your deal tracker.
3. Living Portfolio Briefs: one always-current doc per portfolio company.
4. Board Meeting Prep: forward board materials, get a 7-section memo in Drive.
5. LP Meeting Prep Brief: a brief before every LP meeting.
6. LP Re-Engagement Digest: monthly list of quiet LPs with a hook and a draft each.
7. Warm Intro Thank-You: drafts the thank-you to whoever introduced a founder you met.

Then show the planned questions: which routines, your mail and calendar, where notes and CRM data live, your thesis, the rules for each routine you picked, where reports should reach you, and what the agent may do on its own. Say that nothing is ever sent to founders, LPs or introducers without the user.

## 2. Pick routines

`AskUserQuestion` with multi-select over the seven routines. Recommend starting with 1, 2 and 4 if the user is unsure. Every later question applies only to the routines picked.

## 3. Connections

For each service below, call `mcp__user-input__search_connection_options`, check `CONNECTED_ACCOUNTS` and `mcp__chat__list_agent_integrations` for what already exists, and only request what's missing.

- **Mailbox** (all routines except 5): Gmail or Outlook? `request_connected_account` with `gmail` or `outlook`, reason "Allow access to Gmail to label investor mail and save drafts for your review?".
- **Calendar** (5, 7): `googlecalendar` (or Outlook calendar through `outlook`).
- **Drive and Docs** (3, 4; also 2 for Drive deck links): `googledrive` and `googledocs`. Ask whether briefs should live in Drive or Notion (`notion`).
- **Deal tracker** (2): Google Sheet (`googlesheets`), Affinity, Attio (`attio`) or HubSpot (`hubspot`). Follow the `crm-access` skill. For Affinity, offer the API key route first (`request_secret` with `AFFINITY_API_KEY`), and the browser route if their plan has no API access.
- **LP records** (5, 6): same choices; often a different tool from the deal tracker. Read-only.
- **Meeting notes** (3, 4, optional for 5): Granola (`request_remote_mcp`, slug `granola`), Fireflies (`fireflies-ai`), Otter (`otter-ai`), Fathom (`fathom` connected account), or a Drive folder of notes.
- **Carta** (optional, 3 and 4): `carta` remote MCP, for ownership and invested capital.
- **Dropbox** (optional): `dropbox`, if updates arrive as Dropbox links.
- **Agent's own email inbox** (4, recommended): `mcp__chat__list_available_integration_providers`, then `mcp__chat__add_agent_integration` with provider `platform-email`. Give the user the address to forward board materials to.
- **Delivery channel**: `AskUserQuestion`: in-app only, the agent's Slack DM, the agent's own email, or Telegram. Set up the chosen agent integration and resolve the exact destination with `list_chat_users` or `list_chat_channels`.

## 4. Questions per routine

Ask only for the routines picked, one at a time.

**Triage (1)**
- Label names: keep the defaults (`VC/1 Today's Focus` … `VC/4 Delegated`, plus lane labels) or use their own?
- The hard skip list: which senders or kinds of mail should always be archived? Offer defaults (newsletters with an unsubscribe header, promotions, receipts, social notifications) and ask for additions.
- Who are the people they delegate to (associates, EA), so Delegated can be detected?
- Fund-admin and LP senders: which platforms and domains (fund administrator, LP portal, tax preparer)?
- Digest time, and whether to ping immediately for new Today's Focus items, or wait for the digest.
- If the digest is empty: send a one-line "all clear" or nothing?

**Deal flow (2)**
- Thesis: stages, sectors, geographies, typical check size.
- Opportunity-type allowlist (for example primary seed, Series A, co-invest allocations, secondaries).
- Sender allowlist: trusted introducers, co-investors, scouts, accelerators.
- Domain blocklist.
- Sensitivity threshold: `AskUserQuestion` with low, medium (default), high.
- High-priority alert: immediately, or in the morning digest?

**Portfolio briefs (3)**
- The portfolio list: company, domains, founder emails (accept a pasted list, a sheet, or a CRM list).
- Which metrics matter per company type, beyond revenue, burn, cash, runway and headcount.
- Folder for briefs, and whether a refresh time other than 6am works.

**Board prep (4)**
- Keyword (default "BOD prep") and the addresses they'll forward from.
- Forward to the agent's inbox, or trigger on their own mailbox?
- Drive folder for memos.
- Accept the default Green/Yellow/Red thresholds in `board-prep-memo`, or change them?

**LP meeting prep (5)**
- How to recognize an LP meeting (CRM match on attendee domain, title keywords).
- Lead time: morning-of plus 2 hours before (default), or the evening before?

**LP re-engagement (6)**
- Days-since-contact threshold (default 30), list size (default 10), how to rank relationship value.
- Anyone to always exclude.
- Drafts only in the digest, or also as unsent drafts in the mailbox?
- Paste one or two recent emails to LPs, for voice.

**Thank-you (7)**
- Keep the founder on the thank-you, or introducer only (default)?
- Thank introducers when still evaluating, or only after a decision?
- Paste one thank-you note they've written before, for voice.

**Autonomy (all)**
Confirm the defaults with `AskUserQuestion`: labels, archiving, tracker rows and brief and memo docs happen on their own; drafts are always held; nothing is sent to anyone external. Record any tighter preference (for example "suggest labels, don't apply them for the first week").

## 5. Supervised dry run

For each routine picked, run once on real data without writing anything external:
- Triage: the last 30 inbox messages; show the proposed bucket, lane and why-line per thread; apply labels only after the user approves.
- Deal flow: the last 2 weeks of deal-looking mail; show proposed rows and duplicates; write after approval.
- Portfolio briefs: one company; show the brief, and list anything that didn't open.
- Board prep: the most recent board deck they can forward or point to.
- LP prep: the next LP meeting on the calendar, or a past one.
- LP digest: three LPs.
- Thank-you: one recent intro meeting; show the draft in chat before saving it as a draft.

Ask what to change, apply it, and re-run once if needed.

## 6. Triggers and schedules

Read `/opt/gamut/docs/scheduling-and-resuming.md` and `/opt/gamut/docs/webhooks.md` first. Use the user's timezone.

- Mail routines: `mcp__user-input__get_available_triggers` on the mailbox account, then `mcp__user-input__setup_trigger` as described in `CLAUDE.md` (one narrow trigger per routine if filters exist, otherwise one combined trigger running enabled mail routines in order). No trigger available: `schedule_task` cron `*/15 7-21 * * *` sweep with the ledgers.
- Board prep: incoming mail to the agent inbox starts a session; confirm the routing with a test forward.
- Schedules with `mcp__user-input__schedule_task`, `scheduleType: "cron"`, defaults: triage digest `30 7 * * 1-5`; deal catch-up `0 19 * * 1-5`; portfolio refresh `0 6 * * *`; LP prep `0 6 * * 1-5` and `0 8-18 * * 1-5`; LP re-engagement `0 8 1 * *`; thank-you sweep `0 18 * * 1-5`.
- Each prompt is self-contained. Example for the digest: "Run VC Associate routine 1 digest. Read CLAUDE.md Your context and .claude/skills/agent-onboarding/config.json. Read /workspace/state/triage-ledger.json for threads labeled since the last digest. Build Today's Focus (one why-line each), Action Required, then LP and Fund Admin. Send with mcp__chat__send_chat_message to <integration and destination>. If nothing is in Today's Focus or Action Required and quiet mode is on, send nothing."
- Confirm with `list_scheduled_tasks` and `list_triggers`, and show the user the list.

## 7. Save

Write the answers in plain sentences under `## Your context` in `CLAUDE.md`, and the config to `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "",
  "enabled_routines": ["triage", "deal_flow", "portfolio_briefs", "board_prep", "lp_prep", "lp_reengage", "intro_thank_you"],
  "mailbox": {"provider": "gmail", "account": ""},
  "calendar": {"provider": "googlecalendar", "calendar_id": "primary"},
  "delivery": {"channel": "in_app|slack|email|telegram", "integration_id": "", "destination": "", "quiet_when_empty": true},
  "triage": {"labels": {}, "lane_labels": true, "skip_list": [], "delegates": [], "fund_admin_domains": [], "digest_cron": "30 7 * * 1-5", "instant_focus_alerts": false},
  "deal_flow": {"tracker": {"type": "sheet|affinity|attio|hubspot", "ref": ""}, "thesis": {"stages": [], "sectors": [], "geos": [], "check_size": ""}, "opportunity_types": [], "sender_allowlist": [], "domain_blocklist": [], "sensitivity": "medium", "high_priority_alert": "digest"},
  "portfolio": {"store": "googledocs|notion", "folder": "", "companies": [{"name": "", "domains": [], "founder_emails": [], "extra_metrics": []}]},
  "board_prep": {"keyword": "BOD prep", "intake": "agent_inbox|mailbox_trigger", "sender_addresses": [], "folder": "", "health_thresholds": "default"},
  "crm": {"deals": "", "lps": "", "affinity_route": "api|browser|none"},
  "notes_source": "granola|fireflies-ai|otter-ai|fathom|drive|none",
  "lp_prep": {"match_rules": [], "lead_time": "morning_and_2h"},
  "lp_reengage": {"days_threshold": 30, "max_items": 10, "ranking": "", "exclude": [], "create_mail_drafts": false},
  "intro_thank_you": {"recipients": "introducer_only", "thank_when_evaluating": false},
  "voice_samples": [],
  "triggers": [],
  "schedules": []
}
```

Create `/workspace/state/` and empty ledgers. Finish with a short summary: which routines are on, what runs when, where output lands, and that every external message stays a draft.
