---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Journey Friction PR Agent"
  - "PostHog"
  - "Fable"
  - "GitHub"
  - "Workflow Automation"
works_with:
  - type: mcp
    slug: posthog
  - type: api_account
    slug: github
developer:
  name: "@euboid"
  url: "https://x.com/euboid"
---

# Journey Friction PR Agent

Analyze PostHog journeys and Fable recordings for reproducible friction; gather evidence and prepare a bounded GitHub fix.

## What it does

- Act as the Journey Friction PR Agent: analyze PostHog journeys and Fable recordings for reproducible friction; gather evidence and prepare a bounded GitHub fix.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **PostHog** — SuperAgent MCP `posthog`.
- **Fable** — external connection; no canonical registry slug.
- **GitHub** — SuperAgent API account `github`.

## Sample use cases

- Analyze PostHog journeys and Fable recordings for reproducible friction.
- Gather evidence and prepare a bounded GitHub fix.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@euboid](https://x.com/euboid) on [Bot Directory](https://botdirectory.ai/bots/journey-friction-pr-agent/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
