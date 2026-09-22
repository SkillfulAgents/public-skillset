---
name: agent-onboarding
description: Configures the Ad Anomaly Watch template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Ad Anomaly Watch workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the agency name, and which Google Ads and Meta accounts are in play?

2. Where do client caps and CPA targets live (sheet, Slack, a doc)?

3. What is a spike for you (example: 2x CPA for 4 hours, daily cap at 80%)?

4. Is there a hard kill switch, or is every pause founder-approved?

5. Which Slack channel gets flags, and who is the founder?

6. Confirm the first run: recs only, no pauses unless you already set a kill switch.

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
  "first_run_goal": "Check live campaigns for spend and CPA spikes, draft pause-or-rec notes, and do not pause anything unless a kill switch is already configured."
}
```

## First task prompt

After onboarding, suggest this first task:

> Check live campaigns for spend and CPA spikes, draft pause-or-rec notes, and do not pause anything unless a kill switch is already configured.
