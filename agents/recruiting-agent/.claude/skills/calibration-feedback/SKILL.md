---
name: Calibration Feedback Ingestion
description: Process the hiring lead's Advance/Don't-advance verdicts submitted from the recruiting dashboard — ingest each into calibration + screening prompts (the self-improving filter) and execute the candidate action in Ashby/pipeline files + the shared Google Sheets registry (ownership via first-advanced-wins, queued events). Run when the feedback webhook fires or whenever the queue has pending events.
metadata:
  version: "1.1.0"
---

# Calibration Feedback Ingestion

the hiring lead reviews candidates on the recruiting dashboard and clicks **Advance** / **Don't advance**, optionally with a short note. Each click lands as an event in the queue. This skill turns those clicks into (a) calibration that tightens the filter and (b) the actual pipeline action. Goal: the agent's judgment converges on the hiring lead's.

## Files

| File | Writer | Purpose |
|---|---|---|
| `/workspace/pipeline/feedback-queue.jsonl` | dashboard server (append-only, never rewrite) | raw click events |
| `/workspace/pipeline/feedback-processed.jsonl` | this skill via `queue.py mark` (append-only) | handled markers |
| `/workspace/pipeline/.feedback-webhook.json` | agent | webhook URL + HMAC secret the dashboard pings (server-side only, never expose) |
| `/workspace/pipeline/calibration.jsonl` | ingestion | one line per verdict (see schema below) |
| Shared registry (Google Sheet, `sheets-registry` skill) | ingestion | `advanced`/`rejected`/`queued` events + ownership — the cross-install truth (the hiring lead + a teammate) |

Webhook: "Dashboard feedback ingestion (calibration + actions)", trigger `00d74432-5278-40b1-899f-16cb7f07df58` — fires an ingestion session ~90s after the hiring lead's last click in a burst.

## Queue commands

```bash
uv run /workspace/.claude/skills/calibration-feedback/queue.py stats   # {"pending": N, ...}
uv run /workspace/.claude/skills/calibration-feedback/queue.py list   # pending, latest click per candidate
uv run /workspace/.claude/skills/calibration-feedback/queue.py mark <id> [--status processed|error|superseded|skipped] --result "one line"
```

`list` collapses to the latest click per candidate (the hiring lead may change his mind); it prints any `_superseded_ids` — mark those `--status superseded` first. Events with `"test": true` → mark `--status skipped`, no other action.

## Event schema (written by the dashboard)

```json
{"id": "fb_...", "ts": "...", "source": "sourced|inbound",
 "role_key": "<ashby job id>", "role_slug": "founding-engineer-fs", "role_title": "...", "job_id": "...",
 "tim_action": "advance|reject", "feedback": "the hiring lead's note ('' if none)", "override": true,
 "candidate": {"name": "...", "id": "in/…(longlist id, sourced)", "linkedin_url": "...",
                "candidate_id": "…(ashby, inbound)", "application_id": "…(ashby, inbound)", "email": "..."},
 "agent_rec": "shortlisted|scored|rejected-disqualifier|Advance|Reject|Basic review", "agent_score": 74}
```

Agent stance was "advance" iff `agent_rec == "shortlisted"` (sourced) or `agent_rec == "Advance"` (inbound). `agree = (tim_action == "advance") == agent_stance_advance`. Trust the event's `override` but recompute if fields look inconsistent.

## Ingestion procedure — per event, in order

1. **Context**: read `role-<slug>.md` (auto-memory dir) and `/workspace/pipeline/screening/<slug>.md`.
2. **Calibration line** → append to `/workspace/pipeline/calibration.jsonl`:
   `{"date", "role", "candidate", "agent_rec", "agent_score", "tim_verdict": "<action>: <feedback or (no note)>", "agree", "lesson", "source_event": "<id>"}`
   `lesson` = the distilled, generalizable takeaway (null when it's pure agreement with nothing new).
3. **Role calibration log** (`role-<slug>.md`): dated bullet — who, the hiring lead's verdict + note, what changed in the filter because of it.
4. **Filter update** — this is the self-improving part. If the lesson generalizes beyond this one candidate, edit the screening prompt: smallest change that captures it (tighten/loosen a rubric sub-bullet, add/remove a disqualifier, add a positive stamp the rubric was blind to). Note the edit in the calibration log. Re-score only this candidate now; the role's next daily session re-scores broadly with the updated prompt. If the hiring lead's note conflicts with an earlier lesson, flag the tension in the summary instead of silently flip-flopping.
   **BOTH instruments (the hiring lead, 2026-07-24):** if the lesson implicates the search-time pool (archetype, seniority band, geo, movability, title patterns), ALSO edit the role file's "Sourcing queries" section / recipe parameterization so search stops harvesting the wrong pool — scoring-only ingestion is a half-ingestion. Pool-definition changes additionally queue a case-by-case re-cut of the existing shortlist (note it in the calibration log for the role's next daily session, or run it if the queue is small).
   **The re-cut runs over already-SCORED records too, not just the shortlist (Nate Sesti override, 2026-07-27).** A lesson that widens an inclusion rule invalidates past exclusions: the Jarred Sumner rule ("world-class OSS-creator stamp + recent hands-on build = shortlist as stretch, low movability is a reservation not a demotion") was written on 2026-07-24 and applied only to new scoring, so Sesti — the same shape, already sitting at `scored` — stayed off the list until the hiring lead caught it by hand. When an inclusion rule loosens, sweep every record the OLD rule pushed down (`status: scored`/`rejected-score`, and the flags the rule turns on), not only the current shortlist and future harvests.
