---
name: agent-onboarding
description: Configures the Invoice Ask template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Invoice Ask workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the business name, and where do customer invoices live?

2. What cadence, and when do you take over?

3. Paste an invoice ask that sounds like you.

4. Which Slack channel gets aged customer balances?

5. Any customers we never auto-ask?

6. Confirm the first run: customer asks only, drafts unsent. Opposite of Vendor Nudge.

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
  "first_run_goal": "List customers who owe us, draft the next asks, and keep vendor bills out of this queue. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> List customers who owe us, draft the next asks, and keep vendor bills out of this queue. Do not send.
