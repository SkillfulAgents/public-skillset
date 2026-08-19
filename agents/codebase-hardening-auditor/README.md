---
category: "Ops"
icon: code-2
tags:
  - "Ops"
  - "Codebase Hardening Auditor"
  - "GitHub"
  - "Analysis"
works_with:
  - type: api_account
    slug: github
developer:
  name: "@nate-stellar"
  url: "https://github.com/nate-stellar"
---

# Codebase Hardening Auditor

Audit a GitHub repository against a fixed 20-point hardening checklist; report every finding and apply or propose approved fixes.

## What it does

- Act as the Codebase Hardening Auditor: audit a GitHub repository against a fixed 20-point hardening checklist; report every finding and apply or propose approved fixes.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.

## Sample use cases

- Audit a GitHub repository against a fixed 20-point hardening checklist.
- Report every finding and apply or propose approved fixes.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Run the 20-point hardening audit on my main repository
- Show me the committed secrets and dead code first
- Open a PR for the fixes I approved, one concern per commit

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@nate-stellar](https://github.com/nate-stellar) on [Bot Directory](https://botdirectory.ai/bots/codebase-hardening-auditor/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
