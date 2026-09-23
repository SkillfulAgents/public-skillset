---
name: agent-onboarding
description: Configures the Proposal Pilot template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Proposal Pilot workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and where is the proposal template and rate card?

2. Where do call notes live (Granola, CRM, a paste)?

3. Who must approve price, and which Slack channel gets the draft?

4. Paste a proposal intro that sounds like you.

5. Any work types that always need a lawyer or partner pass?

6. Confirm the first run: one proposal from notes, no send.

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
  "first_run_goal": "Turn the latest call notes into a sendable proposal. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Turn the latest call notes into a sendable proposal. Do not send.
