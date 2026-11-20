---
category: "Marketing"
icon: megaphone
tags:
  - "Product Launches"
  - "Social Media"
  - "Changelog"
  - "Release Notes"
  - "Content Approval"
  - "GitHub"
works_with:
  - type: api_account
    slug: github
  - type: api_account
    slug: linear
  - type: api_account
    slug: slack
  - type: api_account
    slug: notion
  - type: api_account
    slug: googledocs
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Release To Social Campaign

> Every customer-facing change your team ships gets a post, a changelog note, and an approver's yes before anything goes live.

## What it does

Release To Social Campaign watches GitHub releases, merged pull requests, Linear completed issues, or your changelog, and keeps only what a customer would notice. Internal refactors, dependency bumps, tests, and reverts are left out, with a short "left out" list so nothing disappears silently. Related changes are grouped into stories that lead with the customer benefit, not the implementation.

For each story it writes two formats you choose (a social post and a changelog note, or a blog blurb) and a separate version per platform rather than one post pasted everywhere. Drafts land in Postiz if you use it, otherwise in a Notion page or Google Doc. The approver gets one Slack message from the agent with the drafts, a proposed schedule, and a link back to each PR or issue so every claim can be checked.

- **Ship-to-campaign drafts** — on each release or merge, or a weekly sweep; never drafts the same item twice and stays quiet when nothing customer-facing shipped.
- **Approval and scheduling** — per-draft approval from the named approver; only approved drafts are scheduled in Postiz or handed over as copy-ready text.
- **72-hour performance summary** — per-post numbers from Postiz or your own X account, with "not available" where a platform can't be read.

Nothing is ever published, scheduled to go live, or posted without explicit approval of the exact draft.

## What you'll need

- **GitHub** — required (or Linear or a changelog page as the shipping source). Reads releases and merged pull requests.
- **Linear** — optional, for completed issues and projects.
- **Slack** — recommended. The agent's own Slack app sends review messages to the approver. Its own email inbox, Telegram, or in-app also work.
- **Notion or Google Docs** — where drafts land when Postiz isn't used.
- **Postiz** — optional, through a Postiz API key; drafts are created there and scheduled only after approval.
- **X or LinkedIn** — optional, your own account, read-only, for the performance summary.
- **API keys:** `POSTIZ_API_KEY` only if you use Postiz.

## Getting started

1. Import the template into Gamut and send the setup message waiting in your message box.
2. The `agent-onboarding` skill connects your sources and draft destination, asks which releases count, which accounts post, who approves, and your voice, then runs a drafts-only test on one past release.
3. Once you're happy with the test, it sets up the release trigger or a weekly sweep.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft a campaign from our last GitHub release as a test
- What shipped in Linear this week that customers would care about?
- Every Monday, send last week's customer-facing changes for approval

## What's inside

- `PROMPT.md` — the setup request placed in your message box after import.
- `CLAUDE.md` — the three routines, Gamut connections and triggers, state files, and safe operating rules.
- `.claude/skills/agent-onboarding/` — first-run setup, drafts-only test, scheduling, and `config.json`.
- `.claude/skills/ship-filter-and-formats/` — what counts as customer-facing, grouping into stories, per-platform format rules, and the review message shape.

## Notes

- Verification links to private PRs and tickets stay in the review message and never appear in public copy.
- Performance numbers are read, never estimated. Platforms the agent can't read are reported as not available.
- Pairs with Tickets To Changelog and Voice-Matched Drafts if you have them installed.

## Credits

Adapted from the original prompt by [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/release-to-social-campaign/), used under the MIT license; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
