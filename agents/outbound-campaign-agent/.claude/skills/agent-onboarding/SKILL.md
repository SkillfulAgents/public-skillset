---
name: agent-onboarding
description: Configure this workspace to run personalized outbound for YOUR team. Use on first run, or whenever the ICP, positioning, senders, caps, cadence, or vendor tools change. Interviews the operator, writes config/outbound.yaml, generates CLAUDE.md standing instructions, seeds positioning files, initializes the database, and runs a dry-run self-test. Run this BEFORE any sourcing, drafting, or sending.
metadata:
  version: "1.9.0"
---

# Outbound Onboarding

Turns a blank import of this template into a working, team-specific outbound motion.

Nothing else in this template will run until `config/outbound.yaml` exists. That is deliberate: every hardcoded company name, cap, ICP rule, and vendor choice was pulled out into that one file, so the motion is portable and the configuration is explicit.

## When to run

- **First import.** Always. Run the full interview.
- **Interrupted mid-interview.** `data/onboarding.partial.json` exists: recap its recorded answers in two lines and resume from its `resume_at` marker. Never restart a paused interview from the top.
- **Something changed.** ICP shift, new sender mailbox, new positioning, cap change, vendor swap. Run the affected section only (`--section icp`).
- **Health check.** `--validate-only` re-checks the existing config without changing it.

## How to run it

This is an *interview*, not a script you fire and walk away from. You (the agent) ask, the operator answers, you write the config.

**Do not invent answers.** If the operator does not know their bounce threshold or their tier mix, use the documented default and tell them what you defaulted to. Guessing an ICP produces a config that looks authoritative and is wrong, which is worse than an obvious gap.

## The operating model: research, propose, confirm

This section is template-agnostic by design. It applies to every question in every section, and it can be lifted verbatim into any other template's onboarding skill.

For anything you need from the operator, the order is:

1. **Research first.** Before asking, check what already answers the question: connected accounts and their read-only APIs, environment variable names, the workspace itself, the company's website, the vendor's docs, a web search. Thirty seconds of research routinely replaces five questions.
2. **Form a hypothesis and present it as a draft to correct.** "Here is what I found and what I think it means; correct me" beats a blank question every time: it is faster for the operator, and their corrections are sharper than their compositions. Use research to make abstract questions concrete with real names ("your CRM has stages Trial, Active, Churned; I would suppress Active and Trial") rather than asking in the abstract.
3. **Verify with the operator.** Corrections are the signal. An unedited proposal is NOT a validated one: read back anything consequential rather than treating silence or a quick "looks fine" as review.
4. **Adjust and proceed.** Ask a cold question only when research returned nothing, and say that you looked.

The boundaries that make this safe, all non-negotiable:

- **Research is read-only.** Never create, modify, enroll, or send anything while researching.
- **Hypotheses are labeled as hypotheses.** Never present an inference as a fact the operator stated.
- **Nothing is configured from research alone.** Every researched value passes through a confirmation before it lands in config.
- **Gated values stay blank rather than guessed.** Anything an enforcement mechanism audits against (caps, thresholds, suppression states) is worse guessed than missing, because a guess looks enforced while enforcing nothing.
- **Personal content needs consent in the moment.** Reading someone's sent email or private documents to build a proposal happens only after they say yes to that specific harvest, never silently.
- **A section may declare itself an exception.** Where a waved-through hypothesis is more dangerous than a slower question, the section says so in `interview.yaml` and gets asked, not proposed. In this template that is the ICP: an inferred ICP that the operator nods past becomes confidently wrong targeting, and nothing downstream catches it.

### Step 0: orient

```bash
cd <template-root>
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/list_adapters.py
```

Shows what is installed, what is scaffolded, and the per-slot menu of common vendor choices from `adapters/catalog.yaml`. This is for YOUR orientation only. **Do not open the conversation by reciting the installed adapters as "what's available today."** The shipped modules are reference implementations; the interview asks what the TEAM uses, and any vendor they name can be scaffolded on the spot. Presenting the installed list as the menu steers the operator into someone else's stack, which is the exact failure this template exists to avoid.

