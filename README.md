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

### Bot Directory light templates

The repository also includes 160 lightweight templates imported from
[Bot Directory](https://botdirectory.ai/). Each lives directly under `agents/`
and contains a concise operating prompt in `CLAUDE.md`, the original source
prompt preserved verbatim in `PROMPT.md`, and marketplace metadata plus creator
credit in `README.md`.

The reviewed import input is preserved in
[`sources/botdirectory/inventory.json`](sources/botdirectory/inventory.json),
with a normalized manifest in
[`sources/botdirectory/catalog.json`](sources/botdirectory/catalog.json).
Every “Connect First” label is classified in
[`sources/botdirectory/connect-first.json`](sources/botdirectory/connect-first.json):
real SuperAgent API-account and MCP slugs appear in `works_with`; browser,
built-in, local, raw-API, and unsupported services remain explicit in the setup
instructions without fabricated registry identifiers. Bot Directory's MIT
license and attribution are preserved in
[`sources/botdirectory/NOTICE.md`](sources/botdirectory/NOTICE.md).

## Agent metadata

Each agent has two core Markdown documents with distinct jobs, and lightweight
prompt imports add a third:

- `CLAUDE.md` contains the agent's operating instructions and core identity.
- `README.md` contains marketplace-facing details and, by convention, the marketing metadata.
- `PROMPT.md`, when present, contains the original getting-started prompt without frontmatter or editorial changes.

Both files may have YAML frontmatter. The index generator shallow-merges the two mappings; when the same top-level key exists in both files, `CLAUDE.md` wins. Nested objects are replaced as a whole rather than deep-merged. The Markdown body of `README.md` becomes the agent's long-form `details` value in `index.json`; frontmatter is removed from that body. A README is optional to the generator for backward compatibility, although every public agent in this repository should include one.

### Fields

| Field | Type | Purpose and fallback |
|---|---|---|
| `name` | string | Display name; defaults to the agent directory name. |
| `description` | string | Short marketplace summary; defaults to an empty string. |
| `createdAt` | ISO-8601 string | Original creation time; defaults to an empty string. |
| `version` | string | Agent template version; defaults to `1.0.0`. |
| `category` | string | Primary marketplace category; defaults to an empty string. |
| `icon` | string | Lowercase kebab-case Lucide icon name; defaults to an empty string. |
| `tags` | string array | Display-ready search and marketing labels; defaults to `[]`. |
| `works_with` | object array | Compatible API Accounts and MCPs, identified by canonical registry slug; defaults to `[]`. |
| `developer` | object | Credit with required `name` and optional `url`; defaults to `{}`. |
| `path` | string | Generated repository path. Do not set this in frontmatter. |
| `details` | Markdown string | Generated from the README body. Do not set this in frontmatter. |

A typical split keeps the operational fields in `CLAUDE.md`:

```yaml
---
name: Example Agent
description: 'A concise marketplace summary'
createdAt: "2026-08-18T00:00:00.000Z"
version: 1.0.0
---
```

And the marketing fields in `README.md`:

```yaml
---
category: Productivity
icon: calendar-check
tags:
  - Planning
  - Automation
works_with:
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: linear
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Example Agent

Long-form marketplace copy starts here.
```

`icon` must be the lowercase kebab-case name of an icon from the [Lucide icon catalog](https://lucide.dev/icons/), such as `inbox`, `presentation`, or `calendar-check`. Store the catalog name rather than the React component export name (`CalendarCheck`). The generator validates the name's syntax but does not embed a particular Lucide release's catalog, so consumers should fall back gracefully when a newer icon is unknown to their installed version.

`tags` are display strings, not identifiers. Preserve human-friendly spacing, capitalization, acronyms, and product names (for example `Email Management`, `SEO`, and `OpenSlide`). Consumers may normalize tags internally for search or filtering, but the index should keep the presentation-ready labels.

Each `works_with` item must contain exactly `type` and `slug`:

- `type: api_account` uses SuperAgent's canonical account `Provider.slug`, which is also the runtime `toolkitSlug` (for example `gmail`, `googlecalendar`, or `microsoft_teams`). Do not use a display name, per-user account ID, `composioSlug`, or `nangoSlug`.
- `type: mcp` uses the canonical `CommonMcpServer.slug` (for example `linear`, `ahrefs`, or `sanity`). Do not use a per-user MCP UUID or name.

Only list a connector transport the agent actually requests or consumes. Browser sessions, built-in chat integrations, public APIs, and services accessed only with a raw API key do not belong in `works_with`. The type is required because some slugs exist in both registries. Slugs are lowercase, exact, and case-sensitive. The generator validates the metadata shape and slug syntax but deliberately does not copy the app registries into this repository, so those registries remain the source of truth.

GitHub Actions checks every `works_with` entry type-by-type against both the
recorded and current canonical registries in `SkillfulAgents/SuperAgent`. It
also checks for newly available exact matches among labels that currently lack
a registry connector. The Bot Directory tests verify three-file completeness,
effective merged metadata, category normalization (`Success` → `Customer
Success`), and first-run account instructions, then compare every prompt and
creator credit with the recorded upstream source checkout.

### Regenerating the index

`index.json` is generated; do not edit it by hand.

```bash
python3 scripts/import_botdirectory.py \
  --inventory sources/botdirectory/inventory.json \
  --crosswalk sources/botdirectory/connect-first.json \
  --source-commit 75b5191e0e0bbc0946f8d307a967f16e6954a804 \
  --overwrite
uv run generate_index.py
uv run tests/test_generate_index.py
```

## Structure

```
.
├── agents/
│   ├── agent-pill/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   └── .claude/skills/...
│   ├── inbox-manager/
│   │   ├── CLAUDE.md
│   │   ├── README.md
│   │   └── .claude/skills/...
│   ├── <bot-directory-template>/
│   │   ├── CLAUDE.md
│   │   ├── PROMPT.md
│   │   └── README.md
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
├── tests/
│   ├── test_generate_index.py
│   ├── test_botdirectory_templates.py
│   ├── test_botdirectory_source.py
│   └── test_superagent_slugs.py
├── sources/
│   └── botdirectory/       (reviewed inventory, manifest, connector crosswalk, license)
└── README.md
```
