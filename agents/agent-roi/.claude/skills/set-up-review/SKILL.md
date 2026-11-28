---
name: set-up-review
description: Set up Agent ROI with the admin in three answers, and show a first dashboard in the same session. Settle scope, ask the setup questions in one form, read a sample of every agent's sessions in parallel to draft its card, confirm all cards in one table, read cost and avatars, show the dashboard, then start the full read of the last 30 days in the background. Also use it later to add an agent, rework a card, or change how value or cost is counted. Use for "set up Agent ROI", "add <agent> to the review", "rework <agent>'s card", or the first session after setup.
---

# Set up the review

Follow the system prompt. This skill adds only what's specific to setup.

The goal of the first session: the admin sees what each agent delivered and what it costs, after three answers.
Everything else runs in the background.

```
T0  Hello            no answer needed, sent once
Q1  Scope            "yes"
Q2  One form         cost of an hour, read consent, cost source
    Sample read      parallel readers draft cards and count what they read
Q3  One table        "yes" confirms every card
    Cost             the five usage page ranges, if signed in
    Avatars          from the Gamut app
    First dashboard  right away, most agents still Incomplete
    Full read        the last 30 days, in the background
```

## Arriving

Read your memory and `review/` first. One of three things is true:
- **New review.** No confirmed cards. Start at T0.
- **Unfinished setup.** Open with one short status: where setup stands and the one thing you need. Carry on from there. Never re-ask anything already answered.
- **Revisit.** The review runs. Ask what the admin wants to add or change, then do just that (*Revisits*).

## Writing to the admin

- Plain words, short messages. Each question names what you found and offers your best answer, so "yes" is a complete reply.
- Write options and reasons in the admin's terms. Never cite your instructions or this skill.
- No long per-agent cards in chat. Card detail lives in `cards.json` and opens on click in the dashboard.
- When a message lists items under a count, take the count from the list you print, after you've built it.

## T0. Hello

In the first session, `agent-onboarding` has already sent the hello. Don't send another.
When setup starts any other way, send that same hello, as plain text, before any tool call.

## Q1. Scope

List the agents, from names and descriptions only. Propose three groups: team agents you'd include, personal agents you'd leave out, and ones you're unsure about, each with a one-line reason where it isn't obvious.
Each agent appears in exactly one group: check the three lists against each other before you send. Leave this review agent itself out.
End with your suggestion for the unsure ones and "Reply yes, or tell me what to move."
On the answer, record each agent in `coverage.json` with `in_scope`. Out-of-scope agents are never read, counted or listed again.

## Q2. One form

Ask everything else in one `AskUserQuestion` call with three questions. Put the recommended option first, marked recommended, with a one-line reason in the admin's terms.

1. **What is an hour of a person's time worth?** It prices the time agents save. Offer three figures based on the roles the agents stand in for (for example a loaded salary for those roles, and a typical contractor rate). Record `cost_of_an_hour_usd` in `cards.json`. Set `timezone` to the admin's IANA timezone.
2. **Is your go enough to read the agents' sessions over time?** "Yes, my go is enough" first, then "Each agent's owner must agree". Record it in `workspace.md` under *Reading agents' sessions*.
3. **Where should cost come from?**
   - "Sign in to Gamut Platform (owner or admin)" (recommended)
   - "Skip for now"

Whatever the answer, write `review/cost-source.json`:
```json
{"type": "command", "name": "Usage page", "command": "python3 scripts/usage_page.py cost"}
```
Then start the sample read and handle sign-in alongside it. Skipping cost never blocks anything else.
- **Sign in.** Start it yourself right away; never ask the admin for a link first. Open `https://platform.gamutagents.com/dashboard` in the browser and sign in with `mcp__user-input__request_login` (the account must be an owner or admin of the org). After sign-in the platform lands on the org's usage page, `https://platform.gamutagents.com/dashboard/organizations/<org id>`: record that address (no query) under *Cost source* in `workspace.md`. If the account has several orgs, show their names and ask which one.
- **Skip.** Cost shows as unknown. Add to `needs-you.md`: "Connect cost: sign in to the usage page as an owner or admin, then say refresh the dashboard."

Never estimate spend yourself.

## Sample read

Before the readers start, tell the admin in one line: "You'll get one prompt to let me read your agents. Choose Always Allow, then Always allow reading all agents, so it doesn't ask once per agent."
Start one background reader per in-scope agent, all in parallel. Each reads the agent's session list and its most recent sessions, about 20, and writes through the scripts as it goes, so a reader that dies loses nothing and a restart skips what's done.

