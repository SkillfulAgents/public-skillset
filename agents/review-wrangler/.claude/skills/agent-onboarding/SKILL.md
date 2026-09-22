---
name: agent-onboarding
description: Configures the Review Wrangler template for the user's company, systems, cadence, thresholds, voice, and approval rules.
---

# Agent Onboarding

Welcome. This onboarding configures your Review Wrangler workspace so the agent can run against your own tools and process. Ask the questions below one at a time, wait for each answer, then write the final configuration into `CLAUDE.md` under `## Your context` and create `.claude/skills/agent-onboarding/config.json`.

## Questions to ask

1. What is the shop name, and which Google Business and Yelp listings should we watch?

2. How many hours after a completed job should we ask, and on SMS or email?

3. Paste two replies that sound like you: one happy, one a miss.

4. Which Slack channel gets 1-star and spicy reviews?

5. May 5-star replies auto-post after a trial, or is every public reply one-tap?

6. Confirm the first run: drafts only, nothing public until you approve.

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
  "first_run_goal": "Draft after-job review asks for yesterday's completed jobs and draft Google/Yelp replies. Do not post."
}
```

## First task prompt

After onboarding, suggest this first task:

> Draft after-job review asks for yesterday's completed jobs and draft Google/Yelp replies. Do not post.