5. **Candidate action** (use the `ashby` skill; house write-discipline applies):
   - **sourced × advance** — the hiring lead's click is the per-candidate approval to REACH OUT (the hiring lead, 2026-07-22): it overrides a role-level Outreach HOLD for this person only. In order:
     1. *Cross-role check*: `longlist.py crossrole <linkedin_url>` (linkedin-sourcing skill). Locked (`shortlisted`+ or beyond) in ANOTHER role → take NO action, mark `--result "crossrole-conflict"`, flag at the top of the summary with both roles' scores ("reply 'move <name> to <role>' to switch"). One active role per person.
     1b. *Cross-OWNER check (shared registry, 2026-08-06)*: `registry.py check <key> --role <slug>` (sheets-registry skill). Exit 2 = already owned by another OWNER (e.g. a teammate advanced them first) → take NO action, mark `--result "owned-by-<owner>"`, flag in the summary. Exit 3 = already contacted by any owner → no new initial; flag. Exit 0 → **append the `advanced` event NOW** (`registry.py event '{"candidate_key":"in/…","role":"<slug>","action":"advanced","payload":{"score":N,"source_event":"<id>"}}'`) — first `advanced` row in the Sheet wins ownership; then re-run `check` and confirm `owner == OWNER` before any Ashby write. If another actor's row landed first, back off (no Ashby create, no queue), mark + flag.
     2. Longlist line: `status` → `"shortlisted"`, add `tim_action`, `tim_feedback`, `tim_action_date`.
     3. Ashby: `candidate.search` first (name + LinkedIn URL). **REVISED (the hiring lead, 2026-07-24 — Erica Wu wrong-skip lesson): an Advance is authoritative; a bare Ashby record never blocks the send it authorized.**
        - No record → create candidate + application on the role's job (stage `New Lead`, source `LinkedIn`), then **ALWAYS `candidate.addTag` with tag `agent-sourced` (tagId `{{AGENT_SOURCED_TAG_ID}}`) — `candidate.create` does NOT accept tags; skipping this step caused the 2026-07-24 Erica Wu false-suppression** — **with everything we know**: name, LinkedIn URL as a social link, current title/company/location on the record where fields exist, plus a note carrying the full picture — headline, score, evidence/reasoning, source (mode/recipe/query/date), flags, and "Advanced by the hiring lead via dashboard (<date>): <feedback>".
        - Agent-created record exists (`agent-sourced` tag — the whole pre-2026-07-24 batch of 151 un-advanced New Leads was back-tagged and KEPT in place, the hiring lead 2026-07-24) → reuse the candidate + its existing New Lead application and add the Advance note (create a fresh application only if none exists). Never create a duplicate candidate. **Leave the stage at `New Lead`** — the move to `Reached Out` belongs to the 13:35 batch after a verified send (step 4 below); moving it here would record a contact that has not happened.
        - Pre-existing NON-agent record with **zero contact history** → adopt it: add the Advance note to it and proceed to the send (this was the Erica Wu case; the old suppression-conflict skip is retired). Should be rare now that the search session filters already-in-Ashby people off the list. **Adopt bookkeeping (2026-07-29):** add the `agent-sourced` tag (tagId `{{AGENT_SOURCED_TAG_ID}}`), and if the adopted APPLICATION was created before 2026-07-01, append a pointer `{applicationId, candidateId, jobId, name}` to `/workspace/pipeline/ashby-adopted-apps.json` — the dashboard's Jul-1 cutoff hides old bulk apps and this registry keeps adopted ones on the Leads board (pointers only; all displayed state reads live from Ashby).
        - Pre-existing non-agent record showing **actual prior contact** → do NOT send; mark `--result "prior-contact-conflict"`, flag with the history so the hiring lead can decide. **"Actual prior contact" is a real test, not the existence of a record (Eric Zhang override, the hiring lead 2026-07-27):** it means a human-authored note, a stage past `Reached Out`, a reply, or an interview. A record sitting at `New Lead`/`Reached Out` with zero human notes and no reply is a *bulk-touch marker stamped at creation time* — the hiring lead's words: "we were never really in conversation with him so let us reach out again." That is a **bare touch**: adopt the record (note + proceed to queue the send) exactly like the zero-contact case above. `ashby_crosscheck.py` returns `stale-touch-review` for these and `suppressed-ashby` only for real contact; the agent's own notes never count as contact.
     4. **Queue the outreach — do NOT send here (the hiring lead, 2026-07-24, batched sends).** Ingestion never sends inline and never schedules a per-candidate send task. Append a `queued` event to the **shared registry** (`registry.py event '{"candidate_key":"in/…","role":"<slug>","action":"queued","payload":{"channel":"linkedin","type":"initial","variant":"A|B","by":"<session>","source_event":"<id>","reason":"the hiring lead-advanced <date>","name":"…","linkedin_url":"…","ashby_candidate_id":"…"}}'` — `outreach-log.jsonl` is retired legacy) and stop. The **single recurring daily outreach batch at 13:35 PT weekdays** (task `9798fd67`) drains all `queued` entries and does the actual send via the linkedin-sourcing skill's **Outreach sends** section (pre-send checklist → compose from the role's template + this candidate's evidence + the hiring lead's note → send → VERIFY → `sent` + longlist `status:"contacted"` + Ashby `Reached Out` + note). Report the candidate as **queued for the next 13:35 send**, never as sent. NEVER set the longlist status to `contacted` at queue time — that happens only after a verified send (a 2026-07-27 ingestion session did this for 5 queued people and the mismatch nearly blocked their sends; the ledger, not the longlist, is the send truth).
   - **sourced × reject** — longlist line `status` → `"rejected-by-tim"` (+ tim fields) + registry event `{"action":"rejected-by-tim"}` so the suppression is visible to all owners. This is a suppression: never outreach. If an agent-created Ashby application exists: not yet contacted → archive it with a note; already contacted → stop follow-ups, add note, leave stage.
   - **inbound × advance** — *the hiring lead-authorized carve-out (2026-07-22) to the surface-only rule; valid ONLY for dashboard clicks by the hiring lead.* Move the application to **Initial Screen** (resolve the stage id via `interviewStage.list` on plan `91c63bb1-e873-4170-9600-e1fcca05dc96`) + candidate note "Advanced by the hiring lead via recruiting dashboard (<date>). <feedback>". Update the candidate's line in `inbound-ratings.jsonl`: `tim_verdict`, `stage: "Initial Screen"`.
   - **inbound × reject** — *same carve-out.* Archive the application with the closest archive reason (`archiveReason.list`; pick a quality/not-a-fit reason) + note. Send NO rejection email. Update `inbound-ratings.jsonl`: `tim_verdict`, `stage: "Archived"`.
