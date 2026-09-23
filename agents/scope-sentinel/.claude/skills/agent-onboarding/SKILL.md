---
name: agent-onboarding
description: Configures the Scope Sentinel template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Scope Sentinel workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and where do SOWs and the client tracker live?

2. Where do client asks arrive (Gmail, Slack, both)?

3. Paste a change-order note that sounds like you, and point at the rate card if you have one.

4. Which Slack channel gets out-of-scope flags, and who approves the send?

5. Any clients or work types that always need a founder conversation first?

6. Confirm the first run: drafts only, no client sends.

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
  "first_run_goal": "Scan this week's client asks against the SOW, flag out-of-scope, and draft change orders. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Scan this week's client asks against the SOW, flag out-of-scope, and draft change orders. Do not send.
