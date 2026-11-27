---
category: Ops
icon: calculator
avatar:
  color: tonal-blue
  shape: circle
tags:
  - Mileage
  - Billable Hours
  - Timesheets
  - Freelancers
  - Google Calendar
  - Google Sheets
works_with:
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: google_maps
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googledrive
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Time and Mileage Log

> Your calendar already knows where you drove and who you worked for. Get both reports without reconstructing a single day from memory.

## What it does

**Monthly mileage.** On the last business day of the month, it reads the calendar for in-person meetings and measures the round-trip drive from your home or office. It uses Google Maps when connected and a web lookup otherwise, and says which method it used for each trip. It multiplies by the current IRS standard mileage rate, which it looks up on irs.gov every run and cites. It skips flights and out-of-state trips, uses your fixed amount for airport runs, and flags missing or ambiguous locations instead of guessing. The result is a Google Sheet (or doc) with date, purpose, destination, miles and amount per trip, and the total at the bottom.

**Weekly billable hours.** Every Friday it rebuilds the week by client from your calendar, sent email and the documents you edited. Each block of time links to the meeting, thread or file it came from. Overlaps are counted once, entries are rounded to your billing increment, and anything that looks billable but isn't in your timesheet is flagged.

Every number is labelled an estimate, and you confirm the final figures. It never invoices, files or sends anything to a client. If you opt in, it can push confirmed entries to QuickBooks or Harvest time.

## What you'll need

- **Google Calendar**: required, for both routines. Outlook calendars also work.
- **Google Maps**: recommended, for geocoding and driving distances. Without it, distances come from a web lookup and are labelled that way.
- **Google Sheets**: required, for the monthly and weekly sheets. A Google Doc is available on request.
- **Gmail and Google Drive**: required for the hours recap (sent-mail metadata and documents you edited).
- **QuickBooks**: optional, to compare against logged time and, if you opt in, add confirmed entries.
- **API keys:** none required. Harvest is optional and connects as a regular connected account.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks where your drives start, your trip rules, your clients and how you bill, connects your calendar, maps, sheets, mail and drive, and sets the monthly and weekly runs.
3. Ask for last month's mileage report and last week's hours to check the estimates before the first scheduled run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Build my mileage report for last month at the current IRS rate
- Rebuild this week's billable hours by client with the evidence for each
- Which client meetings this month are missing a location for mileage?

## What's inside

- `AGENTS.md`: both routines, Gamut mechanics, safe operating rules and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup, supervised dry runs, schedules and `config.json`.
- `.claude/skills/mileage-math/`: how to look up and cite the IRS rate, trip inclusion rules, distance methods and the report layout.

## Notes

- Not tax advice. Commuting and deductibility questions are flagged for you or your accountant.
- Calendar events are plans. Trips later on the last day are marked "scheduled" for you to confirm.
- In early January, before the IRS publishes the new rate, the report shows miles only.

## Privacy

Sheets hold event titles, subjects, file names and links, never email bodies or document contents. Home and office addresses stay in the agent's private configuration.
