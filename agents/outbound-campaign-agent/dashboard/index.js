// Outbound performance dashboard. Zero dependencies, Bun.serve.
//
//   bun run dashboard/index.js            # then open http://localhost:3000
//   DASHBOARD_PORT=8080 bun run dashboard/index.js
//
// It reads its JSON at REQUEST time, not at boot, so `report.py
// --write-dashboard` shows up on a refresh instead of a restart.
//
// Nothing here knows your company, your product, your metric names, or your
// ICP tiers. Every label, threshold, KPI card, segment table, sentiment bucket
// and benchmark row comes out of the payload that report.py emits
// (schema `outbound-report/1`). Point it at another team's file and it renders
// their motion with no code edit.
//
// The n_floor suppression is re-enforced HERE, from the denominator, not from
// the payload's `reliable` flag. A hand-written payload that claims a 50% reply
// rate off 2 sends still renders as "1 of 2", never as a percentage.
//
// APPROVALS. The dashboard also reads and writes the approval queue (the
// `drafts` table in campaigns.db, via bun:sqlite): pending drafts render at
// the top with Approve / Reject, and a decision here is exactly a decision by
// `queue.py`: same table, same audit row. Approving is NOT sending; send.py
// still runs every gate.
//
// PATHS. This file runs from two places: the template repo (bun run
// dashboard/index.js) and a copy under /workspace/artifacts/<slug>/ made by
// onboarding. Each data path therefore resolves through a chain: env
// override, then repo-relative, then the workspace root.

import { Database } from "bun:sqlite";
import { existsSync } from "node:fs";

const port = process.env.DASHBOARD_PORT || 3000;
const ROOT = new URL("..", import.meta.url).pathname;

function resolvePath(envName, rel) {
  const candidates = [
    process.env[envName],
    `${ROOT}${rel}`,
    `/workspace/${rel}`,
  ].filter(Boolean);
  return candidates.find(existsSync) || candidates[candidates.length - 1];
}

const LIVE_PATH = () => resolvePath("OUTBOUND_DASHBOARD_DATA", "data/dashboard.json");
const SAMPLE_PATH = () => resolvePath("OUTBOUND_DASHBOARD_SAMPLE", "data/dashboard.sample.json");
const DB_PATH = () => resolvePath("OUTBOUND_DB", "data/campaigns.db");

async function readJson(path) {
  try {
    const file = Bun.file(path);
    if (!(await file.exists())) {
      return { error: `File not found: ${path}. Run report.py --write-dashboard.` };
    }
    return await file.json();
  } catch (e) {
    return { error: `Failed to read ${path}: ${e.message}` };
  }
}

/* ---------- approval queue (drafts table, bun:sqlite) ---------- */

const DEMO_APPROVALS = {
  available: true, demo: true,
  pending: [
    { id: 101, prospect_id: 1, name: "Dana Whitfield", title: "Head of Operations",
      company: "Keystone Freight Co", icp_tier: "T2", step_index: 0, channel: "email",
      sender_id: "alex", confidence: 0.82, created_at: "2026-08-06 16:04:00",
      subject: "Load data at Keystone",
      body: "<p>Dana, saw Keystone is hiring two dispatchers.</p><p>Northwind moves load data between TMS and email so nobody rekeys it. Dispatch teams get 8+ hrs/week back per dispatcher.</p><p>Worth a look? https://northwind.example/try is free, no card.</p>" },
    { id: 102, prospect_id: 2, name: "Ravi Uncertain", title: "VP RevOps",
      company: "Corda Analytics", icp_tier: "T1", step_index: 0, channel: "email",
      sender_id: "alex", confidence: 0.61, created_at: "2026-08-06 16:11:00",
      subject: "RevOps handoffs at Corda",
      body: "<p>Ravi, low-confidence draft example: the observation is thin, which is why the agent staged it for review instead of sending.</p>" },
  ],
  recent: [
    { id: 99, name: "Mia Torres", company: "Bluepine Services", status: "approved",
      decided_at: "2026-08-06 15:40:00", decided_via: "dashboard", decision_reason: null },
  ],
};

function openDb() {
  const path = DB_PATH();
  if (!existsSync(path)) return { err: `No database at ${path} yet. It appears after onboarding initializes the workspace.` };
  try {
    return { db: new Database(path) };
  } catch (e) {
    return { err: `Failed to open ${path}: ${e.message}` };
  }
}

function readApprovals() {
  const { db, err } = openDb();
  if (err) return { available: false, reason: err };
  try {
    const join = "SELECT d.id, d.prospect_id, d.step_index, d.channel, d.sender_id," +
      " d.subject, d.body, d.variant, d.confidence, d.status, d.created_at," +
      " d.decided_at, d.decided_via, d.decision_reason," +
      " p.name, p.title, p.company, p.icp_tier" +
      " FROM drafts d JOIN prospects p ON p.id = d.prospect_id";
    const pending = db.query(join + " WHERE d.status = 'pending' ORDER BY d.created_at").all();
    const recent = db.query(join + " WHERE d.status != 'pending'" +
      " ORDER BY d.decided_at DESC LIMIT 8").all();
    return { available: true, pending, recent };
  } catch (e) {
    // A pre-queue database has no drafts table; that is a state, not a crash.
    return { available: false, reason: `Queue unavailable: ${e.message}` };
  } finally {
    db.close();
  }
}

function decideDraft(id, action, reason) {
  if (!Number.isInteger(id)) return { error: "id must be an integer", status: 400 };
  if (action !== "approve" && action !== "reject") {
    return { error: "action must be approve or reject", status: 400 };
  }
  if (action === "reject" && !(reason && String(reason).trim())) {
    return { error: "a rejection needs a reason; it is what teaches the drafter", status: 400 };
  }
  const { db, err } = openDb();
  if (err) return { error: err, status: 503 };
  try {
    const row = db.query("SELECT * FROM drafts WHERE id = ?").get(id);
    if (!row) return { error: `no draft #${id}`, status: 404 };
    if (row.status !== "pending") {
      return { error: `draft #${id} is already ${row.status}`, status: 409 };
    }
    const status = action === "approve" ? "approved" : "rejected";
    db.query("UPDATE drafts SET status = ?, decided_at = datetime('now')," +
      " decided_via = 'dashboard', decision_reason = ? WHERE id = ?")
      .run(status, reason ? String(reason).trim() : null, id);
    db.query("INSERT INTO decisions (stage, decision, reason, prospect_id, ref)" +
      " VALUES ('approval', ?, ?, ?, ?)")
      .run(status, reason ? String(reason).trim() : "via dashboard",
           row.prospect_id, `draft:${id}`);
    return { ok: true, id, status };
  } catch (e) {
    return { error: e.message, status: 500 };
  } finally {
    db.close();
  }
}

