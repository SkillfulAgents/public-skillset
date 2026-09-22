---
name: agent-onboarding
description: Configures the Desk Deputy template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Desk Deputy workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the business name, and which inbox, calendar, and phone line are the desk?

2. Paste two emails and one missed-call text that sound like you.

3. Which meeting types may we book, and what is off limits on the calendar?

4. May routine confirms and missed-call texts auto-send after a trial, or is everything one-tap?

5. Which Slack channel is you, the founder, for spicy exceptions?

6. Confirm the first run: one desk, drafts only. Not three agents.

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
  "first_run_goal": "Work today's inbox, calendar, and missed calls as one desk. Draft replies, invites, and texts. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Work today's inbox, calendar, and missed calls as one desk. Draft replies, invites, and texts. Do not send.
