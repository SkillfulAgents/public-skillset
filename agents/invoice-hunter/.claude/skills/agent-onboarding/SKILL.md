---
name: agent-onboarding
description: Configures the Invoice Hunter template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Invoice Hunter workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and where do invoices live (QuickBooks, Jobber, a sheet)?

2. What aging cadence should we use, and when does a human take over?

3. Paste one overdue reminder that sounds like you.

4. Which Slack channel gets 90-day and spicy accounts?

5. Any customers we never chase automatically?

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
  "first_run_goal": "Pull overdue invoices, draft the next chase on cadence, and flag anything that needs me. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Pull overdue invoices, draft the next chase on cadence, and flag anything that needs me. Do not send.
