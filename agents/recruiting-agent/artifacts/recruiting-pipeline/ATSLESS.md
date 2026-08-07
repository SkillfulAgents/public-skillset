# Atsless data-source mode

The dashboard server has two data-source modes:

- **ashby** (default) — pipeline state is fetched live from the Ashby ATS API. This is the
  pre-existing behavior and is what runs when no mode file exists.
- **atsless** — pipeline state is read from agent-kept records on disk. The Ashby API and
  `ASHBY_API_KEY` are never touched (no network calls, no key read).

Local pipeline files (`roles.json`, `longlist-*.jsonl`, `inbound-ratings.jsonl`,
`calibration.jsonl`, the feedback queue and the `/api/feedback*` endpoints) work identically
in both modes.

## Activation

1. `PIPELINE_DIR` env var picks the pipeline directory (default `/workspace/pipeline`).
2. The server reads `${PIPELINE_DIR}/datasource.json` **once at startup**:

   ```json
   {"mode": "atsless"}
   ```

   Optional `displayName` overrides the user-visible system-of-record label in the UI
   (sync badge, empty states, footers, timeline copy, toasts, etc.). Resolution order,
   computed once at boot and shipped to the client as `sorName` on `/api/data`:

   1. `cfg.displayName` if present, a string, and non-empty after trim
   2. else `"Pipeline"` when `mode === "atsless"`
   3. else `"Ashby"` (default / ashby mode)

   ```json
   {"mode": "atsless", "displayName": "Greenhouse"}
   ```

   File missing, unreadable, or any other `mode` value → ashby mode, byte-for-byte the
   original behavior (and `sorName` = `"Ashby"` unless `displayName` is set). Changing
   the file requires a server restart. Field names in the payload (`ashbySync`, …) and
   code identifiers are unchanged — only rendered text uses `sorName`.

```
PIPELINE_DIR=/path/to/pipeline DASHBOARD_PORT=3941 bun run index.js
```

The boot line confirms the mode: `... [datasource: atsless — Ashby disabled]`.

## Store: `${PIPELINE_DIR}/atsless/candidates.jsonl`

One JSON object per line. `id`, `name`, `role_slug`, and `stage` are required for a record
to render (records missing `id` or `name` are skipped). `role_slug` must match a slug in
`roles.json` or the record is not shown anywhere.

```jsonc
{
  "id": "c-001",                     // unique; doubles as candidateId AND applicationId
  "name": "Ada Zhang",
  "linkedin_url": "https://linkedin.com/in/ada-zhang",
  "role_slug": "founding-engineer-fs", // must match a roles.json entry's slug
  "stage": "Reached Out",            // New Lead | Reached Out | Replied | Initial Screen |
                                     // First Round | Second Round | Offer | Rejected |
                                     // Unresponsive | Withdrawn
  "score": 82,                       // informational (dashboard's agent-score chip comes
                                     // from the longlist file, matched by linkedin_url/name)
  "title": "Staff Engineer",         // rendered as the card's position line
  "company": "Notion",
  "location": "SF",                  // stored; not currently rendered by the UI
  "source": "LinkedIn",              // shown as the card's source chip
  "notes": [                         // free-form history; stored, not rendered by the UI
    {"date": "2026-08-01T18:00:00Z", "text": "Advanced by the hiring lead"}
  ],
  "outreach": [                      // outreach timeline, oldest→newest (server re-sorts by date)
    {
      "date": "2026-08-01T20:35:00Z",   // ISO timestamp (event `ts` in the payload)
      "action": "sent",                 // queued | sent | accepted | replied | link-shared |
                                        // booked | closed | advanced
      "channel": "dm",                  // connect | dm | inmail | email | connect-note | linkedin
      "type": "initial",                // invite | initial | followup1 | followup2 | nudge
      "variant": "A",                   // A | B (uppercased by the server)
      "message": "Hi Ben, ...",         // optional; capped at 600 chars in the payload
      "subject": null                   // optional (email/InMail subject)
    }
  ],
  "interviews": [
    {
      "round": "First Round",           // label; the row's `stage` field uses the record's
                                        // stage first, this as fallback
      "datetime": "2026-08-06T18:00:00Z",
      "interviewers": ["the hiring lead"],
      "status": "upcoming"              // upcoming | completed | cancelled
                                        // (cancelled = dropped; omitted = derived from datetime)
    }
  ],
  "stage_history": [                    // OPTIONAL richer timeline; when absent the server
    {                                   // synthesizes one current-stage entry from
      "title": "New Lead",              // stage + updated/created
      "enteredStageAt": "2026-08-01T18:00:00Z",
      "leftStageAt": "2026-08-01T20:35:00Z"   // omit on the current stage
    }
  ],
  "created": "2026-08-01T18:00:00Z",
  "updated": "2026-08-01T20:35:00Z"
}
```

### Schema refinements vs the original sketch (why)

- **`channel` / `type` enums widened.** The frontend's chip logic distinguishes
  `connect` (bare invite) from `dm` / `inmail` / `connect-note` / `email` message sends, and
  treats `type: "invite"` as a non-message touch. The narrow `linkedin|inmail|email` set would
  make every invite render as a message. Use `channel: "connect", type: "invite"` for a bare
  connection request and `channel: "dm"` for the post-accept DM — exactly mirroring the
  `#outreach` note vocabulary Ashby mode parses.
- **`action: "advanced"`** is accepted (renders as the Advance bookkeeping node in the
  timeline, excluded from touch counts), matching the notes parser.
- **`stage_history`** (optional) added so a session that tracks stage transitions can show a
  real timeline; otherwise the synthesized single entry drives the "Nd in stage" chip.
- **`notes` and `location`** are part of the record for agent bookkeeping but are not
  rendered by the current UI.

## How stages map to dashboard views

| `stage` value | Where it renders |
|---|---|
| `New Lead`, `Reached Out`, `Replied` | **Leads tab**, one column per stage; outreach chips/timeline from `outreach[]` |
| `Initial Screen`, `First Round`, `Second Round`, `Offer` | **Active pipeline** (interviews tab), one column per stage; `interviews[]` render on the card |
| `Rejected`, `Unresponsive`, `Withdrawn` | Nowhere (terminal — record kept for history/suppression only) |

Interview entries with `status: "upcoming"` and a `datetime` within the next 7 days also
appear in the "Upcoming interviews" strip, regardless of stage.

## Jobs / roles

In atsless mode the "Ashby jobs" list is synthesized from `roles.json`: one job per entry,
`id` = the entry's key, title = the entry's optional `title` field, else a label derived
from the slug (`slugToLabel`). `sourcing: "hidden"` entries stay hidden as in ashby mode.

## Ashby-only features with no atsless equivalent

These return their empty/neutral shape (never an error):

- adopted-record registry (`ashby-adopted-apps.json`) — not read; adoption is an ATS concept
- candidate tags from Ashby (`agent-sourced` chip) — `tags` array on the record, default `[]`
- suppression scan of historical ATS bulk leads — no data, nothing rendered
- `ashbySync` / `pipelineSync` / `leadsSync` health blocks — always report ok/fresh (age 0)
