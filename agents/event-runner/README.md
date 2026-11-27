---
category: Marketing
icon: calendar-check
avatar:
  color: tonal-forest
  shape: arch
tags:
  - Event Marketing
  - Webinars
  - Event Follow-Up
  - Lead Nurturing
  - Eventbrite
  - Zoom
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: eventbrite
  - type: api_account
    slug: zoom
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: hubspot
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Event Runner

> Run your next webinar or event without dropping a ball, and follow up while the leads are still warm.

## What it does

Event Runner owns one event from the first promo to the last follow-up.

- **Run-up readiness.** Every morning until the event it checks the real state of things: promo beats sent, the registration page live with the right time, speakers confirmed in writing, slides and assets in, and reminders scheduled. It ranks what is at risk by how close the event is and splits it into "waiting on me" and "waiting on others". When the next promo or reminder is due, it drafts it for your approval.
- **Post-event follow-up.** Within a day of the event it pulls registrants and attendees from Eventbrite, Zoom, Luma, a sheet or your CRM. It sorts them into hand-raisers (attended and asked a question, answered a poll or clicked your CTA), attendees and no-shows, and drafts a personal follow-up for each. Hand-raisers get a reply to their actual question, and no-shows get the recording link.
- **Stops on its own.** Once the follow-up wave is drafted, the daily check cancels itself.

Every email, post and reminder is a held draft. Nothing goes out until you approve it.

## What you'll need

- **Gmail:** required. Drafts land in your own mailbox. Outlook works too.
- **Google Calendar:** required, for speaker invites and the event block.
- **Registration and attendance source:** Eventbrite or a Zoom webinar as connected accounts. Luma works through an API key if your calendar has API access, otherwise through its guest export. A Google Sheet or HubSpot list also works.
- **HubSpot:** optional, to flag existing deals and log engagement after approval. Salesforce, Attio, Pipedrive and Close also work.
- **Delivery channel:** in-app, or the agent's own Slack app, email inbox, Telegram or iMessage for daily readouts.
- **API keys:** only `LUMA_API_KEY`, and only if you use Luma's API.

## Getting started

1. Import the template into Gamut. The `agent-onboarding` skill starts automatically.
2. Onboarding records the event date, format, speakers and goal, and connects your mailbox, calendar and registration platform. It agrees the timeline and follow-up templates with you, then runs a first readiness check.
3. Approve the first promo or reminder draft, and let the daily readout and the post-event run take over.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Track readiness for our Zoom webinar on December 3 and show what is at risk
- Pull last night's Eventbrite attendees and draft follow-ups by segment
- Draft the T-1 day reminder with the join link and hold it for me

## What's inside

- `AGENTS.md`: the run-up and post-event routines, Gamut mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup, dry run, schedules, config and event record.
- `.claude/skills/event-playbook/`: the default readiness timeline, risk ranking, and segment and follow-up rules.

## Notes

- Zoom attendance, Q&A and poll reports depend on your Zoom plan. If one is not available, the agent asks for an export rather than guessing.
- The post-event run starts about two hours after the scheduled end, so reports and the recording have time to process. No-show drafts wait for a working recording link.
- For recurring community events synced into Notion and Slack, pair with `community-ops-crew`.

## Privacy

Event Runner reads registrant and attendee lists through your own connected accounts. Its state files keep only ids, segments and statuses. It never sends email or changes the event listing without your approval.
