# Scoring rubric: X posts worth replying to

> TEMPLATE — the `## Who we are` section and the GOOD-post examples are written
> by the agent-onboarding skill from the user's product brief
> (`/workspace/product/product-brief.md`). The scoring framework below them is
> product-agnostic; refine it as the user gives feedback on real batches.

## Who we are

<!-- onboarding writes: product name + one-paragraph positioning, target customer (ICP), key differentiators, competitor list (with ambiguous-name warnings if any) -->

## What counts as a GOOD post

<!-- onboarding writes: 3-5 concrete post archetypes worth replying to, e.g. competitor-alternative asks, category/tool recommendations, gripes the product solves, specific-need asks. Include real examples once calibration finds them. -->

## Score 0-100

- **Fit (0-50)**: Is it a genuine ASK or GRIPE (question > statement) the product can credibly answer? Direct competitor-alternative asks = 40-50. Category/tool asks = 35-50. Buildable/solvable specific-need asks = 30-45. Relevant gripes = 25-40. Vague musings, self-promo threads, news commentary = 0-10.
- **Author (0-25)**: Real human in or near the ICP. Followers: 500-5k = 10, 5k-50k = 18, 50k+ = 25 (300+ genuine person still gets 8). Spam/engagement-farm/anon bios = 0 and cap total score at 20.
- **Replyability (0-25)**: Fresh (higher if <48h), not already saturated with identical pitches, a reply from the founder/team would land as helpful rather than spammy. Question posts with modest engagement (2-50 replies) are ideal.

## Hard disqualifiers (score 0)

- The post is itself promoting a product/thread/newsletter
- Engagement bait ("drop your favorite tool 👇" from a growth account)
- Job posts, academic papers, news links
- Classic retweets (no original text)
- Out-of-ICP topics <!-- onboarding adds product-specific exclusions here, e.g. crypto noise, adjacent-but-wrong audiences -->

## Quote / RT check (required)

`search.py` attaches `is_quote`, `quoted_text`, `quotes_launch`. Always inspect these before scoring.

- Classic RTs are already dropped in search; if one slips through, score 0.
- Quote of a competitor launch/shipping post (`quotes_launch` true, or quoted_text clearly a launch): do NOT treat the quoted launch as the ask. Score only the author's OWN text; keep only if it is a standalone genuine ask/gripe, and label it ("quote of a launch") when surfacing so the user can judge.

## Output

Return ONLY a JSON array of posts scoring >= 55, sorted by score desc:

```json
[{"id": "...", "url": "...", "score": 78, "category": "...", "author": "...", "followers": 1234, "age_hours": 12.3, "text": "<full tweet text>", "why": "<1 sentence>", "angle": "<1 sentence: what a good reply would say>"}]
```

If none score >= 55, return `[]`. Aim to surface only the top 1-3 per run.
