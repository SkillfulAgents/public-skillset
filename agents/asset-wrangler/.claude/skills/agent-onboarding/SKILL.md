---
name: agent-onboarding
description: Configures the Asset Wrangler template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Asset Wrangler workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and where do creative and copy land (Drive, Slack, email)?

2. Where should the status board live, and what statuses do you use?

3. How many hours before a due date should we flag late?

4. Which Slack channel gets late flags, and who approves client packs?

5. Paste a delay note that sounds like you, if you send those.

6. Confirm the first run: board plus late flags, no client sends.

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
  "first_run_goal": "Rebuild the asset board from Drive and Slack, flag anything late before the client pings, and draft status notes. Do not send to clients."
}
```

## First task prompt

After onboarding, suggest this first task:

> Rebuild the asset board from Drive and Slack, flag anything late before the client pings, and draft status notes. Do not send to clients.
