---
category: Sales
icon: calendar-check
tags:
  - Inbound Leads
  - Lead Qualification
  - Call Booking
  - Reply Drafts
  - HubSpot
  - Professional Services
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: hubspot
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Inquiry Desk

> Take every inbound inquiry all the way to a qualified call on your calendar, not a polite we-will-be-in-touch.

## What it does

Inquiry Desk owns inbound for founder-led consulting, accounting, insurance, and staffing firms. It watches the web form, email, and referral intros for new inquiries and scores each one against your fit rules: company size, problem, budget signal if they gave one, geography, and conflicts. For a fit, it reads your calendar, offers two or three real windows, and queues the invite for one-tap send. Poor fits get a polite, honest reply instead of a ghost.

It also catches prospects who reply to your outbound emails, and demo or consult requests. Within minutes of each one arriving, it drafts a reply in your voice, learned from your sent mail: short, direct, friendly, no filler. The reply answers what they actually asked and moves toward a booked call with real times from your calendar. A "not now" gets a gracious reply and a dated follow-up task, and a "no" is never argued with. Every reply stays in your Gmail drafts, and the agent never quotes fees unless a published rate is in config.

## What you'll need

- **Gmail** — required for inquiry intake, outbound replies, your writing voice, and reply drafts. Outlook works too.
- **Google Calendar** — required to offer real windows and book the call.
- **HubSpot** — the supported CRM connector for logging inquiries. Another CRM can be configured during onboarding.
- **Slack** — for alerts on new qualified leads and drafts waiting, sent from the agent's own Slack app. Email or in-app also work.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It asks for your inquiry sources, how to spot your outbound threads, your fit rules, who takes the call, which calendar to book against, and where alerts go. It reads your sent mail to learn your voice, then saves the answers into `CLAUDE.md` and `.claude/skills/agent-onboarding/config.json`.
3. Ask for the first run: Work today's inbound inquiries through a qualified call on the calendar, drafting invites for approval. After you approve, it sets up the new-mail trigger.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Work today's inbound inquiries and draft invites for the qualified ones
- Draft replies to the prospects who answered my outreach this week
- On every new inquiry, draft my reply with three open times and Slack me

## What's inside

- `CLAUDE.md` — the inbound and prospect reply routines, reply types and voice rules, the Gamut setup, safe operating rules, and the `## Your context` block that onboarding fills in.
- `.claude/skills/agent-onboarding/` — the first-run interview that captures your systems, fit rules, voice, and booking rules, runs a supervised drafting pass, and sets up the trigger.

## Notes

- Built for 2-200 person founder-led professional firms with inbound sitting in the inbox.
- Every reply is a draft for your review. The agent never sends, never books a time the calendar does not show, and never stops at a qualified-lead list without offering a call.
