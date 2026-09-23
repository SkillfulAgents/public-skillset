---
name: agent-onboarding
description: Configures the Job Status Scout template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Job Status Scout workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and where do when-are-you-coming texts land?

2. Which system has the real window (Jobber, Housecall Pro, ServiceTitan, a calendar)?

3. Paste one status reply that sounds like you.

4. May on-time replies auto-send after a trial, or is every reply one-tap?

5. Which Slack channel gets late, missing-window, and angry cases?

6. Confirm the first run: draft status replies from the real board, send nothing spicy.

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
  "first_run_goal": "Answer today's when-are-you-coming messages with the real window from the board. Draft replies. Do not send the spicy ones."
}
```

## First task prompt

After onboarding, suggest this first task:

> Answer today's when-are-you-coming messages with the real window from the board. Draft replies. Do not send the spicy ones.
