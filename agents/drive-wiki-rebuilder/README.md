---
category: "Ops"
icon: book-open
tags:
  - "Ops"
  - "Drive Wiki Rebuilder"
  - "Google Drive"
  - "Notion"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: notion
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Drive Wiki Rebuilder

Reorganize a Google Drive folder into a maintained Notion wiki; assign owners and flag stale material while preserving originals.

## What it does

- Act as the Drive Wiki Rebuilder: reorganize a Google Drive folder into a maintained Notion wiki; assign owners and flag stale material while preserving originals.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Drive** — SuperAgent API account `googledrive`.
- **Notion** — SuperAgent API account `notion`.

## Sample use cases

- Reorganize a Google Drive folder into a maintained Notion wiki.
- Assign owners and flag stale material while preserving originals.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Rebuild this Drive folder as a Notion wiki by topic
- Assign an owner to every page and banner what is stale
- Start with one subfolder so I can check the structure

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/drive-wiki-rebuilder/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
