---
category: "Sales"
icon: badge-dollar-sign
tags:
  - "Sales"
  - "Product Expert"
  - "GitHub"
  - "Glean"
  - "Research"
works_with:
  - type: api_account
    slug: github
developer:
  name: "@kristaletz"
  url: "https://x.com/kristaletz"
---

# Product Expert

Answer deep customer product questions from GitHub and Glean sources; cite the source of truth and hand back a usable response.

## What it does

- Act as the Product Expert: answer deep customer product questions from GitHub and Glean sources; cite the source of truth and hand back a usable response.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **GitHub** — SuperAgent API account `github`.
- **Glean** — external connection; no canonical registry slug.

## Sample use cases

- Answer deep customer product questions from GitHub and Glean sources.
- Cite the source of truth and hand back a usable response.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- How does our rate limiting actually work?
- Give me an answer I can say out loud on this call
- Cite the source of truth behind that answer

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@kristaletz](https://x.com/kristaletz) on [Bot Directory](https://botdirectory.ai/bots/product-expert/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
