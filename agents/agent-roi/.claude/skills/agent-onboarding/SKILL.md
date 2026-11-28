---
name: agent-onboarding
description: First-run setup for Agent ROI. Says hello, creates the review folder, then hands over to the set-up-review skill, which shows a first dashboard.
first_prompt: Set up Agent ROI
---

# Agent onboarding

Keep this short. The folder is housekeeping, not the setup, so don't mention it to the user.

0. **Hello.** The system prompt's *First session* sends it before any tool call. If it hasn't been sent in this session, send it now. Never twice.
1. **Create the review folder** if it's missing, without overwriting anything that exists:
   - `review/workspace.md` with the headings *Who this is for*, *Who decides what*, *Reading agents' sessions*, *Cost source*, *Gamut app*, *Rules*, *Decisions*, each empty.
   - `review/cards.json`: `{"cost_of_an_hour_usd": null, "timezone": null, "scope": "listed", "people_time": {"in_cost": false}, "agents": []}`
   - `review/coverage.json`: `{"agents": []}`
   - `review/changelog.md` with a `# Changelog` heading, and an empty `review/needs-you.md`.
   - empty `review/costs/`, `review/drafts/` and `review/exports/` folders.
2. **Hand over** to the `set-up-review` skill. It starts at scope, since you sent the hello.
