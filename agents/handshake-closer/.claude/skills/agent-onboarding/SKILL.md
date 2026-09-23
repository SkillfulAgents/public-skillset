---
name: agent-onboarding
description: Configures the Handshake Closer template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Handshake Closer workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the business name, and where do verbal yeses show up (SMS, notes, voicemail)?

2. Where is the rate card, and what does a boxed estimate look like for you?

3. How many days of silence before the one nudge?

4. Paste an estimate send and a one-nudge note that sound like you.

5. Which Slack channel gets silence flags?

6. Confirm the first run: drafts only, one nudge max, nothing sent until you approve.

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
  "first_run_goal": "Find verbal yeses that still have no sent estimate, draft the estimates, and show any silence after one nudge. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Find verbal yeses that still have no sent estimate, draft the estimates, and show any silence after one nudge. Do not send.