### Step 1: interview

**The questions are data, not prose.** `interview.yaml` in this skill's directory is the single source for the interview: section order, question wording, type, options, defaults, and the config key each answer lands in. Read it before asking anything, then walk it section by section. The notes further down are conduct guidance per section; the questions themselves come from the file.

**The question type is a contract, not a suggestion:**

- `choice` and `multi` questions MUST be asked through `AskUserQuestion` (with `multiSelect: true` for `multi`). Batch up to four related questions from the same section into one call. Never restate the options as prose in chat. **Tripwire: if you have just asked two consecutive plain-chat questions that listed options in prose, you are doing it wrong. Stop and use the tool.**
- `text` questions are asked in plain chat, at most two per message. Never send a numbered wall of questions.
- **Ask exactly once.** One message per ask: fold the acknowledgment of the previous answer and the next question into a single message, send it once, and end your turn. Never re-send or lightly rephrase a message you already sent; the operator's screen shows every copy, and a doubled question reads as a glitch. If your previous message already asks the question, wait for the answer.
- The UI adds "Other" to every choice automatically. An Other answer is first-class: capture the free text and act on it (for tool questions, that usually means scaffolding).

**Stack first, then adapt.** The stack section comes immediately after identity, because what the team already runs changes what the rest of the interview should even ask:

- Open with the free-text stack question and let them describe what they actually use. Pre-fill every slot you can from that answer and **confirm your mapping in one line instead of re-asking**; only ask the per-slot choice questions their description left open.
- **Named tool? Knowledge file first, search second, ask last.** `adapters/vendor-knowledge.yaml` summarizes the most common tools per capability: what each is, what it owns, the mode implication, the typical connection path. Check it before searching; for tools it covers, you can propose immediately. The trust split is stated at the top of that file and is not optional: **trust the slow-changing facts (category, ownership, mode); verify the fast-changing ones live (auth, endpoints, docs URLs) before requesting any credential**, and believe the live result over the file when they disagree. A tool not in the file gets a web search (`mcp__web__web_search`), domain-anchored for ambiguous names, before you say anything about it; a tool being absent from the file never means "unknown". Search establishes what the tool *is*; only the operator knows how *they* use it, so every path ends in a one-line confirmation, never in configuring a slot from research alone. Asking the operator to describe their own tool is the last resort, for when research comes back empty or contradictory.
- **Connect and explore before interrogating.** Once the mapping is confirmed, get connected to each tool right then. **"It is not connected" is a to-do, not an answer.** When no connection exists, researching the ways in is your job, never the operator's. The discovery ladder, in order:
  1. Search the platform's connection catalogs for the vendor: `mcp__user-input__search_connected_account_services` (OAuth toolkit?) and `mcp__user-input__search_remote_mcp_services` (MCP endpoint?).
  2. Web-search the vendor's developer and API documentation yourself. Never ask the operator for a docs URL you can find with a search.
  3. If no API exists at all, offer a read-only browser session (`browser_open`, delegating to the web-browser agent) where the operator completes the login themselves.

  Present what you found as a ranked choice with a recommendation ("Monaco has a REST API, docs at their developer site: recommend an API key, or I can read the settings through the browser"), then act on the pick immediately: `mcp__user-input__request_connected_account` for OAuth, `mcp__user-input__request_secret` for API keys, `mcp__user-input__request_remote_mcp` for MCP. **Explain every access request before it fires**: one line per service in chat saying what will be read and what that unlocks, and a `reason` field naming that concrete purpose ("Allow access to Slack to list channels and propose where drafts and digests go?"), never a generic "for setup". A permission dialog the operator cannot connect to a purpose reads as a grab. If the platform reports a connection already exists or is registered, use it; never re-issue the request. Then explore and drive the rest yourself: **never ask the operator for a fact the connected tool can report.** "What's programmed in Monaco today" is a query, not a question; read the mailboxes, volumes, schedules, warmup state, and whether an org-level ceiling exists, then present a findings summary with your recommendations for one confirmation. The operator can override anything, but the default is you driving best practice from what you found, not them dictating their own tool's settings from memory. If they decline every connection path, fall back to asking directly and say what stays manual until it is connected; a blank field still beats a plausible guess, because the governor audits against these numbers.
