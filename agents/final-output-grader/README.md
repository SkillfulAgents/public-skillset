---
category: "Ops"
icon: workflow
tags:
  - "Ops"
  - "Final Output Grader"
  - "Grok"
  - "Analysis"
works_with: []
developer:
  name: "@DeryaTR_"
  url: "https://x.com/DeryaTR_"
---

# Final Output Grader

Evaluate candidate outputs against your criteria; check completeness, accuracy, consistency, and required formatting.

## What it does

- Act as the Final Output Grader: evaluate candidate outputs against your criteria; check completeness, accuracy, consistency, and required formatting.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Grok** — external connection; no canonical registry slug.

## Sample use cases

- Evaluate candidate outputs against your criteria.
- Check completeness, accuracy, consistency, and required formatting.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Grade this output against my rubric and explain the score
- Which criteria failed and what needs revising?
- Send it back for revision instead of passing it through

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@DeryaTR_](https://x.com/DeryaTR_) on [Bot Directory](https://botdirectory.ai/bots/final-output-grader/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
