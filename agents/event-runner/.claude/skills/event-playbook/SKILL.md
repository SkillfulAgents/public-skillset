---
name: event-playbook
description: 'Default readiness timeline for webinars and in-person events, risk ranking, and the post-event segmentation and follow-up structure. Use when building or checking an event checklist and when drafting follow-ups.'
---

# Event playbook

Defaults only. The user's own lead times in `config.json` override them.

## Readiness timeline (T = event start)

| Due | Webinar | In person |
|---|---|---|
| T-28 to T-21 | Title, abstract, speakers confirmed in writing; registration page live; announcement sent | Venue contracted; registration page live; announcement sent |
| T-21 to T-14 | Speaker bios and headshots; promo beat 2 (social plus a partner or speaker share) | Catering and AV quotes; promo beat 2 |
| T-14 | Slides draft; polls and CTA defined; recording settings checked | Run-of-show; signage and badges ordered |
| T-7 | Reminder 1; tech check booked; final slides | Reminder 1 with logistics; headcount estimate to venue |
| T-3 | Last promo push; speaker tech check done | Final headcount to catering (or the venue's deadline) |
| T-1 | Reminder 2 with calendar link; follow-up drafts prepared | Reminder 2 with address, entry, parking and check-in |
| T-1h | Reminder 3 with the one-click join link | Day-of text or email for late changes |
| T+0 to T+1 | Post-event follow-up wave | Post-event follow-up wave |

## Risk ranking

Risk = how far the item is past its due date, or how close it is to due, weighted by impact:
- **Blocks the event:** registration page down, no speaker, no venue, wrong time on the page or invites.
- **Hurts turnout:** missed promo beat, missing reminder, flat registrations.
- **Hurts quality:** slides late, no tech check, no CTA.

Sort by impact, then by days to due. Split into Waiting on me / Waiting on others (name, since when, last chased).

## Segments and follow-up structure

| Segment | Rule (default) | Draft must contain |
|---|---|---|
| Hand-raiser | attended 10+ min and (asked a question, poll answer showing intent, CTA click, booked meeting, or logged conversation) | their own question or signal, an answer or resource, a concrete next step with two time options |
| Attendee | attended 10+ min, no signal | thanks, recording and slides, one relevant highlight, light next step |
| No-show | registered, attended under 10 min or not at all | "sorry we missed you", recording link, one key takeaway, next event |
| Existing pipeline or customer | email or domain matches an open deal or account | flag for the owner; draft only if the user is the owner |

Remove before segmenting: internal domains, speakers, test sign-ups, duplicates (merge on lowercase email).

Subject lines: specific, under about 50 characters, no "Thanks for attending!" alone. Reference the event title or the person's question.