- **Exploration is strictly read-only.** During onboarding, never create, modify, enroll, or send anything in a connected tool. You are reading state to make recommendations, not operating yet. Read-only binds *discovery*, not direct instructions: when the operator explicitly asks you to create something (a Slack channel, a saved view), confirm the exact action once and do it rather than refusing in the name of exploration.
- Before moving past the stack section, do the `after` step from `interview.yaml` out loud: what their tools already own, which later sections collapse into confirmations, what this template adds around their stack, and your recommendation, all grounded in what you actually read from the connections.
- Then declare the mode and run the rest of the interview in it:
  - **TEMPLATE-EXECUTED**: a bare mailbox (Gmail, Outlook) sends. This template is the only thing enforcing caps, windows, ramps, and cadence, so every senders/cadence question gets asked in full.
  - **SEQUENCER-EXECUTED**: their tool (Instantly, Smartlead, or similar) owns mailboxes, warmup, schedules, and sequence execution. Do not interrogate them about mechanics their tool enforces; read what is *already programmed there* through the connection and confirm the summary, asking directly only for what the API cannot report. The governor still needs true per-mailbox volume either way, because per-campaign rates stack and most sequencers have no org-level cap. The template's role shifts to what the sequencer does not do: qualification, suppression, drafting in the operator's voice, the do-not-touch gate, and meeting-sourced reporting.

**Conducting it.** This interview is long because it takes over an entire prospecting motion, and the answers are the difference between outbound that gets replies and outbound that gets marked as spam. Make that worth the operator's time:

- **Open by showing the route, not just the destination.** Before the first question: the section list in order, one phrase each; which sections need their answers and which you research and they only confirm; and what exists at the end (a validated config, a self-test, live examples they judge, and an executed first dry run). Say roughly how long the whole thing takes, and that **every question has a documented default**, so "I don't know" or "default it" is always an acceptable answer and never stalls the interview. People come along willingly when they can see the path.
- **Say why before each section**, one sentence, tied to their outcome, not the config. Each section in `interview.yaml` carries a `why` line for exactly this. "Voice samples are the difference between email that sounds like you and email that sounds like AI" works. "Now I need to populate the voice block" does not.
- **Mark progress at natural breaks** ("section 4 of 12; that was the longest one, two short ones left"), so the end is always visible.
- **Checkpoint the operator's energy about every 15 minutes.** Track elapsed time mechanically (`date +%s` at Step 0, compare at section boundaries), not by feel. At the nearest section boundary past the mark, give a one-line progress readout with a real ETA for what remains, then ask via `AskUserQuestion`: keep going now, or pause and resume later. If they pause: write every answer so far to `data/onboarding.partial.json` with a `resume_at` section id, say exactly what remains and how long it takes, and offer to schedule a resume reminder (`mcp__user-input__schedule_task`). The goal is a motion that reaches "it runs" without burning the operator out; a clean pause beats a rushed second half.
- **Guide, then yield.** You drive: propose the next step, the recommended answer, the researched draft. The operator overrides: any redirect wins immediately and without argument, and you say what changes downstream as a result. Driving without yielding is railroading; yielding without driving is a questionnaire.
- **Never praise answers.** No "great answer", "love it", "perfect". Stakes create engagement; cheerleading erodes trust in everything else you say. If an answer is genuinely consequential, say what it unlocks: "that booking link means replies can turn into meetings with zero back-and-forth."

#### Section conduct notes

