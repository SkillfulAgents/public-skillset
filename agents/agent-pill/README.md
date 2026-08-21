---
category: Agent Creation
icon: pill
tags:
  - Onboarding
  - Agent Builder
  - Workflow Discovery
  - Tool Discovery
  - Personalization
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
  - type: api_account
    slug: slack
  - type: api_account
    slug: microsoft_teams
  - type: api_account
    slug: discord
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: github
  - type: api_account
    slug: linear
  - type: api_account
    slug: notion
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: googlesheets
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Agent Pill

> Stop staring at the “create new agent” screen. Agent Pill finds the single most useful first agent for you—and builds it.

## What it does

Agent Pill is a first-run guide for people who know they want an agent but do not yet know which workflow is worth automating. It has a short, natural conversation about your work, identifies recurring friction, and turns the best opportunity into a concrete agent.

With your permission, it can inspect patterns and metadata from one to three connected work tools. It looks for signals such as recurring senders, meeting load, channel activity, and repeated project work; it does not read private content unless you explicitly approve that deeper look. It can also do public research about your role or company when that would sharpen the recommendation.

Rather than returning a generic list of ideas, it ranks a few specific candidates, explains why the strongest one should matter to your week, and helps you refine it. Once you choose, Agent Pill creates the new agent in your workspace and gives you a portable copy of its prompt.

## What you'll need

- **Accounts:** None are required. Connecting one or more work tools makes its recommendations more specific.
- **API keys:** None.
- **Time:** A few minutes for the interview and optional tool scan.

## Getting started

1. Import the template into Gamut.
2. Start a conversation; the onboarding flow begins automatically.
3. Describe the part of your week you most want to improve.
4. Optionally connect the tools that best represent that work.
5. Review the ranked ideas and pick one to build.

Agent Pill steps aside after the handoff. Your newly created agent owns the workflow from then on.

## Example prompts

- Help me find the first agent worth building
- Look at my connected tools and spot the recurring work
- Build the agent we agreed on and hand me the prompt

## What's inside

- `CLAUDE.md` — the agent's durable role, voice, privacy rules, and handoff behavior.
- `.claude/skills/agent-onboarding/` — the interview, opt-in tool scan, research, recommendation, and agent-creation workflow.

## Privacy

Tool inspection is optional and consent-driven. The default scan uses structural signals and metadata rather than message or document bodies. Agent Pill explains any deeper access it wants, why it would help, and waits for explicit approval.
