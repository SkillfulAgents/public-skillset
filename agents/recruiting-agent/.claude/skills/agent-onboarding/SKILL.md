---
name: Agent Onboarding
description: First-run onboarding interview for a NEW company adopting this recruiting-agent template. Walks the customer through everything that must be configured — ATS (or not) + system of record, where sourced candidates are saved (workspace / Google Sheet registry / Excel), role import (all vs manual clickbox select), which roles get a daily search cron, per-role screening criteria (agent proposes, user edits), outreach voice/templates/authorization, calendar booking link, LinkedIn access, recurring triggers, dashboard, chat integration, escalation. Run when a new customer says "set up", "onboard", "get started", or when the workspace has no configured roles/CLAUDE.md pipeline config.
metadata:
  version: "1.1.0"
---

# Agent Onboarding — turn the template into THEIR recruiting agent

This skill runs the guided setup for a company adopting this recruiting agent. It is an **interview + scaffolding procedure**: ask, then immediately build. At the end the agent is live — roles configured, screening prompts written, triggers scheduled, CLAUDE.md rewritten for the customer.

**HOW TO RUN THE INTERVIEW (read this first — it's where fresh agents fail):**
- **Your first reply IS the interview.** Two sentences of welcome max, then the Phase 1 questions in that same turn. Do NOT summarize the onboarding process, list the phases, offer a menu, or ask permission to start. The user's first message — whatever it says — is the start signal.
- **Every choice goes through the `AskUserQuestion` tool** so the user gets clickable options, not a wall of text ending in "let me know". Plain chat questions ONLY for free-text facts (product pitch, JD contents, pasted messages). If a turn of yours ends without either an `AskUserQuestion` call or a specific free-text question, you've broken the interview.
- **One phase (or coherent question batch) per turn.** After the user answers: build that phase's artifacts immediately and silently, give a one-line "done" note, and ask the next batch in the same turn. Momentum over ceremony.
- Do not stop until Phase 8's summary — the only valid endings mid-way are the user explicitly deferring, or a blocked external dependency (missing API key etc.), and then you say exactly what's pending.

**Principles**
- **Propose, don't quiz.** Wherever the agent can draft a strong default (screening rubric from a JD, outreach template from the product pitch, trigger times), PROPOSE it and ask the user to confirm/edit. Only ask open questions for facts that cannot be inferred (comp band, panel, API keys).
- **Clickboxes over free text.** Use `AskUserQuestion` for every choice (single or multiSelect). Free text only for descriptions, pitches, and JDs. Users can always pick "Other".
- **Build as you go.** After each phase, write the artifacts for that phase before moving on. If the session dies, setup resumes from the state file.
- **Resumable.** Track progress in `/workspace/pipeline/onboarding-state.json`: `{ "phase": <n>, "answers": {...}, "completed": [...] }`. On invocation, read it first; skip completed phases; confirm stale answers only if they'd now change.
- **This template ships with Gamut's own config as an example.** On a fresh customer instance, Phase 0 clears it. Never run the clearing step on the Gamut/Datawizz origin workspace.

---

## Phase 0 — Preflight

1. Read `/workspace/pipeline/onboarding-state.json` (resume if mid-onboarding).
2. Detect leftover template-owner data: `grep -l "Gamut\|Datawizz\|Tim" /workspace/CLAUDE.md /workspace/pipeline/roles.json` and check for populated `longlist-*.jsonl` / memory role files. If present AND this is a new customer instance, tell the user you'll archive the example data to `/workspace/pipeline/_template-example/` (move, never delete) and start clean. Ask before archiving.
3. Scaffold empty dirs if missing: `/workspace/pipeline/{screening,outreach,shortlists,reports}`.

## Phase 1 — Company & hiring lead

Both intro questions are `AskUserQuestion` clickboxes offering **URL vs describe** — always prefer researching a URL over making the user type:

- **Company** — header "Company": **"How should the agent learn about your company?"**
  - "Share a URL (Recommended)" — description: paste your website (or LinkedIn/Crunchbase page) and the agent researches the rest. On answer: fetch the site + web-search the company, then draft the one-line product pitch AND the **founder/credibility claims bank** (founder background, notable backers, traction proof, stage — this becomes `_company-voice.md` in Phase 6) and play it back for correction in one message.
  - "Describe it yourself" — free-text follow-up: name, what you build, one-line pitch, founder cred, backers, traction, stage.
- **Hiring lead** (the person the agent works for and sends outreach as) — header "Hiring lead": **"Who does the agent work for?"**
  - "Share their LinkedIn (Recommended)" — paste the profile URL; the agent pulls name, role, and background from it (background feeds outreach attribution), then confirms.
  - "Describe them yourself" — free-text follow-up: name, role, 1-line background.
  - Whichever path: confirm this is the identity all outreach is sent as.
- Then free-form (one message): office location + in-office policy (remote / hybrid / N days — becomes the default geo constraint in every screening prompt) and timezone (drives all trigger schedules). Skip anything already learned from the URL research — confirm instead of re-asking.

Clickbox (`AskUserQuestion`):
- **Autonomy model** — header "Autonomy": (a) "Advance-gated (Recommended)" — agent sources + shortlists autonomously, but a candidate is only contacted after the hiring lead clicks Advance; (b) "Fully autonomous" — agent also sends outreach to its own shortlist without per-candidate approval; (c) "Review everything" — agent proposes, human approves each step. Record the choice; it parameterizes Phases 6 and 8. Default strongly to (a) and say why (calibration first, autonomy earned as agreement % rises).

## Phase 2 — ATS / system of record

Clickbox Q1 — header "ATS": **"Do you use an ATS (applicant tracking system)?"**
- Options: "Yes — Ashby", "Yes — Greenhouse", "Yes — Lever", "No ATS". ("Other" is auto-provided — if picked, ask which and check whether it has an API.)

### Branch A — has an ATS
1. `request_secret` for the API key (`ASHBY_API_KEY` / `GREENHOUSE_API_KEY` / `LEVER_API_KEY` / `<ATS>_API_KEY`). Reason format: "Add <NAME> so the agent can read open roles and manage the candidate pipeline?"
2. Verify the key with a lightweight read (list jobs). If it fails, show the error and re-request.
3. **Ashby:** reuse the existing `ashby` skill as-is. **Greenhouse/Lever/Other:** create a new skill `/workspace/.claude/skills/<ats>-ats/` exposing the same operations the pipeline needs (list jobs, search candidates, create candidate+application, add note, change stage, list interviews) and map the customer's stage names to the pipeline stages (Sourced → Shortlisted → Contacted/Reached Out → Replied → In conversation → Interview scheduled). Save the stage mapping in the skill's SKILL.md.
4. Survey their ATS conventions (stage names, sources, tags) and write `reference-<ats>-conventions.md` to memory.
5. → Phase 3A. The ATS is the **system of record**; skip the system-of-record question.

### Branch B — no ATS
1. Ask (free-form): **"What roles are you hiring for, and what's the description of each?"** Accept pasted JDs, links, or uploaded files (`request_file` if they mention having JD docs). One role at a time is fine; loop until they say that's all.
2. Clickbox — header "Records": **"Where should the candidate pipeline of record live?"**
   - "Agent database (Recommended)" — local structured store the agent owns (`/workspace/pipeline/atsless/` — see below); dashboard renders it; zero external setup.
   - "Google Sheet" — one spreadsheet, one tab per role; needs a Google connection (`request_connected_account`, toolkit `googlesheets`).
   - "Excel file" — `/workspace/pipeline/pipeline.xlsx`, delivered via `deliver_file` on every update.
   Recommend the agent database: same columns as an ATS export whenever they want out, no sync lag, no API quota.
3. **Agent database layout** (if chosen): `/workspace/pipeline/atsless/candidates.jsonl` — the schema is documented in `/workspace/artifacts/recruiting-pipeline/ATSLESS.md` (the dashboard reads this store natively; follow that file exactly, including the outreach `channel`/`type` enums and optional `stage_history`). Every rule in CLAUDE.md that says "Ashby" applies to this store instead: it is the single source of truth, every outreach/stage change is logged there in the same session, and the dashboard renders ONLY it.
4. → Phase 3B.

### Both branches — where do SOURCED candidates live?

Sourced candidates (the longlist/shortlist pool, pre-outreach) never sit in the ATS — they enter the system of record only when the hiring lead clicks Advance. So ask where this pool should be saved. Clickbox — header "Sourced pool": **"Where should sourced candidates be saved before outreach?"**
- **"Agent workspace (Recommended)"** — per-role longlist files (`/workspace/pipeline/longlist-<slug>.jsonl`) the agent owns; the dashboard renders the pool; zero external setup; exportable any time.
- **"Google Sheet"** — a shared registry spreadsheet (`events` + `candidates` tabs) via the `sheets-registry` skill. Pick this to browse/edit the pool in Sheets, or if MORE THAN ONE person will run an install of this agent on the same pipeline (ownership + cross-install contact suppression). Setup: `request_connected_account` (toolkit `googlesheets`) → write `GSHEETS_ACCOUNT_ID` + derived `OWNER` to `.env` → `registry.py init` (creates the Sheet, writes `pipeline/registry.json`). Longlist files remain the local working cache: `registry.py reconcile` at session start, `push` at session end.
- **"Excel file"** — `/workspace/pipeline/sourced.xlsx`, regenerated from the longlists and delivered via `deliver_file` after each search session (browse-only convenience; workspace files stay authoritative).

Record the choice in onboarding-state; it flows into CLAUDE.md at Phase 8. (No-ATS + "Agent database" from the Records question above covers the pipeline of record; this question is about the pre-Advance pool and can differ.)

## Phase 3 — Roles

### 3A — import from ATS
1. List open jobs from the ATS. Filter out obviously internal/hidden ones (e.g. prefixed test jobs) but SHOW them as options anyway — the user decides.
2. Clickbox — header "Role import": **"Import all open roles from your ATS, or pick them manually?"** Options: "Take all N roles", "Select manually".
   - **This question is about VISIBILITY only** — which roles the agent knows about, screens inbound for, and shows on the dashboard. It is NOT about which roles get active sourcing; that is Phase 4, asked separately.
3. If "Select manually": present the job list as **multiSelect clickboxes** (`AskUserQuestion`, `multiSelect: true`). Options are capped at 4 per question and 4 questions per call → chunk the job list into groups of 4, up to 16 jobs per call, repeat calls until the whole list has been offered. Label each option with the job title; description = team/location from the ATS.
4. For each imported role: slugify the title, add to `/workspace/pipeline/roles.json` as `{ "<ats_job_id>": {"slug": "...", "sourcing": "inbound-only", "note": "imported at onboarding"} }` (sourcing flips in Phase 4).

### 3B — roles by hand (no ATS)
For each role from Phase 2B: slugify, add to `roles.json` with a generated id, save the JD text to `/workspace/pipeline/postings/<slug>.md`.

### Both branches — scaffold per role
Using the templates in this skill's `templates/` dir, create for EVERY imported/created role:
- `role-<slug>.md` in the auto-memory dir (+ MEMORY.md index line) — from `templates/role-file.md`, filled from the posting/JD. Leave `Outreach status: HELD` until Phase 6 decides.
- `/workspace/pipeline/screening/<slug>.md` — from `templates/screening-prompt.md`, DRAFTED by the agent from the JD (Phase 5 refines it with the user).
- `/workspace/pipeline/longlist-<slug>.jsonl` — empty.

## Phase 4 — Which roles get a daily search? (crons)

Not every visible role needs active sourcing — some are inbound-only, paused, or exploratory (in the template's origin config only 1 of 9 jobs had an active search).

1. Clickbox (multiSelect, chunked like 3A.3) — header "Daily search": **"Which of these roles should get a daily sourcing search?"** Every imported role is an option; preselect nothing; description per option = 1-line role summary.
2. For selected roles: set `"sourcing": "active"` in roles.json; unselected → `"inbound-only"` (ATS) or `"passive"` (no ATS).
3. Schedule triggers (`schedule_task`, cron, weekdays, user's timezone): **one search session per active role**, ~45 min each, staggered (9:00, 9:45, 10:30, …) so each owns the browser/LinkedIn exclusively. Prompt per trigger: run the full search workflow for `<slug>` per CLAUDE.md.
4. Tell the user each search costs roughly a 45-minute agent session per weekday per role — pick accordingly; roles can be flipped on/off any time by asking.

## Phase 5 — Screening criteria (detailed, propose-first)

For each role with an active search (do inbound-only roles too if the user has patience; otherwise offer to defer them):

1. **Propose first.** Show the user the drafted screening prompt as a short readable summary: hard checks, the 4 criteria (academic excellence / company quality / career trajectory / role fit), disqualifiers, and the seed-company list. The proposal should already encode the template's philosophy — filter on **clock speed and a history of crushing whatever they do**, not on years-of-X; hunt stamps of excellence (olympiads, selective shops, OSS, competitive fellowships, founders); recall over precision.
2. Then ask, per role (clickboxes where possible, free text for the rest):
   - Must-haves that are truly hard (geo/onsite from Phase 1 default — confirm; visa sponsorship yes/no; language; start-date).
   - Seniority band (years range or "band by evidence, not years").
   - Seed companies: propose 5–10 from the JD + company's space; ask the user to add/strike ("which companies' people would you hire on sight?").
   - Anti-patterns / disqualifiers beyond the base set (tenure <1yr, job-hopping): e.g. big-co-lifer, agency-only, active founder.
   - Comp band + equity philosophy (stored in role memory ONLY for answering candidate questions — never goes in outreach).
   - Interview process + panel (who takes the first call?).
3. Rewrite `/workspace/pipeline/screening/<slug>.md` and `role-<slug>.md` (rubric section) from the answers. The screening prompt IS the filter; keep the "calibration log" section at the bottom, empty but present.
4. Explain the calibration loop in one paragraph: every Advance/Reject verdict the user gives (dashboard click or chat) updates the rubric — the filter is self-improving, and lessons update both scoring AND sourcing queries.

## Phase 6 — Outreach: channels, voice, templates, authorization

1. **Channels** — clickbox (multiSelect), header "Channels": LinkedIn (Recommended — primary), Email, "None yet — build shortlists only".
   - LinkedIn: whose seat/identity? What tier (Sales Navigator / Recruiter / basic — affects search recipes and InMail budget)? First trigger session verifies the tier in-browser. Login happens in-browser via `request_browser_input` when first needed.
   - Email: `request_connected_account` (gmail/outlook). Note: template experience is that email response rates are poor — fallback only.
2. **Voice file** — create `/workspace/pipeline/outreach/_company-voice.md` from `templates/voice-file.md`, filled with Phase 1's claims bank. Ask the user to paste 1–2 outreach messages they (or their founder) have actually SENT that got replies — those calibrate tone and length better than any description. House defaults unless overridden: ~50–90 words, hook-first, name-swap-only personalization, no comp numbers in outreach, fixed A/B templates with variant logged for reply-rate comparison.
3. **Per-role templates** — draft `/workspace/pipeline/outreach/<slug>.md` (Variant A cred-stack, Variant B stealth/asymmetry — adapt skeleton names to the company's story) and show them for approval. Sent verbatim after approval; `{{first_name}}` is the only substitution.
4. **Authorization + cadence** — from Phase 1's autonomy model:
   - Advance-gated (default): shortlist → dashboard → user clicks Advance → candidate enters system of record → queued → **daily outreach batch** (pick a time, default 13:35 local, weekdays; `schedule_task`).
   - Fully autonomous: same batch, but the whole shortlist queues without clicks. Warn: run 2+ weeks Advance-gated first to calibrate.
   - Confirm cadence defaults: follow-up 1 at +4d, follow-up 2 at +10d, Unresponsive at ~+15d; channel order = free DM if available, else bare connection request (no note), full template on accept, InMail escalation at +4d unaccepted.
5. **Booking link** — ask for a self-serve scheduling link (Calendly / Google appointment page / SavvyCal) for the hiring lead. If they have none, walk them through creating one — it's the single highest-leverage config: the agent's job is to get candidates to click it. No calendar automation: bookings are confirmed from the conversation thread, never by watching the calendar.

## Phase 7 — Recurring machinery & surfaces

Schedule (all weekday, user's timezone, `schedule_task` cron) and record each task id in CLAUDE.md:
- **Role-sync** (ATS branch only, ~8:45): diff open ATS jobs vs roles.json; new job → scaffold role + ask user about search activation; closed job → cancel trigger, mark closed.
- **Inbound screening** (ATS branch only, ~8:15): rate every new applicant with the role's screening prompt; pull the resume before scoring; surface on dashboard; NEVER auto-reject (unless Phase 1 autonomy = fully autonomous AND the user explicitly opts in to auto-archive).
- **Per-role searches** — already scheduled in Phase 4.
- **Outreach batch** — already scheduled in Phase 6 (only if a send channel exists).
- **Reply sweep + nurture** — 2–4×/day off-slot (default 08:00/14:00/16:00/18:00) if LinkedIn outreach is on.
- **Weekly report** — Friday 16:00: per role sourced / sent / reply rate per variant / interviews scheduled / calibration changes / asks.
- **Dashboard** — the full recruiting-pipeline dashboard SHIPS with the template at `/workspace/artifacts/recruiting-pipeline/` (Bun server `index.js` + frontend `public/index.html`). **Do NOT rebuild it — keep the UI exactly as shipped; only the wiring changes:**
  - Role count is already dynamic (reads `pipeline/roles.json`) — nothing to do there.
  - **Ashby branch:** works out of the box — it reads `ASHBY_API_KEY` from `/workspace/.env` and renders pipeline state from Ashby notes/stages. **No-ATS branch (agent database): also built in** — write `pipeline/datasource.json` with `{"mode": "atsless"}` and the dashboard reads `pipeline/atsless/candidates.jsonl` natively (schema + details: `artifacts/recruiting-pipeline/ATSLESS.md`); no code changes. **Other-ATS branch only:** delegate to the dashboard-builder agent to swap ONLY the Ashby data-access functions in `index.js` for the customer's ATS adapter, keeping every endpoint shape, tab, and rendering identical (the atsless adapter block is the pattern to copy).
  - **The UI's system-of-record label is dynamic** (payload field `sorName`): it reads `displayName` from `pipeline/datasource.json` — absent file = "Ashby", `mode: "atsless"` = "Pipeline". On the other-ATS branch set `{"displayName": "Greenhouse"}` (etc.) so the badge/banners/empty-states name the customer's ATS; never hand-edit the strings.
  - Replace the hardcoded `America/Los_Angeles` timezone strings in `index.js`/`public/index.html` with the customer's timezone (Phase 1).
  - Create the feedback webhook (`create_webhook_endpoint`, prompt = run the `calibration-feedback` skill) and write `pipeline/.feedback-webhook.json` with the URL + HMAC secret — the Advance/Don't-advance buttons ping it.
  - `start_dashboard`, click through every tab in the container browser, and verify the feedback buttons append to `pipeline/feedback-queue.jsonl`.
- **Chat integration** — clickbox: Slack / Telegram / iMessage / none. If chosen, set up via `mcp__chat__add_chat_integration`; used for time-sensitive flags (candidate wants to talk, platform logged out) and the weekly report link.

## Phase 8 — Finalize

1. **Rewrite `/workspace/CLAUDE.md`** for this customer: keep the template's operating rules (pipeline stages, write discipline, recall-over-precision calibration loop, honesty, scope-ends-at-booked-interview) but substitute their company, hiring lead, ATS/system of record, sourced-pool storage choice, autonomy model, channels, booking link, timezone, trigger table, and role list. Strip every Gamut/Datawizz-specific fact.
2. **Fill placeholders:** sweep `/workspace/CLAUDE.md` and `/workspace/.claude/skills/` for `{{...}}` tokens shipped by the template bundle (`{{COMPANY}}`, `{{BOOKING_LINK}}`, `{{AGENT_SOURCED_TAG_ID}}`, `{{FOUNDER}}`, trigger times, etc.) and replace them with onboarding answers. `{{AGENT_SOURCED_TAG_ID}}`: on the Ashby branch, create (or find) an `agent-sourced` candidate tag and substitute its id.
3. Seed memory: `user-<name>.md` (hiring lead profile), `project-<company>-context.md`, `reference-<ats>-conventions.md`, per-role files already exist. Index everything in MEMORY.md.
4. Delete `/workspace/pipeline/onboarding-state.json`.
5. **Summary message** to the user: table of roles (visible / searching daily / outreach status), the trigger schedule, what happens tomorrow morning, and the 3 things they should do first (e.g. connect LinkedIn in the first search session, click Advance on the first shortlist, give feedback on anything that looks wrong — the agent calibrates from it).

---

## Question phrasing rules

- All `AskUserQuestion` headers ≤12 chars; make the recommended option first and suffix "(Recommended)".
- Ask AT MOST 4 questions per call; group related ones.
- Never ask something inferable from the JD, the website, or an earlier answer. Every question should change what gets built.
- If the user skips/defers a question, record `"deferred"` in onboarding-state.json and move on — flag deferred items in the Phase 8 summary.

## Files this skill creates

| Artifact | Path |
|---|---|
| Onboarding state (resumable) | `/workspace/pipeline/onboarding-state.json` |
| Roles registry | `/workspace/pipeline/roles.json` |
| Role memory (per role) | memory dir `role-<slug>.md` + MEMORY.md line |
| Screening prompt (per role) | `/workspace/pipeline/screening/<slug>.md` |
| Outreach templates (per role) | `/workspace/pipeline/outreach/<slug>.md` |
| Voice / claims bank | `/workspace/pipeline/outreach/_<company>-voice.md` |
| No-ATS pipeline store | `/workspace/pipeline/atsless/candidates.jsonl` |
| Non-Ashby ATS adapter | `/workspace/.claude/skills/<ats>-ats/` |
| Rewritten agent manual | `/workspace/CLAUDE.md` |
