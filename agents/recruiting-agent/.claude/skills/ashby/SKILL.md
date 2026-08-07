---
name: Ashby ATS
description: Read and write the Ashby ATS via API — list jobs, search/create candidates, add notes, create applications, change stages, list interview schedules. Use for ALL hiring-pipeline state reads and updates.
metadata:
  version: "1.0.0"
---

# Ashby ATS

Thin CLI over the Ashby RPC API (all endpoints are `POST https://api.ashbyhq.com/<endpoint>`, HTTP Basic auth with the API key as username and empty password). Docs: https://developers.ashbyhq.com/reference

Requires `ASHBY_API_KEY` in `/workspace/.env`.

## Usage

```bash
uv run --env-file /workspace/.env --with requests /workspace/.claude/skills/ashby/ashby.py <endpoint> ['<json-payload>'] [--all]
```

`--all` follows cursor pagination on `.list` endpoints and merges all pages into `results`.

## Common endpoints

| Endpoint | Payload example | Purpose |
|---|---|---|
| `job.list` | `{"status": ["Open"]}` (must be an array) | Open jobs + IDs |
| `candidate.search` | `{"email": "a@b.com"}` or `{"name": "Jane Doe"}` | Dedupe before creating |
| `candidate.create` | `{"name": "...", "email": "...", "linkedInUrl": "..."}` | New sourced candidate |
| `candidate.createNote` | `{"candidateId": "...", "note": "..."}` | Log outreach/replies/reasoning |
| `application.create` | `{"candidateId": "...", "jobId": "..."}` | Attach candidate to a role |
| `application.list` | `{"jobId": "...", "createdAfter": 1721500000000}` | Review new inbound |
| `application.changeStage` | `{"applicationId": "...", "interviewStageId": "..."}` | Move pipeline stage |
| `interviewPlan.list` / `interviewStage.list` | `{"interviewPlanId": "..."}` | Stage IDs for a job |
| `interviewSchedule.list` | `{}` | Scheduled interviews |
| `candidate.addTag` | `{"candidateId": "...", "tagId": "..."}` | Tag a candidate. **`agent-sourced` tagId: `{{AGENT_SOURCED_TAG_ID}}`** — MANDATORY after every agent `candidate.create` (create can't set tags) |
| `candidateTag.list` / `candidateTag.create` | `{"title": "..."}` | Tag definitions |
| `archiveReason.list` | `{}` | Archive reason IDs (all 7 are rejection-flavored; no neutral one as of 2026-07-24) |
| `application.update` | `{"applicationId": "...", "archiveReasonId": "..."}` | ⚠️ Returns success but does NOT archive (silent no-op, observed 2026-07-29) — use changeStage below |
| `application.changeStage` | `{"applicationId": "...", "interviewStageId": "<Archived stage id>", "archiveReasonId": "..."}` | The WORKING archive call (validated 2026-07-29); archiveReasonId is required when the target stage type is Archived. FE-FS plan's Archived stage: `9ead1bda-ff0f-49ae-9558-01bdb7392fe0` |
| `application.delete` | `{"applicationId": "..."}` | EXISTS but returns `missing_endpoint_permission` as of 2026-07-24 — the hiring lead must enable it on the API key |

No `candidate.delete` / `candidate.remove` endpoints exist — candidate records cannot be deleted via API, only their applications.

## Conventions

- Always `candidate.search` before `candidate.create` (avoid duplicates).
- Every pipeline action gets a `candidate.createNote` (channel + date + summary).
- Responses are `{"success": true, "results": ...}`; non-success exits 1 with the API error printed.
- Verified live 2026-07-21 (`job.list` works; note the array-typed filters). Keep updating examples here as endpoints get exercised.
