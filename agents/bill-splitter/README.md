---
category: Personal
icon: calculator
tags:
  - Bill Splitting
  - Venmo
  - Roommates
  - Personal Finance
  - Gmail
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: outlook
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Bill Splitter

> Stop fronting the electric bill and forgetting to collect: every shared bill turns into tap-to-send requests at month end.

## What it does

At the end of each month, Bill Splitter looks for bill emails from the senders you named, such as the utility, the internet provider or a shared subscription. It never searches the rest of your inbox. It reads the amount and due date from the email or the attached statement, and if the amount isn't clear it asks you instead of guessing. Then it works out each person's share with the split you set up: equal, percentages, fixed amounts or custom.

You get one summary with each bill attached or linked, every person's share, and a prefilled Venmo request link for each person, with a short note like "Electric-Aug-2026". The shares always add up to the cent. It flags a bill that jumped from its usual amount and a bill that hasn't arrived yet. You tap each link, check the request in the Venmo app and send it yourself. The agent never messages the people you split with and never moves money.

Prefer Splitwise? It can record each bill there instead, after you approve it.

## What you'll need

- **Gmail or Outlook**: required. Read access limited to the bill senders you name.
- **Venmo**: no connection needed. The agent builds request links that open in your Venmo app.
- **Splitwise**: optional alternative to Venmo links, as a connected account.
- **A place for the summary**: the agent's own email inbox (recommended, so links are tappable on your phone), Slack, Telegram, iMessage or in-app.
- **API keys:** none.

## Getting started

1. Import the template into Gamut.
2. The `agent-onboarding` skill runs before first use. It records your bills, who's in each split and their Venmo handles, connects your mailbox, and checks that the request links open correctly on your phone.
3. Ask it to split last month's shared bills so you can check the amounts before the first scheduled run.

Re-run onboarding anytime by asking the agent to run the `agent-onboarding` skill.

## Example prompts

- Split last month's electric and internet bills between the three of us
- Show me this month's shares with Venmo request links for each person
- Change the internet split so Sam pays a flat 20 dollars from next month

## What's inside

- `CLAUDE.md`: the month-end routine, splitting rules, Gamut mechanics, safe operating rules and the `## Your context` block.
- `.claude/skills/agent-onboarding/`: first-run setup, the Venmo link check, a supervised split, the schedule and `config.json`.
- `.claude/skills/venmo-request-links/`: the Venmo request link format, encoding, a small builder, first-run verification and fallbacks.

## Notes

- Venmo request links are not officially documented and have changed before. The agent checks them on first run and falls back to copy-ready text if they stop working.
- Links only fill in a request. Nothing is sent until you tap Request in Venmo.
- Late fees and past-due balances are not split unless you say so.

## Privacy

The agent reads only mail from the bill senders you list. Request notes never include account numbers or service addresses. It stores no passwords. If a provider's portal must be opened to read an amount, you sign in yourself, each time.
