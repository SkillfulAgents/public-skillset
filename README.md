# Super Agent Public Skillset

A public collection of agent templates and skills for the Super Agent app.

## Agent Templates

### Agent Pill

Onboarding agent that interviews a new user, inspects their connected tools (with permission), and builds their highest-impact first Super Agent -- both as a created agent and a copyable prompt.

### Inbox Manager

Email management agent that helps users organize their Gmail inbox, screen and categorize emails, and unsubscribe from unwanted mailing lists.

## Structure

```
.
├── agents/
│   ├── agent-pill/
│   │   ├── CLAUDE.md
│   │   └── .claude/skills/...
│   └── inbox-manager/
│       ├── CLAUDE.md
│       └── .claude/skills/...
├── skills/          (future standalone skills)
├── index.json
├── generate_index.py
└── README.md
```
