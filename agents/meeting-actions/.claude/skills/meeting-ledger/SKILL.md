---
name: meeting-ledger
description: 'Extraction rules, task fingerprinting, the recap layout, and the decisions-log format for Meeting Actions. Use on every meeting processed and whenever reading or writing /workspace/state/meeting-actions/.'
---

# Meeting ledger

## Extraction checklist

For each meeting, produce three lists. Every item carries a transcript timestamp or note line so the user can check it.

**Decision** (all must hold): a choice between options was made; someone with authority agreed or nobody objected after it was stated as settled; it changes what people will do. Record the decision in one sentence, the decision owner, and the follow-through owner if different.

**Action item** (all must hold): a specific person is named or clearly implied ("I'll", "Dana, can you", "Dana: yes"); a concrete deliverable; it is meant to happen after the meeting. Record owner, deliverable, due date, due-is-estimate flag, and context (one or two sentences so the task stands alone).

**Open question**: raised, not settled, and needs an answer or a decision. Record who is expected to answer, if anyone.

Not action items: "we should", "it would be nice", ideas parked for later, status reports about work already in a task (those are updates to the existing task).

## Owner resolution

1. Match the spoken name or speaker label to calendar attendees (first name, full name, email local part).
2. If two attendees share a first name, or the speaker label is generic, check the surrounding lines for who answered. Still unsure: assign the user, mark "(owner unclear)", and list it in "Confirm".
3. Map the attendee to a tracker user with the `people` map in config. No mapping: create the task unassigned with the person's name in the description, and ask the user to add the mapping.

## Fingerprint and dedupe

`fingerprint = sha1(lower(owner_email) + "|" + normalized_deliverable + "|" + (client or project))`, where `normalized_deliverable` is lowercased, punctuation stripped, stopwords removed, and words sorted. Check `tasks.json` for the fingerprint, then search the tracker for open items in the same project created in the last 60 days whose title shares most key words. A hit means comment and update, never create.

Tracker search hints:
- Linear GraphQL: `issues(filter: {team: {key: {eq: "ENG"}}, title: {containsIgnoreCase: "vendor comparison"}, state: {type: {nin: ["completed", "canceled"]}}})`.
- Jira: `POST /rest/api/3/search/jql` with JQL `project = OPS AND statusCategory != Done AND summary ~ "vendor comparison"`.
- Asana: `GET /workspaces/{gid}/tasks/search?text=vendor%20comparison&completed=false`.
- GitHub: `GET /search/issues?q=repo:org/name+is:issue+is:open+in:title+vendor+comparison`.

## Task body

Title: verb first, under 80 characters ("Send Q3 vendor comparison to finance").
Description: context sentence, the exact quote if it contains numbers or dates, meeting name and date, link to the transcript, due date with "(est.)" if estimated. Never paste the whole transcript.

## Recap layout

```
<Meeting title> · <date>
Yours: <items with due dates>
Decided: <decisions>
Tasks: created N, updated M (<links>)
Routed: <channel or person: what>
Their court: <external owners' items>
Open questions: <items>
Drafts waiting: <group follow-up, external notes>
Confirm: <ambiguous owners, low-confidence lines, possible reversals>
```

Omit empty sections. If the meeting produced nothing, the recap is one line.

## Decisions log format

Top of doc: "Open going into next meeting" (follow-through items not done, oldest first, with days overdue). Below it, one entry per decision, newest first:

```
2026-11-18 · Weekly leadership
Decision: Move the pricing change to January 6.
Decided by: CEO · Follow-through: Head of Sales, due 2026-11-25
Status: Open · Source: <transcript link>
Supersedes: 2026-10-14 "Ship pricing change December 1"
```

Mark superseded entries by appending "Superseded by <date>" on their Status line. Never rewrite their text.

## State files

`processed-meetings.json`: `{"<meeting_id>": {"status": "done", "processed_at": "...", "title": "...", "tasks": ["<fingerprint>"]}}`

`tasks.json`: `{"<fingerprint>": {"tracker": "linear", "id": "ENG-123", "url": "...", "meetings": ["<meeting_id>"], "owner": "...", "due": "2026-11-25", "due_is_estimate": true}}`

Write both atomically (temp file, then rename).
