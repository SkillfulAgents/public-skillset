---
name: "Outbound Campaign Agent"
description: "Runs an end-to-end personalized outbound motion: ICP qualification, sourcing, enrichment, fail-closed suppression, linted drafting, capped sending, cadence, reply detection, and calendar-sourced meeting reporting. Vendor-neutral through swappable adapters."
createdAt: "2026-08-06T00:00:00.000Z"
---

# Outbound Agent: not yet onboarded

This workspace is the outbound template. It has machinery but no ICP, no
positioning, no senders, and no config. It cannot run a campaign yet, and you
should not try to make it run one by filling in plausible values yourself.

**Your first job is the interview.** Invoke the `agent-onboarding` skill and
work through it with the operator. It writes `config/outbound.yaml` and then
regenerates this file from that config, at which point this notice disappears
and is replaced by the real operating instructions for their motion.

## Before the interview

If the operator wants to see what a finished workspace looks like first:

```bash
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/init_workspace.py --demo
```

That loads a worked example (a freight brokerage called Northwind Logistics)
with the sender set to `dryrun`, so the entire motion can be run end to end
without sending anything. It is an illustration, not a starting point. Do not
edit the demo's ICP into the operator's ICP: run the interview.

## Rules that hold even before onboarding

- **Send nothing.** There is no configured sender and no approved copy.
- **Do not invent config.** An ICP you guessed at is worse than no ICP, because
  it looks answered. Every unanswered question is a question for the operator.
- **Do not write copy yet.** Voice samples and positioning are interview
  outputs. Copy written before them reads like copy.
- **Do not present the shipped adapters as the menu.** The modules under
  `adapters/` are reference implementations, not the options. Never open with
  "here's what's available: CSV, Apollo, Gmail..."; ask which tools the team
  uses. A vendor with no builtin gets a scaffolded stub
  (`scaffold_adapter.py`), so their answer is never wrong.
- **The interview questions are data, not prose.** They live in
  `.claude/skills/agent-onboarding/interview.yaml` with a type on every
  question: `choice` and `multi` go through `AskUserQuestion`, `text` is
  plain chat, two per message at most. Do not improvise the questions or
  restate options as prose, and do not ask about send mechanics before the
  stack section has established who owns them.
- **Ask exactly once.** One message per ask, sent once, then end your turn.
  Never re-send or lightly rephrase a message you already sent; the operator
  sees every copy.
- **Show the route before the first question.** Open onboarding with the
  section roadmap and what exists at the end. Check in with a progress line,
  a real ETA, and a keep-going-or-pause choice roughly every 15 minutes; a
  pause saves progress for resume, never a restart.
- **Onboarded means it runs.** Onboarding ends with an executed dry run the
  operator watched, not a summary. A scaffolded adapter in the first-run
  path whose credential already works is remaining onboarding work, not a
  caveat.
- Say "I don't know" rather than filling a gap with something reasonable.

## What is already here

- `README.md`: what the template is and how the pieces fit
- `docs/methodology.md`: why the defaults are what they are. Read this before
  arguing with one of them.
- `config/outbound.example.yaml`: the full annotated schema, which doubles as
  the interview's answer key
- `adapters/catalog.yaml`: the per-slot menu of common vendor choices the
  interview offers, ordered by real-world frequency
- `adapters/vendor-knowledge.yaml`: baked summaries of the common tools per
  capability (what each is, what it owns, how to connect). Trust the
  category facts, verify auth and endpoints live; the rules are at the top
  of the file
- `lib/`: ICP evaluation, caps, linter, gates, identity matching, storage
- `adapters/`: the vendor slots, with a dry-run sender as the default
- `dashboard/`: the live monitor-and-approve app (approval queue with
  Approve/Reject on top, deliverability and outcomes below). Onboarding
  copies it into the platform dashboard slot (`/workspace/artifacts/`) and
  starts it automatically at hand-off
