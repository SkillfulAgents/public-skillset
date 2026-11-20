---
name: agent-onboarding
description: 'First-run setup for Bill Splitter: records each shared bill, its sender and split rule, the people and their Venmo handles, connects the mailbox, runs a supervised split on last month''s bills, then schedules the month-end run.'
first_prompt: 'Set up Bill Splitter for our shared bills'
---

# Bill Splitter onboarding

## 1. Welcome

In two sentences: you'll find each shared bill from the senders the user names at month end, work out everyone's share, and send them a summary with one-tap Venmo request links. You never message the other people and never move money. Then list the questions:

1. Which bills you split
2. Who's in each split, and how it's divided
3. Everyone's Venmo handle
4. Which mailbox the bills arrive in
5. Where to send your summary
6. Venmo links or Splitwise

## 2. Check connections

Call `mcp__user-input__search_connection_options` for Gmail, Outlook and Splitwise. Call `mcp__chat__list_agent_integrations` for an existing agent email inbox, Slack, Telegram or iMessage.

## 3. Ask, one at a time

1. **Mailbox** (`AskUserQuestion`): Gmail or Outlook.
2. **Bills**: for each shared bill, its name as you want it in notes (for example "Electric", "Internet", "Streaming"), the sender address or domain, and a subject pattern if the sender also sends other mail. Offer to find candidates: search the last 90 days for likely bill senders the user names (not the whole inbox) and show what you found for confirmation.
3. **People**: display names and Venmo handles (without `@`), or the phone number or email they use on Venmo. Ask the user to double-check the spelling of each handle, because a wrong handle sends the request to a stranger.
4. **Split rule per bill** (`AskUserQuestion` for the type, then details): equal among listed people, percentages, fixed amounts, or custom. Confirm whether the user is part of each split (usually yes) and that the user absorbs any leftover cent.
5. **What to split**: current charges only (default), or the full amount due. Late fees and past-due balances: ask each time (default) or always split.
6. **Labeling** (`AskUserQuestion`): name the month by service period (default) or by arrival month.
7. **Delivery** (`AskUserQuestion`): the agent's own email inbox (recommended, so the statement can be attached and links stay tappable), Slack DM, Telegram, iMessage or in-app. Set up the integration if missing (`mcp__chat__list_available_integration_providers` then `mcp__chat__add_agent_integration`, or `mcp__user-input__request_integration_setup`).
8. **Venmo or Splitwise** (`AskUserQuestion`): Venmo request links (default), Splitwise expenses after approval, or both.
9. **Timing**: month-end evening (default 18:00 on the last day) and timezone, and whether to also split each bill as soon as it arrives.

## 4. Connect

- `mcp__user-input__request_connected_account` with `gmail` (or `outlook`): "Allow access to Gmail to read bills from the senders you named?"
- If Splitwise: `splitwise`: "Allow access to Splitwise to add shared bills after you approve them?"

## 5. Verify the Venmo format, then dry run

Follow the `venmo-request-links` skill: search the web for current notes on Venmo payment links, then ask the user to tap a test link on their phone and confirm the right request screen opens (then cancel it). Save the result to `/workspace/state/bill-splitter/venmo-format.json`.

Then run the split on last month's bills and show the summary exactly as it would be delivered. Check each amount with the user against the statement. Fix anything once (wrong amount field, split rule, note wording).

## 6. Schedule

- `schedule_task`, cron `0 18 28-31 * *` in the user's timezone, with a self-contained prompt. The prompt says to exit unless tomorrow is the 1st, gives the config path `/workspace/.claude/skills/agent-onboarding/config.json` and the ledger `/workspace/state/bill-splitter/ledger.json`, names the delivery channel and the user as the only recipient, says to ask when an amount is unclear, and states the limits: charge links only; never message anyone else; never move money.
- Optional on-arrival: `get_available_triggers` on the mailbox account, then `setup_trigger` on new mail. The prompt exits unless the sender matches a configured bill.
- Confirm with `list_scheduled_tasks` / `list_triggers`.

## 7. Save

Summarize under `## Your context` in `CLAUDE.md` and write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/Los_Angeles",
  "mailbox": {"provider": "gmail", "account_id": ""},
  "people": [{"id": "me", "name": "You", "venmo": null}, {"id": "p1", "name": "", "venmo": ""}],
  "bills": [
    {
      "id": "electric",
      "label": "Electric",
      "senders": ["billing@example-utility.com"],
      "subject_pattern": "statement",
      "split": {"type": "equal", "people": ["me", "p1"]},
      "amount_basis": "current_charges",
      "late_fees": "ask"
    }
  ],
  "label_month_by": "service_period",
  "leftover_cent_to": "me",
  "unusual_change_pct": 30,
  "payout": {"venmo_links": true, "splitwise": false, "splitwise_auto_create": false, "splitwise_group_id": null},
  "delivery": {"channel": "platform-email", "integration_id": "", "to": ""},
  "schedule": {"cron": "0 18 28-31 * *", "on_arrival": false},
  "scheduled_tasks": [],
  "triggers": []
}
```

Split types: `equal`, `percent` (`{"p1": 40, "me": 60}`), `fixed` (`{"p1": 2000}` in cents, the user takes the rest) and `custom` (described in words and confirmed).

End with when it runs, where the summary goes, and a reminder that the user taps every request themselves.
