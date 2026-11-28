---
name: refresh-review
description: Bring the dashboard up to date. Reads every in-scope agent's sessions since the last read, re-reads the five usage page ranges, captures avatars for new agents, and reports what changed in a few lines. Also holds how to count sessions, which setup's full read uses. Use for "refresh the dashboard", "refresh the review", or "update the numbers".
---

# Refresh the review

Follow the system prompt. This skill adds only what's specific to a refresh.
A refresh runs in a session someone is in: the usage page needs a person to sign in when its session has lapsed.

**A newer template?** Your template's source is in `.skillset-agent-metadata.json` at the top of your workspace. The app owns that file: read it, don't edit it. When the `version` in that template's `AGENTS.md` is newer than yours and you haven't said so before, tell the admin in one line: saying "update from template" reviews it.

**Claim first.** Claim the review as the system prompt describes. Remove the claim when you finish or stop.

```
1 Sessions   count every in-scope agent's sessions since the last read
2 Verify     open a sample of the new receipts
3 Cost       re-read the five usage page ranges
4 Avatars    only for agents new since the last capture
5 Report     what changed, in a few lines
```

Tell the admin it's started and roughly how long it will take. Do 1 in the background, and 3 alongside it.

## 1. Sessions

For each confirmed card, cover every session active since the last read (`ledger.py state` per month shows what's done), back to the start of the last 30 days at most.
Skip sessions a draft already has. Count the way *How to count* says.

Background readers can die without a word: check their writes on disk every few minutes, restart any with no new writes for 10 minutes, and never wait idle on one.

## 2. Verify

Open a sample of the new receipts for every outcome type with new outcomes: at least 3, or 10%, weighted to the types worth the most.
Each one found gets `ledger.py verify` with how you checked. Each one that doesn't hold up gets `ledger.py reject`, and then open more of that type.

## 3. Cost

Run the `read-usage-page` skill for all five ranges.
Signed out with nobody able to sign in: keep the old readings, and say cost is as of the last read.

## 4. Avatars

Run `capture-avatars` for in-scope agents with no entry in `artifacts/agent-roi/public/avatars.json`. Skip it when there are none.

## 5. Report

Run `scripts/review_math.py --period last30` and read it. Every number you write comes from it.
Tell the admin in a few lines: what moved in cost, worth and return, agents that changed band, and anything you couldn't read.
Numbers that moved a lot need a reason you can name: new outcomes, a price change, sessions left unread, rejected receipts.
The dashboard reads the review on every load. If it isn't running, start it (`artifacts/agent-roi`).

## How to count

Months are storage: pass `--period` as the month a session or delivery happened in, in the review's timezone.

**Sort sessions by kind first.** From the session list alone (name, schedule, who started it), group each agent's sessions into kinds: a 30-minute poll, a nightly snapshot, a person's chat. For each kind, decide whether it can ever deliver one of the card's outcomes.
- A kind that **can't deliver** and has no person in it: open a sample (at least 5, or 5% of them), confirm none delivered, then record the rest in batches with `ledger.py scan-routine`. Record the kind and the sample in `workspace.md` under *Rules*. If any sampled run delivered, the kind isn't routine: read all of it.
- Every session where a person was involved or an outcome could be delivered: open and read it.

Readers can work in parallel, one per agent. Each writes through `ledger.py` as it goes, so a restart loses nothing and a rerun skips what's done.
1. **Read the session.** Match deliveries to the card's outcome types using what counts and what doesn't. Partial or abandoned work is not an outcome.
2. **Find the receipt.** When the transcript doesn't show the id, look in the agent's own records. Asking the agent itself needs the admin's yes for that agent first. Never use personal details as a receipt. For an outcome type that counts on use, the receipt shows the use.
3. `ledger.py add` per outcome, `--status reported`, with its delivery date, the receipt in the card's form, and a short quote showing the delivery. A refused receipt was already counted or rejected. Never work around it.
4. `ledger.py scan` for the session:
   - **Setup or work.** Setup when the session changed the agent itself and delivered nothing. Otherwise work. One line of reason.
   - **People time.** Pass the session's messages in order, each as person or agent with its time (`--messages`). Without message times, pass how many messages a person sent (`--person-messages`). Never compute minutes yourself.
5. `ledger.py listed` once per month the last 30 days touch: the sessions active in that month from the start of the last 30 days on, and how many of those you didn't get to. An agent is fully counted only when nothing is left unread.

Record anything real the numbers leave out with `ledger.py exclusion`: what it is, its size ("53 bans · $5.3k" or "unknown") and which way it skews the numbers.
When something doesn't fit the card (a kind of delivery you've never seen, a rule that keeps misfiring), don't change the card. Bring it to the admin with your proposal.
If a session shows an exposed secret or a lapsed legal promise, return it to the main session in a few words, so the admin hears it once in chat. Never write the secret down.
