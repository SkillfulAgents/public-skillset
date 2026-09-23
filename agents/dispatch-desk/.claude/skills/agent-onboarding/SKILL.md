---
name: agent-onboarding
description: Configures the Dispatch Desk template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Dispatch Desk workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and where does tomorrow's schedule live?

2. Who is allowed to move crews (founder, dispatcher), and who approves customer texts?

3. Paste one 'we are coming' text that sounds like you.

4. Where do parts notes live, and what should we flag as not on the truck?

5. Which Slack channel gets the board and spicy exceptions?

6. May on-time window texts auto-send after a trial, or is every text one-tap?

7. Confirm the first run: tomorrow's board plus drafts, no customer texts until you approve.

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
  "first_run_goal": "Build tomorrow's board with crew, parts, and windows, and draft the customer texts. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Build tomorrow's board with crew, parts, and windows, and draft the customer texts. Do not send.
