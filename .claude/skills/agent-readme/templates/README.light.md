---
category: "{{CATEGORY}}"
icon: {{LUCIDE_ICON}}
tags:
  - "{{CATEGORY}}"
  - "{{AGENT_NAME}}"
  - "{{SERVICE_OR_TOPIC}}"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: {{SLUG}}
developer:
  name: "{{AUTHOR_HANDLE}}"
  url: "{{AUTHOR_URL}}"
---

# {{AGENT_NAME}}

{{CLAUDE_DESCRIPTION_VERBATIM}}

## What it does

- Act as the {{AGENT_NAME}}: {{CLAUDE_DESCRIPTION_LOWERCASED}}
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **{{SERVICE_LABEL}}** — SuperAgent API account `{{SLUG}}`.

## Sample use cases

- {{FIRST_CLAUSE_AS_SENTENCE}}
- {{SECOND_CLAUSE_AS_SENTENCE}}

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- {{FIRST_RUN_ASK}}
- {{SIGNATURE_ASK}}
- {{DEPTH_OR_CADENCE_ASK}}

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [{{AUTHOR_HANDLE}}]({{AUTHOR_URL}}) on [Bot Directory](https://botdirectory.ai/bots/{{SOURCE_SLUG}}/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
