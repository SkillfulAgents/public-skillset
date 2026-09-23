---
name: agent-onboarding
description: Configures the Lead Lightning template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Lead Lightning workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and which zips or cities are in play?

2. Where do web, phone, and form leads land today (Jobber, Housecall Pro, ServiceTitan, Gmail, a form inbox)?

3. What counts as same-day, and what is the last bookable time?

4. Paste one confirm text that sounds like you.

5. Which Slack channel gets spicy exceptions, and who is the founder who approves sends?

6. May same-day confirms auto-send after a clean trial, or is every send one-tap?

7. What is off limits: job types, zips, or customers the agent should never book?

8. Confirm the first run: book from today's inbound, draft confirms, send nothing until you approve.

## Configuration to save

Create `.claude/skills/agent-onboarding/config.json` with this structure:

```json
{
  "company_name": "",
  "service_areas": [],
  "source_system": "",
  "source_system_connected": false,
  "alert_destination": "",
  "workflow_owner": "",
  "escalation_contact": "",
  "cadence": "",
  "voice_notes": "",
  "approval_required_for": [],
  "business_rules": {},
  "do_not_touch": [],
  "first_run_goal": "Handle today's new web, phone, and form leads through a booked same-day slot where the board allows it. Draft confirms. Do not send until I approve."
}
```

## First task prompt

After onboarding, suggest this first task:

> Handle today's new web, phone, and form leads through a booked same-day slot where the board allows it. Draft confirms. Do not send until I approve.