**Identity.** Pre-fill before asking, per the `prefill` directive in `interview.yaml`: `CONNECTED_ACCOUNTS` gives the operator's email; a connected Gmail's `settings/sendAs` gives display name and their existing signature; a connected Calendar's settings give the timezone; the email domain gives the company site; a web search gives their title. If nothing is connected when the section starts, the first answers are the research seeds: a company name alone is enough to find the website, verify it names the company, and propose it. Never ask for a website you could have searched for. Open the section with one confirm-or-correct proposal and ask only what research left blank. Carry two harvests forward: the existing signature pre-answers the signature question in message standards, and the website read means you arrive at positioning with drafts for them to react to. The one question research cannot answer, so always ask it: *is there a name you must NOT use publicly yet?* Retired brands, internal codenames, and pre-launch product names go in `company.forbidden_names`, and the linter will hard-fail any draft containing them. If the brand is not public yet, set `company.brand_public_from` and the drafting layer falls back to the legal entity automatically.

**Current stack.** These are questions about *their* stack, not a tour of what ships with the template. Options come from `adapters/catalog.yaml`, ordered by how often real teams answer with them, `builtin: true` marking what works out of the box. Phrase options by vendor ("Apollo", "Clay"), never by module status ("installed", "ready"). Then, per answer:
- **Builtin exists**: set the slot. If it needs a credential, request it with `mcp__user-input__request_secret` or note it as pending.
- **No builtin** (Outlook, Instantly, Attio, Calendly, anything via Other): scaffold it immediately so the config names their real stack:
  ```bash
  uv run --with pyyaml .claude/skills/agent-onboarding/scripts/scaffold_adapter.py \
    --slot sender --name outlook --env GRAPH_TOKEN
  ```
  The stub satisfies the contract and fails closed on every call until implemented. Say plainly: the slot is configured for their vendor and selftest reports it as scaffolded rather than ready. **If the connect step already produced a working credential, implementing the adapter is part of this onboarding, not a follow-up**: say it is next, give a time estimate, and implement unless the operator explicitly defers. Most slots are two or three small functions, and a scaffold in the first-run path means the motion cannot run, which is the difference between "onboarded" and "a config file". If the API surface is large, scaffold with the discovered endpoints and env names noted in the stub so the implementation starts warm, and tell the operator what stays broken until it lands.
- **They use nothing for a capability**: set the slot to `none` and say what that leaves invisible (no calendar means meetings are only counted when a reply mentions one; no notify means every alert is silent). A visible gap beats a guessed vendor.

The calendar question is part of this section because meetings booked is the outcome metric. State the limit out loud so it is not discovered later in a board deck: a calendar proves a meeting was **scheduled and not cancelled**. It cannot prove anyone attended. "Held" in this system means exactly that, and no-shows have to be marked by a human.

**The sender slot still starts as `dryrun` no matter what they answered.** Record their real sender by scaffolding or selecting it now, but do not make it live: the team walks a full batch through the motion and reads the output before a single real email leaves.

**Senders and caps.** In template-executed mode, push back if the operator proposes more than 25/day/mailbox on a primary domain: that is the ceiling that keeps domain reputation intact at low volume, and higher numbers need a dedicated sending domain plus a warmup provider, not a bigger config value. New mailboxes get a `ramp` block; opening a cold mailbox at full volume is the fastest route to the spam folder. In sequencer-executed mode, skip the mechanics questions and record what the tool already enforces; the governor still audits the totals.

**Ask every sender for their booking link**, whichever mode. It goes in `calendar_link` on that sender, and it is the CTA that turns a reply into a meeting without a scheduling round trip. One per sender, never one for the team: a link that books time on someone else's calendar is worse than no link, because the prospect finds out only after committing.

**ICP.** The longest section, and the deliberate exception to research-propose-confirm: **asked, never hypothesized** (operator decision). Do not pre-fill it from the website, do not recommend answers from what you inferred about their business. The section is structured as specific multiple-choice questions (size, geos, industry focus and whether it is exclusive, industries to never include, buyer function, buyer map, signals, disqualifiers, segments) precisely so asking stays fast without inference. Your judgment shows up afterward: assemble `icp.tiers` from their answers and read the assembled result back before writing it. At sub-200-employee companies the champion often replies faster than the CEO, because they own the workflow and have a quieter inbox.

