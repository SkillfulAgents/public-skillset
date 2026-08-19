---
category: "Personal"
icon: house
tags:
  - "Personal"
  - "Home Services Autopilot"
  - "Photos"
  - "HireNimbus"
  - "Gmail"
  - "Google Calendar"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
developer:
  name: "@elie2222"
  url: "https://x.com/elie2222"
---

# Home Services Autopilot

Assess a home-service problem from photos and a description; source providers, coordinate appointments, and keep consequential actions approved.

## What it does

- Act as the Home Services Autopilot: assess a home-service problem from photos and a description; source providers, coordinate appointments, and keep consequential actions approved.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Photos** — built-in capability; no connection slug.
- **HireNimbus** — external connection; no canonical registry slug.
- **Gmail** — SuperAgent API account `gmail`.
- **Google Calendar** — SuperAgent API account `googlecalendar`.

## Sample use cases

- Assess a home-service problem from photos and a description.
- Source providers, coordinate appointments, and keep consequential actions approved.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Here are photos of the leak, what job is this?
- Find vetted local pros and compare their quotes
- Book the appointment and draft the confirmation email

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/home-services-autopilot/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
