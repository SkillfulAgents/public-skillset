---
name: sourcing-sheet
description: 'Column schema, scoring bands, and write procedure for the Google Sheet produced by the Candidate Sourcing Run. Use when creating or appending a sourcing sheet so every run has the same shape.'
---

# Sourcing sheet

One spreadsheet per search (title: `Sourcing – <Role> – <Client or Company>`), one tab per run (`<YYYY-MM-DD>`), so later runs append without overwriting the user's status edits. Store the spreadsheet ID in `/workspace/state/searches.json` under the search.

## Columns (in this order)

| # | Column | Content |
|---|---|---|
| A | Rank | 1..n by Score, ties broken by archetype priority |
| B | Name | Full name as returned by search or enrichment |
| C | Status | Empty dropdown for the user: `To review`, `Reach out`, `Contacted`, `Replied`, `Pass`, `Do not contact`. Default `To review` |
| D | Score | Integer 1–100 |
| E | Archetype | One of the plan's 2–4 backgrounds, or `Adjacent` |
| F | Fit notes | 1–2 lines: which must-haves are met, the main gap, the non-obvious signal |
| G | Title | Current title |
| H | Company | Current company |
| I | Location | City / region as returned |
| J | Profile URL | Exactly as returned by the data source; blank if none. Never constructed by hand |
| K | Closest connection | Teammate name, or `None found` |
| L | Connection confidence | `High` / `Medium` / `Low`, with the evidence in a cell note or after a dash |
| M | Outreach note | Under 300 characters, in the user's voice |
| N | Source | `Clay`, `Built-in enrichment`, or `Web search` |
| O | Notes | Free column for the user. Leave empty |

Freeze row 1 and column B, add a filter, and apply data validation to column C. Sort by D descending before sharing.

## Score bands

- 85–100: every must-have, priority archetype, plus at least one non-obvious fit signal.
- 70–84: every must-have, secondary archetype or one soft gap.
- 50–69: most must-haves; one real gap worth a call to probe.
- Below 50: stretch or volume profile; keep only if the pool is thin, and say so in Fit notes.
Aim for a real spread: if more than half the list sits within a 10-point range, re-score against the must-haves.

## Write procedure

1. Check the dedup sources (ATS candidates for the role, `/workspace/state/contacted.json`, `/workspace/state/do-not-contact.json`, current employees of the hiring company, the client's off-limits list). Drop matches before enriching.
2. Create the spreadsheet (or open the stored one) with the Google Sheets API, add the dated tab, write the header row and the rows in one batch update.
3. Add a summary row block on a `Plan` tab on first creation: the JD outcomes, must-haves, hard filters, archetypes, titles, target companies, location filter.
4. Return the sheet link and a short summary. Never share the sheet with anyone but the user unless asked.

## Outreach note pattern

`<specific personalization from their background> + <one-line draw of this role> + <light ask>`. Example shape: "Your work moving a payments team onto event-driven billing stood out. We're hiring a staff engineer to lead the same shift at a Series B fintech, fully remote. Open to a quick chat?" Count characters; trim to under 300.
