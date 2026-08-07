import { readdirSync, readFileSync, existsSync, appendFileSync } from "node:fs";
import { createHmac, randomBytes } from "node:crypto";

// Overridable so a fixture dir can be pointed at for testing without touching
// the live pipeline (or the live Ashby cache warm).
const PIPELINE_DIR = process.env.PIPELINE_DIR || "/workspace/pipeline";
const ENV_FILE = "/workspace/.env";
const UI_FILE = `${import.meta.dir}/public/index.html`;

// Data-source mode, read ONCE at boot. {"mode":"atsless"} switches every
// ATS-derived view (jobs, leads, active pipeline, interviews) to agent-kept
// records in ${PIPELINE_DIR}/atsless/candidates.jsonl — the Ashby API and
// ASHBY_API_KEY are never touched. Missing/unreadable file or any other mode
// value = live Ashby, byte-for-byte the pre-existing behavior.
//
// Display name for the system-of-record (user-visible UI strings only):
//   cfg.displayName (trimmed, non-empty) → that string
//   else mode === "atsless"              → "Pipeline"
//   else                                 → "Ashby"
// Exposed to the frontend as `sorName` on the main /api/data payload.
const { ATSLESS, SOR_NAME } = (() => {
  let cfg = null;
  try {
    cfg = JSON.parse(readFileSync(`${PIPELINE_DIR}/datasource.json`, "utf8"));
  } catch {
    cfg = null;
  }
  const atsless = !!(cfg && cfg.mode === "atsless");
  const custom =
    cfg && typeof cfg.displayName === "string" ? cfg.displayName.trim() : "";
  const sorName = custom || (atsless ? "Pipeline" : "Ashby");
  return { ATSLESS: atsless, SOR_NAME: sorName };
})();
const ATSLESS_FILE = `${PIPELINE_DIR}/atsless/candidates.jsonl`;

// Feedback loop files (the hiring lead's Advance/Reject reviews). The webhook config is
// SECRET — its url/secret/header must NEVER leak into a response or the client.
const WEBHOOK_CONFIG_FILE = `${PIPELINE_DIR}/.feedback-webhook.json`;
const QUEUE_FILE = `${PIPELINE_DIR}/feedback-queue.jsonl`; // server APPENDS only
const PROCESSED_FILE = `${PIPELINE_DIR}/feedback-processed.jsonl`; // read-only here
const CALIB_FILE = `${PIPELINE_DIR}/calibration.jsonl`; // read-only here
const OUTREACH_FILE = `${PIPELINE_DIR}/outreach-log.jsonl`; // read-only — real send ledger
const REGISTRY_FILE = `${PIPELINE_DIR}/registry.json`; // shared Google Sheets registry pointer
const PING_DEBOUNCE_MS = 90 * 1000; // one coalesced ping per burst of clicks
// Shared candidate registry (Google Sheets via authenticated proxy). Sourced
// candidates + outreach index read from here; Ashby-backed tabs are untouched.
const SHEETS_TTL_MS = 120 * 1000;
const SHEETS_CANDIDATES_RANGE = "candidates!A1:U100000";
const SHEETS_EVENTS_RANGE = "events!A1:F100000";

const ASHBY_BASE = "https://api.ashbyhq.com";
const ASHBY_URL = `${ASHBY_BASE}/job.list`;
const ASHBY_TTL_MS = 10 * 60 * 1000; // 10 minutes
const INTERVIEW_TTL_MS = 5 * 60 * 1000; // 5 minutes (interview schedules)
const APP_INFO_TTL_MS = 5 * 60 * 1000; // 5 minutes (per-application enrichment)
const APP_HISTORY_TTL_MS = 10 * 60 * 1000; // 10 minutes (per-application stage history)
const STAGEHIST_MAX_PER_REFRESH = 120; // cap on application.info history calls per refresh
const CAND_TTL_MS = 60 * 60 * 1000; // 60 minutes (per-candidate enrichment)
const ENRICH_MAX_PER_REFRESH = 40; // cap on candidate.info calls per pipeline refresh
const ENRICH_ROLE_LIMIT = 30; // only enrich roles with <= this many kept apps
// Interview stages we lay out as columns, in order.
const PIPELINE_STAGES = ["Initial Screen", "First Round", "Second Round", "Offer"];
// Leads (Tab) — Lead-status applications the hiring lead has advanced into Ashby. These are
// the pre-interview funnel stages, in order.
const LEAD_STAGES = ["New Lead", "Reached Out", "Replied"];
// Ashby holds ~3,873 historical bulk leads from pre-July 2025 campaigns that must
// stay OUT of the UI (standing decision). createdAfter (epoch-ms NUMBER — verified
// working against the live application.list API) keeps them out of every fetch.
const LEADS_CREATED_AFTER = Date.parse("2026-07-01T00:00:00Z");
const LEADS_TTL_MS = 10 * 60 * 1000; // 10 minutes (leads pipeline)
const LEADS_ENRICH_MAX_PER_REFRESH = 60; // cap on candidate.info calls per leads refresh
// Adopted-record registry: pre-Jul-1 Ashby applications the agent works (bare
// bulk-touch records adopted on the hiring lead's Advance). The createdAfter filter would
// hide them, so ingestion sessions append pointers here at adopt time and the
// server fetches each application LIVE from Ashby — the file holds ids only,
// never state. Ashby remains the single source of truth for everything shown.
const ADOPTED_FILE = `${PIPELINE_DIR}/ashby-adopted-apps.json`;
// Outreach display state comes from Ashby candidate NOTES (source of truth —
// the hiring lead, 2026-07-29), parsed per candidate. Cached like the other enrichments.
const NOTES_TTL_MS = 10 * 60 * 1000; // 10 minutes (candidate notes)
const NOTES_MAX_PER_REFRESH = 80; // cap on candidate.listNotes calls per refresh
// Ashby sits behind Cloudflare bot protection; a browser-ish UA is required.
const ASHBY_UA =
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36";

// ---------------------------------------------------------------------------
// Generic file helpers
// ---------------------------------------------------------------------------
function parseJsonl(filePath) {
  const out = [];
  if (!existsSync(filePath)) return out;
  let text;
  try {
    text = readFileSync(filePath, "utf8");
  } catch {
    return out;
  }
  for (const line of text.split("\n")) {
    const t = line.trim();
    if (!t) continue;
    try {
      out.push(JSON.parse(t));
    } catch {
      // skip malformed line, keep going
    }
  }
  return out;
}

// LinkedIn is a hard condition (the hiring lead 2026-07-24): a candidate with no resolvable
// linkedin.com/in/ profile can never be advanced or contacted, so showing one on
// the sourced list only burns a click. Placeholder slugs (UNKNOWN-*, pending-*)
// wear a linkedin.com/in/ costume and must be treated as unresolved.
function hasRealLinkedIn(c) {
  if (!c || c.needs_linkedin === true) return false;
  const u = String(c.linkedin_url || "").trim().toLowerCase();
  const at = u.indexOf("linkedin.com/in/");
  if (!u.startsWith("http") || at === -1) return false;
  const slug = u.slice(at + "linkedin.com/in/".length).replace(/\/+$/, "");
  if (!slug) return false;
  return !/^(unknown|tbd|placeholder|pending)/.test(slug);
}

function loadRoleCandidates(file) {
  const all = parseJsonl(file);
  const shown = all.filter(hasRealLinkedIn);
  const hidden = all.length - shown.length;
  if (hidden > 0) {
    console.log(
      `[linkedin-gate] ${file}: ${hidden} record(s) hidden from the sourced list (no resolvable linkedin.com/in/ profile)`
    );
  }
  return shown;
}

