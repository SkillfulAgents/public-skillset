---
name: Outbound Campaign
description: Run the outbound motion end to end - source and qualify prospects, enrich for contact data, draft personalized openers, send within caps, run the follow-up cadence, detect replies, and report. Use for any request to find prospects, write outbound email, send a campaign, run a cadence tick, check replies, or report on outbound performance. Requires config/outbound.yaml (run agent-onboarding first).
metadata:
  version: "1.2.0"
---

# Outbound Campaign

The runtime. `agent-onboarding` configures the motion; this executes it.

Everything reads `config/outbound.yaml`. Never hardcode a company name, cap, ICP rule, or vendor into a script, and never call a vendor API directly. Go through the adapter so a vendor swap stays a one-line config change.

All commands run from the workspace root.

## The loop

```
pipeline.py   source -> enrich -> qualify -> suppress -> store
brief.py      assemble the drafting material for one prospect
  (you draft)
queue.py      stage drafts for operator review; record approve/reject decisions
send.py       gate -> send -> log   (email automated; LinkedIn manual, see below)
tick.py       check replies, retire the answered, surface what is due
mark.py       record what only a human can know (LI accepts, LI replies, no-shows)
meetings.py   read the calendar, record booked meetings
report.py     measure
weekly_report.py  compose the weekly digest, post it on request
```

**The loop needs a heartbeat.** If the operating loop was not scheduled at onboarding, offer to schedule it with the platform scheduler: the cadence tick each send-day morning and the weekly digest (preceded by `meetings.py`) per `reporting.schedule`. The tick sends nothing on its own, so scheduling it is safe; every actual send still passes through `send.py` and its gates.

## Intake

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/pipeline.py --limit 20 [--dry-run]
```

Runs every gate in order and writes a `decisions` row at each one, so "why was this person dropped" stays answerable weeks later. `--dry-run` evaluates everything and stores nothing; use it the first time a new source is wired.

If it exits 2, a suppression source was unreachable and the run halted before storing anything. That is correct behavior, not a bug. Fix the source. Do not work around it.

## Drafting

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/brief.py --prospect 12 --step 0
```

**You write the copy. No script does.** A script that generates the sentence generates the same sentence for everyone, which defeats the only thing personalized outbound has going for it.

The brief gives you the prospect, why they qualified, ranked candidate use cases, the operator's voice samples, the constraints the linter will enforce, and everything already said to this person. Use all of it:

- **Read the voice samples before writing.** If the brief says there are none, say so to the operator and ask for one to three real emails. Copy written without them reads like copy, and that is the most common reason agent-written outbound gets ignored.
- **Pick one use case the prospect would plausibly own.** If the brief matched none, do not invent one and do not fall back to praising their company. Tell the operator the prospect has no mapped workflow.
- **On follow-ups, read `ALREADY SAID` and take a different angle.** A bump that restates the opener is worse than no bump.

Write the body as inner HTML to a file, then send it. Short paragraphs, one blank line between them, never one dense block.

## The approval queue

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/queue.py add \
  --prospect 12 --step 0 --subject "..." --body-file draft.html --confidence 0.8
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/queue.py list --status pending
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/queue.py approve 3   # chat-relayed decision
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/queue.py reject 3 --reason "wrong angle"
```

Any draft that needs a human before it sends goes through the queue: every draft of a **first batch**, anything below the **confidence threshold**, and anything **out of pattern**. Staging lints the copy first, so the operator never spends attention on a draft the linter would have bounced anyway.

The operator decides from either surface, and both land in the same table and audit log:

- **The live dashboard** (slug `outbound`, under `/workspace/artifacts/`): pending drafts render at the top with Approve and Reject buttons. This is the primary review surface; point the operator at it whenever drafts are waiting.
- **Chat**: they tell you; you record it with `queue.py approve/reject`. A rejection always carries a reason, because the reason is what improves the next draft.

`send.py` enforces the queue mechanically: a `pending` draft refuses to send, a `rejected` one refuses with the recorded reason, and an `approved` one sends only as the exact copy that was approved (changed copy must be re-staged). Approving is NOT sending: the approved draft still passes every gate (do-not-touch, caps, window, pacing, deliverability) and only goes out via `send.py`.

## Sending

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/send.py \
  --prospect 12 --step 0 --subject "..." --body-file draft.html [--confidence 0.8]
```

Every check is blocking, and they run in a fixed order so the cheapest and most consequential fire first. Exit codes are distinct so you can tell what stopped you.

**The linter is a gate, not a suggestion.** If a draft fails it, fix the copy. Do not reword around the check, do not disable it, and do not ask the operator to waive it. It enforces exactly the rules they agreed to at onboarding.

Pass `--confidence` honestly. A draft below the configured threshold stops and waits for the operator rather than sending. Under-reporting confidence to get a send through is the one failure mode this gate cannot catch on its own.

`--force-window` bypasses the send window only. It never bypasses a cap, and there is no flag that does.

### LinkedIn steps are manual, by design

There is no LinkedIn executor and you must not build or improvise one: automating LinkedIn actions violates its terms and gets the sender's account restricted, which ends every channel at once. The flow for a `linkedin_invite` or `linkedin_message` step:

1. Draft the note (`brief.py` as usual). Invites have a hard 300-character ceiling; the linter enforces it because LinkedIn truncates past it mid-sentence.
2. Run `send.py` for the step **without** `--manual`: it lints the note, checks the invite cap, and prints it as a ready-to-send manual action. Nothing is logged.
3. The sender performs the action on LinkedIn themselves.
4. Once they confirm, re-run the same command **with** `--manual` to record it. The cadence, caps, and reporting see it from then on.

Connection requests are capped per sender per day (`daily_linkedin_invite_cap`); messages to accepted connections are not. Never record a touch the operator has not confirmed happened.

## Human-reported events

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/mark.py --prospect 12 --linkedin-accepted
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/mark.py --prospect 12 --replied "let's talk" --sentiment positive --channel linkedin
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/mark.py --meeting 3 --meeting-status no_show
```

When the operator says "Dana accepted my invite", "he replied on LinkedIn", "she no-showed", record it immediately with `mark.py`. These facts unlock conditioned cadence steps, stop cadences, and correct the meetings numbers, and they exist nowhere else: the email and calendar detectors cannot see them. An operator statement left in chat history is a fact the motion never learns.

## Cadence

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/tick.py
```

Checks replies first, then computes what is due. That order is deliberate: a reply that landed overnight has to suppress this morning's follow-up.

**Any reply stops the cadence, including an ambiguous one.** The operator decides whether to re-engage. Never auto-reply, and never restart a stopped sequence on your own.

`tick.py` reports; it does not send. Draft each due message with `brief.py` and send it through `send.py`, so the gates apply to follow-ups exactly as they do to openers.

Its output separates **emails schedulable now** (you can send these through `send.py` today, within budget) from the **manual LinkedIn queue** (draft each note, hand it to the sender, record with `--manual` once done). Surface the manual queue to the operator; it does not clear itself.

## Meetings

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/meetings.py [--since ISO] [--until ISO] [--sender ID]
```

Reads each sender's calendar and writes `meetings` rows. Run it before reporting, otherwise the outcome number is stale.

**Most booked meetings never produce a reply.** The prospect clicks the booking link and books; nothing lands in the mailbox. That is why meetings are sourced from the calendar rather than inferred from reply text, and why a `none` calendar slot means the meetings number counts only what a human flagged.

**Matching is on work email, exactly, and nothing else.** If a meeting is obviously with a prospect but did not get attributed, the prospect's email in the database does not match the address on the invite. Fix the record. Do not match it by hand on name or company, and do not add a fuzzy fallback: one false positive costs more than ten missed meetings, because it is the number the operator quotes to other people.

**`held` means scheduled and not cancelled. It does not mean anyone attended.** Say it that way when you report it. A calendar cannot detect a no-show, so `no_show` is only ever set by a human, and you should never infer one.

## Reporting

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/report.py --window week [--write-dashboard]
```

Two rules when you relay numbers to the operator:

- **Never state a rate without its denominator.** "18% reply rate" off 11 sends is noise presented as signal. Below the configured floor, give the raw count instead.
- **There is no open rate.** Open tracking is deliberately absent: the pixel hurts deliverability and the number has been unreliable since Apple Mail Privacy Protection. If the operator asks for opens, explain why they are not there rather than approximating them.

Report the negative numbers as plainly as the positive ones.

**Meetings come from the `meetings` table, not from reply flags.** `report.py` reads it directly and falls back to the old reply-flag derivation only when the table is absent, saying so in a note when it does. A meeting that no send can be attributed to still counts in the totals and is reported separately; it is never quietly reassigned to a nearby send, and it is never dropped.

## Weekly digest

```bash
uv run --with pyyaml .claude/skills/outbound-campaign/scripts/weekly_report.py [--send] [--week ISO_DATE]
```

Prints the week's digest, meetings first, and posts nothing without `--send`. Delivery goes through the configured `notify` adapter; with `notify: none` it prints the digest and tells the operator how to wire a destination.

`--week` takes any date inside the week you want and reports the seven days ending there, so last Friday's digest can be reproduced exactly rather than sliding with the clock.

Run `meetings.py` before it. The digest leads with the outcome number, and a stale calendar makes that number wrong in the one place the operator is most likely to quote it.

## Standing rules

- **The first batch of any campaign needs operator approval before it sends.** Stage every draft of it in the approval queue and point the operator at the dashboard (or walk them through in chat). This gate cannot be disabled. After the configured number of approved drafts you may continue that batch unattended, but still stage anything you are not confident in.
- **Never send outside ICP without an explicit operator override**, per prospect, in the current conversation.
- **Never raise a cap.** Caps are per sender per day and per-campaign rates stack. If the operator wants more volume, that is an approval gate and usually the real answer is a dedicated sending domain, not a bigger number.
- **Never add tracking pixels or link wrappers.** They are what get a low-volume primary domain filtered.
- **Log before reporting success.** An unlogged send is a send that will be repeated.
- If enrichment returns a personal address (gmail.com and similar) for a corporate prospect, treat it as a probable bad match and flag it rather than sending.

## When something is missing

Say so. An empty use-cases file, absent voice samples, a `none` adapter slot, and a missing credential are all visible gaps that the operator can fix in minutes. Filling them in with plausible invention produces output that looks finished and is wrong, and nobody catches it until the replies do not come.
