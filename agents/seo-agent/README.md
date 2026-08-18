---
category: Marketing
icon: search-check
tags:
  - seo
  - content-marketing
  - keyword-research
  - link-building
  - technical-seo
  - analytics
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: github
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# SEO Agent — template

An autonomous SEO specialist that owns one website's organic growth end to end:

- **Content engine** — a prioritized backlog burned down daily: keyword-researched,
  multi-angle-researched, fact-checked, humanized articles published through your CMS,
  plus on-site "surface" improvements (metas, internal links, structured data).
- **Link building** — competitor-backlink prospecting, directory/listing submissions,
  and (optionally) personalized email outreach with a local CRM, ramp caps, and
  follow-up discipline.
- **Technical SEO** — a monthly comprehensive audit (sitemap, indexing, redirects,
  performance, structured data) that ends in PRs or tickets, not just findings.
- **Strategy & reporting** — a weekly steering session that pulls KPIs, replenishes
  backlogs, and sends a one-page report by email or Slack; a live **SEO Master
  dashboard** (Ahrefs + Search Console + program activity).

## What it needs

| Requirement | Used for | Required? |
|---|---|---|
| **Ahrefs API key** (plan with API access; Site Explorer endpoints ideally) | Keyword research, backlink/DR tracking, competitor analysis | Yes (SEMrush possible with skill edits) |
| **Google Search Console** service account added to the property | Clicks/impressions/rankings — the north-star metrics | Yes |
| **CMS or repo access** (Sanity/WordPress/Ghost/git/hosted builder) | Publishing content | Yes, for the content engine |
| **Gmail (connected account)** | Weekly report by email; outreach inbox (ideally a dedicated inbox on a separate warmed domain) | Optional |
| **Slack (chat integration)** | Weekly report via Slack instead of email | Optional |
| **GitHub (connected account)** | Site PRs, awesome-list submissions | Optional |
| **Unsplash API key** | Blog imagery (Openverse works keyless) | Optional |

## What onboarding does

Importing this template auto-launches a setup session (the `agent-onboarding` skill):

1. **Tools** — connects GSC + Ahrefs (offers to drive signup in the browser if you have
   neither), confirms the domain, kicks off an Ahrefs site audit.
2. **Research** — explores your website, current rankings and backlinks, and your
   competitors; presents a baseline analysis; agrees a keyword list with you (with a
   light primer on head vs tail terms and search intent).
3. **Plan** — technical audit scheduling, link-building approach, content cadence and
   backlog, plus 1–2 creative ideas for your specific business; agrees goals/targets.
4. **Cadences** — schedules the daily content / daily links / weekly strategy / monthly
   audit tasks, connects the report channel (email/Slack), and verifies the dashboard
   renders with your data.

Nothing is published, sent, or merged without an explicit autonomy grant you make
during onboarding (recorded in `seo/STATE.md`).

## Layout

```
CLAUDE.md                  agent instructions (generic; onboarding personalizes)
.env.example               required/optional secrets
seo/                       program state: config.json, STATE.md, backlogs, CRM, log
artifacts/seo-master/      the SEO dashboard (React + Bun; collector-fed)
.claude/skills/            11 skills (see CLAUDE.md for the table)
```

## Import

Upload the zip as a new agent template / import it as an agent workspace. The onboarding
session starts automatically. Have your Ahrefs key handy; GSC setup can be done together
during onboarding.