Bun.serve({
  port,
  async fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/api/data") {
      const which = url.searchParams.get("source") === "demo" ? SAMPLE_PATH() : LIVE_PATH();
      const data = await readJson(which);
      return Response.json(data, { headers: { "Cache-Control": "no-store" } });
    }

    if (url.pathname === "/api/approvals" && req.method === "GET") {
      const data = url.searchParams.get("source") === "demo" ? DEMO_APPROVALS : readApprovals();
      return Response.json(data, { headers: { "Cache-Control": "no-store" } });
    }

    if (url.pathname === "/api/approvals" && req.method === "POST") {
      let body;
      try {
        body = await req.json();
      } catch {
        return Response.json({ error: "invalid JSON body" }, { status: 400 });
      }
      if (body && body.demo) return Response.json({ ok: true, demo: true });
      const result = decideDraft(body?.id, body?.action, body?.reason);
      return Response.json(result, { status: result.status && result.error ? result.status : 200 });
    }

    if (url.pathname === "/" || url.pathname === "") {
      return new Response(HTML, {
        headers: { "Content-Type": "text/html; charset=utf-8" },
      });
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Outbound performance dashboard on :${port}`);
console.log(`  live   ${LIVE_PATH()}`);
console.log(`  demo   ${SAMPLE_PATH()}`);
console.log(`  queue  ${DB_PATH()}`);

const HTML = /* html */ `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Outbound performance</title>
<style>
  :root {
    --bg: #f4f6f8;
    --panel: #ffffff;
    --fg: #1c2430;
    --muted: #5a6776;
    --faint: #8a96a3;
    --border: #e3e7ec;
    --border-strong: #cfd6de;
    --accent: #2563eb;
    --accent-soft: #eaf1ff;
    --green: #16855c;
    --green-soft: #e6f4ee;
    --green-line: #b8e0cd;
    --amber: #b45309;
    --amber-soft: #fdf2e2;
    --amber-line: #f0d6a8;
    --red: #b42318;
    --red-soft: #fdecea;
    --red-line: #f3c4bf;
    --grey: #64748b;
    --grey-soft: #eef1f4;
    --blue-soft: #e6effc;
    --blue-line: #bcd6f5;
    --bar: #93b4f5;
    --bar-strong: #2563eb;
    --radius: 10px;
    --gap: 16px;
    --shadow: 0 1px 2px rgba(20,30,45,.05), 0 1px 1px rgba(20,30,45,.04);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--fg); font-size: 14px; line-height: 1.45;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 1280px; margin: 0 auto; padding: 20px 20px 72px; }

  header.top {
    display: flex; flex-wrap: wrap; align-items: center; gap: 14px;
    justify-content: space-between; margin-bottom: 16px;
  }
  .brand { display: flex; flex-direction: column; gap: 2px; }
  .brand h1 { margin: 0; font-size: 19px; font-weight: 650; letter-spacing: -.01em; }
  .brand .sub { color: var(--muted); font-size: 12.5px; }

  .header-controls { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }

  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 11px; font-weight: 700; letter-spacing: .06em;
    padding: 5px 10px; border-radius: 6px; text-transform: uppercase;
  }
  .badge.demo { background: #fdebc8; color: #8a5400; border: 1px solid #f1d199; }
  .badge.live { background: var(--green-soft); color: var(--green); border: 1px solid var(--green-line); }

  .toggle-wrap { display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--muted); }
  .switch { position: relative; width: 40px; height: 22px; flex: none; }
  .switch input { opacity: 0; width: 0; height: 0; }
  .slider {
    position: absolute; inset: 0; cursor: pointer; background: var(--border-strong);
    border-radius: 999px; transition: background .15s;
  }
  .slider:before {
    content: ""; position: absolute; height: 16px; width: 16px; left: 3px; top: 3px;
    background: #fff; border-radius: 50%; transition: transform .15s; box-shadow: 0 1px 2px rgba(0,0,0,.2);
  }
  .switch input:checked + .slider { background: var(--amber); }
  .switch input:checked + .slider:before { transform: translateX(18px); }

  .seg-toggle { display: inline-flex; background: var(--panel); border: 1px solid var(--border); border-radius: 8px; padding: 3px; box-shadow: var(--shadow); }
  .seg-toggle button {
    border: none; background: transparent; color: var(--muted); cursor: pointer;
    font-size: 13px; font-weight: 600; padding: 6px 16px; border-radius: 6px; transition: all .12s;
    text-transform: capitalize;
  }
  .seg-toggle button.active { background: var(--accent); color: #fff; }

  .updated { font-size: 12px; color: var(--faint); }
  .updated b { color: var(--muted); font-weight: 600; }

  .panel {
    background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 18px;
  }
  .panel + .panel, .grid + .panel, .panel + .grid, .row + .row, .row + .panel, .panel + .row { margin-top: var(--gap); }

  .tier-rule {
    display: flex; align-items: center; gap: 12px; margin: 26px 0 12px; color: var(--faint);
    font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
  }
  .tier-rule:first-of-type { margin-top: 6px; }
  .tier-rule::after { content: ""; flex: 1; height: 1px; background: var(--border); }

  .section-title { font-size: 13px; font-weight: 700; letter-spacing: .02em; text-transform: uppercase; color: var(--muted); margin: 0 0 14px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .section-title .hint { text-transform: none; letter-spacing: 0; font-weight: 500; color: var(--faint); font-size: 12px; }

  .deliv-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }
  .deliv-grid .wide { grid-column: span 2; }
  .dtile {
    border: 1px solid var(--border); border-radius: 9px; padding: 13px 14px;
    display: flex; flex-direction: column; gap: 3px; min-height: 92px; position: relative;
  }
  .dtile .dlabel { font-size: 11px; font-weight: 700; letter-spacing: .03em; text-transform: uppercase; color: var(--muted); }
  .dtile .dval { font-size: 24px; font-weight: 680; letter-spacing: -.02em; font-variant-numeric: tabular-nums; line-height: 1.1; }
  .dtile .dsub { font-size: 11.5px; color: var(--faint); }
  .dtile .dstatus { font-size: 12px; font-weight: 700; }
  .dtile.ok { background: var(--green-soft); border-color: var(--green-line); }
  .dtile.ok .dval, .dtile.ok .dstatus { color: var(--green); }
  .dtile.warn { background: var(--amber-soft); border-color: var(--amber-line); }
  .dtile.warn .dval, .dtile.warn .dstatus { color: var(--amber); }
  .dtile.crit { background: var(--red-soft); border-color: var(--red-line); }
  .dtile.crit .dval, .dtile.crit .dstatus { color: var(--red); }
  .dtile.neutral { background: var(--grey-soft); border-color: var(--border); }
  .dtile.neutral .dval { color: var(--grey); font-size: 17px; font-weight: 650; }
  .auth-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
  .auth-pill { border-radius: 8px; padding: 9px 10px; border: 1px solid var(--border); text-align: center; cursor: default; }
  .auth-pill .an { font-size: 11px; font-weight: 700; letter-spacing: .04em; }
  .auth-pill .as { font-size: 12px; font-weight: 700; text-transform: uppercase; margin-top: 2px; }
  .auth-pill.ok { background: var(--green-soft); border-color: var(--green-line); }
  .auth-pill.ok .as { color: var(--green); }
  .auth-pill.warn { background: var(--amber-soft); border-color: var(--amber-line); }
  .auth-pill.warn .as { color: var(--amber); }
  .auth-pill.crit { background: var(--red-soft); border-color: var(--red-line); }
  .auth-pill.crit .as { color: var(--red); }
  .auth-pill.neutral .as { color: var(--grey); }

  .spark { display: flex; align-items: flex-end; gap: 2px; height: 44px; margin-top: 4px; position: relative; }
  .spark-bar { flex: 1; border-radius: 2px 2px 0 0; min-height: 2px; background: var(--bar); }
  .spark-bar.over { background: var(--red); }
  .spark-cap { position: absolute; left: 0; right: 0; border-top: 1px dashed var(--amber); pointer-events: none; }

  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: var(--gap); }
  .kpi {
    background: var(--panel); border: 1px solid var(--border); border-radius: var(--radius);
    box-shadow: var(--shadow); padding: 15px 16px; display: flex; flex-direction: column; gap: 4px;
  }
  .kpi.feature { border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent-soft), var(--shadow); }
  .kpi .label { font-size: 12px; color: var(--muted); font-weight: 600; }
  .kpi .value { font-size: 28px; font-weight: 680; letter-spacing: -.02em; line-height: 1.08; font-variant-numeric: tabular-nums; }
  .kpi .value.small { font-size: 20px; font-weight: 650; color: var(--faint); }
  .kpi .meta { font-size: 12px; color: var(--faint); }
  .kpi .meta b { color: var(--fg); font-weight: 700; }
  .nsmall { font-size: 12px; color: var(--faint); font-style: italic; }

  .ab-state {
    font-size: 11px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase;
    padding: 5px 11px; border-radius: 999px; border: 1px solid var(--border);
  }
  .ab-state.nodata { background: var(--grey-soft); color: var(--grey); }
  .ab-state.directional { background: var(--amber-soft); color: var(--amber); border-color: var(--amber-line); }
  .ab-state.trending { background: var(--blue-soft); color: var(--accent); border-color: var(--blue-line); }
  .ab-state.significant { background: var(--green-soft); color: var(--green); border-color: var(--green-line); }
  .ab-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap); }
  .ab-card { border: 1.5px solid var(--border); border-radius: var(--radius); padding: 16px; position: relative; }
  .ab-card.winner { border-color: var(--green); background: var(--green-soft); }
  .ab-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
  .ab-name { font-size: 15px; font-weight: 700; }
  .win-pill { font-size: 10px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; color: #fff; background: var(--green); padding: 4px 9px; border-radius: 999px; }
  .ab-sends { font-size: 12px; color: var(--faint); margin: 6px 0 12px; }
  .ab-rows { display: grid; gap: 10px; }
  .ab-metric .ab-mlabel { font-size: 11.5px; color: var(--muted); display: flex; justify-content: space-between; align-items: baseline; gap: 8px; }
  .ab-metric .ab-mlabel b { color: var(--fg); font-variant-numeric: tabular-nums; font-size: 13px; }
  .ab-bar-track { height: 8px; background: #edf0f4; border-radius: 999px; overflow: hidden; margin-top: 5px; }
  .ab-bar-fill { height: 100%; background: var(--bar-strong); border-radius: 999px; }
  .ab-card.winner .ab-bar-fill { background: var(--green); }
  .ab-sig {
    margin-top: 14px; padding: 12px 14px; border-radius: 9px; background: var(--accent-soft);
    border: 1px solid var(--blue-line); display: flex; flex-wrap: wrap; gap: 16px; align-items: center;
  }
  .ab-sig .big { font-size: 19px; font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
  .ab-sig .lbl { font-size: 11.5px; color: var(--muted); }
  .ab-sig .lbl b { color: var(--fg); }
  .caption { font-size: 12px; color: var(--muted); margin-top: 12px; display: flex; gap: 6px; align-items: flex-start; line-height: 1.5; }
  .caption .mark { color: var(--amber); font-weight: 700; }

  table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
  th, td { text-align: right; padding: 8px 10px; font-size: 13px; border-bottom: 1px solid var(--border); }
  th:first-child, td:first-child { text-align: left; }
  thead th { color: var(--muted); font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: .03em; cursor: pointer; user-select: none; white-space: nowrap; }
  thead th.nosort { cursor: default; }
  thead th .arrow { opacity: .55; font-size: 10px; }
  tbody tr:last-child td { border-bottom: none; }
  tbody td:first-child { font-weight: 600; }
  .muted-cell { color: var(--faint); font-style: italic; font-size: 11.5px; }
  .rate-cell { white-space: nowrap; }
  .rate-bar { display: inline-block; height: 6px; background: var(--bar); border-radius: 3px; vertical-align: middle; margin-left: 6px; }

  .mtg-list { display: flex; flex-direction: column; }
  .mtg-row { display: grid; grid-template-columns: 150px 1fr auto; gap: 12px; align-items: baseline; padding: 8px 0; border-bottom: 1px solid var(--border); }
  .mtg-row:last-child { border-bottom: none; }
  .mtg-when { font-size: 12.5px; font-weight: 700; font-variant-numeric: tabular-nums; }
  .mtg-who { font-size: 13px; }
  .mtg-who span { color: var(--faint); margin-left: 6px; font-size: 12px; }
  .mtg-sender { font-size: 11px; color: var(--muted); background: var(--grey-soft); border-radius: 999px; padding: 2px 9px; white-space: nowrap; }

  .sent-list { display: flex; flex-direction: column; gap: 9px; }
  .sent-row { display: grid; grid-template-columns: 130px 1fr 42px; gap: 12px; align-items: center; }
  .sent-name { font-size: 13px; font-weight: 600; text-transform: capitalize; }
  .sent-track { height: 20px; background: #f0f3f7; border-radius: 5px; overflow: hidden; }
  .sent-fill { height: 100%; border-radius: 5px; min-width: 0; }
  .sent-count { text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; font-size: 13px; }

  .cad-grid { display: grid; gap: 12px; }
  .cad-row { display: grid; grid-template-columns: 118px 1fr minmax(120px, auto); gap: 12px; align-items: center; }
  .cad-label { font-weight: 600; font-size: 13px; }
  .cad-count { font-weight: 500; font-size: 11px; color: var(--faint); margin-top: 1px; }
  .cad-track { height: 22px; background: #f0f3f7; border-radius: 5px; overflow: hidden; }
  .cad-fill { height: 100%; background: var(--bar-strong); border-radius: 5px; }
  .cad-meta { text-align: right; font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .cad-meta.muted { font-style: italic; color: var(--faint); }

  .funnel { display: flex; flex-direction: column; gap: 6px; }
  .funnel-row { display: grid; grid-template-columns: 120px 1fr 132px; gap: 10px; align-items: center; }
  .funnel-name { font-size: 13px; font-weight: 600; }
  .funnel-track { height: 26px; background: #f0f3f7; border-radius: 6px; overflow: hidden; }
  .funnel-fill { height: 100%; border-radius: 6px; }
  .funnel-end { text-align: right; font-size: 12.5px; font-variant-numeric: tabular-nums; }
  .funnel-end b { font-weight: 700; font-size: 13.5px; }
  .funnel-end .conv { color: var(--faint); font-size: 11.5px; }
  .funnel-note { font-size: 11.5px; color: var(--faint); margin-top: 10px; line-height: 1.5; }

  .row { display: grid; gap: var(--gap); }
  .row.two { grid-template-columns: 1.35fr 1fr; }
  .row.three { grid-template-columns: repeat(auto-fit, minmax(440px, 1fr)); }

  .empty {
    text-align: center; color: var(--muted); padding: 22px 16px; border: 1px dashed var(--border-strong);
    border-radius: 8px; background: #fafbfc; font-size: 13px;
  }
  .empty b { color: var(--fg); display: block; font-size: 14.5px; margin-bottom: 4px; }
  .global-empty { border-color: var(--accent); background: var(--accent-soft); color: var(--fg); padding: 30px 20px; }
  .global-empty b { color: var(--accent); font-size: 16px; }

  .bench-src { font-size: 11.5px; color: var(--faint); margin-top: 12px; line-height: 1.5; }
  .bench-src b { color: var(--muted); }

  .loading { padding: 40px; text-align: center; color: var(--muted); }
  .err { background: var(--red-soft); border: 1px solid var(--red-line); color: var(--red); padding: 14px 16px; border-radius: 8px; font-size: 13px; }

  .appr-panel { border-color: var(--amber-line); }
  .appr-count { font-size: 11px; font-weight: 800; letter-spacing: .05em; padding: 4px 10px; border-radius: 999px; background: var(--amber-soft); color: var(--amber); border: 1px solid var(--amber-line); }
  .appr-count.zero { background: var(--green-soft); color: var(--green); border-color: var(--green-line); }
  .appr-list { display: flex; flex-direction: column; gap: 12px; }
  .appr-card { border: 1px solid var(--border); border-radius: 9px; padding: 13px 14px; }
  .appr-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 12px; }
  .appr-who { font-size: 13.5px; font-weight: 700; }
  .appr-who span { color: var(--muted); font-weight: 500; }
  .appr-chip { font-size: 10.5px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; padding: 2px 8px; border-radius: 999px; background: var(--grey-soft); color: var(--grey); }
  .appr-conf { font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
  .appr-conf.low { color: var(--amber); font-weight: 700; }
  .appr-subj { font-size: 13px; font-weight: 600; margin-top: 8px; }
  .appr-body { margin-top: 5px; font-size: 12.5px; color: var(--muted); white-space: pre-wrap; line-height: 1.5; border-left: 3px solid var(--border); padding: 2px 0 2px 10px; }
  .appr-actions { display: flex; gap: 8px; margin-top: 10px; align-items: center; }
  .abtn { border: 1px solid var(--border-strong); border-radius: 7px; padding: 6px 16px; font-size: 12.5px; font-weight: 700; cursor: pointer; background: var(--panel); transition: all .12s; }
  .abtn.approve { background: var(--green); border-color: var(--green); color: #fff; }
  .abtn.approve:hover { filter: brightness(1.08); }
  .abtn.reject { color: var(--red); border-color: var(--red-line); background: var(--red-soft); }
  .abtn.reject:hover { filter: brightness(.97); }
  .abtn:disabled { opacity: .5; cursor: not-allowed; }
  .appr-err { color: var(--red); font-size: 12px; }
  .appr-recent { margin-top: 12px; font-size: 12px; color: var(--faint); line-height: 1.7; }
  .appr-recent b { color: var(--muted); }

  @media (max-width: 820px) {
    .row.two { grid-template-columns: 1fr; }
    .ab-grid { grid-template-columns: 1fr; }
    .deliv-grid .wide { grid-column: span 1; }
    .funnel-row { grid-template-columns: 92px 1fr 118px; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand">
      <h1 id="title">Outbound performance</h1>
      <div class="sub" id="subtitle"></div>
    </div>
    <div class="header-controls">
      <span id="modeBadge" class="badge live">Live</span>
      <div class="toggle-wrap">
        <label class="switch">
          <input type="checkbox" id="demoToggle" />
          <span class="slider"></span>
        </label>
        <span>Demo data</span>
      </div>
    </div>
  </header>

  <div class="header-controls" style="justify-content: space-between; margin-bottom: var(--gap);">
    <div class="seg-toggle" id="windowToggle"></div>
    <div class="updated" id="updated"></div>
  </div>

  <div id="approvals"></div>
  <div id="root"><div class="loading">Loading...</div></div>
</div>

<script>
const $ = (sel, el=document) => el.querySelector(sel);
const STATE = {
  window: null,
  demo: new URLSearchParams(location.search).get("demo") === "1",
  data: null,
  approvals: null,
  sort: {},
};

// Fallback only. The real value always arrives in payload.config.n_floor.
const N_FLOOR_FALLBACK = 10;

function pct(x, digits=1) {
  if (x === null || x === undefined || isNaN(x)) return "-";
  return (x * 100).toFixed(digits) + "%";
}
function num(x) { return (x ?? 0).toLocaleString("en-US"); }
function fmtDate(iso) {
  if (!iso) return "unknown";
  const d = new Date(iso);
  if (isNaN(d)) return iso;
  return d.toLocaleString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "numeric", minute: "2-digit" });
}
function esc(s) { return String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c])); }
// Meeting timestamps are formatted textually, never through Date(), because
// parsing them would silently reinterpret the stored clock time in the browser's
// timezone and move every meeting by the viewer's UTC offset.
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function fmtWhen(s) {
  const m = String(s ?? "").match(/^(\\d{4})-(\\d{2})-(\\d{2})[T ](\\d{2}):(\\d{2})/);
  if (!m) return String(s ?? "") || "no start time";
  return MONTHS[Number(m[2]) - 1] + " " + Number(m[3]) + ", " + m[4] + ":" + m[5];
}
function human(s) { return String(s ?? "").replace(/_/g, " "); }

/* ---------- the suppression rule, enforced in the render layer ----------
   A rate is only ever shown as a percentage when its own denominator clears
   n_floor. The payload's "reliable" flag is ignored on purpose: this must hold
   for a hand-written file too. */
function nFloor() {
  const cfg = (STATE.data && STATE.data.config) || {};
  return cfg.n_floor ?? N_FLOOR_FALLBACK;
}
function showable(r) {
  return !!r && (r.d || 0) >= nFloor() && r.value !== null && r.value !== undefined;
}
function rateText(r, digits=1) {
  // A numerator with no denominator is not "no data": a meeting booked this
  // week off a send from last month lands in a window with nothing to rate it
  // against. Show the count and say the denominator is missing.
  if (r && !(r.d > 0) && (r.n > 0)) {
    return '<span class="muted-cell">' + num(r.n) + ', no denominator this window</span>';
  }
  if (!r || !(r.d > 0)) return '<span class="muted-cell">no data</span>';
  if (!showable(r)) return '<span class="muted-cell">' + num(r.n) + ' of ' + num(r.d) + ' (n&lt;' + nFloor() + ')</span>';
  return pct(r.value, digits);
}
function denomText(r) {
  if (!r || !(r.d > 0)) return "0 of 0";
  return num(r.n) + " / " + num(r.d);
}

async function load() {
  const root = $("#root");
  if (!STATE.data) root.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const res = await fetch("api/data?source=" + (STATE.demo ? "demo" : "live") + "&t=" + Date.now());
    STATE.data = await res.json();
    render();
  } catch (e) {
    root.innerHTML = '<div class="err">Failed to load data: ' + esc(e.message) + '</div>';
  }
  loadApprovals();
}

/* ---------- approval queue ----------
   A decision here is a decision: it writes the same table and the same audit
   row as queue.py. Approving stages the send; every send still passes the
   gates (caps, window, do-not-touch, suppression) in send.py. */
async function loadApprovals() {
  try {
    const res = await fetch("api/approvals?source=" + (STATE.demo ? "demo" : "live") + "&t=" + Date.now());
    STATE.approvals = await res.json();
  } catch (e) {
    STATE.approvals = { available: false, reason: e.message };
  }
  renderApprovals();
}

function bodyText(html) {
  // DOMParser yields an inert document: nothing executes, nothing loads.
  // Block-level closers become newlines so paragraphs stay separated.
  const withBreaks = String(html || "")
    .replace(/<\\/(p|div|li|h[1-6])>/gi, "\\n")
    .replace(/<br\\s*\\/?>/gi, "\\n");
  const doc = new DOMParser().parseFromString(withBreaks, "text/html");
  return (doc.body.textContent || "").replace(/\\n{3,}/g, "\\n\\n").trim();
}

function renderApprovals() {
  const el = $("#approvals");
  const a = STATE.approvals;
  if (!a) { el.innerHTML = ""; return; }

  if (!a.available) {
    el.innerHTML = '<div class="panel appr-panel" style="margin-bottom:var(--gap)">' +
      '<div class="section-title">Approval queue' +
      '<span class="appr-count zero">unavailable</span></div>' +
      '<div class="empty">' + esc(a.reason || "Queue not readable.") + '</div></div>';
    return;
  }

  const pending = a.pending || [];
  const chip = pending.length
    ? '<span class="appr-count">' + pending.length + ' awaiting review</span>'
    : '<span class="appr-count zero">nothing waiting</span>';

  let cards;
  if (!pending.length) {
    cards = '<div class="empty"><b>No drafts awaiting approval.</b>' +
      'The agent stages drafts here when a human needs to review them: first batches, low-confidence copy, out-of-pattern sends.</div>';
  } else {
    cards = '<div class="appr-list">' + pending.map(d => {
      const conf = d.confidence !== null && d.confidence !== undefined
        ? '<span class="appr-conf' + (d.confidence < 0.7 ? ' low' : '') + '">confidence ' + d.confidence.toFixed(2) + '</span>' : "";
      return '<div class="appr-card" data-id="' + d.id + '">' +
        '<div class="appr-head">' +
          '<span class="appr-who">' + esc(d.name) + ' <span>' + esc(d.title || "") + ' at ' + esc(d.company || "") + '</span></span>' +
          (d.icp_tier ? '<span class="appr-chip">' + esc(d.icp_tier) + '</span>' : "") +
          '<span class="appr-chip">step ' + d.step_index + ' &middot; ' + esc(human(d.channel)) + '</span>' +
          (d.variant ? '<span class="appr-chip">variant ' + esc(d.variant) + '</span>' : "") +
          conf +
        '</div>' +
        (d.subject ? '<div class="appr-subj">' + esc(d.subject) + '</div>' : "") +
        '<div class="appr-body">' + esc(bodyText(d.body)) + '</div>' +
        '<div class="appr-actions">' +
          '<button class="abtn approve" data-act="approve" data-id="' + d.id + '">Approve</button>' +
          '<button class="abtn reject" data-act="reject" data-id="' + d.id + '">Reject</button>' +
          '<span class="appr-err" data-err="' + d.id + '"></span>' +
        '</div></div>';
    }).join("") + '</div>';
  }

  const recent = (a.recent || []).slice(0, 5).map(r =>
    '<b>' + esc(r.name || ("draft #" + r.id)) + '</b> (' + esc(r.company || "") + ') ' +
    esc(r.status) + (r.decided_via ? ' via ' + esc(r.decided_via) : "") +
    (r.decision_reason ? ': ' + esc(r.decision_reason) : "")).join(" &middot; ");

  el.innerHTML = '<div class="panel appr-panel" style="margin-bottom:var(--gap)">' +
    '<div class="section-title">Approval queue' +
    '<span class="hint">approve here or in chat; approving stages the send, every gate still runs</span>' +
    chip + '</div>' + cards +
    (recent ? '<div class="appr-recent">Recent: ' + recent + '</div>' : "") +
    '</div>';

  el.querySelectorAll(".abtn").forEach(btn => {
    btn.addEventListener("click", () => decide(Number(btn.dataset.id), btn.dataset.act));
  });
}

async function decide(id, action) {
  let reason = null;
  if (action === "reject") {
    reason = prompt("Why reject this draft? The reason is recorded and teaches the drafter.");
    if (reason === null) return;
    if (!reason.trim()) { alert("A rejection needs a reason."); return; }
  }
  const card = document.querySelector('.appr-card[data-id="' + id + '"]');
  if (card) card.querySelectorAll(".abtn").forEach(b => b.disabled = true);
  try {
    const res = await fetch("api/approvals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, action, reason, demo: !!STATE.demo }),
    });
    const out = await res.json();
    if (out.error) throw new Error(out.error);
  } catch (e) {
    const errEl = document.querySelector('[data-err="' + id + '"]');
    if (errEl) errEl.textContent = e.message;
    if (card) card.querySelectorAll(".abtn").forEach(b => b.disabled = false);
    return;
  }
  loadApprovals();
}

function renderWindowToggle(cfg) {
  const wins = cfg.windows && cfg.windows.length ? cfg.windows : Object.keys(STATE.data.windows || {});
  if (!STATE.window || !wins.includes(STATE.window)) {
    STATE.window = cfg.default_window && wins.includes(cfg.default_window) ? cfg.default_window : wins[0];
  }
  $("#windowToggle").innerHTML = wins.map(w =>
    '<button data-win="' + esc(w) + '"' + (w === STATE.window ? ' class="active"' : '') + '>' + esc(w) + '</button>'
  ).join("");
}

function render() {
  const data = STATE.data;
  if (!data || data.error) {
    $("#root").innerHTML = '<div class="err">' + esc(data && data.error ? data.error : "No data") + '</div>';
    return;
  }
  const cfg = data.config || {};
  $("#title").textContent = cfg.title || "Outbound performance";
  $("#subtitle").textContent = cfg.subtitle || "";
  document.title = (cfg.title || "Outbound performance");

  const badge = $("#modeBadge");
  badge.className = "badge " + (data.demo ? "demo" : "live");
  badge.textContent = data.demo ? "Demo Data" : "Live";
  $("#updated").innerHTML = "Last updated <b>" + esc(fmtDate(data.generated_at)) + "</b>";

  renderWindowToggle(cfg);
  const win = (data.windows && data.windows[STATE.window]) || {};
  const totals = win.totals || {};
  const hasSends = (totals.sends || 0) > 0;

  let html = "";
  html += '<div class="tier-rule">Tier 1 &middot; summary</div>';
  html += renderDeliverability(data, cfg, win);
  html += renderKPIs(win, cfg);
  html += renderMeetings(win);

  html += '<div class="tier-rule">Tier 2 &middot; operator detail</div>';
  if (!hasSends) html += renderGlobalEmpty();
  html += renderAB(win);
  html += '<div class="row two">' + renderFunnel(win, cfg) + renderSentiment(win) + '</div>';
  html += renderSegments(win);
  html += renderCohorts(data.cohorts || []);
  html += renderBenchmarks(cfg, win);

  $("#root").innerHTML = html;
  attachSortHandlers();
}

function renderGlobalEmpty() {
  return '<div class="empty global-empty"><b>No sends in this window.</b>' +
    'Flip on <b>Demo data</b> (top right) to preview a populated dashboard, or wait for the next cadence tick. ' +
    'Deliverability and authentication stay visible above.</div>';
}

/* ---------- Tier 1: deliverability ---------- */
function renderDeliverability(data, cfg, win) {
  const dl = win.deliverability || {};
  const br = dl.bounce_rate || null;
  const warn = dl.warn ?? (cfg.thresholds || {}).bounce_warn ?? 0.02;
  const halt = dl.halt ?? (cfg.thresholds || {}).bounce_halt ?? 0.05;
  const sends = dl.sends || 0;

  const statusMap = { ok: ["ok", "Healthy"], warn: ["warn", "Elevated"], halt: ["crit", "Over halt threshold"], none: ["neutral", "No sends"] };
  const [bClass, bStatus] = statusMap[dl.status] || statusMap.none;

  const bounceTile =
    '<div class="dtile ' + bClass + '">' +
      '<div class="dlabel">Bounce rate</div>' +
      '<div class="dval">' + (sends > 0 ? rateText(br, 2) : "-") + '</div>' +
      '<div class="dsub">' + num(dl.bounces) + ' of ' + num(sends) + ' sends (' + esc(STATE.window) + ')</div>' +
      '<div class="dstatus">' + esc(bStatus) + ' &middot; warn ' + pct(warn, 1) + ' / halt ' + pct(halt, 1) + '</div>' +
    '</div>';

  const complaintTile =
    '<div class="dtile neutral" title="No complaint feedback loop is wired into this payload.">' +
      '<div class="dlabel">Complaints</div>' +
      '<div class="dval">Not tracked</div>' +
      '<div class="dsub">No feedback loop wired.</div>' +
      '<div class="dsub">Check your provider console manually.</div>' +
    '</div>';

  const series = data.daily_send_series || [];
  const cap = cfg.daily_cap || 0;
  const maxVal = Math.max(cap || 0, ...series.map(d => d.count || 0), 1);
  const overDays = series.filter(d => d.over_cap).length;
  const capTop = cap > 0 ? (1 - cap / maxVal) * 100 : -1;
  const bars = series.map(d => {
    const c = d.count || 0;
    const h = Math.max(2, (c / maxVal) * 100);
    return '<div class="spark-bar' + (d.over_cap ? ' over' : '') + '" style="height:' + h.toFixed(1) + '%" title="' + esc(d.date) + ': ' + c + '"></div>';
  }).join("");
  const volTile =
    '<div class="dtile wide" style="background:var(--panel);border-color:' + (overDays > 0 ? "var(--red-line)" : "var(--border)") + '">' +
      '<div class="dlabel" style="display:flex;justify-content:space-between;gap:8px"><span>Volume vs ' + num(cap) + '/day cap</span>' +
        '<span style="color:' + (overDays > 0 ? "var(--red)" : "var(--faint)") + ';font-weight:600">' +
        (overDays > 0 ? overDays + " day(s) over cap" : "within cap") + '</span></div>' +
      '<div class="spark">' + (series.length ? (capTop >= 0 ? '<div class="spark-cap" style="top:' + capTop.toFixed(1) + '%"></div>' : '') + bars : '<span class="dsub">No send history.</span>') + '</div>' +
      '<div class="dsub">Last ' + series.length + ' days &middot; emails/day &middot; dashed line = cap</div>' +
    '</div>';

  const auth = cfg.auth || {};
  const authKeys = Object.keys(auth);
  const authPill = (key) => {
    const a = auth[key] || { status: "unknown", detail: "" };
    const cls = a.status === "pass" ? "ok" : a.status === "warn" ? "warn" : a.status === "fail" ? "crit" : "neutral";
    return '<div class="auth-pill ' + cls + '" title="' + esc(a.detail || "") + '">' +
      '<div class="an">' + esc(String(key).toUpperCase()) + '</div>' +
      '<div class="as">' + esc(String(a.status || "?").toUpperCase()) + '</div></div>';
  };
  const authTile = authKeys.length
    ? '<div class="dtile wide" style="background:var(--panel)">' +
        '<div class="dlabel">Email authentication</div>' +
        '<div class="auth-row" style="margin-top:6px;grid-template-columns:repeat(' + authKeys.length + ',1fr)">' +
        authKeys.map(authPill).join("") + '</div>' +
        '<div class="dsub" style="margin-top:6px">Hover for the record detail.</div>' +
      '</div>'
    : "";

  return '<div class="panel"><div class="section-title">Deliverability health' +
    '<span class="hint">the binding constraint on a low-volume sending domain</span></div>' +
    '<div class="deliv-grid">' + bounceTile + complaintTile + volTile + authTile + '</div></div>';
}

/* ---------- Tier 1: KPI cards, defined entirely by the payload ---------- */
function renderKPIs(win, cfg) {
  const kpis = win.kpis || [];
  if (!kpis.length) return "";
  const inner = kpis.map(k => {
    const r = k.rate;
    const isRate = k.kind === "rate";
    const ok = isRate && showable(r);
    const value = ok ? pct(r.value) : num(k.count);
    let meta;
    if (!isRate) {
      meta = '<div class="meta">count in window</div>';
    } else if (ok) {
      meta = '<div class="meta"><b>' + denomText(r) + '</b>' + (k.denominator_label ? ' ' + esc(k.denominator_label) : '') + '</div>';
    } else if (r && r.d > 0) {
      meta = '<div class="meta"><b>' + denomText(r) + '</b>' + (k.denominator_label ? ' ' + esc(k.denominator_label) : '') + '</div>' +
             '<span class="nsmall">n too small for a rate (' + num(r.d) + ' &lt; ' + nFloor() + ')</span>';
    } else {
      meta = '<span class="nsmall">no denominator yet</span>';
    }
    return '<div class="kpi' + (k.feature ? ' feature' : '') + '">' +
      '<span class="label">' + esc(k.label) + '</span>' +
      '<span class="value' + (ok || !isRate ? '' : ' small') + '">' + value + '</span>' + meta + '</div>';
  }).join("");

  return '<div style="margin-top:var(--gap)">' +
    '<div class="section-title">Headline metrics<span class="hint">window: ' + esc(STATE.window) +
    (win.label ? ' (' + esc(win.label) + ')' : '') + '</span></div>' +
    '<div class="kpi-grid">' + inner + '</div></div>';
}

/* ---------- Tier 1: meetings, the outcome metric ----------
   Sits directly under the KPI strip because booked meetings are the only
   number on this page that a revenue forecast can be built from. Every
   string, including the "held" qualifier and the attribution notes, is read
   from the payload so the caveat cannot drift away from the number. */
function renderMeetings(win) {
  const m = win.meetings || {};
  const rates = m.rates || {};
  const booked = m.booked || 0;

  const heldSub = m.held_note ? '<div class="dsub">' + esc(m.held_note) + '</div>' : "";
  const tiles =
    '<div class="dtile" style="background:var(--panel)">' +
      '<div class="dlabel">Meetings booked</div>' +
      '<div class="dval">' + num(booked) + '</div>' +
      '<div class="dsub">' + num(m.no_show || 0) + ' no-show, ' + num(m.cancelled || 0) + ' cancelled and not counted</div>' +
    '</div>' +
    '<div class="dtile" style="background:var(--panel)">' +
      '<div class="dlabel">Held</div>' +
      '<div class="dval">' + num(m.held || 0) + '</div>' + heldSub +
    '</div>' +
    '<div class="dtile" style="background:var(--panel)">' +
      '<div class="dlabel">Meeting rate</div>' +
      '<div class="dval">' + rateText(rates.meeting_rate) + '</div>' +
      '<div class="dsub">' + denomText(rates.meeting_rate) + ' meetings / emails sent</div>' +
    '</div>' +
    '<div class="dtile" style="background:var(--panel)">' +
      '<div class="dlabel">Meeting to opportunity</div>' +
      '<div class="dval">' + rateText(rates.meeting_to_opp) + '</div>' +
      '<div class="dsub">' + denomText(rates.meeting_to_opp) + ' opportunities / booked</div>' +
    '</div>';

  const up = m.upcoming || [];
  let upBody;
  if (!up.length) {
    upBody = '<div class="empty"><b>Nothing on the calendar ahead.</b>Meetings appear here once a future start time is booked.</div>';
  } else {
    upBody = '<div class="mtg-list">' + up.map(e =>
      '<div class="mtg-row">' +
        '<div class="mtg-when">' + esc(fmtWhen(e.starts_at)) + '</div>' +
        '<div class="mtg-who">' + esc(e.prospect_name) + '<span>' + esc(e.company) + '</span></div>' +
        '<div class="mtg-sender">' + esc(e.sender_id) + '</div>' +
      '</div>').join("") + '</div>';
    const extra = (m.upcoming_total || up.length) - up.length;
    if (extra > 0) upBody += '<div class="funnel-note">' + num(extra) + ' more scheduled beyond this list.</div>';
  }

  const srcRows = (m.by_source || []).filter(s => (s.count || 0) > 0 || booked === 0);
  let srcBody;
  if (!srcRows.length) {
    srcBody = '<div class="empty"><b>No meetings in this window.</b>Nothing to break down by detection path.</div>';
  } else {
    const max = Math.max(...srcRows.map(s => s.count || 0), 1);
    srcBody = '<div class="sent-list">' + srcRows.map(s => {
      const w = ((s.count || 0) / max) * 100;
      return '<div class="sent-row"><div class="sent-name">' + esc(human(s.source)) + '</div>' +
        '<div class="sent-track"><div class="sent-fill" style="width:' + w.toFixed(1) + '%;background:#2563eb"></div></div>' +
        '<div class="sent-count">' + num(s.count) + '</div></div>';
    }).join("") + '</div>';
  }

  const notes = (m.notes || []).map(n => '<div class="funnel-note">' + esc(n) + '</div>').join("");

  return '<div style="margin-top:var(--gap)">' +
    '<div class="section-title">Meetings<span class="hint">the outcome metric, sourced from the calendar</span></div>' +
    '<div class="deliv-grid">' + tiles + '</div>' +
    '<div class="row two" style="margin-top:var(--gap)">' +
      '<div class="panel"><div class="section-title">Upcoming meetings' +
        '<span class="hint">booked, start time still ahead</span></div>' + upBody + '</div>' +
      '<div class="panel"><div class="section-title">How they were detected' +
        '<span class="hint">calendar vs reply vs manual</span></div>' + srcBody + notes + '</div>' +
    '</div></div>';
}

/* ---------- Tier 2: A/B ---------- */
function renderAB(win) {
  const ab = win.ab_test || {};
  const state = ab.state || "No data";
  const cls = { "No data": "nodata", "Directional": "directional", "Trending": "trending", "Significant": "significant" }[state] || "nodata";
  const arms = ab.arms || [];

  let body;
  if (arms.length < 2) {
    body = '<div class="empty"><b>No variant comparison yet.</b>' + esc(ab.note || "Sends are not split across two arms.") + '</div>';
  } else {
    const metricKeys = ["reply_rate", "positive_reply_rate", "meeting_rate"];
    const maxOf = (key) => Math.max(...arms.map(a => ((a.rates || {})[key] || {}).value || 0), 0.0001);
    body = '<div class="ab-grid">' + arms.map(a => {
      const isWin = ab.leader === a.name;
      const rows = metricKeys.filter(k => (a.rates || {})[k]).map(k => {
        const r = a.rates[k];
        if (!showable(r)) {
          return '<div class="ab-metric"><div class="ab-mlabel"><span>' + esc(human(k)) + '</span>' +
            '<span class="nsmall">' + num(r.n) + ' of ' + num(r.d) + ', n too small</span></div></div>';
        }
        const w = Math.min(100, (r.value / maxOf(k)) * 100);
        return '<div class="ab-metric"><div class="ab-mlabel"><span>' + esc(human(k)) + ' &middot; ' + denomText(r) + '</span><b>' + pct(r.value) + '</b></div>' +
          '<div class="ab-bar-track"><div class="ab-bar-fill" style="width:' + w.toFixed(1) + '%"></div></div></div>';
      }).join("");
      return '<div class="ab-card' + (isWin ? ' winner' : '') + '">' +
        '<div class="ab-head"><div class="ab-name">' + esc(a.name) + '</div>' +
        (isWin ? '<span class="win-pill">Leader</span>' : '') + '</div>' +
        '<div class="ab-sends">' + num(a.sends) + ' sends &middot; ' + num(a.replies) + ' replies &middot; ' +
        num(a.positive) + ' positive &middot; ' + num(a.meetings) + ' meetings</div>' +
        '<div class="ab-rows">' + rows + '</div></div>';
    }).join("") + '</div>';

    const s2s = ab.sends_to_significance;
    body += '<div class="ab-sig">' +
      (s2s !== null && s2s !== undefined
        ? '<div><div class="big">~' + num(s2s) + '</div><div class="lbl">more sends <b>per arm</b> to reach significance' +
          (ab.required_n_per_arm ? ' (' + num(ab.required_n_per_arm) + ' total/arm)' : '') + '</div></div>'
        : '<div><div class="big">-</div><div class="lbl">significance target unavailable</div></div>') +
      '<div><div class="big">' + (ab.p_value !== null && ab.p_value !== undefined ? ab.p_value.toFixed(4) : "n/a") + '</div><div class="lbl">p-value (two-proportion z)</div></div>' +
      '<div><div class="big">' + esc(ab.leader || "tie") + '</div><div class="lbl">current leader</div></div>' +
      '</div>';
    if (ab.note) body += '<div class="caption"><span class="mark">Note:</span> ' + esc(ab.note) + '</div>';
  }

  return '<div class="panel"><div class="section-title" style="justify-content:space-between">' +
    '<span>A/B readout <span class="hint">state is honest about sample size</span></span>' +
    '<span class="ab-state ' + cls + '">' + esc(state) + '</span></div>' + body + '</div>';
}

/* ---------- Tier 2: funnel ---------- */
const FUNNEL_RAMP = ["#94a3b8", "#7dade8", "#60a5fa", "#3b82f6", "#2563eb", "#1d4ed8", "#16855c"];

function renderFunnel(win, cfg) {
  const stages = win.funnel || [];
  const top = stages.length ? (stages[0].count || 0) : 0;
  let body;
  if (!stages.length || top === 0) {
    body = '<div class="empty"><b>No funnel yet.</b>Stages populate after the first sends.</div>';
  } else {
    const max = Math.max(...stages.map(s => s.count || 0), 1);
    body = '<div class="funnel">' + stages.map((s, i) => {
      const w = Math.max(1.5, ((s.count || 0) / max) * 100);
      const prev = i > 0 ? (stages[i-1].count || 0) : null;
      const conv = i === 0 ? "start" : (prev > 0 ? "from prev " + pct((s.count || 0) / prev) : "from prev -");
      const color = FUNNEL_RAMP[Math.min(i, FUNNEL_RAMP.length - 1)];
      return '<div class="funnel-row"><div class="funnel-name">' + esc(s.name) + '</div>' +
        '<div class="funnel-track"><div class="funnel-fill" style="width:' + w.toFixed(1) + '%;background:' + color + '"></div></div>' +
        '<div class="funnel-end"><b>' + num(s.count) + '</b> <span class="conv">' + conv + '</span></div></div>';
    }).join("") + '</div>';
    const notes = (cfg.notes || []).map(n => '<div class="funnel-note">' + esc(n) + '</div>').join("");
    body += notes;
  }
  return '<div class="panel"><div class="section-title">Conversion funnel<span class="hint">stage to stage</span></div>' + body + '</div>';
}

/* ---------- Tier 2: sentiment ---------- */
const TONE_COLORS = { good: "#16855c", warn: "#b45309", bad: "#b42318", neutral: "#94a3b8" };

function renderSentiment(win) {
  const rows = win.sentiment || [];
  const total = rows.reduce((a, s) => a + (s.count || 0), 0);
  let body;
  if (total === 0) {
    body = '<div class="empty"><b>No replies categorized.</b>Sentiment appears once replies are tagged.</div>';
  } else {
    const max = Math.max(...rows.map(s => s.count || 0), 1);
    body = '<div class="sent-list">' + rows.map(s => {
      const w = ((s.count || 0) / max) * 100;
      const color = TONE_COLORS[s.tone] || TONE_COLORS.neutral;
      return '<div class="sent-row"><div class="sent-name">' + esc(human(s.label)) + '</div>' +
        '<div class="sent-track"><div class="sent-fill" style="width:' + w.toFixed(1) + '%;background:' + color + '"></div></div>' +
        '<div class="sent-count">' + num(s.count) + '</div></div>';
    }).join("") + '</div>';
    body += '<div class="funnel-note">' + num(total) + ' categorized replies in this window.</div>';
  }
  return '<div class="panel"><div class="section-title">Reply sentiment<span class="hint">quality over rate</span></div>' + body + '</div>';
}

/* ---------- Tier 2: segments ---------- */
function renderSegments(win) {
  const segs = win.segments || [];
  if (!segs.length) return "";
  const bars = segs.filter(s => s.display === "bars");
  const tables = segs.filter(s => s.display !== "bars");
  let html = "";
  if (bars.length) html += '<div class="row two">' + bars.map(renderSegBars).join("") + '</div>';
  if (tables.length) html += '<div class="row three">' + tables.map(renderSegTable).join("") + '</div>';
  return html;
}

function renderSegBars(seg) {
  const rows = seg.rows || [];
  let body;
  if (!rows.length) {
    body = '<div class="empty"><b>No data yet.</b>Appears after the first sends.</div>';
  } else {
    const max = Math.max(...rows.map(r => r.sends || 0), 1);
    body = '<div class="cad-grid">' + rows.map(r => {
      const w = Math.max(2, ((r.sends || 0) / max) * 100);
      const rate = (r.rates || {}).reply_rate;
      const meta = showable(rate)
        ? '<div class="cad-meta">reply ' + pct(rate.value) + ' &middot; ' + denomText(rate) + '</div>'
        : '<div class="cad-meta muted">' + num(r.replies) + ' of ' + num(r.sends) + ', n too small</div>';
      return '<div class="cad-row"><div class="cad-label">' + esc(r.name) +
        '<div class="cad-count">' + num(r.sends) + ' sends</div></div>' +
        '<div class="cad-track"><div class="cad-fill" style="width:' + w.toFixed(1) + '%"></div></div>' +
        meta + '</div>';
    }).join("") + '</div>';
  }
  return '<div class="panel"><div class="section-title">' + esc(seg.title) +
    '<span class="hint">rates hidden below the n floor</span></div>' + body + '</div>';
}

const RATE_COLS = [
  { key: "reply_rate", label: "Reply%" },
  { key: "positive_reply_rate", label: "Pos%" },
  { key: "meeting_rate", label: "Mtg%" },
];

function renderSegTable(seg) {
  const rows = (seg.rows || []).map(r => ({ ...r }));
  let body;
  if (!rows.length) {
    body = '<div class="empty"><b>No data yet.</b>Segment breakdown appears after sends.</div>';
  } else {
    const sortState = STATE.sort[seg.key] || { col: "sends", dir: "desc" };
    const valueOf = (row, col) => {
      if (col === "name") return String(row.name || "").toLowerCase();
      if (col in row) return row[col] ?? 0;
      const r = (row.rates || {})[col];
      return showable(r) ? r.value : -1;   // suppressed rows sort last, not first
    };
    rows.sort((a, b) => {
      const av = valueOf(a, sortState.col), bv = valueOf(b, sortState.col);
      const cmp = av < bv ? -1 : av > bv ? 1 : 0;
      return sortState.dir === "asc" ? cmp : -cmp;
    });
    const maxRate = Math.max(...rows.map(r => {
      const rr = (r.rates || {}).reply_rate;
      return showable(rr) ? rr.value : 0;
    }), 0.0001);
    const arrow = (col) => sortState.col === col ? (sortState.dir === "asc" ? " ▲" : " ▼") : "";
    const th = (col, lbl) => '<th data-seg="' + esc(seg.key) + '" data-col="' + esc(col) + '">' + esc(lbl) + '<span class="arrow">' + arrow(col) + '</span></th>';
    const cell = (r, key) => {
      const rate = (r.rates || {})[key];
      if (!showable(rate)) return '<td>' + rateText(rate) + '</td>';
      if (key === "reply_rate") {
        const bw = Math.min(40, (rate.value / maxRate) * 40);
        return '<td class="rate-cell">' + pct(rate.value) + '<span class="rate-bar" style="width:' + bw.toFixed(0) + 'px"></span></td>';
      }
      return '<td>' + pct(rate.value) + '</td>';
    };
    body = '<table><thead><tr>' + th("name", seg.column || "Group") + th("sends", "Sends") + th("replies", "Repl") +
      RATE_COLS.map(c => th(c.key, c.label)).join("") + '</tr></thead><tbody>' +
      rows.map(r => '<tr><td>' + esc(r.name) + '</td><td>' + num(r.sends) + '</td><td>' + num(r.replies) + '</td>' +
        RATE_COLS.map(c => cell(r, c.key)).join("") + '</tr>').join("") +
      '</tbody></table>';
  }
  return '<div class="panel"><div class="section-title">' + esc(seg.title) +
    '<span class="hint">click a header to sort</span></div>' + body + '</div>';
}

function attachSortHandlers() {
  document.querySelectorAll("th[data-col]").forEach(th => {
    th.addEventListener("click", () => {
      const seg = th.dataset.seg, col = th.dataset.col;
      const cur = STATE.sort[seg] || { col: "sends", dir: "desc" };
      if (cur.col === col) cur.dir = cur.dir === "asc" ? "desc" : "asc";
      else { cur.col = col; cur.dir = col === "name" ? "asc" : "desc"; }
      STATE.sort[seg] = cur;
      render();
    });
  });
}

/* ---------- Tier 2: weekly cohorts ---------- */
function renderCohorts(cohorts) {
  let body;
  if (!cohorts.length) {
    body = '<div class="empty"><b>No weekly cohorts yet.</b>Week over week trend appears after the first send week.</div>';
  } else {
    const maxRate = Math.max(...cohorts.map(c => {
      const r = (c.rates || {}).reply_rate;
      return showable(r) ? r.value : 0;
    }), 0.0001);
    body = '<table><thead><tr><th class="nosort">Week</th><th class="nosort">Prospects</th>' +
      '<th class="nosort">Sends</th><th class="nosort">Replies</th><th class="nosort">Reply%</th><th class="nosort">Pos%</th></tr></thead><tbody>' +
      cohorts.map(c => {
        const rr = (c.rates || {}).reply_rate;
        const pr = (c.rates || {}).positive_reply_rate;
        const bar = showable(rr) ? '<span class="rate-bar" style="width:' + Math.min(44, (rr.value / maxRate) * 44).toFixed(0) + 'px"></span>' : "";
        return '<tr><td>' + esc(c.label) + '</td><td>' + num(c.prospects) + '</td><td>' + num(c.sends) + '</td>' +
          '<td>' + num(c.replies) + '</td><td class="rate-cell">' + rateText(rr) + bar + '</td><td>' + rateText(pr) + '</td></tr>';
      }).join("") + '</tbody></table>';
  }
  return '<div class="panel"><div class="section-title">Weekly cohorts<span class="hint">decay or improvement over time</span></div>' + body + '</div>';
}

/* ---------- Tier 2: benchmarks (only if the config supplies them) ----------
   Expected shape: config.benchmarks = { source: "...", rows: [
     { label: "Reply rate", metric: "reply_rate", range: "3-7% good" } ] }   */
function renderBenchmarks(cfg, win) {
  const bm = cfg.benchmarks;
  if (!bm || !bm.rows || !bm.rows.length) return "";
  const rates = win.rates || {};
  const table = '<table><thead><tr><th class="nosort">Metric</th>' +
    '<th class="nosort" style="text-align:right">You (' + esc(STATE.window) + ')</th>' +
    '<th class="nosort" style="text-align:left">Reference range</th></tr></thead><tbody>' +
    bm.rows.map(r => '<tr><td>' + esc(r.label) + '</td><td>' + rateText(rates[r.metric]) + '</td>' +
      '<td style="text-align:left;color:var(--muted)">' + esc(r.range || "-") + '</td></tr>').join("") +
    '</tbody></table>';
  return '<div class="panel"><div class="section-title">Benchmark reference<span class="hint">orientation, not targets</span></div>' +
    table + '<div class="bench-src"><b>Directional ranges.</b> Source: ' + esc(bm.source || "n/a") + '</div></div>';
}

/* ---------- controls ---------- */
$("#windowToggle").addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-win]");
  if (!btn) return;
  STATE.window = btn.dataset.win;
  render();
});

$("#demoToggle").addEventListener("change", (e) => {
  STATE.demo = e.target.checked;
  STATE.data = null;
  load();
});

if (STATE.demo) $("#demoToggle").checked = true;
load();
setInterval(load, 60000);
</script>
</body>
</html>`;
