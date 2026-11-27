---
name: time-reconstruction
description: 'How to rebuild a week of billable time by client from calendar, sent email and edited docs, with evidence per block, estimate labels, overlap removal and unlogged-time flags. Use in every Billable Hours Recap run.'
---

# Time reconstruction

Read-only. You never create time entries or invoices from this; the founder confirms hours first.

## 1. Gather evidence for the window (default Monday 00:00 to Friday 23:59, user timezone)

| Source | What counts | Estimate rule (defaults, configurable) |
|---|---|---|
| Calendar (`googlecalendar` or `outlook`) | Events the user accepted or organized, with at least one attendee on a client domain, or titled with a client name | Scheduled duration. Skip declined, cancelled and "tentative, no-show" events. All-day events count as zero and are listed for review. |
| Sent email (`gmail` or `outlook`) | Messages the user sent to a client domain | 0.1 h per substantive message; threads with several sends in a sitting are one block, capped at 0.5 h unless the user raised the cap |
| Docs edited (`googledrive` / `googledocs`, `one_drive`) | Files the user modified in a client folder or with a client name in the title | Cluster edits less than 30 minutes apart into one session; session length from first to last edit plus 0.25 h, capped at 3 h per session |
| Time tracker (Harvest, Toggl, sheet) | Entries already logged | Used only for comparison, never as evidence of new time |

## 2. Assign each block to a client

Match by attendee or recipient domain, then the client map in config (domains, folder ids, nicknames), then the event or file title. If two clients match, or none, put the block in **Unassigned** with the reason. Internal meetings (only the agency's own domain) are non-billable unless the title names a client and the config says to count them.

## 3. Remove overlap

The same minutes cannot be billed twice. When an email or doc session falls inside a meeting, keep the meeting and drop the other block. When doc sessions overlap each other, merge them.

## 4. Round

Round each client's daily total up to the configured increment (default 0.25 h; some shops use 0.1 h). Show raw and rounded.

## 5. Compare with what is logged

Per client per day: estimated vs. logged. Flag **possibly unlogged** when the estimate exceeds logged time by more than the configured gap (default 0.5 h or 25%, whichever is larger). Flag **logged with no evidence** separately, gently; it may be offline work.

## 6. Output format

Per client, one table: date, block (start-end), source, evidence (event title, email subject, or file name with a link), estimated hours. Then client totals: estimated, logged, possibly unlogged. End with Unassigned and the all-day events. Every hours figure carries the word "est." and the header says: "Estimates from calendar, email and document activity. Confirm before billing."

Never quote email bodies or document contents beyond the subject or title.
