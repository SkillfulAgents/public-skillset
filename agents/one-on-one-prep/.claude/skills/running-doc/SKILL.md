---
name: running-doc
description: 'Layout of the private running 1:1 doc per person, the carry-forward and evidence rules, and the agenda ordering by relationship. Use on every 1:1 prep run before writing to a doc.'
---

# Running 1:1 doc

One doc per person, titled `1:1 – <Person name> (private)`. The newest section goes on top, under a fixed header. Never edit or delete older sections.

## Layout

```
1:1 – Sam Rivera (private)
To raise (type here anytime; the agent picks it up before the next 1:1)
- 

────────────────────────────
Tue 24 Nov 2026 · 10:00
Waiting on you
- Approve the Q1 contractor budget ("need a yes by Friday", 18 Nov). [link]

You owe them
- Send the revised onboarding plan (said 17 Nov). Open, no evidence found. (2nd week)

They owe you
- Draft of the vendor comparison (said 17 Nov). Done: shared 20 Nov. [link]

Since last time
- Shipped the billing fix on 19 Nov. [link]
- Flagged a risk on the March launch date in #proj-launch, 21 Nov. [link]

Your topics
- Q1 hiring plan (you added 20 Nov)

Suggested agenda
1. Contractor budget decision
2. Onboarding plan (overdue a week)
3. Launch date risk
4. Q1 hiring plan

My talking points
- 

────────────────────────────
Tue 17 Nov 2026 · 10:00
...
```

## Carry-forward rules

- Every open item from the previous section reappears with its original date. Increase its carry count; show "(2nd week)", "(3rd week)" from the second carry.
- At three carries, move it to the top of the agenda with "keep or drop?".
- Done needs evidence: a sent email, a shared doc, a closed ticket, a message saying it shipped. Link it. Done items appear once in the next section, then drop off.
- Anything the user wrote in the previous section (talking points, notes, "done" ticks) wins over your inference. If the user ticked an item done, treat it as done.
- Items the user deleted from the previous section are dropped; do not resurrect them.

## Agenda ordering by relationship

| Relationship | Order |
|---|---|
| Report | their blockers and asks waiting on you → their updates → items they owe → your topics → feedback and growth |
| Manager | decisions you need from them → status of what they asked you for → your topics → their updates |
| Peer | shared dependencies and handoffs → items either side owes → your topics |
| Client | open deliverables and dates → anything that reads as risk or dissatisfaction → their asks → your topics |

Three to five agenda lines. Items marked "(3rd week)" and anything waiting on the user for more than a week always make the list.

## Markdown fallback

Without a docs connection, keep the same layout in `/workspace/one-on-ones/<person-slug>.md` and deliver it with `mcp__user-input__deliver_file`. Read the "To raise" box from the file the user last edited if they upload it back.
