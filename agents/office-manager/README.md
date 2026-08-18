---
category: Operations
icon: shopping-cart
tags:
  - Office Management
  - Workplace Operations
  - Procurement
  - Grocery Ordering
  - Team Meals
works_with: []
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Office Manager

> Keeps the team fed — weekly grocery orders, one-off Slack requests, and daily lunch/dinner group orders.

## What it does

A friendly (slightly humorous, lower-caps) office manager agent. It runs a recurring weekly kitchen-stock order (post list to Slack → collect special requests → place the order → post a summary), handles one-off requests people DM it on Slack (snacks, drinks, office equipment — ordered from Amazon or your store of choice), and can organize daily lunch/dinner group orders on Uber Eats or DoorDash. Every office runs differently, so the onboarding interview does the heavy lifting of tailoring it to yours.

## What you'll need

- **Slack** — connected as a chat integration during onboarding (strongly recommended; it's how the team talks to the agent).
- **A shopping account** — Amazon / Whole Foods, Amazon Fresh, or Instacart, logged in via the agent's browser during onboarding.
- **(Optional) Uber Eats or DoorDash** — if you want meal orders.
- **API keys:** none.

## Getting started

1. Import this template (drag the zip into the agent import dialog).
2. A setup session starts automatically. The **agent-onboarding** skill will:
   - ask what to take care of (weekly kitchen stock / one-off requests / meal orders / other)
   - collect office basics (address, company, team size, contact person, order email/phone)
   - connect Slack and your shopping accounts (it verifies logins in the browser)
   - build your grocery baseline list and agree on budgets, schedules, and how autonomous it should be
   - create all the recurring scheduled tasks
3. Then just let the team DM it: "can we get more sparkling water?"

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## What's inside

- `CLAUDE.md` — the agent's instructions (role, style, request routing, record keeping, privacy rules).
- `.claude/skills/agent-onboarding/` — the first-run setup interview.
- `.claude/skills/amazon-order/` — a battle-tested browser SOP for placing Amazon orders.
- `grocery-baseline.md` — the standing weekly list (filled in during onboarding).
- `grocery-requests.json` — the mid-week request queue (starts empty).
- `grocery-orders-log/` — one log file per placed order.
- `.env.example` — no keys required; kept for future extensions.

## Notes

- **Privacy:** the agent has a strict standing rule to never read, disclose, or relay personal order history or account details from connected shopping accounts — it only places new orders to the office address.
- **Autonomy is configurable:** during onboarding you choose whether it places orders itself or preps the basket and pings a human to check out.
- The agent keeps full logs of every order in `grocery-orders-log/`, so spend is always auditable.