**Positioning.** If the identity pre-fill read the company site, arrive here with proposed drafts for the wedge, pain, and not-a list and let the operator correct them; react-to-a-draft is faster and produces sharper answers than compose-from-scratch. Their corrections are the signal, so never treat an unedited proposal as validated: read it back. After the questions, seed `positioning/use-cases.json` with their real use cases. The drafting step reads this file to pick a concrete, role-relevant workflow per prospect; with an empty file every opener collapses into generic praise. Hold them to a single number on the proof metric, never a range.

**Cadence.** In sequencer-executed mode the sequence lives in their tool: record what is programmed there and confirm it stops on reply. In template-executed mode, the choice question covers the common shapes; LinkedIn steps are manual (the agent drafts, a human sends, `send.py --manual` records).

**Message standards.** Most defaults are good. The one to confirm explicitly is the CTA: a self-serve link converts better than a meeting ask for products people can try alone.

**Suppression.** `fail_closed: true` is stated, not asked. If the suppression source is unreachable the run must halt, not proceed. Emailing a current customer as a cold prospect is a worse outcome than a delayed batch. If a CRM is connected, read its actual stages read-only and propose the suppress mapping in their own vocabulary; the generic multi-select is the no-CRM fallback.

**Escalation.** Two separate questions, and operators routinely conflate them: where routine output goes (a channel) versus who gets interrupted (a person). If Slack is connected, list its channels read-only and propose the likeliest destination by name; propose the operator as the escalation contact. Keep the trigger list short; the recommended defaults are all pre-marked in `interview.yaml`. If `adapters.notify` is `none`, say so plainly: the agent has no way to reach them and every notification will be silent.

**Voice.** The single highest-leverage section and the easiest to skip. One to three real emails into `positioning/voice-samples.md`. With the mailbox connected, offer to harvest candidates from their sent mail so they choose instead of digging; this is the one research move that touches personal content, so the consent boundary from the operating model applies at full strength: ask first, read only after an explicit yes, show candidates, write only what they selected. The linter enforces mechanics; it cannot enforce voice, and copy drafted without samples reads like copy. Their never-want-to-see answers go in `voice.banned_phrases` and become hard linter errors.

**Do not touch.** Keep the three gates straight for them, because they will merge them: **ICP** says *not a fit*, **suppression** says *already engaged*, **do not touch** says *never, and fit is irrelevant*. Ask it concretely with names research surfaced (customers from the CRM, investors and partners from the site): real names get real answers, and the abstract version gets "no, nothing" from people who absolutely have exclusions. Capture a reason for every entry. An empty list is a legitimate answer, but ask twice before accepting it.

**First run.** Whatever they choose, it is a dry run, it is small, and a human reads the output. `require_operator_review` stays true.

### Step 2: write and validate

```bash
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/init_workspace.py \
  --answers /tmp/answers.json                 # writes config/, CLAUDE.md, data/, positioning stubs
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/validate_config.py config/outbound.yaml
```

The answers file is a **partial config**: any subset of the schema in `config/outbound.example.yaml`, same nesting, same keys. `init_workspace.py` deep-merges it over the documented example, so unanswered fields keep their commented defaults rather than vanishing. It never overwrites an existing `config/outbound.yaml` without `--force`.

Fix every ERROR before continuing. WARNs are judgement calls: relay them to the operator with your recommendation rather than silently accepting them.

### Step 3: self-test

```bash
uv run --with pyyaml .claude/skills/agent-onboarding/scripts/selftest.py
```

Walks fixture prospects through the entire motion with the dry-run sender: config load, adapter resolution, ICP qualification, suppression, cap enforcement, drafting, linting, logging. Sends nothing. If this passes, the wiring is correct and only the *content* remains to be judged.

### Step 4: calibrate on live examples

The `calibration` section of `interview.yaml` runs here, after the config exists, because it needs the assembled ICP, the real positioning and voice files, and the linter. Three artifacts, one at a time, each judged through `AskUserQuestion`: a real company the ICP qualifies, the contact the buyer map leads with there, and a linted Day-0 opener for that contact. All read-only; nothing is created, enrolled, or sent.

