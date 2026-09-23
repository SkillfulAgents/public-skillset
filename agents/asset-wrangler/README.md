---
category: Ops
icon: list-checks
tags:
  - Creative Ops
  - Asset Tracking
  - Client Delivery
  - Google Drive
  - Agency Ops
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: slack
  - type: api_account
    slug: gmail
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Asset Wrangler

> Know where every creative and copy file stands before the client has to ask.

## What it does

Asset Wrangler owns the creative-and-copy pipeline for founder-led marketing, creative, and web shops. It watches the intake channel, the Drive drop, and email for new creative and copy, then keeps a status board you can paste anywhere: in, in progress, internal review, client review, late, done.

It compares due dates to today and warns the owner and the founder before the client pings. When work clears internal approval it packages the files plus copy and Slacks you a client-ready pack for send or portal upload. Nothing unfinished or unapproved goes to the client, and the agent never invents a due date or a brief.

## What you'll need

- **Google Drive** — required. Where creative and copy land and where client packs get assembled.
- **Slack** — required for the intake channel, late warnings, and client-pack handoffs.
- **Gmail** — required to catch files and copy that arrive by email.
- **Status board** — optional. A tracker or sheet the agent keeps current; it can run from Slack alone.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for where intake lands, which status board to keep, how many days count as late, and who approves client packs, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Rebuild the asset board from Drive and Slack, flag anything late, and draft status notes without sending to clients.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Rebuild the asset board from Drive and Slack and show me what is late
- Package the approved Acme banner set with its copy for client review
- Every morning at 8, post the status board and flag anything due in two days

## What's inside

- `CLAUDE.md` — the agent's operating instructions, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, cadence, voice, and approval rules and writes `config.json`.

## Notes

- Built for 2-200 person founder-led agencies tired of clients asking where the files are.
- Client packs stay in draft until the founder sends. The agent never approves creative on the client's behalf.
