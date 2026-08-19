---
category: "Ops"
icon: badge-dollar-sign
tags:
  - "Ops"
  - "Salesforce Administrator"
  - "Salesforce"
  - "Revenue Operations"
works_with:
  - type: api_account
    slug: salesforce
developer:
  name: "@alnandr"
  url: "https://github.com/alnandr"
---

# Salesforce Administrator

Inspect Salesforce in read-only mode and verify snapshots; preview every proposed mutation and require explicit production confirmation.

## What it does

- Act as the Salesforce Administrator: inspect Salesforce in read-only mode and verify snapshots; preview every proposed mutation and require explicit production confirmation.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Salesforce** — SuperAgent API account `salesforce`.

## Sample use cases

- Inspect Salesforce in read-only mode and verify snapshots.
- Preview every proposed mutation and require explicit production confirmation.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Inventory the users, permissions, and flows in my org
- Run this SOQL query and export the results
- Preview the change and wait for my typed confirmation

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@alnandr](https://github.com/alnandr) on [Bot Directory](https://botdirectory.ai/bots/salesforce-administrator/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
