---
category: "Personal"
icon: plane
tags:
  - "Personal"
  - "Starlink Flight Finder"
  - "Google Flights"
  - "Airline booking websites"
  - "Google Calendar"
  - "Research"
works_with:
  - type: api_account
    slug: googlecalendar
developer:
  name: "@benln"
  url: "https://x.com/benln"
---

# Starlink Flight Finder

Find flight options for a route and dates; prioritize aircraft and airlines with verified Starlink availability.

## What it does

- Act as the Starlink Flight Finder: find flight options for a route and dates; prioritize aircraft and airlines with verified Starlink availability.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Google Flights** — browser session; no registry slug.
- **Airline booking websites** — browser session; no registry slug.
- **Google Calendar** — SuperAgent API account `googlecalendar`.

## Sample use cases

- Find flight options for a route and dates.
- Prioritize aircraft and airlines with verified Starlink availability.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@benln](https://x.com/benln) on [Bot Directory](https://botdirectory.ai/bots/starlink-flight-finder/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
