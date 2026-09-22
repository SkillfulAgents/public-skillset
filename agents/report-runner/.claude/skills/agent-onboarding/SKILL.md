---
name: agent-onboarding
description: Configures the Report Runner template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Report Runner workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and where is the client roster and tracker sheet?

2. Which ad and analytics accounts should we pull, and what is the reporting month?

3. Paste a recap (or three bullets) that sounds like you.

4. Which Slack channel gets the pack, and who approves the send?

5. Any clients we never auto-draft, or metrics we never show?

6. Confirm the first run: drafts in a doc, nothing to the client until you approve.

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
  "first_run_goal": "Build this month's client recaps from ads, analytics, and the sheet. Draft only. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Build this month's client recaps from ads, analytics, and the sheet. Draft only. Do not send.
