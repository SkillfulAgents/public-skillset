---
name: messaging-doc-format
description: 'Default structure for a per-segment living messaging doc, the quote record format, evidence levels and the merge rules for folding a new call into existing themes. Use when creating or updating a Voice of Customer messaging doc, unless the user supplied their own format.'
---

# Messaging doc format

If the user gave you an existing doc during onboarding, its structure wins: map the sections below onto theirs and keep their headings. Use this default only when there is no existing format.

## Doc layout (one doc per segment)

```
<Segment name> messaging doc
Last updated <date> · <N> calls mined · <M> companies

1. Summary (5 lines max: top jobs, top pains, top objection, best line)
2. Jobs to be done
3. Pains and triggers
4. Objections and what answered them
5. Their words (vocabulary for the problem, the category, the outcome)
6. What lands / what falls flat
7. Proof points (asked for, offered)
8. Quote bank
9. Fading (themes not heard in ~90 days)
10. Sources
---
Product feedback lane (not messaging)
   Bugs · Feature requests · Integrations · Pricing and packaging
```

## Theme entry

```
- <Theme in the customer's framing> [recurring · 3 companies · last heard 2026-11-12]
  Evidence: <Company A> (2026-10-02), <Company B> (2026-10-28), <Company C> (2026-11-12)
  Best quote: "<exact words>" (VP Finance, <Company B>, 2026-10-28, [call])
```

Evidence levels:
- **observed**: one company. Phrase as "one prospect said…".
- **recurring**: two or three independent companies.
- **established**: four or more companies, across at least two weeks. Only these may be phrased as confident statements in the summary.

Count distinct companies, not calls. Note in the entry when a rep introduced the phrasing and the customer only agreed.

## Quote record

Every quote in the bank:
- Exact text from the transcript. Ellipsis for trims. No edits inside quotation marks.
- Speaker role (and name only if the user allowed names), company, call date.
- Link to the transcript or recording, with timestamp when the recorder provides one.
- The theme(s) it supports.
- "OK to use publicly": unknown by default.

## Merge rules for a new call

1. For each extracted item, compare against existing themes in the same segment and lane by meaning, not wording.
2. Match: add the company and date to evidence, bump the level if the count crosses a threshold, swap in the new quote only if it is clearer or more vivid, and update "last heard".
3. No match: add a new theme as "observed".
4. Two existing themes that turn out to be the same: merge them, keep all evidence, and mention the merge in the recap.
5. Contradicting evidence (one segment says price is the blocker, another says it is not) stays visible; write both and the companies behind each.
6. Product feedback goes only to the bottom lane, with attribution, and never counts toward messaging themes.

## Sources list

One line per mined call: date, company, attendees' roles, segment, recorder link. Keep it in date order, newest first.
