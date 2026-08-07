---
name: Shared Candidate Registry (Google Sheets)
description: Multi-owner shared state for the recruiting pipeline — sourced candidates, ownership (who advanced whom), outreach queue/cadence events, and suppression live in a shared Google Sheet so multiple agent installs (the hiring lead, a teammate) cooperate without double-contacting anyone. Use for every advance, send, reply, and pre-write ownership check, and to push/pull longlists at session boundaries.
metadata:
  version: "1.1.0"
---

# Shared Candidate Registry

**Sheet:** `{{COMPANY}} Recruiting — Shared Candidate Registry` — id + URL in `/workspace/pipeline/registry.json`.
**Identity:** `OWNER` env var in `/workspace/.env` (`alice` on one install, `bob` on another). Every write is stamped with it. `registry.py` refuses writes without it.

## Data model

- **`events` tab — append-only source of ordering/audit truth.** One row per material action: `ts, actor, candidate_key, role, action, payload(JSON)`. Actions: `sourced, advanced, rejected-by-tim, suppressed, queued, held, sent, accepted, replied, link-shared, booked, unresponsive, status`. Sheets append order settles races: **first `advanced` row wins ownership**; the loser backs off and flags. Cadence math (+4d/+10d follow-ups) runs off `sent` events with `payload.type = initial`.
- **`candidates` tab — current state, upserted.** One row per `(candidate_key, role)`: core columns (score, status, owner, queue_state, ashby ids…) + the full longlist record as JSON in `payload`. This is what dashboards render.
- `candidate_key` = `in/<linkedin-slug>` (same normalize rule as `longlist.py`).

## Ownership rules

1. **First Advance wins.** `advanced` event sets `owner` (never overwritten). Owner's install is solely responsible for outreach + nurture — sends go through that person's LinkedIn seat.
2. **Contact by ANY owner suppresses for all.** `check` exits 3 if any `sent/accepted/replied/link-shared/booked` event exists.
3. **`push` never touches rows owned by someone else** — it skips and reports them.
4. Local longlist files are this install's working cache; the Sheet is truth. On divergence, the Sheet wins for `owner`, contact state, and queue state.

## Commands

```bash
R="uv run --env-file /workspace/.env --with requests /workspace/.claude/skills/sheets-registry/registry.py"

$R init --title "Recruiting — Shared Candidate Registry"
                                          # FIRST RUN ONLY, when no registry.json exists:
                                          # creates the spreadsheet (events + candidates tabs
                                          # with headers) under the connected account and
                                          # writes /workspace/pipeline/registry.json
$R event '{"candidate_key":"in/foo","role":"founding-engineer-fs","action":"advanced","payload":{"score":86,"source_event":"fb_..."}}'
$R events < events.jsonl                  # bulk append
$R check in/foo --role founding-engineer-fs   # exit 0 free · 2 owned-by-other · 3 contacted
$R push --file /workspace/pipeline/longlist-founding-engineer-fs.jsonl --role founding-engineer-fs
$R pull --role founding-engineer-fs > remote.jsonl
$R reconcile --file /workspace/pipeline/longlist-founding-engineer-fs.jsonl --role founding-engineer-fs
                                          # session-start sync: Sheet wins for owner/contact/queue
                                          # state; inserts rows sourced by the other owner
$R queue                                  # my queued-not-sent, score-descending
$R cadence                                # my sent timestamps per candidate (due-date math)
$R stats
```

## Mandatory call sites (contract with the other skills)

- **Session start (any recurring session):** `reconcile --file <longlist> --role <slug>` — merges Sheet truth (owner/contact/queue state, other-owner finds) into the local longlist before doing anything.
- **Session end (search sessions):** `push --file <longlist> --role <slug>` so new harvest/scoring is visible to all owners.
- **Before ANY advance (calibration-feedback):** `check` — exit 2 means the other owner got there first: skip the Ashby create/queue, flag in summary. Then append the `advanced` event, re-read `check` output; if another actor's `advanced` row landed first, back off (undo nothing in Ashby yet — create happens after the check).
- **Before ANY send (13:35 batch, follow-ups, InMail):** `check` — exit 3 = already contacted by someone, skip. Queue drain = `queue` (owner-scoped); never send for `owner != me`.
- **After every outreach action:** append the matching event (`queued/sent/accepted/replied/link-shared/booked/unresponsive`) with `payload` `{channel, type, variant, message?}` — this replaces `outreach-log.jsonl`, which is legacy read-only.
- Ashby notes + stages remain the pipeline-of-record mirror for advanced candidates (unchanged rule); the Sheet adds the cross-install layer.

## Onboarding a new owner (any {{COMPANY}} teammate)

The Sheet lives on the **{{COMPANY}} shared drive → Recruiting folder** (moved 2026-08-06), so every company Google account already has access — no per-person sharing step.

A fresh install (unzipped collaborator bundle) needs exactly one connection:
1. Connect Google Sheets with their company Google account (`request_connected_account`, toolkit `googlesheets`).
2. First-run setup (agent does this automatically when `OWNER` or `GSHEETS_ACCOUNT_ID` is missing from `.env`): set `GSHEETS_ACCOUNT_ID` from the connected account, derive `OWNER` from the account email prefix (e.g. `teammate@{{COMPANY_DOMAIN}}` → `mike`), confirm with the user, write both to `.env`, then run `registry.py stats` to verify access. `registry.json` ships in the collaborator bundle with the spreadsheet id — nothing to configure there. **On a fresh customer install (public template — no `registry.json` in the bundle): run `registry.py init` once to create a brand-new registry Sheet, then move it to a shared drive folder if teammates will run their own installs.**
3. Their sends use their own LinkedIn seat; their advances land in Ashby stamped with their `OWNER` in the note's `#outreach` line.
