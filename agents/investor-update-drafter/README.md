---
category: Ops
icon: pen-line
tags:
  - Investor Updates
  - Founders
  - Fundraising
  - LP Updates
  - Gmail
  - Stripe
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: stripe
  - type: api_account
    slug: linear
  - type: api_account
    slug: github
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Investor Update Drafter

> Your monthly update is 90% written before you remember it's due, and it never forgets what you promised last time.

## What it does

Investor Update Drafter starts from the last update you actually sent, found in your sent mail or a Drive folder. It lists the metrics you reported, the asks you made, and every "next period" commitment. Then it gathers what changed: what shipped in GitHub and Linear, revenue from Stripe, numbers from your metrics sheet, hires, fundraising and pipeline movement, customer wins, and the risks your team raised internally.

It drafts in your voice and your structure. The headline comes first, metrics are stated against last period, every old commitment is marked done, in progress or dropped with a reason, and the asks are specific enough to act on. When it can't find or reconcile a number, it writes "(needs number)" and lists every gap in a short summary. If a draft already exists for the period, or nothing material changed, it skips and tells you why.

It works for a founder's monthly update, an LP letter, or a partner-meeting recap. An EA or chief of staff can also use it to draft for a principal. The draft lands in your Gmail drafts or a Google Doc. It never sends.

## What you'll need

- **Gmail** (or Outlook): required. Finds your last update and saves the new draft in your own mailbox.
- **Google Drive**: needed if past updates or the output live in Drive. Google Docs is used when the draft should be a Doc.
- **Google Sheets**: optional, for a metrics sheet. Excel works too.
- **Stripe**: optional, for revenue and subscription metrics.
- **Linear** and **GitHub**: optional, for what shipped this period.
- **PostHog, Amplitude or Mixpanel**: optional, through their MCP servers, for product metrics.
- **A CRM** (HubSpot, Salesforce or Attio): optional, for pipeline and customer wins.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs on first use. It asks whether you send the update or draft it for someone, what kind of update it is and when it's due, where past updates and your numbers live, and where the draft and summary should land. Then it connects those accounts and runs one supervised draft with you.
3. Ask for your first draft: "Draft this month's investor update from last month's."

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Draft this month's investor update starting from the one I sent last month
- What did I promise investors last update, and where does each one stand?
- Every month, draft my update 3 days before the 5th and leave it in Gmail

## What's inside

- `CLAUDE.md`: the drafting routine, the details that keep updates honest, connection and scheduling mechanics, and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup that writes `config.json` and creates the schedule.
- `.claude/skills/update-structure/`: the default update structure, LP and partner-recap variants, and the pre-handoff checklist.

## Notes

- It only drafts. Sending, adding recipients, and sharing the doc are always up to you.
- It never invents numbers, and it never computes fund performance figures for LP letters. Missing values stay as visible placeholders.
- Run state lives in `/workspace/state/` (which periods were drafted, and the running commitments list).

## Privacy

The agent reads your sent mail, drafts, and the sources you connect, only to build the update. Anything sensitive, such as customers under NDA, people matters or round terms, is flagged for your decision rather than written into the draft.
