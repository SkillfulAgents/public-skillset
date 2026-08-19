---
category: "Ops"
icon: shield-check
tags:
  - "Ops"
  - "Supply Chain Threat Sentinel"
  - "GitHub"
  - "GitHub Actions"
  - "Monitoring"
works_with:
  - type: api_account
    slug: github
developer:
  name: "@APompliano"
  url: "https://x.com/APompliano"
---

# Supply Chain Threat Sentinel

Inspect dependency files, releases, workflows, and packages for supply-chain threats; explain evidence, severity, and remediation.

## What it does

- Act as the Supply Chain Threat Sentinel: inspect dependency files, releases, workflows, and packages for supply-chain threats; explain evidence, severity, and remediation.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.
- **GitHub Actions** — SuperAgent API account `github`.

## Sample use cases

- Inspect dependency files, releases, workflows, and packages for supply-chain threats.
- Explain evidence, severity, and remediation.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Scan this dependency update for supply-chain risk
- Explain the evidence and severity behind each finding
- Give me prioritized remediation steps, no auto-blocking

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@APompliano](https://x.com/APompliano) on [Bot Directory](https://botdirectory.ai/bots/supply-chain-threat-sentinel/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
