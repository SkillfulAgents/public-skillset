---
name: agent-onboarding
description: Configures the Ledger Hawk template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Ledger Hawk workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the firm name, and where do invoices and time live?

2. What are payment terms, and when does a human take over the chase?

3. Paste one invoice note and one overdue note that sound like you.

4. Which Slack channel gets aged receivables?

5. Any clients we never auto-draft?

6. Confirm the first run: drafts only, invoices and chases unsent.

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
  "first_run_goal": "Draft invoices for completed unbilled work and the next overdue chases. Do not send."
}
```

## First task prompt

After onboarding, suggest this first task:

> Draft invoices for completed unbilled work and the next overdue chases. Do not send.
