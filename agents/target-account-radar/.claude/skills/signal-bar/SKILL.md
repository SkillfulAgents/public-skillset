---
name: signal-bar
description: 'Decides whether a news item or X post about a watched account clears the bar for the digest or an alert, and how to write the outreach angle. Use before including any item.'
---

# Signal bar

## Gate (all must be true)

1. **Sourced:** a working link and a publication date. Prefer the company's own release, a filing, or a primary outlet.
2. **Fresh:** inside the lookback window (digest default 14 days; X watch: since the last check).
3. **New:** not in `/workspace/state/target-account-radar/seen.json`, and not the same story under a different URL.
4. **Right entity:** domain, industry or named people confirm it is the watched account.
5. **Relevant:** it plausibly changes what the account needs, who decides, or when, in relation to the user's angle.

## Strength

| Strength | Examples |
|---|---|
| High (alert-worthy on X) | new exec in the buying function; funding round; acquisition (either side); launch in the user's category; public complaint about a competitor's product; layoffs or reorg in the buying team |
| Medium (digest) | earnings with stated priorities; expansion to a new region; hiring cluster in a relevant function; partnership; conference keynote on a relevant topic |
| Low (drop unless the user asked) | awards, generic thought leadership, reposts, event attendance, minor product updates |

X alerts require High. The digest takes High and Medium.

## Angle formula

One sentence each:
- **Fact:** what happened, with the date.
- **Implication:** what that likely means for them (label it as an inference).
- **Opening:** a first line that ties the fact to the user's offer, and asks a question rather than pitching.

Example shape: "Saw the expansion into two new regions announced on the 4th. Teams scaling support across time zones usually hit routing problems first. Is that on your radar for Q1?"

Avoid: bare congratulations, pity angles on layoffs, guessing at confidential details, and any claim the source does not support.

## X query hygiene

- One query per topic, using quoted phrases, `from:` lists, and `-is:retweet -is:reply`.
- `max_results` 10-20 unless the user asked for more. Pass `since_id` from `x-cursors.json`.
- Request only `tweet.fields=created_at,public_metrics,author_id`.
- Rough cost is $0.005 per post returned and $0.010 per user object. Track the posts read per run in state, and warn the user when the projected monthly cost passes the budget.