This is where fourteen structured answers meet reality. A "not a fit" verdict is config signal: name the answer that produced the miss, change it, re-validate, and re-run that artifact with a fresh example. Do not skip this step because the interview "went well"; the operator judging three concrete artifacts catches what no amount of question-answering can.

### Step 5: stand up the dashboard, prove the first run, hand off

**Build the live dashboard first, automatically; it is not a question.** A motion with approval gates needs a place to approve, and the operator should watch the first run land where they will keep watching. The template ships the app; the platform hosts it:

1. `mcp__dashboards__create_dashboard` with slug `outbound`, framework `plain`, named for their motion.
2. Replace the scaffold with the shipped app: copy `dashboard/index.js` and `dashboard/package.json` into `/workspace/artifacts/outbound/`.
3. `mcp__dashboards__start_dashboard` and check the returned screenshot: the approval queue panel and the deliverability strip must render. Empty states are fine; the Demo toggle shows a populated preview.
4. Bookmark the URL in `/workspace/bookmarks.json` and tell the operator what lives there: **pending drafts with Approve and Reject buttons** (decisions land in the same table and audit log as chat approvals), deliverability health, and outcome metrics. `report.py --write-dashboard` refreshes the numbers on every tick.

If the dashboard tooling is unavailable in this runtime, fall back to `bun run dashboard/index.js`, give the local URL, and say why.

**The hand-off criterion is an executed first run.** Run the first-run goal chosen in the interview (dry run; it sends nothing), stage its drafts in the approval queue, and show the operator the output in the dashboard they just got. If any adapter in its path is still a scaffold, onboarding is not complete: with a working credential, implement it now (see the stack notes); without one, get an explicit operator decision to stop here and say plainly what cannot run until it is connected. Never present onboarding as complete while the printed next command is known to fail; "complete" means the operator watched drafts come out.

Then tell the operator, concretely:
1. What you configured, and anything you defaulted because they did not know.
2. Which adapter slots are `none`, `dryrun`, or scaffolded, and what each of those means they cannot yet do. A scaffolded slot names their real vendor but fails closed until implemented; list what implementing each one needs.
3. The exact next command to draft their first batch, and the dashboard URL where its drafts will wait for their approval.
4. That the first batch requires their approval before any send, and that this gate cannot be disabled. Approving in the dashboard and approving in chat are the same decision in the same audit log.
5. **Offer to schedule the operating loop.** A configured motion with no heartbeat is a manual process with extra steps. Using the platform scheduler (`mcp__user-input__schedule_task`), in the operator's timezone, offer:
   - the **cadence tick** each send-day morning just before the window opens (`reporting.schedule.cadence_tick_cron`): processes due follow-ups, checks replies, surfaces the manual LinkedIn queue
   - the **weekly report** (`reporting.schedule.weekly_report_cron`, default Friday afternoon): syncs meetings from the calendar, then sends the digest to the routine-output destination
   Confirm both times with the operator instead of assuming the config defaults. The tick sends nothing on its own, so it is safe to schedule before the first batch is approved; actual sends still pass through `send.py` and every gate.

## Guardrails

- Never set a live sender during onboarding. `dryrun` until the operator has read real output and approved.
- Never declare onboarding complete while the first-run command is known to fail. A scaffolded slot with a working credential is remaining work, not a caveat for the summary.
- Exploration of connected tools during onboarding is read-only. Never create, modify, enroll, or send anything through a connection made for discovery. An explicit operator instruction to create something is not discovery: confirm the exact action once and do it.
- Never re-request a connection or MCP server the platform reports as already registered.
- Never write a secret into `config/outbound.yaml`. The config stores the environment variable NAME; the value stays in `.env`. If a needed secret is missing, request it with `mcp__user-input__request_secret`.
- Never copy another team's ICP, positioning, or use cases as a starting point. An inherited ICP reads plausible and produces confidently wrong targeting. Empty and honest beats populated and wrong.
- If the operator asks to disable `stop_on_reply`, `suppression.fail_closed`, or the first-batch approval gate, refuse and explain the specific failure each one prevents. `validate_config.py` enforces these independently, so a hand-edited config will fail too.
- Re-run `validate_config.py` after any hand edit.
