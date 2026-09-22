---
name: agent-onboarding
description: Configures the Billing Chaser template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Billing Chaser workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and where do time, invoices, and retainers live?

2. At what remaining percent should we warn, and how many days before end date should we draft renewal?

3. Paste one billing note and one renewal note that sound like you.

4. Which Slack channel gets aging and churn-risk accounts?

5. Any clients we never auto-draft invoices for?

6. Confirm the first run: drafts only. Renewal is part of this job.

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
  "first_run_goal": "Pull unbilled time, overdue invoices, and retainers running low, and draft any renewals due. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Pull unbilled time, overdue invoices, and retainers running low, and draft any renewals due. Do not send.
