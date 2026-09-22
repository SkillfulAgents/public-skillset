---
name: agent-onboarding
description: Configures the Onboarding Desk template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Onboarding Desk workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and where is the client folder template and tracker?

2. What counts as signed (SOW, first payment, founder note)?

3. Paste a kickoff email that sounds like you.

4. Default first report date (30 days or something else), and who attends kickoff?

5. Which Slack channel gets the onboarding pack?

6. Confirm the first run: one client, folder plus kickoff plus first report date, no client send until you approve.

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
  "first_run_goal": "Onboard the newest signed client into the folder, the tracker, a kickoff on the calendar, and a first report date. Draft the client note. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Onboard the newest signed client into the folder, the tracker, a kickoff on the calendar, and a first report date. Draft the client note. Do not send.
