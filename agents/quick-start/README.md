---
category: Agent Creation
icon: pill
tags:
  - Onboarding
  - Starter Tasks
  - Company Research
  - First Win
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

# Quick Start

> Give it your company's website and walk away from your first session with a real piece of work done, not a tour.

## What it does

Quick Start is a first-session guide for people who are new to Gamut and want to see it do something useful right away. It opens with one question: what is your company's website? It reads the homepage, works out what the company does and who it serves, and asks which role best describes your work there.

From that, it invents four starter tasks that could only exist for your company and your job, each sized to finish in a single session. Some run entirely in the browser with nothing connected; others use a work tool you choose at hand-off. Pick one and Quick Start does it while you watch, showing drafts and asking before anything is sent, posted, or changed.

If you already know what you want, skip the website question and just say it. Quick Start drops the onboarding and gets to work. When a task turns out to be something you would want every day or week, it offers once to set it up as an always-on agent and hands you the prompt.

## What you'll need

- **Accounts:** None are required. Browser-based tasks need nothing connected. If the task you pick uses email, calendar, chat, CRM, docs, or a project tracker, Quick Start asks which product you use and requests that one account.
- **API keys:** None.
- **Time:** A minute to give the website and pick a task, then a few minutes of watching it work.

## Getting started

1. Import the template into Gamut.
2. The first session starts automatically and runs the `agent-onboarding` skill, which asks for your company's website.
3. Answer the role question, pick one of the four starter tasks, and approve any account connection the task needs.

Later sessions behave like a normal assistant. Ask for the next starter task whenever you want another one.

## Example prompts

- Hey Gamut, I'm new here. What can you do for me?
- Read our website and suggest four tasks you could do for me today
- That worked, set it up to run for me every Monday morning

## What's inside

- `CLAUDE.md` — the agent's durable role, voice, the fixed welcome opener, and style rules.
- `.claude/skills/agent-onboarding/` — the website read, role and task pickers, hand-off, and the format used when a task becomes an always-on agent.

## Privacy

Quick Start reads only your company's public homepage. It connects a work account only when the task you chose needs one, one account at a time, after asking. It never sends, posts, submits, or edits anything in a connected app without showing you first.

## Notes

- On a phone, Quick Start offers only tasks that run through connected apps, since browser work is easier to follow on a laptop.
- If the website is unreachable or too generic to learn from, it makes one gentle retry and then continues with default roles rather than blocking.
