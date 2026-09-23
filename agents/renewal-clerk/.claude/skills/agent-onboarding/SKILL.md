---
name: agent-onboarding
description: Configures the Renewal Clerk template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Renewal Clerk workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and where do contracts and end dates live?

2. How many days before end date should we draft, and who owns the relationship?

3. Where does usage live, if anywhere?

4. Paste a renewal note that sounds like you.

5. Which Slack channel gets churn-risk renewals?

6. Confirm the first run: drafts only, no auto-renew.

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
  "first_run_goal": "List contracts inside the renewal window, attach usage if we have it, and draft renewals. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> List contracts inside the renewal window, attach usage if we have it, and draft renewals. Do not send.
