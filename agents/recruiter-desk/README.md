---
category: Human Resources
icon: user-search
tags:
  - Recruiting
  - Sourcing
  - Hiring
  - Interviews
  - Candidate Outreach
  - Greenhouse
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: googlesheets
  - type: api_account
    slug: greenhouse
  - type: mcp
    slug: clay
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Recruiter Desk

> Spend your day on candidate calls while the sourcing sheets, reply reads, scorecards and follow-up drafts get done in the background.

## What it does

Recruiter Desk is for agency and contract recruiters, and for in-house recruiters juggling several open roles. It runs six routines, each switched on or off on its own:

- **Candidate Sourcing Run**: on request, reads the job description, shows you a sourcing plan (titles, 10–20 target companies, location), then finds and enriches 20–50 real people with Clay or Gamut's built-in lead enrichment. Each person gets a 1–100 fit score, an archetype, a possible warm-referral teammate and a short outreach note in your voice, all in a ranked Google Sheet.
- **Candidate Reply Assessment**: when a candidate answers your outreach, scores how likely they are to take a screen on a fixed 0–100 scale, researches them through web search, and leaves you an internal read as a draft in the same thread. "Do not contact" requests are flagged at the top.
- **Post-Interview Candidate Follow-Up**: after an interview, drafts a specific, candidate-facing note for next round, still in process, or a kind pass.
- **Post-Interview Pipeline Update**: fills your scorecard in your ATS's exact format, writes clean notes, and suggests the stage change. Candid notes stay internal.
- **Hiring Manager Weekly Update**: one skimmable update per search, addressed to the right hiring manager or client, leading with movement, asks and at-risk flags.
- **Stalled Candidate Re-Engagement**: twice a week, finds good candidates who went quiet and drafts a nudge that picks up where you left off, using what they told you they care about.

It never contacts candidates or clients on its own. Everything addressed to someone else lands as a draft in your mailbox for you to review and send. It is the lightweight, routine-based option: for a full in-house pipeline with a calibrated screening filter, see Recruiting Agent; for scoring inbound applications, see Applicant Screener or Recruiting Reviewer.

## What you'll need

- **Gmail or Outlook**: required. Drafts land in your mailbox and the reply routine watches your outreach threads.
- **Google Calendar**: required for the post-interview routines and weekly updates.
- **Google Sheets**: required for sourcing sheets; also works as a simple tracker.
- **Greenhouse**: optional, as your ATS. Ashby or Lever also work with an API key, or through the browser if you have no key.
- **Clay**: optional, for sourcing and enrichment. Without it, Gamut's built-in lead enrichment is used.
- **Meeting notes**: optional. Granola, Fathom, Fireflies, Otter or Zoom transcripts make post-interview drafts specific.
- **API keys:** none for Greenhouse or Gmail. An Ashby or Lever API key if that is your ATS.

## Getting started

1. Import the template into Gamut.
2. Onboarding starts automatically with the `agent-onboarding` skill: pick your routines, connect your mailbox, calendar and ATS, share your scorecard, stage names and active searches, paste a few emails so drafts sound like you, and choose where alerts go.
3. It does a supervised dry run on your real data, then schedules the routines you switched on. Start with a sourcing run for one live role.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Source 30 candidates for our senior backend engineer role and show me the plan
- Assess the latest candidate reply on my outreach and leave me a draft
- Every Friday at 8am, draft an update for each hiring manager on my searches

## What's inside

- `CLAUDE.md`: the six routines, the Gamut mechanics, privacy rules and safe operating rules.
- `.claude/skills/agent-onboarding/`: first-run setup, connections, dry run and scheduling.
- `.claude/skills/reply-assessment-rubric/`: the fixed 0–100 likelihood scale and the internal assessment format.
- `.claude/skills/sourcing-sheet/`: the sourcing sheet columns, score bands and write procedure.

## Privacy

- Candidate data stays in the systems it came from (your mailbox, ATS and sourcing sheet). The agent's own run records keep only IDs, dates and scores.
- Research uses public professional information found through web search. It does not open LinkedIn profile pages directly or use people-search sites.
- It never records protected characteristics, and do-not-contact requests are honored in every routine and every future search.
- Internal notes, scores and comp details never go anywhere a candidate can see them. One client's candidates and pipeline are never shown to another client.

## Notes

- Nothing goes to a candidate or client automatically. Rejections and any held ATS stage moves always wait for your approval, because some ATS stage changes email candidates on their own.
- Enrichment uses credits. You approve the sourcing plan before any enrichment runs.
- If you recruit in the EU, UK or California, you may need to tell sourced candidates how their data was obtained. The agent reminds you and keeps sourcing sheets easy to purge.