Each reader:
1. **Drafts the agent's card**, without `confirmed_at`, from what the sessions show, never the description:
   - **Purpose:** one sentence.
   - **Outcome types:** one or two that carry most of the value. What counts and what doesn't, the receipt that proves one (specific to one delivery), delivery or use, the value kind, a `unit` that is a plain plural noun ("sales videos") and a `unit_one` that is its singular ("sales video"), and the price with its reason and anchor. For an estimate, a low end. When nothing delivers, `"outcome_types": []` and `purpose` says what was looked for.
   - **Name:** the agent's name exactly as `list_agents` gives it. Never rename it ("InfoSec", not "InfoSec Agent").
   - **Owner and team:** the owner is one person's name, with "?" right after it when it's a guess ("Graham Cummings?", no space). No notes, roles or other users in the field.
2. **Counts what it read** in the last 30 days, as `refresh-review` *How to count* says: `ledger.py add --status reported` per delivery, `ledger.py scan` per session read, then `ledger.py listed` per month with the sessions it didn't read. The agent then shows as Incomplete.
3. Returns any exposed secret or lapsed legal promise in a few words, for one mention in chat.

Cards and coverage are shared files: have each reader return its card, and write `cards.json` and `coverage.json` yourself as readers finish.
An agent you can't read gets `readable: false` in `coverage.json` and who can grant access.

**Readers can die without a word.** While any are running, check their progress on disk (cards and draft lines they wrote) every few minutes. A reader with no new writes for 10 minutes is dead: start a new one for its unfinished agents, which skips what's done. Never wait idle on a reader.

## Q3. One table

When the readers finish, show one table for all agents:

| Agent | What it delivers | Price | Owner |
|---|---|---|---|
| Video Maker | sales videos | $150–300 each (estimate) | Sales lead? |

Lead with the low end of each price, and mark estimates. Below the table, one line on what you couldn't read. End with "Reply yes or tell me what to fix."
On yes, set `confirmed_at` and `confirmed_by` on every card and log it in `changelog.md`. Apply any fix first. When a fix changes an outcome type, `ledger.py clear` that agent and count its sample again.
When an answer applies beyond one agent (a rule like "drafts never count"), record it in `workspace.md` under *Rules*.

## Cost and avatars

- **Signed in:** run `read-usage-page` for all five ranges.
- Run `capture-avatars` for every in-scope agent.

## First dashboard

Start the dashboard (`artifacts/agent-roi`) if it isn't running, and show it right away.
Say in one line that most agents are Incomplete because only a sample is read so far. Cost shows as unknown when sign-in was skipped. Never type a number the script didn't produce.

## Full read

Then start the full read of the last 30 days in the background: one reader per agent, counting every session as `refresh-review` *How to count* says. Routine runs go in batches with a sample. Every session where a person was involved or an outcome could be delivered is opened.
Tell the admin it's running and roughly how long it will take, from the session counts you've seen (about 1 to 2 hours for a workspace of 15 agents).
When it finishes, verify a sample of receipts (`refresh-review` step 2), re-read the five ranges if the last read is more than a few hours old and someone can sign in, and tell the admin in a few lines what the dashboard now shows.

## Knowing when it's done

Setup is done when every in-scope agent you can read has a confirmed card, the admin has seen the dashboard, and the full read has finished.
What's still missing (cost not connected, agents you can't read) goes in `review/needs-you.md`, not the conversation.
Agents left out stay in `coverage.json`, with the reason.

## Revisits

- **Add an agent.** Read its sample as above, show its one-row table and confirm, capture its avatar, then count its last 30 days.
- **Rework a card.** Restate the change in one line, apply it on yes, log it, then `ledger.py clear` the agent and count it again.
- **Change the cost source.** Show the current `cost-source.json` and the change, and apply it only on their go.

## File shapes

A card in `cards.json`, as `review_math.py` checks it:
```json
{"agent_id": "<id the agent-to-agent tools use>", "agent_name": "", "owner": "", "team": "", "purpose": "",
 "confirmed_at": "YYYY-MM-DD", "confirmed_by": "<admin>",
 "outcome_types": [{"id": "", "name": "", "unit": "<plural noun a reader counts, e.g. bans>",
                    "unit_one": "<its singular, e.g. ban>", "counts_when": "", "receipt": "",
                    "value_kind": "time_saved | money_saved | money_made",
                    "counts_on": "delivery | use", "hours": 0, "hours_low": 0, "price_usd": 0, "price_usd_low": 0,
                    "price_reason": "", "price_anchor": "owner | market_rate | real_cost | estimate"}]}
```
Time saved uses `hours`, plus `rate_usd` only when that work's rate differs from the workspace's cost of an hour. Money saved and money made use `price_usd`.

`coverage.json`: `{"agents": [{"agent_id": "", "name": "", "owner": "", "in_scope": true, "readable": true, "grant_from": ""}]}`. `readable` decides whether the agent is counted.

## Saving progress

`review/` holds every card and count as it lands. Your memory holds only where you are: which moment of setup, which readers finished, and questions still open.
Where the admin hesitated, corrected you, or asked what something meant, write it in your memory.
