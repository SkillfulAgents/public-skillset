---
category: "Marketing"
icon: messages-square
tags:
  - "X"
  - "Social Media"
  - "Relationship Building"
  - "Personal Brand"
  - "Content Creation"
works_with:
  - type: api_account
    slug: twitter
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Reply Drafter

> Stay in the conversations that matter on X without living in the feed: one short list each morning, a draft for each, and nothing on quiet days.

## What it does

Every weekday morning, Reply Drafter checks your mentions and the replies to your posts since its last run, a watch list of people you're building relationships with, and a few topics you care about. It keeps only the 3 to 5 posts that genuinely deserve your time: a mention that needs a response, a question you can answer well, a conversation you should join, or a relationship worth investing in.

For each one you get a one-line reason, a link to the post, and a starting reply or quote post written in your voice, learned from replies you're proud of. It skips engagement bait, giveaways, rage-bait, crowded threads, and anything you already answered, never shows you the same post twice, and sends nothing when nothing clears the bar.

It never posts, replies, likes, reposts, follows, or sends a DM on X. Every reply is yours to rewrite and send.

## What you'll need

- **X** — recommended. Connect your own account so the agent can read your mentions and see what you already replied to. Without it, the agent uses Gamut's built-in public X reads and needs no account.
- **A delivery channel** — the agent's own Slack app (a DM to you), Telegram, its own email inbox, or iMessage, set up during onboarding. In-app only also works.
- **Google Docs or Notion** — optional, if you'd rather edit your watch list in a doc.
- **Cost:** X reads are billed per post returned. With default settings a run costs roughly $0.40, and you set a per-run cap.
- **API keys:** none.

## Getting started

1. Import the template into Gamut and send the setup message that is already in the message box.
2. The `agent-onboarding` skill connects X, collects your watch list, topics, and a few replies you're proud of, and sets the bar, budget, and where the shortlist reaches you.
3. It runs one supervised shortlist on real posts so you can tune it, then schedules the weekday morning run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- What should I reply to on X today? Draft the top three
- Add these five founders to my watch list and drop the pricing topic
- Every weekday at 8am, DM me the X posts worth my reply

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the shortlist routine, X access and cost rules, delivery, state, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup that connects tools, runs a supervised shortlist, schedules the run, and writes `config.json`.
- `.claude/skills/reply-bar/` — the bar a post must clear, ranking, voice and draft rules, reply vs. quote post, and the cost-controlled query plan.

## Notes

- X recent search covers the last seven days only, so the agent works from fresh posts.
- Run state (the last-seen post IDs and the posts already shortlisted) lives in the agent's workspace under `state/reply-drafter/`.
- Pairs with X Opportunity Scout, which looks for posts where your product is the answer.

## Credits

Adapted from the original prompt by [@kevinace](https://x.com/kevinace) on [Bot Directory](https://botdirectory.ai/bots/reply-drafter/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
