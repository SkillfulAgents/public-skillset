---
category: Marketing
icon: search-check
tags:
  - Social Listening
  - X (Twitter)
  - Founder-Led Marketing
  - Reply Opportunities
  - Lead Generation
works_with: []
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# X Opportunity Scout

> Catch the X posts where your product is the answer, while they're still fresh enough to reply to.

## What it does

X Opportunity Scout watches X for high-intent posts about your space: people asking for alternatives to your competitors, asking "what's the best tool for…", describing a need your product answers, or venting about the problem you solve. On a schedule you choose it sweeps recent posts, scores every candidate against a rubric calibrated to your product, and sends you the best 1-3 with a reply angle and a ready-to-paste draft.

You reply personally — the agent never posts on its own. It learns from your feedback: reject a candidate with a reason and that reason becomes a durable scoring rule. Every surfaced post is logged with its score, draft, and outcome, so quality is reviewable over time.

## What you'll need

- **Accounts:** none required. Discovery uses the platform's built-in X API out of the box. Optionally connect Telegram or Slack during onboarding for notifications.
- **API keys:** none required. Optional: a twitterapi.io key for ~30x cheaper discovery reads, and your own X developer app keys for API-posting replies to mentions (see `.env.example`).
- **Costs:** built-in X reads are billed per post scanned (~$0.005/post plus author lookups); a typical sweep runs a few dollars or less.

## Getting started

1. Import the template into Gamut.
2. On import, a setup session starts automatically. The **agent-onboarding** skill learns your product (send a website link and it does most of the work), builds X search queries with you and calibrates them on real tweets from the last 7 days, then sets your sweep schedule and delivery channel.
3. Reply to what it sends you, and give feedback — it sticks. Re-run onboarding anytime by asking for the `agent-onboarding` skill.

## Example prompts

- Run a sweep over the last day and show me the best candidates
- Find posts asking for alternatives to my competitors
- Every weekday at 9am, sweep X and send the top finds to Slack

## What's inside

- `CLAUDE.md` — the agent's instructions: how it scouts, scores, delivers, and the strict never-auto-post rules.
- `.claude/skills/agent-onboarding/` — the first-run setup interview (product brief, query building, calibration, scheduling).
- `.claude/skills/x-post-flagger/` — discovery and scoring: `search.py` (dual-provider X search), `queries.json` (your query bank), `scoring_rubric.md` (your calibrated rubric), `seen_ids.json` (dedupe history), `surfaced_log.jsonl` (append-only history of everything surfaced), `post_reply.py` (optional mention-reply posting).
- `product/` — your product brief, written during onboarding.
- `.env.example` — the optional keys (BYOK reads, API posting).

## Notes

- The agent **never posts to X automatically.** It flags, scores, and drafts; you post. The optional API poster only works for replying to people who mentioned you (X policy since 2026-02-23) and only on your explicit per-tweet instruction.
- Built-in X search covers the last 7 days only.
- Reply drafts follow standing style rules: no em dashes, and a weighted 280-char check (URLs count as 23 chars).
