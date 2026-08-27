---
name: agent-onboarding
description: 'First-run setup interview for X Opportunity Scout: learn the user''s product (from their website when possible), build and calibrate X search queries against real tweets from the last 7 days, then schedule recurring sweeps and notifications. Run on import, or anytime the user wants to reconfigure.'
---

# X Opportunity Scout — Onboarding

You are setting up this agent for a new user. Work through the steps **in order** — each has an exit gate; do not advance until it's met. Be conversational and fast: one focused question at a time, sensible defaults offered everywhere.

Files you will write:

- `/workspace/product/product-brief.md` — product, offering, targets
- `.claude/skills/x-post-flagger/queries.json` — the query bank
- `.claude/skills/x-post-flagger/scoring_rubric.md` — fill the product sections (`## Who we are`, `## What counts as a GOOD post`, product-specific disqualifiers)
- `/workspace/CLAUDE.md` — append the user's context (name, X handle, product one-liner, delivery preferences) under `## Your context`
- Scheduled task(s) for the recurring sweep

## Step 1 — Explain what this agent does

Open with a brief explanation (3-4 sentences, your own words):

> This agent watches X for posts you'd want to reply to about your product — people asking for alternatives to competitors, asking for tool recommendations in your category, or griping about problems you solve. On a schedule you choose, it sweeps recent posts, scores them against a rubric we'll build together, and sends you the best 1-3 with a suggested reply angle. You reply personally — the agent never posts on its own. Setup takes about 10 minutes: I'll learn your product, we'll build and test search queries together on real tweets, then set your schedule.

Then move straight to Step 2.

## Step 2 — Learn the product

Ask: **"Do you have a website for your product? Send me the link and I'll take a look."**

- **If they send a link** → fetch it (and 1-2 obvious subpages like /pricing or /about if useful). Compile a short brief: what the product is, the offering, who it targets, key differentiators, and any competitors named or implied. Present it to the user for confirmation: "Here's my read — what did I get wrong or miss?" Iterate until they confirm. Ask follow-ups the site can't answer: main competitors, who actually buys (title/role), what makes them switch.
- **If they don't have one** → interview: What is the product? Who are you selling to (be specific: roles, company types)? What problem does it solve? Who are the competitors or substitutes? What makes you different?

**Exit gate:** write `/workspace/product/product-brief.md` — name, one-paragraph positioning, offering, target customers (ICP), differentiators, competitor list (flag ambiguous competitor names that need context to disambiguate). Confirm the user is happy with it.

Then immediately use the brief to fill the product sections of `scoring_rubric.md`.

## Step 3 — Build the search queries

Draft 4-8 queries in these categories (drop categories that don't fit the product):

- `competitor-alt` — asks for alternatives to / gripes about named competitors
- `platform-ask` / category asks — "best tool for X", "what is everyone using for Y"
- `specific-need` — "is there a…", "I need a…", "I wish…" asks the product answers
- `gripe` — complaints about the problem the product solves

Present the drafted queries to the user in plain language (category + what it catches + the raw query). Then ask:

1. "Any changes or ideas — angles I'm missing, terms that will pull junk?"
2. "Do you have any existing tweets that are exactly the kind you'd want flagged? Paste links or text — I'll use them as calibration examples."

If they share example tweets, extract the vocabulary people actually use in them and fold it into the queries. Record any examples in the rubric's GOOD-post section.

**Exit gate:** write `.claude/skills/x-post-flagger/queries.json` — base queries under `queries` (syntax that works on both providers: parentheses, OR, quoted phrases, `-term`), and both `common_exclusions` entries (`builtin`: `-is:retweet -is:reply lang:en` plus product-specific exclusions using v2 operators; `twitterapi`: the equivalent with `-filter:retweets`). If the product is crypto/web3, note that sweeps must use `--no-crypto-filter`.

## Step 4 — Calibrate on real tweets

Run the queries over the last 7 days with the built-in provider:

```bash
uv run --env-file /workspace/.env /workspace/.claude/skills/x-post-flagger/search.py \
  --since-hours 168 --out /tmp/calibration_candidates.json
```

(Keep `--page-size` modest (~25) on the first pass — every returned post is billed.)

Score all candidates against the rubric, distill the best few (aim 3-6), and present them: link, author, text, score, and why each was picked. Ask for feedback on every one.

- **All good** → continue to Step 5.
- **Feedback** ("this one's off-ICP", "too promotional", "missing the X angle") → encode it: adjust queries, exclusions, and rubric (Fit definitions, disqualifiers, GOOD-post examples), re-run the sweep, present the new batch. **Iterate until the user is happy with a batch.** Record durable feedback rules in the rubric, not just in conversation.

**Exit gate:** user has approved a candidate batch; queries + rubric reflect all their feedback.

## Step 5 — Cadence and notifications

1. **When:** "How often do you want a sweep — once a day, twice, three times? What hours (and timezone)? Weekends too?" (Suggest a sensible default: 2x on workdays, e.g. 10am and 4pm local.)
2. **Where:** "Where should the results go — Telegram, Slack, iMessage, or just here in chat?" For an external channel, set up the chat integration (read `/opt/gamut/docs/chat-integrations.md`) and send a test message. Delivery format for copy-paste channels: two messages per candidate — context first (link, author, score, why, angle, ending "Draft below:"), then the bare reply draft alone so it can be copied in one tap.
3. **Cron:** read `/opt/gamut/docs/scheduling-and-resuming.md`, then create the scheduled task(s). Each run's prompt must be self-contained: run search.py with a lookback matching the gap since the previous run (+1h overlap), score with `scoring_rubric.md`, dedupe against `seen_ids.json`, deliver top 1-3 (score ≥55) to the chosen channel, then append each surfaced tweet's ID to `seen_ids.json` and its full record to `surfaced_log.jsonl` (format in the x-post-flagger SKILL.md). Drafts ≤280 weighted chars (URLs/domains count as 23), and **never post to X from a scheduled run**.

Also ask for their **X handle** (to exclude their own/company posts from sweeps and to record in CLAUDE.md for the posting rules).

**Exit gate:** schedule created, channel connected and test message confirmed received, CLAUDE.md `## Your context` updated.

## Step 6 — First live run

Run one full sweep now, end to end: search (lookback = the cadence window), score, dedupe, deliver over the user's chosen channel — exactly as the cron will. Confirm with the user that it arrived and looks right. If anything is off (format, channel, quality), fix it and update the cron prompt to match.

## Step 7 — Optional: cheaper reads (BYOK)

Close by mentioning the cost lever once, without pushing:

> One last thing — sweeps currently use the platform's built-in X API, which just works but bills ~$0.005/post scanned (plus author lookups). If sweep costs ever bother you, I can switch discovery to twitterapi.io with your own API key — roughly 30x cheaper per read. You'd sign up at twitterapi.io, load a few dollars of credit, and give me the key. Want that now, or keep the default?

If yes: request the `TWITTERAPI_IO_KEY` secret, verify with a small test sweep (`--provider twitterapi --since-hours 4`), then update the cron prompt(s) to pass `--provider twitterapi`. If no: done — tell them they can switch anytime.

## Wrap up

Summarize: product brief written, N queries live, rubric calibrated on their feedback, sweep schedule, delivery channel, and how to change any of it ("just ask, or re-run onboarding"). Remind them: the agent flags and drafts; **they** post.
