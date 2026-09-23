---
name: agent-onboarding
description: Configures the Referral Scout template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Referral Scout workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and where do clients and wins live?

2. What kind of intro do you actually want?

3. How many days after a win before we ask, and how long until we ask again?

4. Paste an ask that sounds like you.

5. Which Slack channel gets the weekly list, and who approves sends?

6. Confirm the first run: names plus drafts, no sends.

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
  "first_run_goal": "List who to ask for an intro this week, draft the asks, and show the open intro log. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> List who to ask for an intro this week, draft the asks, and show the open intro log. Do not send.