6. **Mark** the event: `queue.py mark <id> --result "<what happened>"`. Failures → `--status error --result "<why>"` and flag in the summary (never leave events pending after a run).
   ⚠️**CLAIM FIRST, ACT SECOND — mandatory (concurrency defect, 2026-07-27).** A webhook burst can spawn more than one ingestion session, and recurring sessions also drain this queue opportunistically, so two agents routinely work the same events. `mark` is the only lock and it normally lands *after* the Ashby write, which produced three duplicate candidate records in one afternoon (Ashby has no merge endpoint, and every archive reason is rejection-flavoured, so a duplicate of a strong candidate cannot be cleaned up — only flagged for a manual UI merge). Therefore: **before doing any work on a batch, `mark` every event you intend to process with `--result "CLAIMED in-flight <time> by session <id> (<candidate>)"`, then process, then `mark` again with the authoritative result.** A claimed event disappears from `queue.py list`, so the other session skips it. Also re-`candidate.search` immediately before any `candidate.create` (name + LinkedIn-slug identity, per `ashby_crosscheck.py`) — that narrows the race window but does not close it; the claim is what closes it. If you find an event already carrying a CLAIMED marker from another session, leave it alone.
7. **Summary** (end of session): flags first (suppression conflicts, errors, rubric tensions), then verdicts ingested (agree vs override), filter changes made, Ashby actions taken. Report only what verifiably completed.

## Also runs opportunistically

Any recurring session should run `queue.py stats` at start and drain pending events with this procedure before its main work — the webhook is the fast path, not the only path.
