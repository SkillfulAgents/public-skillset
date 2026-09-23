---
name: agent-onboarding
description: Configures the Call Closer template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Call Closer workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and where do call notes and the CRM live?

2. Who owns default follow-up tasks if the call did not name someone?

3. Paste a recap that sounds like you.

4. Which Slack channel gets close-outs, and who approves the client recap?

5. May we book the next meeting automatically when they already agreed a time, or is every invite one-tap?

6. Confirm the first run: one call, full close-out, no client send until you approve.

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
  "first_run_goal": "Close out the last call: recap, tasks, CRM, and next meeting on the calendar. Draft the client recap. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Close out the last call: recap, tasks, CRM, and next meeting on the calendar. Draft the client recap. Do not send.
