---
category: Marketing
icon: star
tags:
  - Reviews
  - Reputation
  - Home Services
  - Google Business Profile
  - Yelp
works_with:
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Review Wrangler

> Ask for the review after every job and answer Google and Yelp in the shop's voice, with the one-star ones parked for you.

## What it does

Review Wrangler owns the after-job review ask and public replies for founder-led home services shops. It watches completed jobs on the board and, once the cooling window passes, drafts the review ask. On your cadence it checks Google Business Profile and Yelp for new reviews and drafts each public reply from your voice samples: specific thanks, never a helpdesk tone.

One-star and two-star reviews, legal or safety mentions, named employees, and anything that looks like it will spread go to a spicy queue: you get a private-resolution draft in Slack, unsent. Five-star replies can auto-post only if you pre-authorize that. The agent never asks for a review on a job with an open complaint and never offers refunds, deletes, or hides reviews.

## What you'll need

- **Slack** — required. Review asks, reply drafts, and the spicy queue land in your founder channel.
- **Google Business Profile and Yelp** — required for reading reviews and posting approved replies. Connected during onboarding; no registry connector.
- **Jobber** — optional, for completed-job signals. No registry connector; connected during onboarding or use your board.
- **SMS line** — optional, for sending the review ask by text. No registry connector.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your listings, the hours to wait after a job, voice samples, whether 5-star replies may auto-post, and the Slack channel for spicy reviews, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Draft after-job review asks for yesterday's completed jobs and draft Google and Yelp replies without posting.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft review asks for yesterday's completed jobs and replies to new reviews
- Draft a reply to the new three-star Yelp review in our voice
- Every morning, check Google and Yelp and Slack me any review under four stars

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led home services shops that want reviews asked and answered in their voice.
- Public replies stay in draft until the founder approves, unless 5-star auto-post is pre-authorized.
