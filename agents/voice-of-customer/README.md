---
category: Marketing
icon: messages-square
avatar:
  color: tonal-grey
  shape: triangle
tags:
  - Voice of Customer
  - Messaging
  - Positioning
  - Content Ideas
  - Call Insights
  - Granola
works_with:
  - type: mcp
    slug: granola
  - type: api_account
    slug: gong
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googledocs
  - type: api_account
    slug: notion
  - type: api_account
    slug: hubspot
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Voice of Customer

> Write copy in your customers' words, not yours, and never lose a great line from a call again.

## What it does

After every customer or prospect call, Voice of Customer reads the transcript and pulls out what matters for messaging: the jobs people are trying to get done, their pains, the objections they raised, the exact words they use for the problem, which of your messages landed or fell flat, and verbatim quotes worth keeping. Internal meetings and logistics calls are skipped.

It folds each call into a living messaging doc for the right segment. Recurring themes get stronger with each new call instead of being repeated, and a single call is recorded as "observed" until more customers say the same thing. Every quote is exact and attributed to the speaker's role, company and date, with a link to the call, and each doc keeps a sources list. Bugs, feature requests and pricing complaints go into a separate product-feedback section at the bottom, never mixed in with messaging.

Every Monday it sends five to eight content ideas built from that signal and your CRM trends. Each idea comes with its angle, format, hook and target segment, and links back to the call or trend it came from. Topics you covered recently are skipped.

## What you'll need

- **A call recorder**: required. Granola or Gong are listed here; Fathom, Fireflies, Otter and Zoom recordings also work, or the agent can join your calls as a note-taker.
- **Google Calendar**: recommended, to tell customer calls from internal ones.
- **Google Docs or Notion**: where the messaging docs live. Markdown files in the workspace are the fallback.
- **HubSpot**: recommended, for segment fields and pipeline trends. Salesforce works too.
- **Slack or email**: optional. The agent's own Slack app or inbox delivers recaps and the weekly ideas; otherwise they stay in the app.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It connects your recorder, calendar, docs and CRM, then asks for your segment list and your current messaging doc so the new docs follow its format. It also asks how quotes should be attributed and where ideas should go.
3. Mine a handful of recent calls together, review the doc changes, then turn on the per-call trigger, the nightly sweep and the Monday ideas.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Mine my last five customer calls into the messaging docs
- What objections keep coming up with mid-market prospects, in their words?
- Every Monday, send me 5 content ideas from this week's calls and CRM trends

## What's inside

- `AGENTS.md`: the call-mining and weekly-ideas routines, quote and evidence rules, triggers, schedules and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup for the recorder, segments, doc format, delivery and schedules.
- `.claude/skills/messaging-doc-format/`: the default per-segment doc layout, quote record, evidence levels and merge rules.

## Privacy

- The agent reads call transcripts, which contain personal data. Only short excerpts go into the docs; full transcripts are never copied.
- Quote attribution follows your choice: names, titles or company only.
- It asks before writing anything outside the docs, such as tagging personas in your CRM. It never publishes content.
