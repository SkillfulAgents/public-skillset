# Super Agent Public Skillset

A public collection of agent templates for the Super Agent app.

## Agent Templates

### Agent Pill

Onboarding agent that interviews a new user, inspects their connected tools (with permission), and builds their highest-impact first Super Agent -- both as a created agent and a copyable prompt.

### Inbox Manager

Email management agent that helps users organize their Gmail inbox, screen and categorize emails, and unsubscribe from unwanted mailing lists.

## Structure

Each agent template lives under `skills/` and includes:
- `SKILL.md` -- the agent's core instructions (CLAUDE.md)
- `skills/` -- sub-skills the agent uses at runtime
