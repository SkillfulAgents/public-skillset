---
name: LinkedIn Sourcing (Sales Navigator)
description: Longlist-building AND outreach sends on LinkedIn via the browser — Sales Navigator search recipes, two-touch harvest, company-graph expansion, account-safety caps, the longlist.py store (append/dedupe/update/stats + cross-role exclusivity lock), and the personalized-outreach send procedure (the hiring lead-approved advances, owner-scoped queue, shared-registry events). Queue/cadence events live in the shared Google Sheets registry (sheets-registry skill); sends are owner-scoped (OWNER env var). Use for ALL LinkedIn sourcing and outreach work.
metadata:
  version: "1.3.0"
---

# LinkedIn Sourcing (Sales Navigator seat)

Browser-driven sourcing on the hiring lead's logged-in LinkedIn account — **Sales Navigator seat as of 2026-07-23** (see `reference-platform-access` memory). The goal is a per-role **longlist** of potentially exceptional people, harvested cheaply and deduped forever.

## Files per role

- Company graph: `/workspace/pipeline/companies-<role-slug>.md` — sections **Tier A** (bar as high as the seeds; harvest deeply), **Tier B** (promising; sample ~5 profiles before committing), **Rejected** (with 1-line why, so they're never re-proposed). Row format: `| Company | Why this tier | Source | Date |`. Seeds from role memory go in Tier A on day one.
- Longlist store: `/workspace/pipeline/longlist-<role-slug>.jsonl`, managed ONLY via `longlist.py` (handles dedupe). **This is the local working cache — the SHARED truth is the Google Sheets registry (`sheets-registry` skill, 2026-08-06 multi-owner model).** Session start: `registry.py reconcile --file <longlist> --role <slug>` (Sheet wins for owner/contact/queue state; inserts other-owner finds). Session end: `registry.py push --file <longlist> --role <slug>` so new harvest/scoring is visible to all owners (the hiring lead + a teammate). A row owned by another OWNER is read-only here: never shortlist, queue, or send against it.

## longlist.py

```bash
uv run /workspace/.claude/skills/linkedin-sourcing/longlist.py --file <path> <command>
  add '<json>'            # one record; dedupes by normalized LinkedIn URL; warns on name+company soft-dupes
  bulk                    # JSONL records on stdin; same dedupe; prints added/skipped
  update <id> '<json>'    # shallow-merge fields into an existing record (e.g. deep-profile data, score, status)
  list [--status X] [--min-score N] [--limit N] [--format json|md]
  stats                   # counts by status + touch
  crossrole <url|name>    # no --file needed: find a person across ALL role longlists (shows locked flag)
```

**Cross-role exclusivity (the hiring lead, 2026-07-22): one active role per person.** Enforced by the store: `add`/`bulk` refuse anyone who is `shortlisted`/`contacted`/`replied`/`in-conversation`/`interview-scheduled` in another role (`crossrole-locked`); `update` refuses to set one of those statuses when the person is locked elsewhere (`crossrole-conflict`). Merely harvested/scored/rejected in another role → add allowed, tagged `crossrole: [...]`. On a conflict where the NEW role looks like the better fit, don't force it — flag to the hiring lead with both roles' scores.

**LinkedIn is a hard condition (the hiring lead, 2026-07-24): no LinkedIn, no shortlist.** The store refuses any lock-status transition (shortlisted+) whose `linkedin_url` is not a real `linkedin.com/in/` profile — outcome `needs-linkedin`. Excellence-pool finds carrying a GitHub/personal-site/`pending-enrich://` URL are harvested fine but flagged `needs_linkedin: true`; resolve the real profile (web search + browser) and `update` with the LinkedIn URL (the store re-keys the id + clears the flag), or DQ if unresolvable (resolve-then-DQ).

Record shape (only `linkedin_url` and `name` required at card stage):

```json
{"name": "Jane Doe", "linkedin_url": "https://linkedin.com/in/jane-doe", "headline": "Staff SWE @ X",
 "current": {"title": "Staff SWE", "company": "X", "tenure": "2y 3m"}, "location": "SF",
 "source": {"kind": "salesnav-search", "recipe": "R1", "query": "tier-A current", "date": "2026-07-23"},
 "touch": "card", "status": "harvested", "score": null}
```

Statuses: `harvested → scored → shortlisted | rejected-disqualifier | rejected-score | rejected-by-tim | suppressed-ashby | stale-touch-review` → `contacted → replied → in-conversation → interview-scheduled` (terminal: `unresponsive`, `rejected-by-candidate`). Set `contacted` ONLY after a verified send — see Outreach sends; `replied`+ is owned by the Reply sweep.

**Ashby crosscheck at SHORTLIST time (the hiring lead, 2026-07-24 — "I don't want to see people in the list that are already in Ashby"):** before setting anyone `shortlisted`, run `candidate.search`. **Search the name in VARIANTS, and grep the suppression index by surname (Shaoru Ian Huang miss, 2026-07-27).** `candidate.search` accepts only `name` and `email` — a `linkedInUrl` payload returns `success:false`, so "name + LinkedIn URL" is not actually a thing the endpoint does — and the name match is string-based, not fuzzy: `"Shaoru Ian Huang"` returned zero while `"Shaoru Huang"` returned the record that had been Reached Out in May. So for any name with 3+ tokens, an added Western/middle name, or a hyphenated surname, run first+last alone as a second query, and `grep -i "<surname>" /workspace/pipeline/suppression-ashby.jsonl` as a third check. Confirm identity on the LinkedIn slug in the record's `socialLinks`, not on the name string. A pre-existing record the agent didn't create → **probe its CONTACT DEPTH before suppressing (Eric Zhang override, the hiring lead 2026-07-27: "we were never really in conversation with him so let us reach out again")**. Suppressing on the mere *existence* of a record was silently deleting the top of the funnel — the 2026-07-27 cut hid 15 people that way, including a 91, an 87, an 86 and an 85. The test: **REAL CONTACT** = any human-authored note, any stage past `Reached Out`, or any non-`Lead` status → `status: "suppressed-ashby"` + `suppress_reason`, off the list as before. **BARE TOUCH** = `New Lead`/`Reached Out` with zero human notes and no reply (a bulk-touch marker stamped at record-creation time, not a conversation) → `status: "stale-touch-review"`: it **stays on the sourced list** flagged `prior-touch (stale, N days)` with the record id, and the hiring lead decides. The agent still never sends to one of these on its own — an Advance click is what authorizes it, and then the existing record is adopted, never duplicated.

**Weight job-match when judging depth (Scott Hickmann advance, 2026-07-27):** a stale touch whose application sits on a *different* job is weaker evidence still — Hickmann was suppressed out of Founding Engineer - Full Stack by a Sept-2025 bare touch on Founding Engineer - ML. Same-job bare touch and other-job bare touch are both `stale-touch-review`, but say which in the flag so the hiring lead isn't reading a cross-role artifact as history on this role. On adoption, leave the other job's application untouched and create a fresh one on the advancing role. **A no-reply touch is re-approachable (Timothy Feng, the hiring lead 2026-07-27: "we only reached out to him before and he did not reply")** — ~2.5 months was fine by him. Carry "this is a SECOND approach" into the send brief so the batch does not replay the original opener. Ambiguous or unprobeable contact depth → fail closed (suppress + flag), never silently. Agent-created records (`agent-sourced` tag, incl. the back-tagged 2026-07-24 batch, even if their application was deleted/archived in the cleanup) do NOT suppress — those people are workbench inventory and stay listable; on a later the hiring lead Advance, restore/reuse that record instead of creating a duplicate. This upstream gate is what makes a dashboard Advance always safe to send. **Run it with `uv run /workspace/.claude/skills/linkedin-sourcing/ashby_crosscheck.py <in.json> <out.json>`** (rows of `{name, linkedin_url, score, tier}` → per-row `verdict`: `clear | agent-created-reuse | stale-touch-review | suppressed-ashby | possible-collision-review | search-failed`) — it does the name-variant queries, the slug-based identity confirmation, and the contact-depth probe (`contact_depth`) described above.

## Sales Navigator mode (current default, 2026-07-23)

the hiring lead upgraded to **Sales Navigator** (not Recruiter — `/talent/` still bounces). Entry point: `https://www.linkedin.com/sales/` → lead search at `/sales/search/people`. First session on the new seat: confirm it loads, note the plan tier (Core vs Advanced) and InMail credit balance, and update `reference-platform-access` if reality differs.

How to run the recipes natively:
- **Lead-search filters that now exist:** Current company / Past company (R2 works as a real filter at last), Years in current position (R1's ≥2 yr tenure), Years of experience (R3's ≤8), Geography, Seniority level, Function, Current/past job title with boolean, Keywords. Batch tier-A companies 3–5 per search as before.
- **No commercial-use search limit** on Sales Nav — the old "prefer company People tabs to save searches" workaround is obsolete. Account-safety caps below still apply.
- **Saved searches + lead lists:** save each proven (recipe × role) query; Sales Nav alerts on new matches — check saved searches at session start before running fresh queries. Optionally mirror shortlists into a lead list per role for spotlight tracking.
- **Spotlights:** "Changed jobs in past 90 days" and "Posted on LinkedIn recently" exist; **open-to-work does NOT** (Recruiter-only) — R4 stays approximated: use job-changed-90d as the movability proxy, tag `source.spotlight: "job-change-90d"`.
- **URL discipline:** lead pages are `/sales/lead/...`. The longlist dedupe key is the public `/in/` URL — grab it from the lead page (three-dot menu → "View LinkedIn profile" or the profile link) before `add`/`bulk`. Never store a `/sales/lead/` URL as `linkedin_url`.
- **InMail credits (~50/mo on Core):** replies land in the **Sales Nav inbox** (`/sales/inbox/`) — reply sweep checks it every run. Sends still follow the Outreach sends channel order (InMail remains the fallback, not the opener).

## Regular-LinkedIn fallback mode (if the Sales Nav seat lapses)

Longlist store, two-touch procedure, company-graph expansion, and scoring are UNCHANGED — only the harvest mechanic changes.

Approximating each recipe on regular LinkedIn:
- **Search entry:** `https://www.linkedin.com/search/results/people/` with `keywords=` (boolean OK) + the "Current company" / "Locations" facets. Free/Premium has NO past-company or years-in-role filter — capture tenure at card stage instead.
- **R1 (tier-A current ICs):** best via the **company People tab** — `linkedin.com/company/<slug>/people/`, then the "Keywords" box (e.g. `software engineer`, `member of technical staff`) + title/geo facets. Highest-yield regular-mode move; harvest the company directly rather than global search.
- **R2 (tier-A alumni):** global people search `keywords="<Company>" AND (engineer OR "technical staff")`; at card/profile stage keep only those where the tier-A company is a PAST role. No past-company facet — manual card-stage filter.
- **R3 (fast risers):** people search `keywords=(staff OR principal OR founding OR "tech lead")`; judge YoE at profile stage.
- **R4 (open-to-work):** NOT available on regular seat — skip, note the gap.
- **R5 (colleagues-of):** confirmed-great person's profile → "People also viewed" panel + their company's People tab. Works fine on regular seat.

Regular-mode caveats:
- **Commercial-use search limit:** free/Premium caps monthly *global* people-searches. Company People tabs and profile views burn it slower — prefer them. On "You've reached the monthly limit," STOP global search, note it, finish via company tabs.
- Cards rendering as "LinkedIn Member" (out of network, no name) — skip, don't count against harvest.
- Take what's visible on 2nd/3rd-degree profiles; don't force-connect.

## Search recipes (run via Sales Nav lead search)

Run per role, tier-A companies in batches of 3–5. If a filter is missing on the current seat, approximate with boolean title search and check tenure at card stage instead.

Pool defaults (the hiring lead, 2026-07-21): **tenure ≥ 2 yrs at the stamp company · any seniority (scoring handles level) · geography United States, remote ok** — role files may override.

- **R1 — Tier-A current ICs**: Current company ∈ tier-A batch · Current title = role family (boolean, e.g. `("software engineer" OR swe OR "member of technical staff") NOT (manager OR director OR VP)`) · Years in current position ≥ 2 · Location: United States.
- **R2 — Tier-A alumni** (cleared a high bar once, movable now): Past company ∈ tier-A batch · current company NOT ∈ tier-A batch · title family. Recruiter can't filter past-company tenure — verify the ≥2 yrs there at card/profile stage. Alumni now at tiny startups are often the highest-signal pool.
- **R3 — Fast risers**: Current title contains `staff OR principal OR "tech lead" OR founding` · Years of experience ≤ 8. Promotion velocity is a core exceptional-signal.
- **R4 — Spotlight priority pass**: R1/R2 + a movability spotlight → higher reply odds; prioritize in outreach ordering. On Sales Nav use "Changed jobs in past 90 days" (`source.spotlight: "job-change-90d"`); open-to-work is Recruiter-only. Never the only pass — the best people aren't flagged as movable.
- **R5 — Colleagues-of (excellence clusters)**: every candidate who scores 85+ (later: every good interview) seeds a cluster search — co-founders, co-authors, people who overlapped with them at small companies. Log `source: {"kind": "colleagues-of", "anchor": "<person>"}`. Excellence clusters; confirmed-great people are the best pointer to more.

## Search recipes — BUSINESS roles (GTM / Growth / Recruiting — the second engine)

Business-role excellence reads differently from engineering excellence: pedigree + output-you-can-point-at, not OSS/systems. Run these independently of R1–R5, against the role's own company graph (`companies-founding-gtm.md`, `companies-growth.md`, ...), into the role's own longlist.

- **B1 — MBB escapees**: Past company ∈ {McKinsey, Bain, BCG} · current company = startup/scale-up (NOT consulting) · 2–8 yrs out. The archetype: cleared the MBB bar, then chose building over advising. (Regular-seat: keyword search `"McKinsey" AND (founder OR GTM OR "account executive" OR growth)`, past-company confirmed at card stage.)
- **B2 — Top-MBA operators**: School ∈ {Harvard Business School, Stanford GSB, Wharton} · current role at seed/Series-A startup in GTM/growth/ops. Filter out those who went straight to big-co strategy roles.
- **B3 — First/founding GTM**: Title contains `founding AE OR "first sales hire" OR "founding account executive" OR "GTM lead" OR "head of growth"` at companies ≤50 people. Owning a motion from zero is the core evidence.
- **B4 — Forward-deployed archetype**: Palantir FDE/deployment-strategist alumni; solutions engineers at technical products (Retool, Datadog, Scale) who build demos themselves. For technical-GTM roles.
- **B5 — Founder alumni**: YC/venture founders whose companies wound down or exited small, now open — strongest build-from-zero evidence there is (`yc-companies --status Inactive|Acquired`).
- **Growth-specific overlay**: candidate MUST have a public content portfolio (X/YouTube/newsletter/blog). Verify OFF LinkedIn before shortlisting: real followings, real content quality. A growth candidate with no public work fails the posting's bar regardless of pedigree.

Verification norms per family: engineering → GitHub/papers/talks; business → content channels, funding/exit records (YC pages, press), "grew X from A→B" claims cross-checked against company trajectory.

## Two-touch harvest procedure

1. **Card touch** (cheap): from search result pages, capture name, profile URL, headline, current title/company, tenure-in-role if shown, location → `bulk` into the longlist. ≤ ~5 pages per query, then vary the query.
2. **Quick screen** on cards: obvious title/space mismatch or visible disqualifier → `update <id> '{"status":"rejected-disqualifier","reject_reason":"..."}'` — do not open the profile.
3. **Profile touch** (expensive, budgeted): open remaining profiles; extract full experience history (titles+dates → tenure shape, promotion velocity), education, honors/publications, founder/early stints, anything "built X used by Y" → `update` with `touch: "profile"` + a `profile` object. This is the input to 0–100 scoring.

## Company-graph expansion (every session, ~10 min)

From tier-A company pages: "Pages people also viewed" + Recruiter's similar-company suggestions; cross-check with the `yc-companies` skill for the role's space; propose lookalikes from judgment. Every addition gets a tier + why. the hiring lead can edit the file directly — respect his edits as calibration.

**Stamp precision (the compounding loop):** `longlist.py stats` reports avg score and 85+ rate per source company/recipe. Harvest high-yield stamps deeper; a stamp that keeps producing sub-bar people gets demoted to Rejected with the numbers as the why. The graph should literally learn which bars predict our bar.

## Outreach sends (personalized, role-dependent)

**Who may be messaged (authorization, in force 2026-07-22):**
1. **the hiring lead-advanced candidates** (dashboard Advance click on a sourced row) — the click IS the per-candidate send approval and overrides a role-level Outreach HOLD/PAUSED.
2. **Agent-shortlisted candidates** on roles whose role file says Outreach ACTIVE (bulk outbound sessions).
Fully autonomous sends on agent judgment alone (no the hiring lead click, role held): NOT enabled — future state, gated on calibration agreement % staying high.

**ASHBY IS THE SINGLE SOURCE OF TRUTH for outreach state (the hiring lead, 2026-07-29).** Every outreach — bare invite, DM, InMail, follow-up, detected acceptance, reply, link-shared, booking, unresponsive-close — is logged in the SAME session as (a) a candidate NOTE in Ashby and (b) the matching stage change. The dashboard renders Ashby only (stage history + parsed notes); the local ledger below is internal batch mechanics (queue draining, cadence math) and never display truth. **Every outreach note MUST end with a machine line** the dashboard parses:
`#outreach action=sent|accepted|replied|link-shared|booked|closed channel=connect|dm|inmail|email type=invite|initial|followup1|followup2 variant=A|B date=YYYY-MM-DD`
(omit keys that don't apply, e.g. a bare invite has no variant; `date` = the send date when the note is written later). Human-readable text above the tag as always — full message text for DMs/InMails, "bare connection request sent, no note" for invites.

**Send ledger — MOVED to the shared registry (2026-08-06): the `events` tab of the Google Sheet (`sheets-registry` skill).** `/workspace/pipeline/outreach-log.jsonl` is retired legacy, read-only — its 334 historical events were migrated into the Sheet. Every queue/cadence event is now appended via `registry.py event` with the same vocabulary:
`{"candidate_key": "in/…", "role", "action": "queued|sent|accepted|held|replied|link-shared|booked|unresponsive", "payload": {"channel": "connect|dm|inmail|email", "type": "invite|initial|followup1|followup2", "variant": "A|B", "message": "<full text>", "by": "<session type>"}}` — `ts`/`actor` auto-filled (actor = `OWNER` env var). `variant` is required on every templated send (`initial`/followups); a bare invite (`channel: "connect", type: "invite"`) carries no text and no variant — keep the variant assigned at queue time and apply it when the first real message goes out. Weekly report computes reply rate per role per variant off `initial` sends (`registry.py cadence`). The registry is the single source of truth for cadence math: follow-up due-ness reads the latest `type: "initial"` `sent` ts (the invite is a door-knock, not a message), a `replied`/`unresponsive` event stops the cadence. Because events are shared, a send by EITHER owner suppresses re-contact by both.

**Pre-send checklist (every send, no exceptions):**
0. **`registry.py check <key> --role <slug>` (shared-registry gate, 2026-08-06):** exit 2 = owned by another OWNER (their pipeline — skip + note), exit 3 = already contacted by ANY owner (skip; follow-ups only via cadence). This is what prevents the hiring lead's and a teammate's installs double-contacting one person.
1. `longlist.py crossrole <url>` → person must be active in THIS role only (one active role per person).
2. Ashby `candidate.search` (name + LinkedIn URL) → **REVISED (the hiring lead, 2026-07-24 — Erica Wu wrong-skip lesson).** The already-in-Ashby gate now lives UPSTREAM in the search session (already-in-Ashby people never reach the sourced list), so at send time:
   - **the hiring lead-advanced candidate → SEND.** His Advance is authoritative — the record his Advance created (or adopted) NEVER blocks the send it authorized. Agent-created records (`agent-sourced` tag — incl. the back-tagged 2026-07-24 batch) never block either.
   - The only remaining skip: a non-agent record showing **actual prior contact** (outreach messages, interview activity, an active conversation) → skip + flag with the history (double-contact risk). A bare untouched record with zero contact history does NOT block a the hiring lead-advanced send. **"Prior contact" needs evidence of a touch, not just a stage name (Eric Zhang, 2026-07-27):** a record sitting at `Reached Out` since its own creation date with zero non-agent notes is a bulk-import marker, and blocking on it costs real candidates. Probe depth (notes / stage past Reached Out / non-Lead status) the way `ashby_crosscheck.py` does before calling it prior contact.
   - **Bulk ACTIVE sends (no the hiring lead click):** any pre-existing non-agent record still = skip + flag (unchanged).
3. registry events → an existing `sent` for this person by ANY owner (any role) → do not re-initiate; follow-ups only per cadence (covered by check exit 3, but re-verify when adjudicating follow-ups vs initials).
4. **NO self-imposed daily send cap (the hiring lead, 2026-07-28: "get rid of the limit of outreaches").** Invites and DMs: send every authorized (queued) candidate in the batch, no numeric ceiling. InMails stay at **≤3/day** — that pacing is the hiring lead's own 2026-07-28 credit rule (~50/mo), separate from the removed cap. The only remaining brakes are LinkedIn's own signals: human pace between sends, and ANY warning banner / "you're out of invitations" / checkpoint = STOP the batch immediately, log the remainder as still `queued`, flag to the hiring lead. (LinkedIn's platform ceiling is ~200–250 invites/wk on a Sales Nav seat, shrunk by poor acceptance rates — respect it by watching for those signals, not by pre-capping.)

**Batched daily send (the hiring lead, 2026-07-24 — replaces per-advance sends):** advances/shortlists do NOT send inline and never schedule per-candidate tasks — they only append a `queued` event to the ledger. A **single recurring daily outreach batch at 13:35 PT weekdays** (task `9798fd67`) is the ONLY sender. It runs after the 09:00–13:30 PT search slots (never concurrent with them) and before the 14:00 reply sweep.

**Daily outreach batch procedure** (task `9798fd67`, `35 13 * * 1-5`): build the working set = `registry.py queue` — every candidate whose `queue_state` is `queued` AND `owner == OWNER` (this install's identity; never drain another owner's queue — their sends go through their LinkedIn seat). None → end with a one-line note. For each, run the pre-send checklist below → follow the Channel order (DM path → full template; no DM path → BARE invite, no note) → send AS the hiring lead → VERIFY on screen → append `sent` (or `held`/`skipped` + reason) → `longlist.py update <id> '{"status":"contacted"}'` → Ashby note with `#outreach` tag + stage per the **Stage semantics** below (message delivered → `Reached Out`; bare invite → stage stays `New Lead`). The batch ALSO drains the due InMail-escalation queue (Channel order step 4) — those InMails DO move `New Lead → Reached Out`. No batch-size cap (the hiring lead, 2026-07-28) — drain the whole queue; only InMail pacing and LinkedIn's own warning signals stop a send. Flag every `held`/`skipped` to the hiring lead; report real sent counts only.

**Voice rules (the hiring lead, 2026-07-22 — "this sounds terribly AI" feedback; non-negotiable):**
- **NO em-dashes. No semicolons.** Use a comma, a plain hyphen, or start a new sentence. Em-dashes are the #1 AI tell.
- **NEVER quote comp numbers or the posted band** in any message (the hiring lead: a wide band "looks ridiculous"). Comp question → "depends on level and how you want to split cash vs equity, easier to talk through live" + booking link, and flag it to the hiring lead in the summary. The band stays internal context only.
- First touches and cadence follow-ups: fixed templates, no length judgment needed (the hiring lead 2026-07-24: short + hook-first, calibrated on {{FOUNDER}}'s sent examples). Live REPLIES in conversation: shorter than feels natural, write it, cut half, send. Fragments fine. lowercase starts fine.
- Plain words. No cleverness quota, no stacked adjectives, no "hell of a", no "thrilled/excited/passionate", at most one exclamation mark per conversation and ideally zero.
- One specific true detail about them, max. Don't recite their resume back at them.
- Read-aloud test: if it sounds like a LinkedIn recruiter or a press release, rewrite it.

**Composing the message (TEMPLATED — the hiring lead, 2026-07-23: same text per role, only the name changes, for clean A/B testing):**
- **Send the role's template verbatim from `/workspace/pipeline/outreach/<role-slug>.md`** (Template A/B for DM/InMail, T2/T3 follow-up templates; connect-note versions RETIRED 2026-07-28 — invites go bare). `{{first_name}}` is the ONLY substitution. Shared rules + company language bank: `/workspace/pipeline/outreach/_company-voice.md`. Role has no template file yet → create one from `_company-voice.md` + the role file before sending.
- **A/B discipline:** alternate variants within a role across sends; log `"variant": "A"|"B"` in every ledger event; NEVER edit a live template mid-test (a revision = new variant letter + date). Bespoke hand-written messages only when the hiring lead explicitly asks (e.g. dashboard-advance note).
- Messages send AS the hiring lead, company is **{{COMPANY}}**. Never present the message as agent-written (the RL template pitching the agent stack as the role's tooling is different and approved), never discuss comp/equity, never invent facts.
- Channel shapes: DM/open-profile and InMail get the full Template A/B (**short + hook-first, ~50–90 words — recalibrated 2026-07-24 on {{FOUNDER}}'s actual sent templates;** skeletons in `_company-voice.md`). Connection requests go **BARE — no note, ever** (the hiring lead, 2026-07-28; connect-note templates retired). The full template reaches invite-path candidates the moment they accept, or via the InMail escalation if they don't.

**Channel order — SEQUENCED (the hiring lead, 2026-07-28: "i want to avoid connection notes as much as possible" — supersedes the 2026-07-27 always-note rule):**
1. **Check the DM path first, per candidate.** `browser_snapshot` the profile and look for a real **Message** button — present for 1st-degree AND for Open Profile members at 2nd/3rd degree (compose window shows "Premium · Free message"). Present → DM the full Template A/B (`channel: "dm", type: "initial"`). Never default to an invite without having checked; Open Profile is invisible from the search card.
2. **No DM path → BARE connection request, NO note.** Do NOT click "Add a note" — just Connect → Send. the hiring lead's reasoning: a generic teaser note depresses acceptance and burns the pitch before a thread exists; a bare invite from a founder profile reads as curiosity. It also protects quota — LinkedIn scales the weekly invite cap on acceptance rate. Log `channel: "connect", type: "invite"`, no message text, no variant.
3. **Invite accepted → send the full Template A/B immediately** (`channel: "dm", type: "initial"`, variant from the queued event). The reply sweep watches pending invites and fires this in the same session it detects the acceptance; the +4d/+10d cadence anchors on THIS send. **This DM (not the acceptance) moves Ashby `New Lead → Reached Out`.**
4. **Invite unaccepted after ~4 days → InMail escalation** (the hiring lead, 2026-07-28 — broadened from 85+-only; "use the 50 credits function"): send the full Template A/B as InMail (`channel: "inmail", type: "initial"`, variant from the queued event). Credits are the scarce resource (~50/mo, Sales Nav Core): drain the due queue **score-descending, ≤3/day** — lower scores wait their turn, credits never go to someone a higher score is waiting on. Invite still pending at +21 days with no InMail sent → `closed` (unresponsive) + archive the agent-created application with a note; a later acceptance reopens them (sweep logs `accepted`, sends the full template, reactivates the Ashby application).

**Unaccepted invite = no thread**: never message-spam or withdraw-and-resend an invite (LinkedIn flags it); the escalation path is the step-4 InMail or a verified work email, else `held` + flag. VERIFY the sent state on screen ("Invitation sent" / message in thread) before logging, and log `channel` as what actually happened (`dm` / `connect` / `inmail`). No channel available (LinkedIn Member, connect blocked, no email on file) → `held` event + flag to the hiring lead.

**Clicking on LinkedIn — refs only, never fuzzy text (2026-07-27 incident):** a `browser_run find text "Connect" click` matched the "People you may know" sidebar and fired a real invite at a non-candidate (withdrawn ~2 min later via `/mynetwork/invitation-manager/sent/` → "Withdraw invitation sent to <name>" → confirm in the dialog). So: `browser_snapshot` first, click by `ref` (`browser_click {ref:"@e34"}`), and confirm the ref's aria-label carries the candidate's name before clicking. The invite modal ("Add a note" / "Send invitation") lives in a nested browsing context — invisible to top-frame JS and `find` locators, and **coordinate clicks on its Send button silently close it without sending** — reach it by snapshot ref only. Then verify the toast before logging.

**After a VERIFIED send, in the same session:** append the `sent` event to the registry (`registry.py event`) → `longlist.py update <id> '{"status":"contacted"}'` → Ashby note **ending in the `#outreach` machine line** (source-of-truth rule above) + stage per the mapping below. Unverified = not sent; never log it as sent.

**Stage semantics (the hiring lead, 2026-07-29): `Reached Out` = a message with CONTENT was delivered — never a bare invite.**
- Bare connection request sent → note only, **stage STAYS `New Lead`** (the chip shows "invite pending"). The invite is a door-knock, not a message — same reasoning as the cadence anchor rule.
- Free DM / post-accept DM / InMail / (legacy) connect-note sent → note + **`New Lead → Reached Out`** at that moment.
- Invite accepted but template not yet sent → still `New Lead` (acceptance is not a message); the post-accept DM is what moves the stage.
- Reply → `Replied` as always. The +21d pending-invite close archives from `New Lead`.
This keeps metrics honest: invite→accept and message→reply are separate conversions; reply rate reads off Reached Out. **Adopted records (application created before 2026-07-01):** ensure the app has a pointer in `/workspace/pipeline/ashby-adopted-apps.json` (`{applicationId, candidateId, jobId, name}`) — the dashboard's Jul-1 cutoff hides old bulk apps, and this registry is how adopted ones stay visible (pointers only; all state still read live from Ashby).

**Cadence** (the hiring lead, 2026-07-27; anchors revised 2026-07-28): initial + up to 2 follow-ups — **followup1 due at initial +4 days, followup2 at initial +10 days** (calendar-day math off the latest `type: "initial"` `sent` timestamp in the ledger — for invite-path candidates that's the post-accept DM or the InMail, NEVER the invite itself; weekend-due → next weekday session), then **Unresponsive at ~+15 days** of silence. A reply anywhere → stop cadence, Ashby `Replied`, hand to conversation flow. Pending (unaccepted) invites are cadence-INELIGIBLE — no thread exists; their path is the step-4 InMail escalation or the +21d close. After an InMail with no reply AND still no accepted invite, there is no free follow-up channel — close as Unresponsive at +15d, never spend a second credit on the same person.

## Reply sweep & conversation sync (recurring trigger; also run after any send batch)

Purpose: no reply sits unanswered, every conversation is mirrored into Ashby's candidate feed, and non-repliers get the follow-up cadence. Runs off-slot (08:00 / 14:00 / 16:00 / 18:00 PT weekdays) so it never fights a search session for the browser.

**Gate first (cheap, no browser):** `registry.py cadence` — zero `sent` events for this OWNER → end with a one-line note. Otherwise build the working set from the registry: everyone whose latest event is `sent` (awaiting reply / mid-conversation) and `owner == OWNER` — the sweep answers only this install's threads (they're in this seat's inbox).

**Sweep:**
1. Open the LinkedIn inbox AND the Sales Navigator inbox (`/sales/inbox/` — live as of 2026-07-23; InMail replies land there). Also check pending-invitation state for invite-path candidates: newly accepted → log `accepted` + Ashby note (`Connection request accepted.` + `#outreach action=accepted channel=connect date=YYYY-MM-DD`) + send the full Template A/B in the same session (Channel order step 3) — the bare invite carried no content, so this DM is their `initial`.
2. Match each conversation to a candidate via the registry (`candidate_key` / `linkedin_url` / name; `registry.py pull` or the cadence output).
3. **On a new reply:**
   - Registry: `registry.py event '{"candidate_key":"in/…","role":"…","action":"replied","payload":{"channel":"dm"}}'`. Longlist: `update <id> '{"status":"replied"}'`.
   - Ashby: stage → `Replied` (agent-created apps, Lead stages — allowed) and **append the FULL new exchange to the candidate feed as a note**, verbatim with speaker labels and timestamps: `LinkedIn conversation (2026-07-23):\n[Candidate] …\n[the hiring lead] …`, ending with `#outreach action=replied channel=dm date=YYYY-MM-DD` (dashboard parses the tag). Every subsequent sweep appends only the NEW messages — the feed accumulates the complete thread. Link-shared and booked notes carry their tags too (`action=link-shared` / `action=booked`).
   - **Respond in the same session** (you write as the hiring lead, {{COMPANY}} voice): answer directly from role memory, keep it short and human, always end with a concrete next step toward a chat. Log the sent reply in the same Ashby note + a ledger event. Questions beyond role memory (comp specifics, equity, visa) → do NOT improvise; tell them the hiring lead will follow up on that point, and flag it at the TOP of the session summary.
   - **Candidate is positive about talking:** send the hiring lead's booking link in the same reply — `{{BOOKING_LINK}}` ("grab any slot that works…"). Google auto-creates the event + emails them the invite/join link when they book. Ledger `link-shared` event + Ashby note. There is NO calendar watcher (deleted 2026-07-27) — a booking is only recorded when the candidate says so in the thread or Ashby shows a scheduled interview: then ledger `booked` + longlist `interview-scheduled`. Link shared but no booking evidence after 2–3 business days → ONE friendly nudge (counts as a cadence touch); check the thread and Ashby first so a booked candidate is never nudged. Positive replies also mean longlist `status: "in-conversation"` once a real exchange is going.
   - A clear "no thanks" → thank them briefly, Ashby stage stays Replied + note; longlist `update` status `rejected-by-candidate`; registry `unresponsive` event with `payload.reason: "declined"`; no follow-ups.
4. **Follow-up cadence (non-repliers — the hiring lead, 2026-07-27: +4d / +10d):** compute due-ness off the latest `type: "initial"` `sent` timestamp (post-accept DM or InMail — never the bare invite): initial ≥4 days old and no `followup1` → send `followup1`; initial ≥10 days old and no `followup2` → send `followup2`; initial ≥15 days old with silence after followup2 → mark **Unresponsive**: registry `unresponsive` event, longlist `status: "unresponsive"`, archive the agent-created Ashby application with an unresponsive/no-response reason + note. **Eligibility check first:** a thread must exist (DM/InMail sent, or invite accepted) — pending invites are skipped here; their escalation is the Channel-order step-4 InMail queue, drained by the daily 13:35 batch. Newly accepted invite → full Template A/B as the `initial` (Channel order step 3). Follow-ups use the role's T2/T3 templates verbatim, never "just bumping this". All sends count against the daily caps and go through the pre-send checklist.
5. Summary: flags first (wants-to-talk, beyond-scope questions, checkpoint hit), then replies handled / follow-ups sent / newly unresponsive, with real numbers only.

## Account safety (non-negotiable)

- You are acting AS the hiring lead. Human pace only: read pages, pause between actions, no rapid-fire pagination or tab storms.
- Daily caps: ≤ ~150 result cards harvested, ≤ ~50 full profile opens, ≤ ~5 pages per single query. Track counts in the session; stop at the cap and note it.
- CAPTCHA / security checkpoint / unusual-activity banner → STOP immediately, `request_browser_input`, and if unresolved end LinkedIn work for the session (never retry through a checkpoint).
- Never send messages/InMails from sourcing (harvest) work — sends happen only under the **Outreach sends** section's authorization + caps (feedback-ingestion and outbound sessions).
- If the Sales Nav search UI differs from these recipes (UI changes constantly), adapt, then UPDATE THIS SKILL with what actually worked.
