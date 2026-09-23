---
name: agent-onboarding
description: Configures the Vendor Nudge template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Vendor Nudge workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the business name, and where do POs and bills live?

2. Who are the regular suppliers, and what is actually late today?

3. Paste a vendor nudge that sounds like you.

4. Which Slack channel gets the pay list and fights?

5. Any vendors we never nudge?

6. Confirm the first run: drafts and a pay list, no sends, no payments.

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
  "first_run_goal": "List late suppliers and bills we owe this week, draft nudges, and a pay list. Do not send or pay."
}
```

## First task prompt

After onboarding, suggest this first task:

> List late suppliers and bills we owe this week, draft nudges, and a pay list. Do not send or pay.
