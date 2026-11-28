---
category: Ops
icon: clipboard-check
tags:
  - Agent ROI
  - ROI
  - Agent Fleet
  - Cost
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
avatar:
  color: tonal-amber
  shape: arch
---
# Agent ROI

An agent that reviews what your workspace's agents deliver and what they cost, with a receipt behind every number.

## What it does

It reads each agent's sessions, counts the finished work (outcomes) each one delivered, and prices it with prices you confirm.
It reads spend from the Gamut Platform usage page.
The dashboard shows cost, worth and return for the same ranges as the usage page: week to date, month to date, and the last 7, 14 and 30 days.

- **Cost** is AI usage and paid tools. People's time is an estimate you can turn on in the Cost panel. It is off by default.
- **Worth** is each outcome times its price, from the low end to the stated price.
- **Return** is worth divided by cost.
- Agents sit in three bands: **Fully counted** (every session in the range read, cost known), **Incomplete** and **Idle**. The totals cover fully counted agents only.
- Every figure opens to its breakdown. Every outcome links to its receipt.

## Setup

Say "Set up Agent ROI". Setup takes three answers:

1. **Scope.** Which agents to review. Reply yes to the proposed groups, or move agents between them.
2. **One form.** What an hour of a person's time is worth, whether your go is enough to read agents' sessions, and whether to sign in to Gamut Platform (owner or admin) for cost or skip it for now.
3. **One table.** The outcome and price drafted for each agent. Reply yes, or say what to fix.

The dashboard opens right after, from a sample of each agent's sessions.
A full read of the last 30 days then runs in the background, about 1 to 2 hours for 15 agents.
Agents move from Incomplete to Fully counted as it finishes.

## Refresh

Nothing runs on a schedule.
Say "refresh the dashboard" in a chat with the agent.
It reads new sessions, re-reads the usage page (you may need to sign in), and tells you what changed.
The dashboard shows when it was last updated, and marks it stale after 24 hours.

## Downloads

The Download menu on the dashboard gives the current range as:
- a one-page PDF to forward
- an agents CSV, one row per agent
- an outcomes CSV, every outcome with its receipt

## What's new in 1.0

- Views follow the Gamut Platform usage page's ranges, defaulting to the last 30 days. Monthly close, statements and monthly reports are gone.
- Refresh is by hand. There is no scheduled run.
- Cost is spend only. People's time is an optional estimate.
- No findings and no cut, keep or invest calls. Each agent shows its return instead.
- Agents are banded Fully counted, Incomplete and Idle.
- Explanations live in tooltips and the About panel.
- Real agent avatars and member stacks, captured from the Gamut app.
- PDF, agents CSV and outcomes CSV downloads.
