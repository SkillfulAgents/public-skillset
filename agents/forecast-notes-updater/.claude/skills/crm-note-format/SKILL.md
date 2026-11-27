---
name: crm-note-format
description: 'Default CRM note structure, qualification-framework field mapping (MEDDICC, BANT, SPICED), matching and dedupe rules, stage-suggestion evidence rules, and how to write notes and fields in Salesforce, HubSpot, Attio or a Google Sheet. Use on every run before proposing or writing an update.'
---

# CRM note format and write rules

## 1. Note structure

If the user gave an example note at onboarding, copy its structure, headings, length and abbreviations exactly. Otherwise use this default:

```
[Call | Demo | Email | Slack] YYYY-MM-DD with <names, titles>
Summary: 1-2 lines on what happened.
Pain / goals: in the buyer's words, quoted where useful.
Qualification: framework fields that changed this touchpoint (see below). Gaps listed.
Objections / risks: competitor named, budget doubt, timing slip, new blocker.
Decisions: what was agreed.
Next steps: <owner> - <action> - <date or "(est.) date">
Source: <transcript or thread link>
```

Keep notes factual and skimmable. No adjectives about the buyer's mood unless they said it. Numbers and dates are quoted exactly.

## 2. Framework mapping

| Signal heard | MEDDICC / MEDDPICC | BANT | SPICED |
|---|---|---|---|
| Measurable outcome, KPI, target | Metrics | Need | Impact |
| Who signs, budget owner | Economic buyer | Authority | Decision |
| How they evaluate, criteria list | Decision criteria | Need | Critical event / Decision |
| Steps, approvals, legal, security review | Decision process / Paper process | Authority / Timeline | Decision |
| The problem in their words | Identify pain | Need | Pain |
| Internal advocate who sells for us | Champion | – | – |
| Other vendors, build in-house, do nothing | Competition | – | – |
| Budget figure or range | (note under Metrics/EB) | Budget | – |
| Deadline driving the purchase | (Decision process) | Timeline | Critical event |
| Current setup, team size | – | – | Situation |

Only fill a field from what was said on this touchpoint or a cited earlier one. Unfilled fields are listed as "Gap: not discussed". Champion is never assumed from enthusiasm alone; it needs evidence (they offered to introduce the buyer, shared internal info, or pushed the deal internally).

## 3. Matching

1. Attendee or correspondent email exactly matches a CRM contact.
2. Else email domain matches an account domain (ignore free-mail domains such as gmail.com and outlook.com).
3. Else company name from the calendar title or signature, fuzzy match, then confirm with the user.
4. Account found: exactly one open opportunity → use it. More than one open opportunity → flag and ask which. None open → flag ("no open deal; log to account only or create one?").
5. Several buyer companies on one call (partner, reseller) → flag; never split a note across accounts on your own.

## 4. Dedupe

Before proposing, read the opportunity's activity for the touchpoint date ±1 day. A proposed note is a duplicate if a note or task exists with the same meeting ID or thread ID, or the same date and an overlapping subject, or the same next step text. If a human already logged a thinner note, propose an append that adds only what is missing. Record the meeting ID or thread ID in the note body (`Source:` line) so later runs can detect it.

## 5. Stage and forecast suggestions

- Suggest at most one stage change per deal per batch, only when the evidence meets the user's stage definition, and quote the supporting line with a timestamp.
- Typical forward evidence: pricing or proposal requested, security review started, mutual action plan agreed, legal redlines received, verbal yes from the economic buyer.
- Backward or closed moves are never suggested as automatic. Closed Lost, Pass, Disqualified, Closed Won: say "possible, your call" with the quote, nothing more.
- Close date, amount and forecast category changes are proposals only, with the quote. Never derive a new amount from a range.

## 6. Human-edit guard

Before every write, re-read the record. If `LastModifiedDate` is later than the touchpoint and `LastModifiedById` is not the connected user via this agent (check `write-log.json`), do not overwrite. Propose an append or flag the conflict.

## 7. Writing per CRM

All calls go through the proxy with the user's connected account.

**Salesforce** (REST, `/services/data/vXX.X/`; discover the version with `GET /services/data/`):
- Activity: create a `Task` with `WhatId` = opportunity ID, `WhoId` = contact ID, `Subject`, `Description` (the note), `ActivityDate`, `Status = Completed`, `TaskSubtype = Call` or `Email`.
- Rich notes if the org uses them: `ContentNote` (body base64-encoded HTML) linked with `ContentDocumentLink` (`LinkedEntityId` = opportunity ID, `ShareType = V`).
- Fields: `PATCH sobjects/Opportunity/{id}` for `NextStep` (255 characters), `Description`, and the user's custom forecast fields (find API names with `GET sobjects/Opportunity/describe`; never guess a `__c` name). `StageName`, `ForecastCategoryName`, `Amount`, `CloseDate` only after explicit approval.
- Query with SOQL: `SELECT Id, Name, StageName, NextStep, LastModifiedDate, LastModifiedById FROM Opportunity WHERE AccountId = '...' AND IsClosed = false`.

**HubSpot** (CRM v3): create a note object (`POST /crm/v3/objects/notes`, `hs_note_body`, `hs_timestamp`) with associations to the deal and contact (and company); next step and custom properties via `PATCH /crm/v3/objects/deals/{id}`. `dealstage` values are pipeline-specific stage IDs; read them from `GET /crm/v3/pipelines/deals`.

**Attio**: create a note (`POST /v2/notes`, `parent_object` = `deals` or `people`, `parent_record_id`, `title`, `content`, `format`); update deal attributes with `PATCH /v2/objects/deals/records/{id}`. Read attribute slugs from the object's attributes endpoint first.

**Google Sheet fallback**: one row per touchpoint (date, account, opportunity, note, next step, owner, due, suggested stage, source link, meeting ID). Append only; never rewrite earlier rows.

After every write, append to `write-log.json` and report the record links to the user.
