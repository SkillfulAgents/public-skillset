---
version: 1.13.0
category: Sales
icon: target
tags:
  - sales-outreach
  - lead-generation
  - prospecting
  - email-campaigns
  - sales-automation
works_with:
  - type: api_account
    slug: gmail
  - type: api_account
    slug: googlecalendar
  - type: api_account
    slug: slack
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Outbound Agent Template

A complete, vendor-neutral outbound motion you import as an agent and configure for your own team: ICP, positioning, tools, senders, caps, cadence, and voice.

It is not a copywriting prompt. Most of what is here is the machinery that decides who gets contacted, who never does, how often, from which mailbox, and what has to be true before a message is allowed out. That machinery is the part that is expensive to rebuild and easy to get quietly wrong.

## Start here

```bash
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/list_adapters.py
```

Then ask the agent to run onboarding. It interviews you and writes `config/outbound.yaml`.

Nothing else runs until that file exists. That is deliberate.

## What you get

| | |
|---|---|
| **Onboarding skill** | A structured interview that writes your config, generates your `CLAUDE.md`, seeds positioning files, initializes the database, and self-tests the wiring. |
| **Campaign skill** | Intake, drafting briefs, the send gate, the cadence tick, a capped manual LinkedIn queue, calendar-sourced meeting tracking, reporting. |
| **Adapter layer** | Seven capability slots. Swap a vendor without touching the motion. |
| **Enforcement** | A copy linter, a send-cap governor, a fail-closed suppression chain, and a do-not-touch gate, all of which run before a message can leave. |
| **Reporting** | Metrics and a zero-dependency dashboard, with meetings read from the sender's calendar rather than inferred from replies. No open tracking, by design. |

## The design decision worth knowing about

**Configuration is the single source of truth, and `CLAUDE.md` is generated from it.**

The usual failure of an agent template is drift: the instructions say one thing, the code does another, and nobody notices for a month. Here the standing instructions are rendered from `config/outbound.yaml`, so a cap change or an ICP change updates both at once. If the two ever disagree, the config wins and you regenerate.

The second decision follows from the first: **rules that matter are enforced mechanically, not asked for politely.** An instruction not to use em dashes is a suggestion a model will occasionally ignore. A linter that refuses the send is not. The same applies to daily caps, suppression, and the approval gate on a campaign's first batch.

## Layout

```
config/
  outbound.example.yaml   every field, documented inline. Your config is merged over it.
  outbound.yaml           yours. Written by onboarding. The source of truth.
lib/
  config.py     typed access, brand embargo, send windows, per-sender caps with ramp
  adapters.py   the registry and the slot contract
  db.py         vendor-neutral SQLite schema
  identity.py   name and LinkedIn matching. Stops same-first-name coworker swaps.
  icp.py        tiering, size bands, disqualifiers, buyer tiers
  linter.py     mechanical copy enforcement
  caps.py       daily gate, stacked-rate governor, deliverability kill switch
  gates.py      the do-not-touch gate
adapters/
  sourcing/ enrichment/ sender/ crm/ calendar/ suppression/ notify/
.claude/skills/
  agent-onboarding/    the interview and its scripts
  outbound-campaign/      the runtime
positioning/
  positioning.md, use-cases.json, voice-samples.md    yours to fill in
```

## Adapters

Seven slots. Each is a directory of interchangeable modules, and **the vendor in each slot is the importing team's choice, not the template's.** Onboarding asks slot by slot which tools the team uses, as multiple choice from `adapters/catalog.yaml` (the most common real-world answers) plus an open "Other".

| Slot | Does | Reference implementation |
|---|---|---|
| `sourcing` | produce prospect rows | `csv` |
| `enrichment` | resolve contact data | `apollo` |
| `sender` | deliver, and report replies | `gmail` (`dryrun` is the starting mode) |
| `crm` | look up and record | `sqlite` (local) |
| `calendar` | report booked meetings | `google` |
| `suppression` | decide who is off limits | `crm`, `local` |
| `notify` | reach a human | `slack` |

The shipped modules are working reference implementations, not the menu. A vendor with no builtin (Outlook, Instantly, Attio, Calendly, anything) gets a stub via `scaffold_adapter.py`: the config names the team's real stack immediately, and the stub fails closed on every call until implemented. `none` disables a slot as a visible gap.

`enrichment` and `suppression` take an ordered list and run as a waterfall.

Writing a new adapter means implementing two or three functions and declaring which environment variables it needs. `lib/adapters.py` documents the contract at the top. The motion does not change when a vendor does.

## The rules that cannot be configured away

These are enforced in code, and `validate_config.py` fails a config that tries to disable them.

- **A reply stops the cadence.** Every reply, including ambiguous ones. A human decides whether to re-engage.
- **Suppression is fail-closed.** If a suppression source is unreachable, the run halts. Contacting a current customer as a cold prospect is worse than a delayed batch.
- **The first batch of a campaign needs human approval.**
- **The first run is a dry run, reviewed by a human.**
- **No tracking pixels, no link wrappers, no open tracking.** They damage deliverability for exactly the low-volume senders this template is built for, and the number they produce has been unreliable since Apple Mail Privacy Protection.
- **No rate is displayed without its denominator.** Below the configured floor, you get the raw count.

## Testing it

The sender defaults to `dryrun`, so the entire motion is exercisable with zero network calls and zero risk.

```bash
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/selftest.py
```

Walks fixture prospects through config load, adapter resolution, identity matching, ICP qualification, cap enforcement, the linter, and the database write path. A missing vendor credential is reported as *not provisioned*, not as a failure, because the wiring is sound either way.

A pass means the machinery is correct. It says nothing about whether your ICP or your copy is any good. Only you can judge those.

## What this does not do

- It does not write your copy unattended. The drafting brief assembles the material; the agent writes the message; the linter gates it; you approve the first batch.
- It does not warm mailboxes. New senders ramp from 10 to 25 a day over roughly four weeks, but you need a real warmup provider and, past about 25 a day per mailbox, a dedicated sending domain.
- It does not give you an ICP. An inherited ICP reads plausible and targets the wrong people confidently. Empty and honest beats populated and wrong.
