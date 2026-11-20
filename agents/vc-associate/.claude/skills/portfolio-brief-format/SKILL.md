---
name: portfolio-brief-format
description: 'The fixed structure for each living portfolio company brief, plus the rules for dating facts, moving old items to Historical, and handling conflicting numbers. Use whenever a portfolio brief is created or updated.'
---

# Portfolio brief format

One doc per company, updated in place. The top of the doc is always current; nothing older than about six months stays above the Historical heading.

## Structure

```
# <Company> — Portfolio Brief
Last updated: YYYY-MM-DD · Stage · Sector · Board seat: yes/no/observer
Ownership / invested (Carta, as of YYYY-MM-DD): ... (omit if not connected)

## Top 3 Asks
1. <What the founder needs from investors now> — asked YYYY-MM-DD [source]

## Open Commitments
### Founder owes me
- <item> — promised YYYY-MM-DD, due YYYY-MM-DD [source]
### I owe founder
- <item> — promised YYYY-MM-DD, due YYYY-MM-DD [source]

## 4-Quarter Snapshot
| Metric | Q-3 | Q-2 | Q-1 | Latest |
|---|---|---|---|---|
| Revenue or ARR (say which) | | | | |
| Net burn | | | | |
| Cash | | | | |
| Runway (months) | | | | |
| Headcount | | | | |

## Recent Context
- YYYY-MM-DD: <what happened> [source]

## Sources
- [n] <email subject or file name>, YYYY-MM-DD, <link>

## Historical
- <items older than ~6 months, newest first>
```

## Rules

- Every fact carries a date and a source number. A number without a source doesn't go in.
- Use the company's metric names and period labels. If a definition changes, keep both rows or footnote the change; never chart across a definition change silently.
- Missing values are "not reported". Computed values (runway from cash and burn) are marked "(computed)".
- A newer source wins. Never replace a number with an older one because an old deck arrived late.
- If two sources disagree, show both with their sources and add a line under Recent Context.
- Completed commitments are struck from Open Commitments and logged once in Recent Context.
- Top 3 Asks are asks, not news. If the founder hasn't asked for anything, write "No open asks".
- At each refresh, move Recent Context items, completed commitments and stale asks older than ~180 days to Historical.
- Add a line at the top, "Couldn't open: <link> (reason)", whenever a link or attachment failed, and keep it there until it's resolved.