function slugToLabel(slug) {
  return slug
    .split("-")
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function discoverRoleFiles() {
  let files = [];
  try {
    files = readdirSync(PIPELINE_DIR);
  } catch {
    return [];
  }
  return files
    .filter((f) => /^longlist-.+\.jsonl$/.test(f))
    .map((f) => ({
      slug: f.slice("longlist-".length, f.length - ".jsonl".length),
      file: `${PIPELINE_DIR}/${f}`,
    }))
    .sort((a, b) => a.slug.localeCompare(b.slug));
}

// Local-file fallback: role_slug → longlist candidates (LinkedIn-gated).
function loadLocalCandidatesByRole() {
  const byRole = {};
  for (const rf of discoverRoleFiles()) {
    byRole[rf.slug] = loadRoleCandidates(rf.file);
  }
  return byRole;
}

// Read the role manifest fresh on every request.
function readManifest() {
  try {
    const text = readFileSync(`${PIPELINE_DIR}/roles.json`, "utf8");
    const obj = JSON.parse(text);
    return obj && typeof obj === "object" ? obj : {};
  } catch {
    return {};
  }
}

// ---------------------------------------------------------------------------
// Env + shared Google Sheets registry (sourced candidates + outreach events).
// Secrets stay server-side; never log PROXY_TOKEN / ASHBY_API_KEY values.
// ---------------------------------------------------------------------------
function readEnvVar(name) {
  let text;
  try {
    text = readFileSync(ENV_FILE, "utf8");
  } catch {
    return null;
  }
  for (const line of text.split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    if (k !== name) continue;
    let v = t.slice(eq + 1).trim();
    if (v[0] === '"' || v[0] === "'") {
      const q = v[0];
      const end = v.indexOf(q, 1);
      v = end === -1 ? v.slice(1) : v.slice(1, end);
    } else {
      const hash = v.indexOf("#"); // strip inline "# Display Name" comment
      if (hash !== -1) v = v.slice(0, hash).trim();
    }
    return v || null;
  }
  return null;
}

function readAshbyKey() {
  return readEnvVar("ASHBY_API_KEY");
}

function readRegistryConfig() {
  try {
    const obj = JSON.parse(readFileSync(REGISTRY_FILE, "utf8"));
    if (obj && typeof obj === "object" && obj.spreadsheet_id) return obj;
  } catch {
    // missing/unreadable
  }
  return null;
}

// Module flag exposed on /api/data so the UI can show sheet vs local-fallback.
let registrySource = "local-fallback";

// range → { at, values } | inflight promise (single-flight + 120s TTL)
const sheetValueCache = new Map();

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function fetchSheetValues(range) {
  const cached = sheetValueCache.get(range);
  if (cached && cached.values && cached.at && Date.now() - cached.at < SHEETS_TTL_MS) {
    return cached.values;
  }
  if (cached && cached.inflight) return cached.inflight;

  const inflight = (async () => {
    const cfg = readRegistryConfig();
    if (!cfg || !cfg.spreadsheet_id) {
      throw new Error("registry.json missing spreadsheet_id");
    }
    const base = readEnvVar("PROXY_BASE_URL");
    const accountId = readEnvVar("GSHEETS_ACCOUNT_ID");
    const token = readEnvVar("PROXY_TOKEN");
    if (!base || !accountId || !token) {
      throw new Error("PROXY_BASE_URL / GSHEETS_ACCOUNT_ID / PROXY_TOKEN missing from .env");
    }
    const url =
      `${base.replace(/\/+$/, "")}/${accountId}` +
      `/sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(cfg.spreadsheet_id)}` +
      `/values/${encodeURIComponent(range)}`;

    const backoffs = [400, 1000, 2500];
    let lastErr = null;
    for (let attempt = 0; attempt <= backoffs.length; attempt++) {
      try {
        const res = await fetch(url, {
          method: "GET",
          headers: {
            Authorization: "Bearer " + token,
            Accept: "application/json",
          },
        });
        if (res.status === 429 || res.status >= 500) {
          lastErr = new Error(`Sheets proxy HTTP ${res.status} for ${range}`);
          if (attempt < backoffs.length) {
            await sleep(backoffs[attempt]);
            continue;
          }
          throw lastErr;
        }
        if (!res.ok) {
          throw new Error(`Sheets proxy HTTP ${res.status} for ${range}`);
        }
        const data = await res.json();
        const values = Array.isArray(data && data.values) ? data.values : [];
        sheetValueCache.set(range, { at: Date.now(), values });
        return values;
      } catch (e) {
        lastErr = e;
        const msg = String((e && e.message) || e);
        const retryable = /HTTP (429|5\d\d)/.test(msg) || /fetch failed|ECONN|ETIMEDOUT|network/i.test(msg);
        if (retryable && attempt < backoffs.length) {
          await sleep(backoffs[attempt]);
          continue;
        }
        throw e;
      }
    }
    throw lastErr || new Error(`Sheets fetch failed for ${range}`);
  })();

  sheetValueCache.set(range, { ...(cached || {}), inflight });
  try {
    return await inflight;
  } catch (e) {
    const cur = sheetValueCache.get(range);
    if (cur && cur.inflight === inflight) {
      // Drop the failed inflight so the next caller retries; keep any prior fresh values.
      if (cur.values && cur.at && Date.now() - cur.at < SHEETS_TTL_MS) {
        sheetValueCache.set(range, { at: cur.at, values: cur.values });
      } else {
        sheetValueCache.delete(range);
      }
    }
    throw e;
  } finally {
    const cur = sheetValueCache.get(range);
    if (cur && cur.inflight === inflight && cur.values) {
      sheetValueCache.set(range, { at: cur.at || Date.now(), values: cur.values });
    }
  }
}

function sheetHeaders(row) {
  return (row || []).map((h) => String(h || "").trim());
}

function sheetRowObject(headers, row) {
  const obj = {};
  for (let i = 0; i < headers.length; i++) {
    const key = headers[i];
    if (!key) continue;
    const v = row[i];
    obj[key] = v == null ? "" : v;
  }
  return obj;
}

function parseMaybeJson(raw, fallback) {
  if (raw == null || raw === "") return fallback;
  if (typeof raw === "object") return raw;
  try {
    return JSON.parse(String(raw));
  } catch {
    return fallback;
  }
}

function overlaySheetCandidate(col) {
  const base = parseMaybeJson(col.payload, {});
  const c = base && typeof base === "object" && !Array.isArray(base) ? { ...base } : {};

  // Column values win over payload (current-state table).
  if (col.candidate_key) {
    c.id = col.candidate_key;
    c.candidate_key = col.candidate_key;
  }
  if (col.name) c.name = String(col.name);
  if (col.linkedin_url) c.linkedin_url = String(col.linkedin_url);
  if (col.score !== "" && col.score != null && col.score !== undefined) {
    const n = Number(col.score);
    if (!Number.isNaN(n)) c.score = n;
  }
  if (col.status) c.status = String(col.status);
  if (col.owner !== undefined && col.owner !== null && String(col.owner).trim() !== "") {
    c.owner = String(col.owner).trim();
  }
  if (col.queue_state !== undefined) c.queue_state = col.queue_state ? String(col.queue_state) : null;
  if (col.advanced_by !== undefined) c.advanced_by = col.advanced_by ? String(col.advanced_by) : null;
  if (col.sourced_by !== undefined) c.sourced_by = col.sourced_by ? String(col.sourced_by) : null;
  if (col.sourced_date) c.sourced_date = String(col.sourced_date);
  if (col.advanced_date) c.advanced_date = String(col.advanced_date);
  if (col.ashby_candidate_id) c.ashby_id = String(col.ashby_candidate_id);
  if (col.ashby_application_id) c.ashby_application_id = String(col.ashby_application_id);
  if (col.variant) c.variant = String(col.variant);
  if (col.last_action) c.last_action = String(col.last_action);
  if (col.last_action_date) c.last_action_date = String(col.last_action_date);
  if (col.flags !== undefined && col.flags !== null && String(col.flags).trim() !== "") {
    // Keep arrays from payload when the column is empty; otherwise take the cell.
    c.flags = col.flags;
  }
  if (!c.id && c.linkedin_url) {
    const k = String(c.linkedin_url).trim().toLowerCase();
    const m = k.match(/\/in\/([^/?#]+)/);
    if (m) c.id = "in/" + m[1].replace(/\/+$/, "");
  }
  return c;
}

function parseCandidatesSheet(values) {
  const byRole = {};
  if (!values || !values.length) return byRole;
  const headers = sheetHeaders(values[0]);
  let hidden = 0;
  let total = 0;
  for (let r = 1; r < values.length; r++) {
    const row = values[r] || [];
    if (!row.length || row.every((c) => c == null || String(c).trim() === "")) continue;
    const col = sheetRowObject(headers, row);
    const role = String(col.role || "").trim();
    if (!role) continue;
    total += 1;
    if (!Object.prototype.hasOwnProperty.call(byRole, role)) byRole[role] = [];
    const cand = overlaySheetCandidate(col);
    if (!hasRealLinkedIn(cand)) {
      hidden += 1;
      continue;
    }
    byRole[role].push(cand);
  }
  if (hidden > 0) {
    console.log(
      `[linkedin-gate] registry candidates: ${hidden}/${total} record(s) hidden (no resolvable linkedin.com/in/ profile)`
    );
  }
  return byRole;
}

async function loadSourcedCandidatesByRole() {
  try {
    const values = await fetchSheetValues(SHEETS_CANDIDATES_RANGE);
    const byRole = parseCandidatesSheet(values);
    registrySource = "sheet";
    const n = Object.values(byRole).reduce((a, b) => a + b.length, 0);
    console.log(
      `[registry] candidates from sheet: ${n} shown across ${Object.keys(byRole).length} role(s)`
    );
    return byRole;
  } catch (e) {
    registrySource = "local-fallback";
    console.error(
      "[registry] candidates sheet failed — falling back to local longlist-*.jsonl:",
      String((e && e.message) || e)
    );
    return loadLocalCandidatesByRole();
  }
}

// Map a Sheets events-tab row onto the legacy outreach-log.jsonl shape so the
// rest of buildOutreachIndex stays unchanged (incl. candidate_key → id).
function parseEventsSheet(values) {
  const out = [];
  if (!values || !values.length) return out;
  const headers = sheetHeaders(values[0]);
  for (let r = 1; r < values.length; r++) {
    const row = values[r] || [];
    if (!row.length || row.every((c) => c == null || String(c).trim() === "")) continue;
    const col = sheetRowObject(headers, row);
    const payload = parseMaybeJson(col.payload, {}) || {};
    const candidateKey = col.candidate_key ? String(col.candidate_key) : null;
    const ev = {
      ts: col.ts || payload.ts || null,
      date: payload.date || null,
      actor: col.actor || payload.actor || null,
      candidate_key: candidateKey,
      id: candidateKey || payload.id || null, // legacy field name
      role: col.role || payload.role || null,
      action: col.action || payload.action || payload.event || null,
      event: payload.event || null,
      channel: payload.channel || null,
      type: payload.type || null,
      variant: payload.variant || null,
      message: payload.message || null,
      note: payload.note || null,
      reason: payload.reason || null,
      verify: payload.verify || null,
      subject: payload.subject || null,
      name: payload.name || payload.candidate || null,
      linkedin_url: payload.linkedin_url || null,
      by: payload.by || col.actor || null,
      source_event: payload.source_event || null,
    };
    // If payload only has a nested blob, still accept top-level channel fields.
    out.push(ev);
  }
  return out;
}

async function loadOutreachEvents() {
  try {
    const values = await fetchSheetValues(SHEETS_EVENTS_RANGE);
    const rows = parseEventsSheet(values);
    // If candidates already fell back, keep local-fallback; otherwise sheet.
    if (registrySource !== "local-fallback") registrySource = "sheet";
    console.log(`[registry] outreach events from sheet: ${rows.length}`);
    return rows;
  } catch (e) {
    console.error(
      "[registry] events sheet failed — falling back to local outreach-log.jsonl:",
      String((e && e.message) || e)
    );
    // Only flip the global flag if candidates also aren't on sheet this request.
    // (Candidates loader runs first in buildData and owns the primary flag.)
    return parseJsonl(OUTREACH_FILE);
  }
}

// ---------------------------------------------------------------------------
// Ashby API — SERVER-SIDE ONLY. The key is read here and never leaves the box.
// ---------------------------------------------------------------------------

// Basic-auth header from the on-box key. The key is NEVER shipped to clients.
function ashbyAuthHeader() {
  const key = readAshbyKey();
  if (!key) throw new Error("ASHBY_API_KEY not found in /workspace/.env");
  return "Basic " + Buffer.from(key + ":").toString("base64");
}

// Single POST to an Ashby endpoint (e.g. "job.list", "application.list").
// Reused by every Ashby fetcher so the Cloudflare-friendly UA + auth live once.
async function ashbyPost(endpoint, body) {
  const res = await fetch(`${ASHBY_BASE}/${endpoint}`, {
    method: "POST",
    headers: {
      Authorization: ashbyAuthHeader(),
      "Content-Type": "application/json",
      Accept: "application/json",
      "User-Agent": ASHBY_UA,
    },
    body: JSON.stringify(body || {}),
  });
  if (!res.ok) throw new Error(`Ashby HTTP ${res.status} (${endpoint})`);
  const data = await res.json();
  if (data && data.success === false) {
    throw new Error(`Ashby ${endpoint} returned success=false`);
  }
  return data;
}

// Interview-only wrapper: retries on 429 (rate limit) with short backoff. Scoped
// to the interview endpoints so it never slows the pre-existing pipeline path.
async function ashbyPostRetry(endpoint, body) {
  const backoffs = [300, 700, 1200];
  for (let attempt = 0; ; attempt++) {
    try {
      return await ashbyPost(endpoint, body);
    } catch (e) {
      const is429 = /HTTP 429/.test(String((e && e.message) || e));
      if (is429 && attempt < backoffs.length) {
        await new Promise((r) => setTimeout(r, backoffs[attempt]));
        continue;
      }
      throw e;
    }
  }
}

async function fetchAllOpenJobs() {
  let cursor = null;
  let pages = 0;
  const all = [];
  do {
    const body = { status: ["Open"] };
    if (cursor) body.cursor = cursor;
    const data = await ashbyPost("job.list", body);
    for (const j of data.results || []) {
      // keep only the fields we need; never ship raw job objects to clients
      all.push({ id: j.id, title: j.title });
    }
    cursor = data.moreDataAvailable && data.nextCursor ? data.nextCursor : null;
    pages += 1;
  } while (cursor && pages < 25);

  return all;
}

// ---------------------------------------------------------------------------
// Active pipeline (Tab 3) — live interview-stage applications per open job.
// ---------------------------------------------------------------------------

// All Active applications for one job, following pagination.
async function fetchActiveApps(jobId) {
  let cursor = null;
  let pages = 0;
  const all = [];
  do {
    const body = { jobId, status: "Active", limit: 100 };
    if (cursor) body.cursor = cursor;
    const data = await ashbyPost("application.list", body);
    for (const a of data.results || []) all.push(a);
    cursor = data.moreDataAvailable && data.nextCursor ? data.nextCursor : null;
    pages += 1;
  } while (cursor && pages < 30);
  return all;
}

// Per-candidate enrichment cache: id -> { url, position, company, fetchedAt }.
const candCache = new Map();

// Fetch (and cache) one candidate's LinkedIn URL + position/company.
// Returns null on failure so callers degrade to a card without a link.
async function fetchCandidateInfo(id) {
  const now = Date.now();
  const cached = candCache.get(id);
  if (cached && now - cached.fetchedAt < CAND_TTL_MS) return cached;
  try {
    const data = await ashbyPost("candidate.info", { id });
    const r = (data && data.results) || {};
    const links = Array.isArray(r.socialLinks) ? r.socialLinks : [];
    const li = links.find(
      (s) => s && s.url && /linkedin/i.test(String(s.type || ""))
    );
    const rec = {
      url: li ? li.url : null,
      position: r.position || null,
      company: r.company || null,
      // Candidate tags (e.g. "agent-sourced") — whitelist titles to strings only.
      tags: Array.isArray(r.tags) ? r.tags.map((t) => t && t.title).filter(Boolean) : [],
      fetchedAt: now,
    };
    candCache.set(id, rec);
    return rec;
  } catch {
    return null; // degrade gracefully
  }
}

function applyEnrichment(app, info) {
  app.linkedin_url = info.url || null;
  app.position = info.position || null;
  app.company = info.company || null;
  // Extra field for the Leads tab; existing pipeline callers simply ignore it.
  app.tags = info.tags || [];
}

// LinkedIn enrichment for smaller roles only, capped per refresh. Groups apps
// by candidateId (dedupe), serves cache hits inline, then fetches the rest in
// parallel up to the budget — MUTATING the app objects in place. Because the
// pipeline cache holds these same objects, badges appear on the next read once
// this completes. Runs in the background so it never blocks the response.
async function enrichPipeline(jobs, byJob) {
  const byId = new Map(); // candidateId -> [app, ...]
  const order = []; // candidateIds needing a fetch, in encounter order
  const now = Date.now();
  for (const job of jobs) {
    const rec = byJob[job.id];
    if (!rec || rec.kept.length > ENRICH_ROLE_LIMIT) continue;
    for (const app of rec.kept) {
      if (!app.candidateId) continue;
      const cached = candCache.get(app.candidateId);
      if (cached && now - cached.fetchedAt < CAND_TTL_MS) {
        applyEnrichment(app, cached);
        continue;
      }
      if (!byId.has(app.candidateId)) {
        byId.set(app.candidateId, []);
        order.push(app.candidateId);
      }
      byId.get(app.candidateId).push(app);
    }
  }
  const toFetch = order.slice(0, ENRICH_MAX_PER_REFRESH);
  await Promise.all(
    toFetch.map(async (id) => {
      const info = await fetchCandidateInfo(id);
      if (info) for (const app of byId.get(id) || []) applyEnrichment(app, info);
    })
  );
}

// ---------------------------------------------------------------------------
// Per-application STAGE HISTORY (Ashby-style candidate timeline). application.info
// returns results.applicationHistory: an ordered list of stage entries with ISO
// enteredStageAt / leftStageAt (leftStageAt absent = the current stage). Cached
// by applicationId; the actual fetch runs DETACHED from the pipeline build (like
// enrichPipeline) so the /api/data response never blocks on these round-trips.
// ---------------------------------------------------------------------------
const stageHistoryCache = new Map(); // appId -> { history, appliedAt, source, fetchedAt }

async function fetchStageHistory(appId) {
  if (!appId) return null;
  const now = Date.now();
  const cached = stageHistoryCache.get(appId);
  if (cached && now - cached.fetchedAt < APP_HISTORY_TTL_MS) return cached;
  try {
    const data = await ashbyPostRetry("application.info", { applicationId: appId });
    const r = (data && data.results) || {};
    const raw = Array.isArray(r.applicationHistory) ? r.applicationHistory : [];
    // Whitelist the timeline fields the UI consumes (never ship raw objects).
    const history = raw.map((h) => ({
      id: (h && h.id) || null,
      stageId: (h && h.stageId) || null,
      title: (h && h.title) || null,
      stageNumber: h && typeof h.stageNumber === "number" ? h.stageNumber : null,
      enteredStageAt: (h && h.enteredStageAt) || null,
      leftStageAt: (h && h.leftStageAt) || null, // absent => current stage
    }));
    const rec = {
      history,
      appliedAt: r.createdAt || null,
      source: (r.source && r.source.title) || null,
      fetchedAt: now,
    };
    stageHistoryCache.set(appId, rec);
    return rec;
  } catch {
    return null; // degrade: card still renders without a timeline
  }
}

function applyStageHistory(app, rec) {
  app.stageHistory = Array.isArray(rec.history) ? rec.history : [];
  if (rec.appliedAt) app.appliedAt = rec.appliedAt;
  if (!app.source && rec.source) app.source = rec.source;
}

// Attach applicationHistory to every kept active-pipeline app, MUTATING the app
// objects in place. Cache hits apply inline; misses are fetched in parallel up to
// the budget. Runs detached from buildActivePipeline so it never blocks the read;
// because pipeCache holds these same objects, timelines materialize on the next
// read once this completes.
async function enrichStageHistory(jobs, byJob) {
  const now = Date.now();
  const toFetch = [];
  for (const job of jobs) {
    const rec = byJob[job.id];
    if (!rec) continue;
    for (const app of rec.kept) {
      if (!app.applicationId) continue;
      const cached = stageHistoryCache.get(app.applicationId);
      if (cached && now - cached.fetchedAt < APP_HISTORY_TTL_MS) {
        applyStageHistory(app, cached);
        continue;
      }
      toFetch.push(app);
    }
  }
  const batch = toFetch.slice(0, STAGEHIST_MAX_PER_REFRESH);
  // Bounded concurrency: many parallel application.info calls otherwise trip
  // Ashby rate limits (429), and failed fetches leave a card without a timeline
  // until the next build. Chunks of 8 keep coverage high while staying polite.
  const CONCURRENCY = 8;
  for (let i = 0; i < batch.length; i += CONCURRENCY) {
    const chunk = batch.slice(i, i + CONCURRENCY);
    await Promise.all(
      chunk.map(async (app) => {
        const rec = await fetchStageHistory(app.applicationId);
        if (rec) applyStageHistory(app, rec);
      })
    );
  }
}

// Build the pipeline map (jobId -> { kept: [...] }) for the given jobs.
// Throws on hard fetch failure so the cache layer can fall back to last-good.
// Ashby calls are parallelized; enrichment is fired in the background so the
// returned structure (names, stages, dates, staleness) is available fast.
async function buildActivePipeline(jobs) {
  const byJob = {};

  // Fetch + bucket every job's Active applications, in parallel.
  const fetched = await Promise.all(
    jobs.map(async (job) => ({ jobId: job.id, apps: await fetchActiveApps(job.id) }))
  );
  for (const { jobId, apps } of fetched) {
    const kept = [];
    for (const a of apps) {
      const stageTitle =
        (a.currentInterviewStage && a.currentInterviewStage.title) || null;
      if (stageTitle === "Application Review") continue; // excluded entirely
      const bucket = PIPELINE_STAGES.includes(stageTitle) ? stageTitle : "Other";
      kept.push({
        applicationId: a.id || null,
        candidateId: (a.candidate && a.candidate.id) || null,
        name: (a.candidate && a.candidate.name) || "Unknown",
        stage: bucket,
        stageTitle,
        createdAt: a.createdAt || null,
        appliedAt: a.createdAt || null, // authoritative createdAt from application.info overrides in enrichStageHistory
        updatedAt: a.updatedAt || null,
        source: (a.source && a.source.title) || null,
        stageHistory: null, // filled by detached enrichStageHistory
      });
    }
    byJob[jobId] = { kept };
  }

  // Enrichment runs detached: it mutates the (now cached) app objects in place,
  // so LinkedIn badges + stage-history timelines materialize on the next read
  // without blocking this one.
  enrichPipeline(jobs, byJob).catch(() => {});
  enrichStageHistory(jobs, byJob).catch(() => {});

  return byJob;
}

// Cache with TTL + last-good fallback, mirroring the jobs cache.
// pipeInFlight coalesces concurrent cold builds so simultaneous requests
// (and the startup warm-up) share a single fetch instead of each paying full
// cold-start latency.
const pipeCache = { data: null, fetchedAt: 0, lastError: null };
let pipeInFlight = null;

async function getActivePipeline(jobs) {
  const now = Date.now();
  if (pipeCache.data && now - pipeCache.fetchedAt < ASHBY_TTL_MS) {
    return {
      byJob: pipeCache.data,
      fetchedAt: pipeCache.fetchedAt,
      fromCache: true,
      stale: false,
      error: null,
    };
  }
  try {
    if (!pipeInFlight) {
      pipeInFlight = buildActivePipeline(jobs).finally(() => {
        pipeInFlight = null;
      });
    }
    const byJob = await pipeInFlight;
    pipeCache.data = byJob;
    pipeCache.fetchedAt = Date.now();
    pipeCache.lastError = null;
    return { byJob, fetchedAt: pipeCache.fetchedAt, fromCache: false, stale: false, error: null };
  } catch (e) {
    const msg = String((e && e.message) || e);
    pipeCache.lastError = msg;
    if (pipeCache.data) {
      return {
        byJob: pipeCache.data,
        fetchedAt: pipeCache.fetchedAt,
        fromCache: true,
        stale: true,
        error: msg,
      };
    }
    return { byJob: null, fetchedAt: null, fromCache: false, stale: false, error: msg };
  }
}

// ---------------------------------------------------------------------------
// Leads (Tab) — Lead-status applications per open job (the hiring lead's advanced sourced
// candidates as they move New Lead -> Reached Out -> Replied). Mirrors the
// active-pipeline machinery: parallel fetch + bucket, detached enrichment
// (LinkedIn/position/company/tags + stage history), TTL cache with last-good
// fallback and in-flight coalescing. Historical bulk leads are excluded by the
// createdAfter filter (epoch-ms NUMBER) so only post-Jul-1 leads ever surface.
// ---------------------------------------------------------------------------

// All Lead applications for one job created after the cutoff, following pages.
async function fetchLeadApps(jobId) {
  let cursor = null;
  let pages = 0;
  const all = [];
  do {
    const body = { jobId, status: "Lead", createdAfter: LEADS_CREATED_AFTER, limit: 100 };
    if (cursor) body.cursor = cursor;
    const data = await ashbyPost("application.list", body); // mirrors fetchActiveApps exactly
    for (const a of data.results || []) all.push(a);
    cursor = data.moreDataAvailable && data.nextCursor ? data.nextCursor : null;
    pages += 1;
  } while (cursor && pages < 30);
  return all;
}

// LinkedIn/position/company/tags enrichment for lead cards. Reuses fetchCandidateInfo
// + applyEnrichment (mutating apps in place), capped per refresh with bounded
// concurrency. Unlike enrichPipeline it applies NO per-role size cutoff — every
// role's leads are eligible; the per-refresh cap is the only limit. Runs detached.
async function enrichLeads(jobs, byJob) {
  const byId = new Map(); // candidateId -> [app, ...]
  const order = []; // candidateIds needing a fetch, in encounter order
  const now = Date.now();
  for (const job of jobs) {
    const rec = byJob[job.id];
    if (!rec) continue;
    for (const app of rec.kept) {
      if (!app.candidateId) continue;
      const cached = candCache.get(app.candidateId);
      if (cached && now - cached.fetchedAt < CAND_TTL_MS) {
        applyEnrichment(app, cached);
        continue;
      }
      if (!byId.has(app.candidateId)) {
        byId.set(app.candidateId, []);
        order.push(app.candidateId);
      }
      byId.get(app.candidateId).push(app);
    }
  }
  const toFetch = order.slice(0, LEADS_ENRICH_MAX_PER_REFRESH);
  const CONCURRENCY = 8;
  for (let i = 0; i < toFetch.length; i += CONCURRENCY) {
    const chunk = toFetch.slice(i, i + CONCURRENCY);
    await Promise.all(
      chunk.map(async (id) => {
        const info = await fetchCandidateInfo(id);
        if (info) for (const app of byId.get(id) || []) applyEnrichment(app, info);
      })
    );
  }
}

// Adopted-record pointers -> live Ashby applications. The registry file holds
// {applicationId, candidateId, name?} entries; every field shown in the UI is
// fetched fresh from application.info here. Unknown/archived/moved-on apps are
// dropped naturally by the same stage filter as the bulk fetch.
async function fetchAdoptedApps(seenAppIds) {
  let reg = [];
  try {
    if (existsSync(ADOPTED_FILE)) reg = JSON.parse(readFileSync(ADOPTED_FILE, "utf8"));
  } catch {
    reg = [];
  }
  if (!Array.isArray(reg) || !reg.length) return [];
  const out = [];
  const CONCURRENCY = 8;
  const todo = reg.filter(
    (r) => r && r.applicationId && !seenAppIds.has(r.applicationId)
  );
  for (let i = 0; i < todo.length; i += CONCURRENCY) {
    const chunk = todo.slice(i, i + CONCURRENCY);
    await Promise.all(
      chunk.map(async (r) => {
        try {
          const data = await ashbyPostRetry("application.info", {
            applicationId: r.applicationId,
          });
          const a = (data && data.results) || null;
          if (a) out.push(a);
        } catch {
          /* skip — registry pointer to something we can't read right now */
        }
      })
    );
  }
  return out;
}

// Build the leads map (jobId -> { kept: [...] }) for the given jobs. Throws on
// hard fetch failure so the cache layer can fall back to last-good. Enrichment is
// fired detached so the returned structure (names, stages, dates) is available fast.
async function buildLeads(jobs) {
  const byJob = {};
  const jobIds = new Set(jobs.map((j) => j.id));

  const fetched = await Promise.all(
    jobs.map(async (job) => ({ jobId: job.id, apps: await fetchLeadApps(job.id) }))
  );
  const keepApp = (a) => {
    const stageTitle =
      (a.currentInterviewStage && a.currentInterviewStage.title) || null;
    if (!LEAD_STAGES.includes(stageTitle)) return null;
    return {
      applicationId: a.id || null,
      candidateId: (a.candidate && a.candidate.id) || null,
      name: (a.candidate && a.candidate.name) || "Unknown",
      stage: stageTitle,
      createdAt: a.createdAt || null,
      appliedAt: a.createdAt || null, // authoritative createdAt overridden by enrichStageHistory
      updatedAt: a.updatedAt || null,
      source: (a.source && a.source.title) || null,
      stageHistory: null, // filled by detached enrichStageHistory
      tags: [], // filled by detached enrichLeads (from candidate.info)
      outreachEvents: null, // filled by detached enrichLeadNotes (Ashby notes)
    };
  };
  const seenAppIds = new Set();
  for (const { jobId, apps } of fetched) {
    const kept = [];
    for (const a of apps) {
      const app = keepApp(a);
      if (!app) continue;
      kept.push(app);
      if (app.applicationId) seenAppIds.add(app.applicationId);
    }
    byJob[jobId] = { kept };
  }

  // Adopted (pre-Jul-1) applications the agent actively works — registry
  // pointers resolved to live Ashby state and merged into their job's bucket.
  const adopted = await fetchAdoptedApps(seenAppIds);
  for (const a of adopted) {
    const jobId = (a.job && a.job.id) || null;
    if (!jobId || !jobIds.has(jobId)) continue;
    const app = keepApp(a);
    if (!app) continue;
    app.adopted = true;
    if (!byJob[jobId]) byJob[jobId] = { kept: [] };
    byJob[jobId].kept.push(app);
    if (app.applicationId) seenAppIds.add(app.applicationId);
  }

  // Detached enrichment mutates the (now cached) app objects in place, so
  // LinkedIn badges, tags, notes timelines and days-in-stage materialize on
  // the next read.
  enrichLeads(jobs, byJob).catch(() => {});
  enrichStageHistory(jobs, byJob).catch(() => {});
  enrichLeadNotes(jobs, byJob).catch(() => {});

  return byJob;
}

// ---------------------------------------------------------------------------
// Outreach state from Ashby candidate NOTES (single source of truth — the hiring lead,
// 2026-07-29). Every outreach the agent performs is logged as a note on the
// candidate (plus a stage change); the dashboard renders ONLY what Ashby holds.
// New notes end with a machine line the batch/sweep sessions write:
//   #outreach action=sent channel=connect type=invite variant=A date=2026-07-28
// Legacy notes (pre-2026-07-29) are recognized by wording heuristics.
// ---------------------------------------------------------------------------
const notesCache = new Map(); // candidateId -> { events, fetchedAt }

// Parse one Ashby note into an outreach event, or null when the note is not an
// outreach/advance record (score notes, duplicate flags, etc.).
function parseOutreachNote(text, createdAt) {
  if (!text) return null;
  const t = String(text);
  const lower = t.toLowerCase();

  // Never treat consolidation/duplicate bookkeeping as outreach.
  if (lower.startsWith("duplicate record") || lower.startsWith("canonical record")) return null;
  if (lower.includes("duplicate consolidation") && !lower.includes("#outreach")) {
    // consolidation copies carry their own #outreach tag; bare bookkeeping doesn't
  }

  // Event date: prefer the tag's date=, else the first YYYY-MM-DD in the text
  // (sends are often logged hours later), else the note's own createdAt.
  const noteTs = createdAt || null;
  const dateFor = (explicit) => {
    if (explicit) {
      // Keep the note's clock time when the day matches, else noon UTC.
      if (noteTs && String(noteTs).slice(0, 10) === explicit) return noteTs;
      return explicit + "T12:00:00Z";
    }
    return noteTs;
  };

  // --- structured tag line (authoritative when present)
  const tag = t.match(/#outreach\b([^\n]*)/i);
  if (tag) {
    const kv = {};
    for (const m of tag[1].matchAll(/(\w+)=([\w-]+)/g)) kv[m[1].toLowerCase()] = m[2];
    if (kv.action) {
      return {
        action: kv.action,
        channel: kv.channel || null,
        type: kv.type || null,
        variant: kv.variant ? kv.variant.toUpperCase() : null,
        ts: dateFor(kv.date || null),
        message: extractNoteMessage(t),
        subject: extractNoteSubject(t),
      };
    }
  }

  // --- legacy heuristics
  const textDate = (t.match(/\b(20\d\d-\d\d-\d\d)\b/) || [])[1] || null;
  const ts = dateFor(textDate);
  const variant = ((t.match(/\b(?:variant|template)\s+([AB])\b/i) || [])[1] || "").toUpperCase() || null;
  const base = { ts, variant, message: extractNoteMessage(t), subject: extractNoteSubject(t) };

  // Advance / adopt bookkeeping -> a single "advanced" timeline node.
  if (
    lower.startsWith("[agent-sourced") ||
    lower.startsWith("agent-sourced") ||
    lower.startsWith("advanced by tim") ||
    lower.startsWith("tim advanced")
  ) {
    return { action: "advanced", channel: null, type: null, variant: null, ts: noteTs, message: null, subject: null };
  }

  const isOutreachy =
    lower.includes("outreach") ||
    lower.includes("inmail") ||
    lower.includes("connection request") ||
    lower.includes("linkedin dm") ||
    lower.includes("free dm") ||
    lower.includes("booking link") ||
    lower.includes("interview booked") ||
    lower.includes("invite accepted") ||
    lower.includes("connection accepted") ||
    lower.includes("reply received") ||
    lower.includes("candidate replied") ||
    lower.includes("marked unresponsive");
  if (!isOutreachy) return null;

  if (lower.includes("reply received") || lower.includes("candidate replied"))
    return { ...base, action: "replied", channel: "linkedin", type: null };
  if (lower.includes("invite accepted") || lower.includes("connection accepted") || lower.includes("accepted the connection"))
    return { ...base, action: "accepted", channel: "connect", type: null };
  if (lower.includes("booking link"))
    return { ...base, action: "link-shared", channel: "linkedin", type: null };
  if (lower.includes("interview booked"))
    return { ...base, action: "booked", channel: null, type: null };
  if (lower.includes("marked unresponsive") || lower.includes("closed unresponsive"))
    return { ...base, action: "closed", channel: null, type: null };

  const followup = (lower.match(/follow[- ]?up\s*([12])/) || [])[1] || null;
  const ftype = followup ? "followup" + followup : "initial";

  // Channel classification: notes routinely MENTION other channels ("InMail
  // escalates at +4 days" on a bare-invite note, "connect-note invite
  // unaccepted" on an InMail note), so match specific channel markers against
  // the HEADER (first line) only and let the EARLIEST occurrence win.
  const header = lower.split("\n")[0].slice(0, 300);
  const markers = [
    { re: /bare connection request|connection request sent, no note/, channel: "connect" },
    { re: /connect-note|connection request with note/, channel: "connect-note" },
    { re: /inmail/, channel: "inmail" },
    { re: /free dm|linkedin dm|\(dm\b/, channel: "dm" },
  ];
  let best = null;
  for (const m of markers) {
    const hit = header.search(m.re);
    if (hit !== -1 && (best == null || hit < best.pos)) best = { pos: hit, channel: m.channel };
  }
  if (best) {
    if (best.channel === "connect")
      return { ...base, action: "sent", channel: "connect", type: "invite", variant: null, message: null };
    return { ...base, action: "sent", channel: best.channel, type: ftype };
  }
  // Fallbacks (no specific marker in the header).
  if (lower.includes("connection request sent") || lower.includes("connection request"))
    return { ...base, action: "sent", channel: "connect", type: "invite" };
  if (lower.includes("outreach sent"))
    return { ...base, action: "sent", channel: "linkedin", type: ftype };
  return null;
}

// Message body: text after "Message:" / "Full text:" (legacy), after the
// subject block, or — for header-classified sends — the greeting paragraph
// after the header. Trailing bookkeeping is stripped. Capped; UI truncates more.
function extractNoteMessage(t) {
  const m =
    t.match(/\b(?:Message|Full text)\s*:\s*"?\s*\n?([\s\S]+)/i) ||
    t.match(/\n\s*Subject:[^\n]*\n\s*\n([\s\S]+)/i) ||
    t.match(/\n\s*\n(Hi |Hey |Hello )([\s\S]+)/);
  if (!m) return null;
  let body = (m.length === 3 ? m[1] + m[2] : m[1]).trim();
  body = body.replace(/\n?#outreach\b[^\n]*$/i, "").trim();
  body = body.split(/\n\s*Verified\b/i)[0].trim(); // "Verified on screen: …" tail
  body = body.replace(/^"|"\s*$/g, "").trim();
  return body ? body.slice(0, 600) : null;
}
function extractNoteSubject(t) {
  const m = t.match(/(?:^|\n)\s*Subject:\s*([^\n]+)/i);
  return m ? m[1].trim().slice(0, 120) : null;
}

async function fetchCandidateNotes(candidateId) {
  if (!candidateId) return null;
  const now = Date.now();
  const cached = notesCache.get(candidateId);
  if (cached && now - cached.fetchedAt < NOTES_TTL_MS) return cached;
  try {
    const data = await ashbyPostRetry("candidate.listNotes", { candidateId });
    const raw = Array.isArray(data && data.results) ? data.results : [];
    const events = [];
    let advancedSeen = false;
    // Ashby returns newest-first; walk oldest-first so dedupe keeps the earliest.
    for (const n of raw.slice().reverse()) {
      let content = n && n.content;
      if (content && typeof content === "object") content = content.value || "";
      const ev = parseOutreachNote(String(content || ""), (n && n.createdAt) || null);
      if (!ev) continue;
      if (ev.action === "advanced") {
        if (advancedSeen) continue; // several bookkeeping notes -> one node
        advancedSeen = true;
      }
      events.push(ev);
    }
    events.sort((a, b) => String(a.ts || "").localeCompare(String(b.ts || "")));
    const rec = { events, fetchedAt: now };
    notesCache.set(candidateId, rec);
    return rec;
  } catch {
    return null; // degrade: card renders with "loading" timeline until next pass
  }
}

// Attach parsed Ashby-note outreach events to every lead app. Detached, capped,
// bounded concurrency — same pattern as enrichLeads/enrichStageHistory.
async function enrichLeadNotes(jobs, byJob) {
  const now = Date.now();
  const byCand = new Map(); // candidateId -> [app, ...]
  const order = [];
  for (const job of jobs) {
    const rec = byJob[job.id];
    if (!rec) continue;
    for (const app of rec.kept) {
      if (!app.candidateId) continue;
      const cached = notesCache.get(app.candidateId);
      if (cached && now - cached.fetchedAt < NOTES_TTL_MS) {
        app.outreachEvents = cached.events;
        continue;
      }
      if (!byCand.has(app.candidateId)) {
        byCand.set(app.candidateId, []);
        order.push(app.candidateId);
      }
      byCand.get(app.candidateId).push(app);
    }
  }
  const toFetch = order.slice(0, NOTES_MAX_PER_REFRESH);
  const CONCURRENCY = 8;
  for (let i = 0; i < toFetch.length; i += CONCURRENCY) {
    const chunk = toFetch.slice(i, i + CONCURRENCY);
    await Promise.all(
      chunk.map(async (id) => {
        const rec = await fetchCandidateNotes(id);
        if (rec) for (const app of byCand.get(id) || []) app.outreachEvents = rec.events;
      })
    );
  }
}

// TTL + last-good fallback + in-flight coalescing, mirroring getActivePipeline.
const leadsCache = { data: null, fetchedAt: 0, lastError: null };
let leadsInFlight = null;
let leadsEnrichInFlight = false;

// The enrichers are capped per pass (rate-limit politeness), so one pass can't
// cover every lead. Re-kick them on every cached read until nothing is missing —
// cache hits inside the enrichers make repeat passes cheap.
function kickLeadsEnrichment(jobs, byJob) {
  if (leadsEnrichInFlight || !byJob) return;
  let missing = false;
  for (const jobId of Object.keys(byJob)) {
    for (const app of (byJob[jobId] && byJob[jobId].kept) || []) {
      if (app.outreachEvents == null || app.stageHistory == null || app.linkedin_url === undefined) {
        missing = true;
        break;
      }
    }
    if (missing) break;
  }
  if (!missing) return;
  leadsEnrichInFlight = true;
  Promise.allSettled([
    enrichLeads(jobs, byJob),
    enrichStageHistory(jobs, byJob),
    enrichLeadNotes(jobs, byJob),
  ]).finally(() => {
    leadsEnrichInFlight = false;
  });
}

// TTL + last-good fallback + in-flight coalescing, exactly like getActivePipeline.
// Blocks on a cold build so the first paint carries real lead data; serves the
// last-good copy (flagged stale) if a refetch fails. On the rare cold-boot 429
// (the interviews application.info flood can rate-limit the leads application.list)
// this returns null the first time and the client's leads catch-up re-fetches
// until leadsSync reports ok — so the tab self-heals within a couple seconds.
async function getLeads(jobs) {
  const now = Date.now();
  if (leadsCache.data && now - leadsCache.fetchedAt < LEADS_TTL_MS) {
    kickLeadsEnrichment(jobs, leadsCache.data);
    return {
      byJob: leadsCache.data,
      fetchedAt: leadsCache.fetchedAt,
      fromCache: true,
      stale: false,
      error: null,
    };
  }
  try {
    if (!leadsInFlight) {
      leadsInFlight = buildLeads(jobs).finally(() => {
        leadsInFlight = null;
      });
    }
    const byJob = await leadsInFlight;
    leadsCache.data = byJob;
    leadsCache.fetchedAt = Date.now();
    leadsCache.lastError = null;
    return { byJob, fetchedAt: leadsCache.fetchedAt, fromCache: false, stale: false, error: null };
  } catch (e) {
    const msg = String((e && e.message) || e);
    leadsCache.lastError = msg;
    if (leadsCache.data) {
      return {
        byJob: leadsCache.data,
        fetchedAt: leadsCache.fetchedAt,
        fromCache: true,
        stale: true,
        error: msg,
      };
    }
    return { byJob: null, fetchedAt: null, fromCache: false, stale: false, error: msg };
  }
}

// In-memory cache with TTL + last-good fallback.
const jobCache = { jobs: null, fetchedAt: 0, lastError: null };

async function getAshbyJobs() {
  const now = Date.now();
  // Fresh cache within TTL -> serve without refetching.
  if (jobCache.jobs && now - jobCache.fetchedAt < ASHBY_TTL_MS) {
    return {
      jobs: jobCache.jobs,
      fetchedAt: jobCache.fetchedAt,
      fromCache: true,
      stale: false,
      error: null,
    };
  }
  // Need to (re)fetch.
  try {
    const jobs = await fetchAllOpenJobs();
    jobCache.jobs = jobs;
    jobCache.fetchedAt = now;
    jobCache.lastError = null;
    return { jobs, fetchedAt: now, fromCache: false, stale: false, error: null };
  } catch (e) {
    const msg = String((e && e.message) || e);
    jobCache.lastError = msg;
    if (jobCache.jobs) {
      // Serve last good cache, flagged stale.
      return {
        jobs: jobCache.jobs,
        fetchedAt: jobCache.fetchedAt,
        fromCache: true,
        stale: true,
        error: msg,
      };
    }
    // No cache ever -> signal failure; caller falls back to longlist files.
    return { jobs: null, fetchedAt: null, fromCache: false, stale: false, error: msg };
  }
}

// ---------------------------------------------------------------------------
// Interviews — live interview schedules from Ashby (the source of truth for who
// is being interviewed). Each schedule is resolved to its candidate/job/stage and
// attached to the matching active-pipeline card (no standalone tab).
// ---------------------------------------------------------------------------

// All interview schedules, following pagination.
async function fetchAllInterviewSchedules() {
  let cursor = null;
  let pages = 0;
  const all = [];
  do {
    const body = {};
    if (cursor) body.cursor = cursor;
    const data = await ashbyPostRetry("interviewSchedule.list", body);
    for (const s of data.results || []) all.push(s);
    cursor = data.moreDataAvailable && data.nextCursor ? data.nextCursor : null;
    pages += 1;
  } while (cursor && pages < 30);
  return all;
}

// Per-application enrichment cache: appId -> { candidateId, candidateName,
// jobId, jobTitle, stage, fetchedAt }. A schedule only carries applicationId,
// so we resolve candidate/job/stage through application.info once per app.
const appInfoCache = new Map();
async function fetchAppInfo(appId) {
  if (!appId) return null;
  const now = Date.now();
  const cached = appInfoCache.get(appId);
  if (cached && now - cached.fetchedAt < APP_INFO_TTL_MS) return cached;
  try {
    const data = await ashbyPostRetry("application.info", { applicationId: appId });
    const r = (data && data.results) || {};
    const c = r.candidate || {};
    const j = r.job || {};
    const cis = r.currentInterviewStage || {};
    const rec = {
      candidateId: c.id || null,
      candidateName: c.name || null,
      jobId: j.id || null,
      jobTitle: j.title || null,
      stage: cis.title || null,
      fetchedAt: now,
    };
    appInfoCache.set(appId, rec);
    return rec;
  } catch {
    return null; // degrade: row still renders with the schedule's own fields
  }
}

// Unique interviewer display names across all of a schedule's events.
function scheduleInterviewers(schedule) {
  const seen = new Set();
  const names = [];
  for (const ev of schedule.interviewEvents || []) {
    for (const iv of (ev && ev.interviewers) || []) {
      if (!iv) continue;
      const name = [iv.firstName, iv.lastName].filter(Boolean).join(" ").trim() || iv.email || null;
      if (!name) continue;
      const key = name.toLowerCase();
      if (seen.has(key)) continue;
      seen.add(key);
      names.push(name);
    }
  }
  return names;
}

// Latest event start-time drives the displayed date; status derives from the
// schedule status + whether that time is still in the future.
function scheduleTiming(schedule) {
  let latestStart = null;
  for (const ev of schedule.interviewEvents || []) {
    const st = ev && ev.startTime ? Date.parse(ev.startTime) : NaN;
    if (!isNaN(st) && (latestStart == null || st > latestStart)) latestStart = st;
  }
  const datetime = latestStart != null ? new Date(latestStart).toISOString() : schedule.createdAt || null;
  let status;
  if (schedule.status === "Complete") status = "completed";
  else if (latestStart != null && latestStart > Date.now()) status = "upcoming";
  else status = "completed";
  return { datetime, status };
}

function roleLabelFor(slug, jobTitle) {
  if (slug === "exploratory-chat") return "Exploratory";
  if (jobTitle) return jobTitle;
  if (slug) return slugToLabel(slug);
  return "—";
}

// Build the interview rows: one row per non-cancelled Ashby schedule, enriched
// via application.info with the candidate, job/role and current stage.
async function buildInterviews(manifest) {
  let schedules = [];
  let ashbyError = null;
  try {
    schedules = await fetchAllInterviewSchedules();
  } catch (e) {
    ashbyError = String((e && e.message) || e); // caller keeps the last-good rows
  }

  // Cancelled schedules are not "being interviewed" — drop them.
  const active = schedules.filter((s) => s && s.status !== "Cancelled");
  const infos = await Promise.all(active.map((s) => fetchAppInfo(s.applicationId)));

  const rows = [];
  active.forEach((s, idx) => {
    const info = infos[idx] || {};
    const { datetime, status } = scheduleTiming(s);
    const jobId = info.jobId || null;
    const entry = jobId && manifest[jobId] ? manifest[jobId] : null;
    const slug = entry ? entry.slug : null;

    rows.push({
      key: "sch-" + s.id,
      candidate: info.candidateName || "Unknown",
      candidate_id: info.candidateId || null,
      application_id: s.applicationId || null,
      role_slug: slug,
      role_label: roleLabelFor(slug, info.jobTitle),
      stage: info.stage || null,
      datetime,
      status,
      interviewers: scheduleInterviewers(s),
    });
  });

  rows.sort((a, b) => String(b.datetime || "").localeCompare(String(a.datetime || "")));
  return { rows, ashbyError };
}

// 5-minute cache with last-good fallback. The refresh is DETACHED (like
// enrichPipeline): getInterviews never blocks the /api/data response on the
// Ashby round-trip. It serves whatever is cached and kicks a background rebuild
// when the cache is cold or stale. Only clean builds (no ashbyError) are cached,
// so a transient 429 self-heals on the next tick.
const interviewCache = { data: null, fetchedAt: 0 };
let interviewInFlight = null;

function refreshInterviews(manifest) {
  if (interviewInFlight) return interviewInFlight;
  interviewInFlight = buildInterviews(manifest)
    .then((built) => {
      if (!built.ashbyError) {
        interviewCache.data = built;
        interviewCache.fetchedAt = Date.now();
      } else if (!interviewCache.data) {
        // Nothing cached yet: store the failed build so the client can see the
        // ashbyError, but leave fetchedAt at 0 so the next call retries.
        interviewCache.data = built;
      }
      return built;
    })
    .catch((e) => {
      console.error("[interviews] refresh failed:", String((e && e.message) || e));
    })
    .finally(() => {
      interviewInFlight = null;
    });
  return interviewInFlight;
}

async function getInterviews(manifest) {
  const now = Date.now();
  const fresh = interviewCache.data && now - interviewCache.fetchedAt < INTERVIEW_TTL_MS;
  if (!fresh) {
    const p = refreshInterviews(manifest);
    // Cold cache (nothing ever built): block on the first build so the very first
    // paint carries the upcoming strip, mirroring getActivePipeline.
    // Warm-but-stale: refresh stays DETACHED (serve last-good, catch up next tick).
    if (!interviewCache.data && p) {
      try { await p; } catch { /* leave cache empty; client will retry */ }
    }
  }
  const data = interviewCache.data || { rows: [], ashbyError: null };
  const stillFresh = interviewCache.data && Date.now() - interviewCache.fetchedAt < INTERVIEW_TTL_MS;
  return {
    rows: data.rows || [],
    ashbyError: data.ashbyError || null,
    fetchedAt: interviewCache.fetchedAt || null,
    stale: !stillFresh,
  };
}

// ---------------------------------------------------------------------------
// Atsless mode — agent-kept candidate records instead of Ashby (schema in
// ATSLESS.md). Each adapter below synthesizes the EXACT response shape of its
// Ashby counterpart (getAshbyJobs / getActivePipeline / getLeads /
// getInterviews) so buildData and the client stay untouched. No caching: the
// store is one small local file, re-read per request like roles.json.
// ---------------------------------------------------------------------------
function readAtslessRecords() {
  return parseJsonl(ATSLESS_FILE).filter((r) => r && r.id && r.name);
}

// role_slug on a record -> the manifest's job id (the byJob bucket key).
function atslessSlugToJobId(manifest) {
  const m = new Map();
  for (const [jobId, e] of Object.entries(manifest)) {
    if (e && e.slug) m.set(e.slug, jobId);
  }
  return m;
}

// getAshbyJobs equivalent: one synthetic "job" per roles.json entry. There is
// no ATS to ask for a title, so the entry's own (optional) title wins, else a
// label derived from the slug.
function atslessJobs(manifest) {
  const jobs = [];
  for (const [jobId, e] of Object.entries(manifest)) {
    if (!e || !e.slug) continue;
    jobs.push({ id: jobId, title: e.title || slugToLabel(e.slug) });
  }
  return { jobs, fetchedAt: Date.now(), fromCache: false, stale: false, error: null };
}

// Atsless records carry no per-stage timeline, so synthesize a single
// current-stage entry — null would render as a forever-"loading" timeline.
// stage_history (optional on the record) overrides when a session keeps one.
function atslessStageHistory(rec) {
  if (Array.isArray(rec.stage_history) && rec.stage_history.length) {
    return rec.stage_history.map((h) => ({
      id: (h && h.id) || null,
      stageId: null,
      title: (h && h.title) || null,
      stageNumber: h && typeof h.stageNumber === "number" ? h.stageNumber : null,
      enteredStageAt: (h && h.enteredStageAt) || null,
      leftStageAt: (h && h.leftStageAt) || null,
    }));
  }
  return [
    {
      id: null,
      stageId: null,
      title: rec.stage || null,
      stageNumber: null,
      enteredStageAt: rec.updated || rec.created || null,
      leftStageAt: null, // absent => current stage (same convention as Ashby)
    },
  ];
}

// One record -> the app card shape both pipeline views share. The record id
// doubles as applicationId AND candidateId (there is no ATS split), which is
// what lets interview rows and inbound ratings attach by candidate id.
function atslessApp(rec) {
  return {
    applicationId: rec.id,
    candidateId: rec.id,
    name: rec.name || "Unknown",
    stage: rec.stage,
    createdAt: rec.created || null,
    appliedAt: rec.created || null,
    updatedAt: rec.updated || rec.created || null,
    source: rec.source || null,
    stageHistory: atslessStageHistory(rec),
    linkedin_url: rec.linkedin_url || null,
    position: rec.title || null,
    company: rec.company || null,
    tags: Array.isArray(rec.tags) ? rec.tags : [],
  };
}

// getActivePipeline equivalent: interview-stage records bucketed by job.
function atslessActivePipeline(jobs, records, slugToJob) {
  const byJob = {};
  for (const j of jobs) byJob[j.id] = { kept: [] };
  for (const rec of records) {
    if (!PIPELINE_STAGES.includes(rec.stage)) continue;
    const jobId = slugToJob.get(rec.role_slug);
    if (!jobId || !byJob[jobId]) continue;
    const app = atslessApp(rec);
    app.stageTitle = rec.stage;
    byJob[jobId].kept.push(app);
  }
  return { byJob, fetchedAt: Date.now(), fromCache: false, stale: false, error: null };
}

// Ashby mode parses outreach state out of candidate NOTES; atsless records
// carry it directly in outreach[]. Mapped to the same event shape the notes
// parser emits so every chip/timeline rule in the client applies unchanged.
function atslessOutreachEvents(rec) {
  const evs = [];
  for (const o of Array.isArray(rec.outreach) ? rec.outreach : []) {
    if (!o || !o.action) continue;
    evs.push({
      action: o.action,
      channel: o.channel || null,
      type: o.type || null,
      variant: o.variant ? String(o.variant).toUpperCase() : null,
      ts: o.date || null,
      message: typeof o.message === "string" ? o.message.slice(0, 600) : null,
      subject: o.subject || null,
    });
  }
  evs.sort((a, b) => String(a.ts || "").localeCompare(String(b.ts || "")));
  return evs;
}

// getLeads equivalent: lead-stage records bucketed by job, outreach attached.
function atslessLeads(jobs, records, slugToJob) {
  const byJob = {};
  for (const j of jobs) byJob[j.id] = { kept: [] };
  for (const rec of records) {
    if (!LEAD_STAGES.includes(rec.stage)) continue;
    const jobId = slugToJob.get(rec.role_slug);
    if (!jobId || !byJob[jobId]) continue;
    const app = atslessApp(rec);
    app.outreachEvents = atslessOutreachEvents(rec);
    byJob[jobId].kept.push(app);
  }
  return { byJob, fetchedAt: Date.now(), fromCache: false, stale: false, error: null };
}

// getInterviews equivalent: one row per non-cancelled entry in each record's
// interviews[]. Explicit status wins; otherwise a future datetime = upcoming.
function atslessInterviews(manifest, records, slugToJob) {
  const rows = [];
  for (const rec of records) {
    const list = Array.isArray(rec.interviews) ? rec.interviews : [];
    list.forEach((iv, i) => {
      if (!iv || iv.status === "cancelled") return;
      const jobId = slugToJob.get(rec.role_slug) || null;
      const entry = jobId && manifest[jobId] ? manifest[jobId] : null;
      let status = iv.status === "upcoming" || iv.status === "completed" ? iv.status : null;
      if (!status) {
        const t = iv.datetime ? Date.parse(iv.datetime) : NaN;
        status = !isNaN(t) && t > Date.now() ? "upcoming" : "completed";
      }
      rows.push({
        key: "atsless-" + rec.id + "-" + i,
        candidate: rec.name || "Unknown",
        candidate_id: rec.id,
        application_id: rec.id,
        role_slug: rec.role_slug || null,
        role_label: roleLabelFor(rec.role_slug, entry && entry.title ? entry.title : null),
        stage: rec.stage || iv.round || null,
        datetime: iv.datetime || null,
        status,
        interviewers: Array.isArray(iv.interviewers) ? iv.interviewers.filter(Boolean) : [],
      });
    });
  }
  rows.sort((a, b) => String(b.datetime || "").localeCompare(String(a.datetime || "")));
  return { rows, ashbyError: null, fetchedAt: Date.now(), stale: false };
}

// ---------------------------------------------------------------------------
// Role assembly
// ---------------------------------------------------------------------------
function makeRole({ jobId, title, slug, sourcing, note, hasLonglist, candidates }) {
  const scores = candidates
    .map((c) => (c && typeof c.score === "number" ? c.score : null))
    .filter((s) => s !== null);
  const statusCounts = {};
  for (const c of candidates) {
    const s = (c && c.status) || "unknown";
    statusCounts[s] = (statusCounts[s] || 0) + 1;
  }
  const avgScore = scores.length
    ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10
    : null;
  return {
    key: jobId || slug || title,
    jobId: jobId || null,
    title,
    label: title,
    slug: slug || null,
    sourcing: sourcing || null,
    note: note || null,
    hasLonglist: !!hasLonglist,
    candidates,
    summary: {
      total: candidates.length,
      scored: statusCounts["scored"] || 0,
      shortlisted: statusCounts["shortlisted"] || 0,
      avgScore,
      statusCounts,
    },
  };
}

const SOURCING_RANK = { active: 1, passive: 2, "inbound-only": 3 };

function buildRoles(sync, manifest, candidatesByRole) {
  const byRole = candidatesByRole && typeof candidatesByRole === "object" ? candidatesByRole : {};
  // Role discovery = union of roles.json slugs + distinct `role` values from the
  // registry (or local longlist files on fallback). Keeps retired longlist-only
  // roles visible when Ashby is down, and sheet-only roles when files lag.
  const localFilesBySlug = {};
  for (const rf of discoverRoleFiles()) localFilesBySlug[rf.slug] = rf;
  const knownSlugs = new Set([
    ...Object.keys(byRole),
    ...Object.keys(localFilesBySlug),
    ...Object.values(manifest)
      .map((e) => (e && e.slug ? e.slug : null))
      .filter(Boolean),
  ]);

  const roles = [];

  if (sync.jobs) {
    // Primary path: role list is driven by OPEN Ashby jobs (auto-sync).
    const seenSlugs = new Set();
    for (const job of sync.jobs) {
      const title = job.title || "(untitled)";
      if (title.startsWith("[PREP]")) continue; // demo artifact
      if (title.includes("Live Demo")) continue; // demo artifact
      const entry = manifest[job.id] || null;
      const sourcing = entry ? entry.sourcing : null;
      if (sourcing === "hidden") continue; // explicitly hidden in manifest
      const slug = entry ? entry.slug : null;
      const note = entry ? entry.note : null;
      const candidates = slug && Array.isArray(byRole[slug]) ? byRole[slug] : [];
      const hasLonglist =
        !!slug &&
        (candidates.length > 0 ||
          Object.prototype.hasOwnProperty.call(byRole, slug) ||
          !!localFilesBySlug[slug]);
      if (slug) seenSlugs.add(slug);
      roles.push(
        makeRole({
          jobId: job.id,
          title,
          slug,
          sourcing,
          note,
          hasLonglist,
          candidates,
        })
      );
    }
    // Registry/local slugs that don't map to an open job are retired -> no pill.
    void seenSlugs;
    void knownSlugs;
  } else {
    // Fallback path: Ashby sync failed with no cache. Render discovered roles
    // (manifest ∪ sheet/local) so the dashboard still works.
    const slugs = Array.from(knownSlugs).sort();
    for (const slug of slugs) {
      let entry = null;
      let jobId = null;
      for (const [jid, e] of Object.entries(manifest)) {
        if (e && e.slug === slug) {
          entry = e;
          jobId = jid;
          break;
        }
      }
      if (entry && entry.sourcing === "hidden") continue;
      const candidates = Array.isArray(byRole[slug]) ? byRole[slug] : [];
      roles.push(
        makeRole({
          jobId,
          title: (entry && entry.title) || slugToLabel(slug),
          slug,
          sourcing: entry ? entry.sourcing : null,
          note: entry ? entry.note : null,
          hasLonglist: true,
          candidates,
        })
      );
    }
  }

  // Ordering: roles with candidates (desc by count) -> active -> passive ->
  // inbound-only -> other; alphabetical tie-break by title.
  roles.sort((a, b) => {
    const ag = a.summary.total > 0 ? 0 : 1;
    const bg = b.summary.total > 0 ? 0 : 1;
    if (ag !== bg) return ag - bg;
    if (ag === 0) {
      if (b.summary.total !== a.summary.total) return b.summary.total - a.summary.total;
      return (a.title || "").localeCompare(b.title || "");
    }
    const ar = SOURCING_RANK[a.sourcing] || 4;
    const br = SOURCING_RANK[b.sourcing] || 4;
    if (ar !== br) return ar - br;
    return (a.title || "").localeCompare(b.title || "");
  });

  return roles;
}

// ---------------------------------------------------------------------------
// Tab 2: Inbound (Application Review) — per-role rated applicants.
// (The old suppression-ashby.jsonl funnel is intentionally NOT rendered.)
// ---------------------------------------------------------------------------
function readInboundBySlug() {
  const rows = parseJsonl(`${PIPELINE_DIR}/inbound-ratings.jsonl`);
  const bySlug = {};
  for (const r of rows) {
    const slug = r && r.role;
    if (!slug) continue;
    (bySlug[slug] = bySlug[slug] || []).push(r);
  }
  return bySlug;
}

function inboundSummary(list) {
  let advance = 0;
  let reject = 0;
  let basicReview = 0;
  let awaiting = 0; // future field: applicants surfaced but not yet rated
  for (const r of list) {
    const rec = r && r.recommendation;
    if (rec === "Advance") advance += 1;
    else if (rec === "Reject") reject += 1;
    else if (rec === "Basic review") basicReview += 1;
    if (!rec) awaiting += 1;
  }
  return { total: list.length, advance, reject, basicReview, awaiting };
}

// Sort: Advance first, then score desc (nulls last), then applied date desc.
function sortInbound(list) {
  return list.slice().sort((a, b) => {
    const aAdv = a.recommendation === "Advance" ? 0 : 1;
    const bAdv = b.recommendation === "Advance" ? 0 : 1;
    if (aAdv !== bAdv) return aAdv - bAdv;
    const an = typeof a.score !== "number";
    const bn = typeof b.score !== "number";
    if (an && bn) {
      /* fall through to date */
    } else if (an) {
      return 1;
    } else if (bn) {
      return -1;
    } else if (a.score !== b.score) {
      return b.score - a.score;
    }
    return String(b.created || "").localeCompare(String(a.created || ""));
  });
}

// ---------------------------------------------------------------------------
// Payload
// ---------------------------------------------------------------------------
async function buildData() {
  const generatedAt = new Date().toISOString();
  const manifest = readManifest();
  // Atsless mode swaps every ATS-backed source for the local store; the local
  // pipeline files (longlists, inbound ratings, feedback) load identically.
  const atsRecords = ATSLESS ? readAtslessRecords() : null;
  const atsSlugToJob = ATSLESS ? atslessSlugToJobId(manifest) : null;
  const sync = ATSLESS ? atslessJobs(manifest) : await getAshbyJobs();
  const nowMs = Date.now();

  // Shared registry (Google Sheets) is the sourced-candidate source of truth;
  // falls back to local longlist-*.jsonl and sets registrySource accordingly.
  const candidatesByRole = await loadSourcedCandidatesByRole();
  const roles = buildRoles(sync, manifest, candidatesByRole);

  // Attach inbound (Application Review) ratings per role, matched by slug.
  const inboundBySlug = readInboundBySlug();
  let totalCandidates = 0;
  let totalShortlisted = 0;
  let totalInbound = 0;
  for (const r of roles) {
    totalCandidates += r.summary.total;
    totalShortlisted += r.summary.shortlisted;
    const list = (r.slug && inboundBySlug[r.slug]) ? sortInbound(inboundBySlug[r.slug]) : [];
    r.inbound = list;
    r.inboundSummary = inboundSummary(list);
    totalInbound += list.length;
  }

  // Agent rating lookup by Ashby candidate id, drawn from the inbound ratings
  // file. Used to badge active-pipeline cards with the score the filter gave.
  const ratingByCand = new Map();
  for (const slug of Object.keys(inboundBySlug)) {
    for (const r of inboundBySlug[slug]) {
      if (r && r.candidate_id && !ratingByCand.has(r.candidate_id)) {
        ratingByCand.set(r.candidate_id, {
          score: typeof r.score === "number" ? r.score : null,
          recommendation: r.recommendation || null,
          role: r.role || null,
          rated_at: r.rated_at || r.created || null,
        });
      }
    }
  }

  // Interviews: live Ashby interview schedules, served from a detached 5-min cache
  // so it never blocks this response on the Ashby round-trip. These are ATTRIBUTES
  // of active-pipeline candidates (no standalone tab): index them by candidate id
  // so each card can list its own interview events.
  const interviews = ATSLESS
    ? atslessInterviews(manifest, atsRecords, atsSlugToJob)
    : await getInterviews(manifest);
  const interviewRows = interviews.rows || [];
  const ivByCand = new Map();
  for (const row of interviewRows) {
    if (!row.candidate_id) continue;
    if (!ivByCand.has(row.candidate_id)) ivByCand.set(row.candidate_id, []);
    ivByCand.get(row.candidate_id).push(row);
  }
  // Chronological within a candidate: earliest round first (natural round order).
  for (const list of ivByCand.values()) {
    list.sort((a, b) => String(a.datetime || "").localeCompare(String(b.datetime || "")));
  }

  // Upcoming-interviews strip: scheduled events in the next ~7 days, all roles.
  const in7Days = nowMs + 7 * 24 * 60 * 60 * 1000;
  const upcomingInterviews = interviewRows
    .filter((r) => {
      if (r.status !== "upcoming" || !r.datetime) return false;
      const t = Date.parse(r.datetime);
      return !isNaN(t) && t >= nowMs && t <= in7Days;
    })
    .map((r) => ({
      key: r.key,
      candidate: r.candidate,
      candidate_id: r.candidate_id,
      role_label: r.role_label,
      datetime: r.datetime,
      interviewers: Array.isArray(r.interviewers) ? r.interviewers : [],
    }))
    .sort((a, b) => String(a.datetime || "").localeCompare(String(b.datetime || "")));

  // Attach live active-pipeline (interview rounds) per role, matched by Ashby job
  // id. Each kept app is enriched in place with its interview events + agent
  // rating so the card is self-contained (no per-request Ashby calls added).
  let pipe = { byJob: null, fetchedAt: null, fromCache: false, stale: false, error: sync.error };
  if (sync.jobs) {
    pipe = ATSLESS
      ? atslessActivePipeline(sync.jobs, atsRecords, atsSlugToJob)
      : await getActivePipeline(sync.jobs);
  }
  let totalInInterviews = 0;
  for (const r of roles) {
    const rec = (pipe.byJob && r.jobId) ? pipe.byJob[r.jobId] : null;
    const stages = { "Initial Screen": [], "First Round": [], "Second Round": [], "Offer": [], "Other": [] };
    if (rec) {
      for (const app of rec.kept) {
        app.interviews = app.candidateId ? (ivByCand.get(app.candidateId) || []) : [];
        app.rating = app.candidateId ? (ratingByCand.get(app.candidateId) || null) : null;
        (stages[app.stage] || stages["Other"]).push(app);
      }
      // Within a column, most-recently-active first.
      for (const k of Object.keys(stages)) {
        stages[k].sort((a, b) =>
          String(b.updatedAt || "").localeCompare(String(a.updatedAt || ""))
        );
      }
    }
    const total = rec ? rec.kept.length : 0;
    r.activePipeline = { stages, total };
    totalInInterviews += total;
  }

  // Attach live LEADS per role, matched by Ashby job id. Outreach send-state is
  // read from ASHBY CANDIDATE NOTES (single source of truth — the hiring lead, 2026-07-29),
  // parsed into events by enrichLeadNotes; the local outreach ledger is batch
  // mechanics only and never feeds this view. Historical bulk leads stay
  // excluded server-side; adopted records come in via the registry.
  let leads = { byJob: null, fetchedAt: null, fromCache: false, stale: false, error: sync.error };
  if (sync.jobs) {
    leads = ATSLESS
      ? atslessLeads(sync.jobs, atsRecords, atsSlugToJob)
      : await getLeads(sync.jobs);
  }
  let totalLeads = 0;
  for (const r of roles) {
    const rec = (leads.byJob && r.jobId) ? leads.byJob[r.jobId] : null;
    const stages = { "New Lead": [], "Reached Out": [], "Replied": [] };
    let total = 0;
    if (rec) {
      // Agent-score lookup from THIS role's longlist, indexed by LinkedIn slug and
      // by lowercased name (LinkedIn wins; name is the fallback).
      const scoreByLi = new Map();
      const scoreByName = new Map();
      for (const c of r.candidates || []) {
        if (!c) continue;
        const entry = {
          score: typeof c.score === "number" ? c.score : null,
          status: c.status || null,
        };
        const k = liKey(c.linkedin_url);
        if (k && !scoreByLi.has(k)) scoreByLi.set(k, entry);
        const nm = c.name ? String(c.name).trim().toLowerCase() : "";
        if (nm && !scoreByName.has(nm)) scoreByName.set(nm, entry);
      }
      // Bucket first, then de-dupe: concurrent Advance drains have historically
      // double-created the same person (same LinkedIn, two candidate ids). When
      // that happens the send/stage-change only hits one app, so the twin sits
      // forever at New Lead while outreach history (matched by LinkedIn) makes
      // BOTH cards look contacted — Leyton Ho 2026-07-29. Prefer the furthest
      // stage, then most-recently-updated; collapse by LinkedIn, else by name.
      const STAGE_RANK = { "New Lead": 0, "Reached Out": 1, "Replied": 2 };
      const allApps = [];
      for (const app of rec.kept) {
        const nameKey = app.name ? String(app.name).trim().toLowerCase() : "";
        // Outreach state straight from Ashby notes (null until the detached
        // notes fetch lands — the UI renders that as "loading"). The full event
        // list ships once as app.outreachEvents; this is just the latest summary.
        const evs = Array.isArray(app.outreachEvents) ? app.outreachEvents : null;
        const latest = evs && evs.length ? evs[evs.length - 1] : null;
        app.outreach = {
          loaded: !!evs,
          action: latest ? latest.action : null,
          ts: latest ? latest.ts : null,
          channel: latest ? latest.channel : null,
          type: latest ? latest.type : null,
          variant: latest ? latest.variant : null,
        };
        // Agent score from the longlist: LinkedIn match first, name fallback.
        app.agentScore =
          scoreByLi.get(liKey(app.linkedin_url)) ||
          (nameKey ? scoreByName.get(nameKey) : null) ||
          null;
        allApps.push(app);
      }
      const better = (a, b) => {
        const ra = STAGE_RANK[a.stage] ?? -1;
        const rb = STAGE_RANK[b.stage] ?? -1;
        if (ra !== rb) return ra > rb ? a : b;
        return String(a.updatedAt || "") >= String(b.updatedAt || "") ? a : b;
      };
      const byIdentity = new Map(); // li:<slug> | name:<n> -> winning app
      for (const app of allApps) {
        const li = liKey(app.linkedin_url);
        const key = li
          ? "li:" + li
          : app.name
          ? "name:" + String(app.name).trim().toLowerCase()
          : "id:" + (app.applicationId || Math.random());
        const prev = byIdentity.get(key);
        byIdentity.set(key, prev ? better(prev, app) : app);
      }
      for (const app of byIdentity.values()) {
        if (stages[app.stage]) stages[app.stage].push(app);
      }
      // Within a column, most-recently-updated first.
      for (const k of Object.keys(stages)) {
        stages[k].sort((a, b) =>
          String(b.updatedAt || "").localeCompare(String(a.updatedAt || ""))
        );
      }
      total = byIdentity.size;
    }
    r.leads = { stages, total };
    totalLeads += total;
  }

  return {
    generatedAt,
    registrySource,
    // User-visible system-of-record name (from datasource.json displayName, else
    // "Pipeline" in atsless mode, else "Ashby"). Field names stay ashby*.
    sorName: SOR_NAME,
    roles,
    // Interview data now lives on the active-pipeline cards (attached above).
    // This block carries only cross-cutting bits: the upcoming-week strip and
    // the Ashby fetch health used by the client's catch-up logic.
    interviews: {
      upcoming: upcomingInterviews,
      ashbyError: interviews.ashbyError || null,
      stale: !!interviews.stale, // true while a detached refresh is still catching up
      ageSeconds: interviews.fetchedAt
        ? Math.max(0, Math.round((nowMs - interviews.fetchedAt) / 1000))
        : null,
    },
    totals: {
      totalCandidates,
      totalRoles: roles.length,
      totalShortlisted,
      totalInbound,
      totalInInterviews,
      totalInterviews: interviewRows.length,
      totalLeads,
    },
    ashbySync: {
      ok: !!sync.jobs,
      fromCache: sync.fromCache,
      stale: sync.stale,
      error: sync.error,
      lastSuccess: sync.fetchedAt ? new Date(sync.fetchedAt).toISOString() : null,
      ageSeconds: sync.fetchedAt
        ? Math.max(0, Math.round((nowMs - sync.fetchedAt) / 1000))
        : null,
      jobCount: sync.jobs ? sync.jobs.length : 0,
    },
    pipelineSync: {
      ok: !!pipe.byJob,
      fromCache: pipe.fromCache,
      stale: pipe.stale,
      error: pipe.error,
      ageSeconds: pipe.fetchedAt
        ? Math.max(0, Math.round((nowMs - pipe.fetchedAt) / 1000))
        : null,
    },
    leadsSync: {
      ok: !!leads.byJob,
      fromCache: leads.fromCache,
      stale: leads.stale,
      error: leads.error,
      ageSeconds: leads.fetchedAt
        ? Math.max(0, Math.round((nowMs - leads.fetchedAt) / 1000))
        : null,
    },
  };
}

// ---------------------------------------------------------------------------
// Feedback loop — the hiring lead's Advance / Reject reviews (ADDITIVE; never touches Ashby).
// Clicks append one line to feedback-queue.jsonl and (debounced) ping an
// HMAC-signed webhook so the recruiting agent ingests them. The webhook config
// is SECRET: url/secret/header NEVER appear in any HTTP response or client HTML.
// ---------------------------------------------------------------------------
function readWebhookConfig() {
  try {
    const obj = JSON.parse(readFileSync(WEBHOOK_CONFIG_FILE, "utf8"));
    if (obj && typeof obj === "object" && obj.url && obj.secret && obj.header) {
      return obj;
    }
    return null;
  } catch {
    return null; // missing/unreadable -> feedback still queues, ping is skipped
  }
}

function processedIdSet() {
  const ids = new Set();
  for (const p of parseJsonl(PROCESSED_FILE)) if (p && p.id) ids.add(p.id);
  return ids;
}

// Pending = queued events whose id has no processed marker yet.
function pendingCount() {
  const done = processedIdSet();
  let n = 0;
  for (const e of parseJsonl(QUEUE_FILE)) if (e && e.id && !done.has(e.id)) n += 1;
  return n;
}

function randomHex(nChars) {
  return randomBytes(Math.ceil(nChars / 2)).toString("hex").slice(0, nChars);
}

// Fire one HMAC-signed webhook ping. Failures are logged only (never thrown).
async function sendWebhookPing(isTest) {
  const cfg = readWebhookConfig();
  if (!cfg) {
    console.warn(
      "[feedback] webhook config missing/unreadable — ping skipped (queue still written)"
    );
    return;
  }
  const payload = {
    kind: "feedback-batch",
    pending: pendingCount(),
    ts: new Date().toISOString(),
  };
  if (isTest) payload.test = true;
  const raw = JSON.stringify(payload);
  const sig = createHmac("sha256", cfg.secret).update(raw).digest("hex");
  console.log(
    `[feedback] sending ${isTest ? "immediate test" : "debounced"} webhook ping (pending=${payload.pending})`
  );
  try {
    const res = await fetch(cfg.url, {
      method: "POST",
      headers: { "Content-Type": "application/json", [cfg.header]: sig },
      body: raw,
    });
    if (!res.ok) console.error(`[feedback] webhook ping returned HTTP ${res.status}`);
  } catch (e) {
    console.error("[feedback] webhook ping failed:", String((e && e.message) || e));
  }
}

// Normal events coalesce into a single ping via one shared 90s timer. Test
// events ping immediately and never touch this timer.
let pingTimer = null;
function scheduleDebouncedPing() {
  if (pingTimer) clearTimeout(pingTimer);
  pingTimer = setTimeout(() => {
    pingTimer = null;
    sendWebhookPing(false);
  }, PING_DEBOUNCE_MS);
}

function validateFeedback(body) {
  if (!body || typeof body !== "object") return "body must be a JSON object";
  if (body.source !== "sourced" && body.source !== "inbound")
    return "source must be 'sourced' or 'inbound'";
  if (body.tim_action !== "advance" && body.tim_action !== "reject")
    return "tim_action must be 'advance' or 'reject'";
  const c = body.candidate;
  if (!c || typeof c !== "object") return "candidate object is required";
  if (typeof c.name !== "string" || !c.name.trim())
    return "candidate.name must be a non-empty string";
  if (body.source === "sourced" && !c.id && !c.linkedin_url)
    return "sourced feedback requires candidate.id or candidate.linkedin_url";
  if (body.source === "inbound" && !c.application_id)
    return "inbound feedback requires candidate.application_id";
  if (body.feedback != null && typeof body.feedback !== "string")
    return "feedback must be a string";
  if (typeof body.role_slug !== "string" || !body.role_slug.trim())
    return "role_slug must be a non-empty string";
  return null;
}

// Build the immutable queue event from an already-validated body.
function buildFeedbackEvent(body) {
  const agentAdvance =
    body.source === "sourced"
      ? body.agent_rec === "shortlisted"
      : body.agent_rec === "Advance";
  const override = (body.tim_action === "advance") !== agentAdvance;
  const feedback = (typeof body.feedback === "string" ? body.feedback : "")
    .trim()
    .slice(0, 2000);
  const c = body.candidate || {};
  const event = {
    id: "fb_" + Date.now() + "_" + randomHex(4),
    ts: new Date().toISOString(),
    source: body.source,
    role_key: body.role_key != null ? body.role_key : null,
    role_slug: body.role_slug,
    role_title: body.role_title != null ? body.role_title : null,
    job_id: body.job_id != null ? body.job_id : null,
    tim_action: body.tim_action,
    feedback,
    candidate: {
      name: c.name,
      id: c.id != null ? c.id : null,
      linkedin_url: c.linkedin_url != null ? c.linkedin_url : null,
      candidate_id: c.candidate_id != null ? c.candidate_id : null,
      application_id: c.application_id != null ? c.application_id : null,
      email: c.email != null ? c.email : null,
      title: c.title != null ? c.title : null,
      company: c.company != null ? c.company : null,
    },
    agent_rec: body.agent_rec != null ? body.agent_rec : null,
    agent_score: typeof body.agent_score === "number" ? body.agent_score : null,
    override,
  };
  if (body.test === true) event.test = true;
  return event;
}

// Shared tail of both feedback transports (POST body / GET ?p=): validate,
// append to the queue, schedule the webhook ping, respond.
function acceptFeedback(body) {
  const err = validateFeedback(body);
  if (err) return Response.json({ error: err }, { status: 400 });
  const event = buildFeedbackEvent(body);
  try {
    appendFileSync(QUEUE_FILE, JSON.stringify(event) + "\n");
  } catch (e) {
    return Response.json(
      { error: "failed to write queue: " + String((e && e.message) || e) },
      { status: 500 }
    );
  }
  // Test events ping immediately; normal events debounce into one ping.
  if (event.test) sendWebhookPing(true);
  else scheduleDebouncedPing();
  return Response.json(
    { ok: true, id: event.id },
    { headers: { "Cache-Control": "no-store" } }
  );
}

// Normalize a LinkedIn identifier (full URL or "in/handle" id) to "in/<handle>".
function liKey(v) {
  if (!v || typeof v !== "string") return null;
  let s = v.trim().toLowerCase();
  const m = s.match(/\/in\/([^/?#]+)/) || s.match(/^in\/([^/?#]+)$/);
  if (!m) return null;
  return "in/" + m[1].replace(/\/+$/, "");
}

// Real outreach send-state, per candidate, from the append-only outreach ledger.
// The ledger is the source of truth for what was actually SENT — the feedback
// "done"/"processed" state only means the Advance click was ingested (record
// created + outreach QUEUED), not that a message went out.
//
// Returns Maps keyed by LinkedIn slug and by lowercased name → an OutreachRec:
//   {
//     // latest event (kept flat for backward-compat with feedback chips)
//     action, ts, variant, reason, channel, type,
//     // full chronological history (oldest → newest) for the Leads timeline
//     events: [{ action, ts, channel, type, variant, reason, message, note, verify, subject }]
//   }
// Legacy ledger rows that used `event` instead of `action` are normalized in.
// Events come from the shared Sheets registry (events tab), with local
// outreach-log.jsonl as fallback when the proxy/sheet is unreachable.
async function buildOutreachIndex() {
  const byLi = new Map();
  const byName = new Map();
  const stamp = (e) => String(e.ts || (e.date ? e.date + "T00:00:00Z" : ""));

  const push = (map, key, event, latest) => {
    if (!key) return;
    let rec = map.get(key);
    if (!rec) {
      rec = { ...latest, events: [event] };
      map.set(key, rec);
      return;
    }
    rec.events.push(event);
    if (!rec.ts || event.ts >= rec.ts) {
      rec.action = latest.action;
      rec.ts = latest.ts;
      rec.variant = latest.variant;
      rec.reason = latest.reason;
      rec.channel = latest.channel;
      rec.type = latest.type;
    }
  };

  const rows = await loadOutreachEvents();
  for (const e of rows) {
    if (!e) continue;
    // Normalize legacy `event` field (one early skipped row used it).
    const action = e.action || e.event || null;
    if (!action) continue;
    const ts = stamp(e);
    const event = {
      action,
      ts,
      channel: e.channel || null,
      type: e.type || null,
      variant: e.variant || null,
      reason: e.reason || null,
      // Cap message bodies so the /api/data payload stays small; UI truncates further.
      message: typeof e.message === "string" ? e.message.slice(0, 600) : null,
      note: typeof e.note === "string" ? e.note.slice(0, 300) : null,
      verify: e.verify || null,
      subject: e.subject || null,
    };
    const latest = {
      action,
      ts,
      variant: event.variant,
      reason: event.reason,
      channel: event.channel,
      type: event.type,
    };
    // candidate_key is mapped to id in parseEventsSheet; accept either.
    push(byLi, liKey(e.linkedin_url) || liKey(e.id) || liKey(e.candidate_key), event, latest);
    if (e.name) push(byName, String(e.name).trim().toLowerCase(), event, latest);
  }

  // Sort each history oldest → newest once at the end (append order is usually
  // chronological but re-queues / corrections can interleave).
  for (const map of [byLi, byName]) {
    for (const rec of map.values()) {
      rec.events.sort((a, b) => String(a.ts || "").localeCompare(String(b.ts || "")));
    }
  }
  return { byLi, byName };
}

// ---------------------------------------------------------------------------
// Weekly alignment (Calibration tab headline: "how aligned are you to me, by week")
// ---------------------------------------------------------------------------
const WEEKLY_CAP = 26; // emit at most the most recent 26 weeks
const DAY_MS = 86400000;
const MON_SHORT = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// Calibration `date` is a plain "YYYY-MM-DD". Parse it as UTC so bucketing never
// drifts a day depending on the server's timezone. Returns null when missing or
// unparseable (those entries are skipped entirely).
function parseCalibDate(v) {
  if (typeof v !== "string") return null;
  const m = v.trim().match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (!m) return null;
  const t = Date.parse(m[0] + "T00:00:00Z");
  if (isNaN(t)) return null;
  const d = new Date(t);
  // Guard against any rollover (e.g. "2026-02-31").
  if (
    d.getUTCFullYear() !== +m[1] ||
    d.getUTCMonth() + 1 !== +m[2] ||
    d.getUTCDate() !== +m[3]
  ) return null;
  return d;
}

// ISO week bucket key: the Monday of the week containing `d` (UTC).
function mondayOfUtc(d) {
  const back = (d.getUTCDay() + 6) % 7; // Mon -> 0 ... Sun -> 6
  return new Date(d.getTime() - back * DAY_MS);
}
function isoDay(d) {
  return d.toISOString().slice(0, 10);
}
// "Jul 20–26", or "Jul 27–Aug 2" when the week straddles two months.
function weekLabel(start, end) {
  const sm = MON_SHORT[start.getUTCMonth()];
  const em = MON_SHORT[end.getUTCMonth()];
  const tail = (em === sm ? "" : em + " ") + end.getUTCDate();
  return sm + " " + start.getUTCDate() + "–" + tail;
}

// A calibration entry's source. Dashboard clicks carry no `source` at all
// (sometimes a `source_event` id instead), so absent/blank means "dashboard".
function calibSource(c) {
  const s = c && typeof c.source === "string" ? c.source.trim() : "";
  return s || "dashboard";
}
// Two families for filtering: `shadow` = the agent scored blind and was compared
// against the hiring lead's historical Ashby disposition (paraform-*); `live` = a verdict the hiring lead
// gave directly (dashboard click, calibration call). Unknown sources -> live.
function calibFamily(source) {
  return String(source).indexOf("paraform") === 0 ? "shadow" : "live";
}

// Empty per-family counter. Shared shape for week/role/all-time buckets so the
// client can collapse to the active source filter without a round trip.
// fp/fn are override DIRECTIONS (the hiring lead = ground truth):
//   fp = AI advance, the hiring lead reject  (agent too loose)
//   fn = AI reject,  the hiring lead advance (agent too tight / missed)
function emptyFamCounts() {
  return {
    live: { scored: 0, agree: 0, unscored: 0, verdicts: 0, overrides: 0, fp: 0, fn: 0 },
    shadow: { scored: 0, agree: 0, unscored: 0, verdicts: 0, overrides: 0, fp: 0, fn: 0 },
  };
}

// Normalize free-text agent_rec / status labels into advance | reject | null.
// Live dashboard rows often store the longlist status ("shortlisted" / "scored"
// / "suppressed-ashby") rather than the word Advance/Reject — those still have
// a clear polarity for calibration.
function polarityAi(agentRec, agentScore) {
  const s = String(agentRec == null ? "" : agentRec).trim().toLowerCase();
  if (s && s !== "none" && s !== "null" && s !== "—") {
    if (/(^|\b)(reject|rejected|demot|disqual|\bdq\b|needs-linkedin)/.test(s)) return "reject";
    if (/suppressed/.test(s)) return "reject";
    // "scored" (and "scored (...)" variants) = on the longlist but NOT shortlisted
    if (s === "scored" || /^scored\b/.test(s)) return "reject";
    if (/(advanc|shortlist|keep-flag|stretch)/.test(s)) return "advance";
  }
  if (typeof agentScore === "number" && !isNaN(agentScore)) {
    return agentScore >= 70 ? "advance" : "reject";
  }
  return null;
}

// Normalize the hiring lead's call: dashboard events use tim_action; calib entries use
// free-text tim_verdict ("advance", "reject: …", "solid …", archive notes).
function polarityTim(timAction, timVerdict) {
  const a = String(timAction == null ? "" : timAction).trim().toLowerCase();
  if (a === "advance" || a === "reject") return a;
  const v = String(timVerdict == null ? "" : timVerdict).trim().toLowerCase();
  if (!v || v === "none" || v === "n/a" || v === "—" || v === "null") return null;
  if (/^(advanc|solid)/.test(v) || /\badvance\b/.test(v) || /positive exemplar/.test(v) || /keep as stretch/.test(v)) {
    return "advance";
  }
  if (/^(reject|don'?t|dont)/.test(v) || /\breject/.test(v) || /anti-exemplar/.test(v) || /lacks skills/.test(v)) {
    return "reject";
  }
  if (/stretch/.test(v)) return "advance";
  return null;
}

// aligned | fp | fn | unscored. the hiring lead is ground truth.
function alignmentOf(aiCall, timCall) {
  if (!aiCall || !timCall) return "unscored";
  if (aiCall === timCall) return "aligned";
  if (aiCall === "advance" && timCall === "reject") return "fp";
  if (aiCall === "reject" && timCall === "advance") return "fn";
  return "unscored";
}

function enrichCalibEntry(c) {
  const source = calibSource(c);
  const family = calibFamily(source);
  const ai_call = polarityAi(c && c.agent_rec, c && c.agent_score);
  const tim_call = polarityTim(null, c && c.tim_verdict);
  // Denominator still follows the explicit `agree` flag (null = unscored).
  // Direction (fp/fn) comes from polarities; if those can't decide on an
  // override, fall back to ai_call alone.
  let alignment = "unscored";
  if (c && c.agree === true) {
    alignment = "aligned";
  } else if (c && c.agree === false) {
    const dir = alignmentOf(ai_call, tim_call);
    if (dir === "fp" || dir === "fn") alignment = dir;
    else if (ai_call === "advance") alignment = "fp";
    else if (ai_call === "reject") alignment = "fn";
    else if (tim_call === "advance") alignment = "fn";
    else if (tim_call === "reject") alignment = "fp";
    else alignment = "unscored";
  }
  return { ...c, source, family, ai_call, tim_call, alignment };
}

function enrichEvent(e) {
  const ai_call = polarityAi(e && e.agent_rec, e && e.agent_score);
  const tim_call = polarityTim(e && e.tim_action, e && e.tim_verdict);
  let alignment = alignmentOf(ai_call, tim_call);
  // Explicit override flag from the dashboard click is authoritative when
  // polarity math and the flag disagree (weird agent_rec status strings).
  if (e && e.override === true) {
    if (alignment !== "fp" && alignment !== "fn") {
      if (ai_call === "advance" || tim_call === "reject") alignment = "fp";
      else alignment = "fn";
    }
  } else if (e && e.override === false && tim_call) {
    alignment = "aligned";
  }
  return {
    ...e,
    family: "live",
    ai_call,
    tim_call,
    alignment,
  };
}

function bumpAlignment(bucket, alignment) {
  if (!bucket) return;
  if (alignment === "aligned") bucket.agree = (bucket.agree || 0) + 1;
  else if (alignment === "fp") {
    bucket.overrides = (bucket.overrides || 0) + 1;
    bucket.fp = (bucket.fp || 0) + 1;
  } else if (alignment === "fn") {
    bucket.overrides = (bucket.overrides || 0) + 1;
    bucket.fn = (bucket.fn || 0) + 1;
  }
}

// Agreement bucketed into ISO weeks (Monday start) over ALL calibration entries.
// Percentages are deliberately NOT computed here: the client derives them so the
// source filter can recompute without another round trip.
function buildWeeklyAlignment(calibAll) {
  const emptyBucket = (monday) => {
    const end = new Date(monday.getTime() + 6 * DAY_MS);
    return {
      week_start: isoDay(monday),
      week_end: isoDay(end),
      label: weekLabel(monday, end),
      total: 0,
      scored: 0,
      agree: 0,
      override: 0,
      unscored: 0,
      // `unscored` is carried per family too so the filtered table can report the
      // right "(n unscored)" for the selected source, not the week-wide count.
      by_family: emptyFamCounts(),
      // by_role[slug] = { scored, agree, unscored, by_family: {live, shadow} }
      // so the by-role "this week" column respects the source filter too.
      by_role: {},
      by_source: {},
    };
  };

  const buckets = new Map();
  for (const raw of calibAll || []) {
    // Accept pre-enriched entries (from buildFeedbackState) or raw ones.
    const c = raw && raw.alignment ? raw : enrichCalibEntry(raw);
    const d = parseCalibDate(c && c.date);
    if (!d) continue; // missing / unparseable date -> not bucketable
    const monday = mondayOfUtc(d);
    const key = isoDay(monday);
    let b = buckets.get(key);
    if (!b) { b = emptyBucket(monday); buckets.set(key, b); }

    // Only true/false count toward agreement. `agree: null` means the hiring lead gave no
    // quality verdict — recorded as unscored, never in the denominator.
    const scored = c.agree === true || c.agree === false;
    const agreed = c.agree === true;
    const source = c.source || calibSource(c);
    const role = c && c.role ? String(c.role) : "(unassigned)";
    const famKey = c.family || calibFamily(source);
    const alignment = c.alignment || (agreed ? "aligned" : scored ? "unscored" : "unscored");

    b.total += 1;
    if (scored) {
      b.scored += 1;
      if (agreed) b.agree += 1; else b.override += 1;
      if (alignment === "fp") b.fp = (b.fp || 0) + 1;
      else if (alignment === "fn") b.fn = (b.fn || 0) + 1;
    } else {
      b.unscored += 1;
    }
    if (!b.by_role[role]) {
      b.by_role[role] = {
        scored: 0, agree: 0, unscored: 0, overrides: 0, fp: 0, fn: 0,
        by_family: emptyFamCounts(),
      };
    }
    if (!b.by_source[source]) {
      b.by_source[source] = { scored: 0, agree: 0, unscored: 0, overrides: 0, fp: 0, fn: 0 };
    }
    const fam = b.by_family[famKey];
    const roleFam = b.by_role[role].by_family[famKey];
    fam.verdicts += 1;
    roleFam.verdicts += 1;
    if (!scored) {
      fam.unscored += 1;
      b.by_role[role].unscored += 1;
      roleFam.unscored += 1;
      b.by_source[source].unscored = (b.by_source[source].unscored || 0) + 1;
    } else {
      for (const a of [fam, b.by_role[role], roleFam, b.by_source[source]]) {
        if (!a) continue;
        a.scored += 1;
        bumpAlignment(a, alignment);
      }
    }
  }
  if (!buckets.size) return [];

  // Emit CONTIGUOUS weeks: a gap week with no verdicts becomes a zero bucket so
  // the trend can't lie by compressing time.
  const keys = Array.from(buckets.keys()).sort();
  const firstT = Date.parse(keys[0] + "T00:00:00Z");
  const lastT = Date.parse(keys[keys.length - 1] + "T00:00:00Z");
  const out = [];
  for (let t = firstT; t <= lastT; t += 7 * DAY_MS) {
    const monday = new Date(t);
    out.push(buckets.get(isoDay(monday)) || emptyBucket(monday));
  }
  return out.length > WEEKLY_CAP ? out.slice(out.length - WEEKLY_CAP) : out;
}

// Read model for the UI: queued events joined with processed markers, plus
// calibration entries and per-role agreement stats.
async function buildFeedbackState() {
  const queue = parseJsonl(QUEUE_FILE);
  const procById = new Map();
  for (const p of parseJsonl(PROCESSED_FILE)) if (p && p.id) procById.set(p.id, p);
  const outreach = await buildOutreachIndex();

  let events = queue.map((e) => {
    const p = procById.get(e.id) || null;
    const c = e.candidate || {};
    const o =
      outreach.byLi.get(liKey(c.linkedin_url)) ||
      (c.name ? outreach.byName.get(String(c.name).trim().toLowerCase()) : null) ||
      null;
    return {
      ...e,
      state: p ? p.status || "processed" : "pending",
      result: p && p.result != null ? p.result : null,
      processed_at: p && p.processed_at != null ? p.processed_at : null,
      outreach: o, // real send-state from the ledger (null = nothing logged yet)
    };
  });
  events.sort((a, b) => String(b.ts || "").localeCompare(String(a.ts || "")));
  if (events.length > 500) events = events.slice(0, 500);

  const calibRaw = parseJsonl(CALIB_FILE);
  // Enrich every entry with source/family + ai_call/tim_call/alignment (aligned
  // | fp | fn | unscored) so the client can filter the verdicts table by
  // override direction without re-deriving polarity.
  const calibAll = calibRaw.map(enrichCalibEntry);
  let calibration = calibAll.slice();
  calibration.sort((a, b) => String(b.date || "").localeCompare(String(a.date || "")));
  if (calibration.length > 500) calibration = calibration.slice(0, 500);

  // Events get the same polarity/alignment fields. Live clicks are always family=live.
  events = events.map(enrichEvent);

  const emptyRole = () => ({
    verdicts: 0,
    scored: 0,
    agree: 0,
    overrides: 0,
    fp: 0,
    fn: 0,
    by_family: emptyFamCounts(),
  });
  const byRole = {};
  for (const c of calibAll) {
    const slug = c && c.role;
    if (!slug) continue;
    if (!byRole[slug]) byRole[slug] = emptyRole();
    const r = byRole[slug];
    const fam = r.by_family[c.family || calibFamily(c.source)];
    r.verdicts += 1;
    fam.verdicts += 1;
    // `scored` is the agreement denominator (agree null = no quality verdict).
    if (c.agree === true || c.agree === false) {
      r.scored += 1;
      fam.scored += 1;
      bumpAlignment(r, c.alignment);
      bumpAlignment(fam, c.alignment);
    } else {
      fam.unscored += 1;
    }
  }

  // All-time totals over EVERY entry (the `calibration` array above is truncated
  // for the UI, so it must not be used as a denominator). Family splits + fp/fn
  // let the top tiles follow the All / Your clicks / Shadow-rated filter.
  const allTime = {
    total: calibAll.length,
    scored: 0,
    agree: 0,
    override: 0,
    unscored: 0,
    fp: 0,
    fn: 0,
    by_family: emptyFamCounts(),
  };
  for (const c of calibAll) {
    const fam = allTime.by_family[c.family || calibFamily(c.source)];
    fam.verdicts += 1;
    if (c && (c.agree === true || c.agree === false)) {
      allTime.scored += 1;
      fam.scored += 1;
      bumpAlignment(allTime, c.alignment);
      // allTime uses `override` (singular) historically — keep it in sync.
      if (c.alignment === "fp" || c.alignment === "fn") {
        allTime.override += 1;
      }
      bumpAlignment(fam, c.alignment);
    } else {
      allTime.unscored += 1;
      fam.unscored += 1;
    }
  }

  return {
    events,
    calibration,
    weekly: buildWeeklyAlignment(calibAll),
    stats: { pending: pendingCount(), byRole, allTime },
  };
}

// ---------------------------------------------------------------------------
// Server
// ---------------------------------------------------------------------------
const port = process.env.DASHBOARD_PORT || 3000;

Bun.serve({
  port,
  async fetch(req) {
    const url = new URL(req.url);
    const path = url.pathname;
    console.log(`[req] ${new Date().toISOString()} ${req.method} ${path}`);

    // API: parse everything fresh from disk on every request.
    if (path.endsWith("/api/data")) {
      try {
        const data = await buildData();
        return Response.json(data, { headers: { "Cache-Control": "no-store" } });
      } catch (e) {
        return Response.json(
          { error: String((e && e.message) || e) },
          { status: 500 }
        );
      }
    }

    // Feedback: append the hiring lead's Advance/Reject verdict to the queue + ping webhook.
    if (req.method === "POST" && path.endsWith("/api/feedback")) {
      let body;
      try {
        body = await req.json();
      } catch {
        return Response.json({ error: "invalid JSON body" }, { status: 400 });
      }
      return acceptFeedback(body);
    }

    // Same endpoint via GET: the platform's dashboard proxy drops POSTs
    // ("fetch failed", observed 2026-07-27) while GETs pass, so the client
    // retries with the payload base64url-encoded in ?p=.
    if (req.method === "GET" && path.endsWith("/api/feedback")) {
      const p = url.searchParams.get("p");
      let body;
      try {
        body = JSON.parse(
          Buffer.from(p.replace(/-/g, "+").replace(/_/g, "/"), "base64").toString("utf8")
        );
      } catch {
        return Response.json({ error: "missing or invalid p param" }, { status: 400 });
      }
      return acceptFeedback(body);
    }

    // Feedback read model for the UI (events + calibration + stats).
    if (path.endsWith("/api/feedback-state")) {
      try {
        return Response.json(await buildFeedbackState(), {
          headers: { "Cache-Control": "no-store" },
        });
      } catch (e) {
        return Response.json({ error: String((e && e.message) || e) }, { status: 500 });
      }
    }

    // Everything else -> serve the single-page UI (robust to subpath serving).
    try {
      const html = readFileSync(UI_FILE, "utf8");
      return new Response(html, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store",
        },
      });
    } catch (e) {
      return new Response("UI file not found: " + String(e), { status: 500 });
    }
  },
});

console.log(
  `Recruiting Pipeline dashboard running on http://localhost:${port}` +
    (ATSLESS ? " [datasource: atsless — Ashby disabled]" : "")
);

// Warm the Ashby caches (jobs + active pipeline) in the background at boot so
// the first real request — including the harness screenshot — rides an
// already-started build instead of paying full cold-start latency. We also
// AWAIT the per-application stage-history enrichment here so the cached pipeline
// objects carry their timelines by the time the first client renders (the
// request path itself still never blocks on these calls — see enrichStageHistory).
(async () => {
  try {
    await buildData();
    if (ATSLESS) return; // everything reads local files — no Ashby caches to warm
    // Warm the interview cache too (buildData only KICKS its detached refresh):
    // this awaits the in-flight build so the upcoming strip is ready
    // on the first paint, mirroring the active-pipeline warm below.
    await refreshInterviews(readManifest());
    const sync = await getAshbyJobs();
    if (sync.jobs) {
      await getActivePipeline(sync.jobs);
      if (pipeCache.data) await enrichStageHistory(sync.jobs, pipeCache.data);
      // Warm the leads cache too. Its LinkedIn/tag + stage-history enrichment
      // fires detached inside buildLeads (mutating the cached objects), so
      // badges/days-in-stage fill in on the next read.
      await getLeads(sync.jobs);
    }
  } catch (e) {
    console.error("Startup cache warm failed:", String((e && e.message) || e));
  }
})();

// Recover clicks made while the server was down: 60s after boot, if anything is
// still pending (no ping had gone out for it), send one.
setTimeout(() => {
  try {
    if (pendingCount() > 0) sendWebhookPing(false);
  } catch (e) {
    console.error("[feedback] boot ping check failed:", String((e && e.message) || e));
  }
}, 60 * 1000);
