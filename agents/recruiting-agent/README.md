---
category: Human Resources
icon: user-search
tags:
  - Recruiting
  - Talent Sourcing
  - Candidate Screening
  - Hiring
  - ATS
  - Outreach
works_with:
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Recruiting Agent Template

A ready-to-run recruiting agent: sourcing → filtering → outbound → nurture → interview scheduling, with a self-improving screening filter calibrated by your feedback.

## First run

Say hello (or "set up"). The agent runs its **`agent-onboarding`** skill: a guided interview that configures your ATS (or a no-ATS pipeline store), imports your roles, sets up per-role screening criteria, outreach voice and templates, the daily search schedule, and the dashboard. ~20 minutes.

## Example prompts

- Set up my roles and screening criteria
- Source candidates for the backend engineer role
- Advance these three and tell the filter why

## What's inside

- `.claude/skills/` — the agent's toolkit (onboarding, ATS access, LinkedIn sourcing, excellence pools, calibration feedback, YC directory)
- `CLAUDE.md` — the operating manual; onboarding fills in the `{{PLACEHOLDER}}` tokens for your company
- `pipeline/` — empty workbench scaffold; your data accumulates here

This bundle contains **no data**: no candidates, no API keys, no memory. Everything is created fresh during onboarding.
