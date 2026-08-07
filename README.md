# Gamut Public Skillset

A public collection of agent templates and skills for the Gamut app.

## Agent Templates

### Agent Pill

Onboarding agent that interviews a new user, inspects their connected tools (with permission), and builds their highest-impact first Gamut agent -- both as a created agent and a copyable prompt.

### Inbox Manager

Email management agent that helps users organize their Gmail inbox, screen and categorize emails, and unsubscribe from unwanted mailing lists.

### Nutrition Agent

Personal nutrition tracker you can message naturally: describe a meal (or send a photo) and it estimates macros and logs it, tracks calories/protein/fat/carbs against your goal, logs body weight, and renders a trends dashboard. No accounts or API keys required.

### Office Manager

Keeps the team fed: runs the recurring weekly grocery/kitchen stock order, handles one-off Slack requests, and organizes daily lunch/dinner orders. Places real orders through the built-in browser on your logged-in shopping accounts, with careful records of everything bought.

### OpenSlide Studio

Slide-deck agent built on the open-slide framework — slides are React components on a fixed 1920×1080 canvas, and the dashboard *is* the OpenSlide app: a searchable deck library, editing and presentation views, live HMR previews, reusable themes, and inspector-comment-driven edits. Ships with a stock Getting Started deck; no accounts or API keys needed.

### Outbound Campaign Agent

Vendor-neutral outbound sales motion: ICP qualification, sourcing, enrichment, fail-closed suppression, linted drafting, capped sending, cadence, reply detection, and calendar-sourced meeting reporting. Swappable adapters for CRM, sender, enrichment, and calendar; nothing sends until onboarding writes your config.

### Recruiting Agent

Owns the hiring pipeline end to end — sourcing (LinkedIn, arXiv, YC directory, excellence pools), filtering with a self-improving screening prompt calibrated by your Advance/Don't-advance feedback, outreach, nurture, and interview scheduling, backed by Ashby or a no-ATS pipeline store.

### SEO Agent

Autonomous SEO specialist that owns one website's organic growth end to end: a daily content engine, link building and outreach with a local CRM, monthly technical audits, and weekly strategy/reporting with a live Ahrefs + Search Console dashboard.

## Structure

```
.
├── agents/
│   ├── agent-pill/
│   │   ├── CLAUDE.md
│   │   └── .claude/skills/...
│   ├── inbox-manager/
│   │   ├── CLAUDE.md
│   │   └── .claude/skills/...
│   ├── nutrition-agent/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── nutrition/     (state: SQLite db, goal, scripts)
│   │   ├── artifacts/     (nutrition dashboard app)
│   │   └── .claude/skills/...
│   ├── office-manager/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── grocery-baseline.md
│   │   └── .claude/skills/...
│   ├── open-slide-studio/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── artifacts/     (the OpenSlide app = the dashboard)
│   │   └── .claude/skills/...
│   ├── outbound-campaign-agent/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── adapters/      (crm, sender, enrichment, calendar, ...)
│   │   ├── lib/           (gates, caps, linter, suppression)
│   │   └── .claude/skills/...
│   ├── recruiting-agent/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   ├── pipeline/      (state: roles, shortlists, outreach)
│   │   └── .claude/skills/...
│   └── seo-agent/
│       ├── CLAUDE.md
│       ├── README.md
│       ├── seo/           (state: config, backlogs, CRM, log)
│       ├── artifacts/     (SEO master dashboard app)
│       └── .claude/skills/...
├── skills/          (future standalone skills)
├── index.json
├── generate_index.py
└── README.md
```
