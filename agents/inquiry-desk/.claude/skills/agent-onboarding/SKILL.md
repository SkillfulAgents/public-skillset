---
name: agent-onboarding
description: Configures the Inquiry Desk template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Inquiry Desk workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and who takes the first call?

2. Where do inquiries land, and which CRM is source of truth?

3. What is a qualified call for you (size, problem, geography, exclusions)?

4. Paste one booking note that sounds like you.

5. May qualified bookings auto-send after a trial, or is every invite one-tap?

6. Which Slack channel gets spicy inquiries?

7. Confirm the first run: qualify and draft bookings, send nothing until you approve.

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
  "first_run_goal": "Work today's inbound inquiries through a qualified call on the calendar. Draft invites. Do not send until I approve."
}
```

## First task prompt

After onboarding, suggest this first task:

> Work today's inbound inquiries through a qualified call on the calendar. Draft invites. Do not send until I approve.
