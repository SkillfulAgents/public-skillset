---
name: X Post Flagger
description: 'Search X for fresh posts where the product is a relevant answer (competitor-alternative asks, category questions, gripes, specific-need requests) using the platform''s built-in X API by default, with optional BYOK twitterapi.io for cheaper reads. Returns deduped, filtered candidate JSON for LLM scoring against scoring_rubric.md.'
metadata:
  version: "2.0.0"
---

# X Post Flagger

Finds fresh X posts worth replying to for the user's product. Discovery layer only — scoring and reply drafting are done by the agent using `scoring_rubric.md` in this directory. Configure via `agent-onboarding` before first real use (it writes `queries.json`, the rubric's product sections, and the sweep schedule).

## Files

- `search.py` — runs the query bank, dedupes, filters (min followers, replies/RTs dropped, optional crypto-noise filter), outputs normalized candidate JSON. Two providers, same output shape.
- `queries.json` — editable query bank grouped by category, plus per-provider `common_exclusions` appended to every query. Written by onboarding.
- `scoring_rubric.md` — 0-100 scoring framework; product sections written by onboarding, refined from user feedback.
- `seen_ids.json` — JSON array of already-surfaced tweet IDs. Always dedupe against it and append after surfacing.
- `surfaced_log.jsonl` — append-only log of every surfaced tweet (one JSON object per line). Written at surfacing time, alongside `seen_ids.json`.
- `post_reply.py` — optional BYOK reply posting (see below).

## Providers

**Default: built-in X API (`--provider builtin`).** Works out of the box — no account, no key. Uses the platform's X proxy (`$ANTHROPIC_BASE_URL/v1/x`, official v2 search syntax, last 7 days only). Billed per object returned: **$0.005/post + $0.010/distinct author** (author expansion is required for the follower/bio filters). A typical multi-query sweep returning ~200 posts costs roughly $1.50-3.00.

**Optional BYOK: twitterapi.io (`--provider twitterapi`).** ~$0.15/1k tweets read (~30x cheaper), needs `TWITTERAPI_IO_KEY` in `/workspace/.env` (user signs up at twitterapi.io and loads credit). Offer this to the user if sweep costs become noticeable; onboarding mentions it at the end.

Query syntax differs per provider — keep both `common_exclusions` entries in `queries.json` in sync when editing queries (v2 operators like `-is:retweet` for builtin, `-filter:retweets` for twitterapi). Base queries (parentheses, OR, quoted phrases, `-term`) work on both.

## Usage

```bash
uv run --env-file /workspace/.env /workspace/.claude/skills/x-post-flagger/search.py \
  --since-hours 24 --out /tmp/sweep_candidates.json            # builtin (default)

uv run --env-file /workspace/.env /workspace/.claude/skills/x-post-flagger/search.py \
  --provider twitterapi --since-hours 24 --out /tmp/sweep_candidates.json
```

Flags: `--since-hours` (float), `--max-pages` (default 1), `--page-size` (builtin, 10-100 posts/page/query, default 25), `--min-followers` (default 150), `--no-crypto-filter` (disable crypto-noise drop — use when the product itself is crypto/web3), `--queries` (path override).

## Scoring (done by the agent after running search)

Score each candidate with `scoring_rubric.md`: Fit (0-50), Author (0-25), Replyability (0-25); hard disqualifiers; mandatory quote/RT check via the `is_quote` / `quoted_text` / `quotes_launch` fields. Surface only candidates ≥55, top 1-3 per run. Dedupe against `seen_ids.json`, append after surfacing.

## Surfaced-tweet log (required on every surfacing)

For **every** tweet surfaced to the user, append one line to `surfaced_log.jsonl` in this directory (and its ID to `seen_ids.json`):

```json
{"surfaced_at": "<ISO-8601 UTC>", "run": "<cron|manual|calibration>", "id": "...", "url": "...", "author": "...", "followers": 1234, "text": "<full tweet text>", "score": 78, "category": "...", "why": "...", "angle": "...", "draft": "<the reply draft sent>", "channel": "<telegram|slack|imessage|chat>"}
```

When the user later reports an outcome ("posted", "skipped", "bad find"), append an update line: `{"id": "...", "outcome": "posted|skipped|rejected", "note": "<their reason>", "at": "<ISO>"}`. This log is the agent's history for quality review ("what did you send last week?", hit-rate analysis, rubric tuning) — never delete it, only append.

## Posting replies (post_reply.py — optional, BYOK)

Posts a reply via the official X API as the user, using their own X developer app OAuth 1.0a keys (`X_API_KEY`/`X_API_SECRET`/`X_ACCESS_TOKEN`/`X_ACCESS_TOKEN_SECRET` in `/workspace/.env`).

**⚠️ X policy (since 2026-02-23):** the API rejects replies to posts unless the author mentioned/quoted the authenticated account (403). So this only works for replying to mentions. **Cold replies to discovered posts must be posted manually by the user** (copy-paste) or via their logged-in browser session.

**STRICT RULE (see CLAUDE.md): only run on the user's explicit instruction for a specific tweet. Never from scheduled runs.**

```bash
# verify credentials (posts nothing):
uv run --env-file /workspace/.env /workspace/.claude/skills/x-post-flagger/post_reply.py --verify
# post an approved reply:
uv run --env-file /workspace/.env /workspace/.claude/skills/x-post-flagger/post_reply.py --reply-to <tweet_id> --text "reply text"
```

X API pricing: $0.015/reply, $0.20 if the text contains a URL. On success prints the posted reply URL — send it back to the user.
