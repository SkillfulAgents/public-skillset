---
name: agent-onboarding
description: Configures the Quote in a Box template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Quote in a Box workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the business name, and where is the rate card or menu?

2. Where do conversations live (Gmail, SMS, notes)?

3. Paste a quote that sounds like you.

4. Which Slack channel gets drafts, and who one-tap sends?

5. What work always needs a custom (not boxed) quote?

6. Confirm the first run: one boxed quote, no send.

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
  "first_run_goal": "Turn the last conversation into a boxed quote with price, scope, and a yes/no ask. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Turn the last conversation into a boxed quote with price, scope, and a yes/no ask. Do not send.
