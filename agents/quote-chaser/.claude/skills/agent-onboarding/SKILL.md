---
name: agent-onboarding
description: Configures the Quote Chaser template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Quote Chaser workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and where do estimates live (Jobber, Housecall Pro, ServiceTitan, a sheet)?

2. After how many quiet days should we nudge, and what is the last nudge before a human call?

3. Paste one follow-up that sounds like you.

4. Which Slack channel gets drafts, and who approves the send?

5. Any customers, job types, or dollar amounts that always need a founder call first?

6. Confirm the first run: drafts only, no sends.

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
  "first_run_goal": "Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Review sitting estimates, draft follow-ups for the ones going cold, and queue one-tap sends. Do not send.
