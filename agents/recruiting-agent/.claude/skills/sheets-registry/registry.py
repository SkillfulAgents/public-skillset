#!/usr/bin/env python3
"""Shared candidate registry on Google Sheets — multi-owner collaboration layer.

Sheet model (see /workspace/pipeline/registry.json for the spreadsheet id):
  events tab     — append-only log: ts, actor, candidate_key, role, action, payload(JSON).
                   Append order is the authority for conflicts (first `advanced` wins)
                   and the basis for outreach cadence math (initial-send timestamps).
  candidates tab — current state, one row per (candidate_key, role), upserted.
                   Core columns + full longlist record as JSON in `payload`.

Identity: OWNER env var (alice, bob, ...) stamps every event and every row update.

Usage:
  uv run --env-file /workspace/.env --with requests registry.py <cmd> ...
    init [--title "..."]           create a NEW registry spreadsheet (events + candidates
                                   tabs with headers) and write registry.json — first-run
                                   only; fails if registry.json already exists
    event '<json>'                 append one event (needs candidate_key, role, action;
                                   ts/actor auto-filled) + upsert the candidate row
    events                         bulk: JSONL events on stdin
    check <key-or-url> [--role R]  pre-write re-check: owner/status/contact state,
                                   straight from the Sheet. Exit 2 = owned by someone
                                   else, exit 3 = already contacted (suppress).
    push --file <longlist.jsonl> --role <slug> [--since YYYY-MM-DD]
                                   batch-upsert local longlist records into candidates;
                                   appends `sourced` events for keys new to the Sheet.
                                   Skips rows owned by a different OWNER (reports them).
    pull [--role R]                dump candidates rows as JSONL to stdout
    queue [--owner O]              queued-not-yet-sent, from events (default: my OWNER)
    cadence [--owner O]            per-candidate latest initial/followup sent ts (for
                                   +4d/+10d due math), from events
    rebuild-row <key> --role R     recompute one candidates row from its events
    stats                          row counts per role/status/owner
"""
import json
import os
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone

import requests

REG_PATH = "/workspace/pipeline/registry.json"
REG = json.load(open(REG_PATH)) if os.path.exists(REG_PATH) else None
SID = REG["spreadsheet_id"] if REG else None
PROXY = os.environ["PROXY_BASE_URL"].rstrip("/")
TOKEN = os.environ["PROXY_TOKEN"]
ACCT = os.environ.get("GSHEETS_ACCOUNT_ID", "").strip()
OWNER = os.environ.get("OWNER", "").strip()
BASE = f"{PROXY}/{ACCT}/sheets.googleapis.com/v4/spreadsheets/{SID}"
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

EVENT_COLS = ["ts", "actor", "candidate_key", "role", "action", "payload"]
CAND_COLS = [
    "candidate_key", "name", "linkedin_url", "role", "score", "status", "owner",
    "sourced_by", "sourced_date", "advanced_by", "advanced_date",
    "ashby_candidate_id", "ashby_application_id", "queue_state", "variant",
    "last_action", "last_action_date", "flags", "payload", "updated_at", "updated_by",
]
# actions that mirror into candidates.last_action / queue_state
QUEUE_ACTIONS = {"queued": "queued", "sent": "sent", "held": "held"}
CONTACT_ACTIONS = {"sent", "accepted", "replied", "link-shared", "booked"}


def die(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_owner():
    if not OWNER:
        die("OWNER env var not set — every registry write must be attributed (add OWNER=<name> to /workspace/.env)")


def api(method, path, retries=7, **kw):
    for i in range(retries):
        r = requests.request(method, f"{BASE}{path}", headers=H, timeout=120, **kw)
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(min(90, 3 * 2 ** i))
            continue
        if not r.ok:
            die(f"sheets api {r.status_code}: {r.text[:500]}")
        return r.json()
    die(f"sheets api gave up after {retries} retries: {r.status_code} {r.text[:300]}")


def get_values(rng):
    q = urllib.parse.quote(rng, safe="!:")
    return api("GET", f"/values/{q}").get("values", [])


def append_rows(tab, rows, chunk=100):
    # chunked: the proxy rejects large payloads ("Payload too large")
    out = None
    for i in range(0, len(rows), chunk):
        out = api(
            "POST",
            f"/values/{tab}!A1:append?valueInputOption=RAW&insertDataOption=INSERT_ROWS",
            json={"values": rows[i:i + chunk]},
        )
    return out


def batch_update_values(data):
    return api(
        "POST",
        "/values:batchUpdate",
        json={"valueInputOption": "RAW", "data": data},
    )


def normalize(url):
    """Same key rule as longlist.py: linkedin url -> in/<slug>."""
    if not url:
        return None
    m = re.search(r"linkedin\.com/(in/[^/?#]+)", url, re.I)
    return m.group(1).rstrip("/").lower() if m else None


def is_linkedin_profile(url):
    if not url or not re.search(r"https?://([a-z0-9-]+\.)?linkedin\.com/in/[^/?#]+", url, re.I):
        return False
    slug = normalize(url) or ""
    return not re.search(r"^in/(unknown|tbd|placeholder|pending)([-_].*)?$", slug)


def keyify(s):
    """Accept a raw key ('in/foo'), a slug, or a full URL."""
    if not s:
        return None
    if s.startswith("in/"):
        return s.rstrip("/").lower()
    k = normalize(s)
    return k or ("in/" + s.strip("/").lower())


# ---------- candidates tab cache ----------

def load_candidates():
    """Return (rows_as_dicts, rownum_by_(key,role)) — row numbers are 1-based sheet rows."""
    vals = get_values("candidates!A1:U100000")
    if not vals:
        die("candidates tab is empty (no header row) — registry not initialized")
    hdr = vals[0]
    out, index = [], {}
    for i, row in enumerate(vals[1:], start=2):
        d = {hdr[j]: (row[j] if j < len(row) else "") for j in range(len(hdr))}
        out.append(d)
        index[(d.get("candidate_key", ""), d.get("role", ""))] = i
    return out, index


def row_from_dict(d):
    return [str(d.get(c, "") if d.get(c) is not None else "") for c in CAND_COLS]


def upsert_candidates(dicts, index=None):
    """Upsert candidate row dicts keyed by (candidate_key, role). Returns fresh index."""
    if index is None:
        _, index = load_candidates()
    updates, appends = [], []
    next_row = max(index.values(), default=1) + 1
    for d in dicts:
        k = (d["candidate_key"], d["role"])
        if k in index:
            updates.append({"range": f"candidates!A{index[k]}", "values": [row_from_dict(d)]})
        else:
            appends.append(row_from_dict(d))
            index[k] = next_row
            next_row += 1
    if updates:
        for i in range(0, len(updates), 100):
            batch_update_values(updates[i:i + 100])
    if appends:
        append_rows("candidates", appends)
    return index


def merge_event_into_row(row, ev):
    """Fold one event into an existing candidates-row dict (row may be {})."""
    a = ev["action"]
    row.setdefault("candidate_key", ev["candidate_key"])
    row.setdefault("role", ev["role"])
    p = ev.get("payload") or {}
    if isinstance(p, str):
        try:
            p = json.loads(p)
        except (ValueError, TypeError):
            p = {}
    for f in ("name", "linkedin_url", "score", "variant", "ashby_candidate_id", "ashby_application_id"):
        if p.get(f):
            row[f] = p[f]
    if a == "sourced":
        row.setdefault("sourced_by", ev["actor"])
        row.setdefault("sourced_date", ev["ts"][:10])
        if p.get("status"):
            row["status"] = p["status"]
    elif a == "advanced":
        if not row.get("owner"):
            row["owner"] = ev["actor"]
            row["advanced_by"] = ev["actor"]
            row["advanced_date"] = ev["ts"][:10]
        row["status"] = "shortlisted" if row.get("status") in ("", "harvested", "scored", "shortlisted") else row.get("status")
    elif a in ("rejected-by-tim", "rejected"):
        row["status"] = "rejected-by-tim"
    elif a == "suppressed":
        row["status"] = "suppressed-ashby"
    elif a in QUEUE_ACTIONS:
        row["queue_state"] = QUEUE_ACTIONS[a]
        if a == "sent":
            row["status"] = "contacted"
    elif a == "replied":
        row["status"] = "replied"
        row["queue_state"] = ""
    elif a == "link-shared":
        row["status"] = "in-conversation"
    elif a == "booked":
        row["status"] = "interview-scheduled"
    elif a == "unresponsive":
        row["status"] = "unresponsive"
    elif a == "status" and p.get("status"):
        row["status"] = p["status"]
    row["last_action"] = a
    row["last_action_date"] = ev["ts"][:10]
    row["updated_at"] = now()
    row["updated_by"] = ev["actor"]
    return row


# ---------- commands ----------

def cmd_event(argv, bulk=False):
    require_owner()
    if bulk:
        evs = [json.loads(line) for line in sys.stdin if line.strip()]
    else:
        evs = [json.loads(argv[0])]
    rows = []
    for ev in evs:
        for f in ("candidate_key", "role", "action"):
            if not ev.get(f):
                die(f"event missing required field {f}: {ev}")
        ev["candidate_key"] = keyify(ev["candidate_key"])
        ev.setdefault("ts", now())
        ev.setdefault("actor", OWNER)
        pl = ev.get("payload", {})
        rows.append([ev["ts"], ev["actor"], ev["candidate_key"], ev["role"], ev["action"],
                     json.dumps(pl, ensure_ascii=False) if not isinstance(pl, str) else pl])
    append_rows("events", rows)
    # fold into candidates tab
    cands, index = load_candidates()
    by_key = {(c["candidate_key"], c["role"]): c for c in cands}
    touched = {}
    for ev in evs:
        k = (ev["candidate_key"], ev["role"])
        row = touched.get(k) or by_key.get(k, {})
        touched[k] = merge_event_into_row(row, ev)
    upsert_candidates(list(touched.values()), index)
    print(json.dumps({"appended": len(evs), "candidates_upserted": len(touched)}))


def read_events(candidate_key=None, role=None):
    vals = get_values("events!A2:F200000")
    evs = []
    for r in vals:
        r = r + [""] * (6 - len(r))
        ev = dict(zip(EVENT_COLS, r))
        if candidate_key and ev["candidate_key"] != candidate_key:
            continue
        if role and ev["role"] != role:
            continue
        evs.append(ev)
    return evs


def cmd_check(argv):
    key = keyify(argv[0])
    role = None
    if "--role" in argv:
        role = argv[argv.index("--role") + 1]
    cands, _ = load_candidates()
    mine = [c for c in cands if c["candidate_key"] == key]
    evs = read_events(candidate_key=key)
    contacted = [e for e in evs if e["action"] in CONTACT_ACTIONS]
    result = {
        "candidate_key": key,
        "rows": [{k: c.get(k, "") for k in ("role", "status", "owner", "score", "queue_state", "last_action", "last_action_date")} for c in mine],
        "events": len(evs),
        "contacted": bool(contacted),
        "first_contact": contacted[0]["ts"] if contacted else None,
        "contact_actors": sorted({e["actor"] for e in contacted}),
    }
    print(json.dumps(result, indent=2))
    other_owner = [c for c in mine if c.get("owner") and c["owner"] != OWNER and (not role or c["role"] == role)]
    if other_owner:
        sys.exit(2)
    if contacted:
        sys.exit(3)


def cmd_push(argv):
    require_owner()
    if "--file" not in argv or "--role" not in argv:
        die("push needs --file <longlist.jsonl> --role <slug>")
    path = argv[argv.index("--file") + 1]
    role = argv[argv.index("--role") + 1]
    since = argv[argv.index("--since") + 1] if "--since" in argv else None
    recs = [json.loads(line) for line in open(path) if line.strip()]
    if since:
        recs = [r for r in recs if (r.get("scored_date") or r.get("source", {}).get("date") or "9999") >= since]
    cands, index = load_candidates()
    by_key = {(c["candidate_key"], c["role"]): c for c in cands}
    upserts, new_events, skipped = [], [], []
    ts = now()
    for r in recs:
        key = r.get("id") or normalize(r.get("linkedin_url"))
        if not key:
            continue
        existing = by_key.get((key, role), {})
        if existing.get("owner") and existing["owner"] != OWNER:
            skipped.append(key)
            continue
        cur = r.get("current") or {}
        flags = r.get("flags")
        row = dict(existing)
        row.update({
            "candidate_key": key, "role": role,
            "name": r.get("name", existing.get("name", "")),
            "linkedin_url": r.get("linkedin_url", ""),
            "score": r.get("score") if r.get("score") is not None else existing.get("score", ""),
            "status": r.get("status", existing.get("status", "")),
            "flags": json.dumps(flags, ensure_ascii=False) if isinstance(flags, list) else (flags or ""),
            "ashby_candidate_id": r.get("ashby_candidate_id", existing.get("ashby_candidate_id", "")),
            "ashby_application_id": r.get("ashby_application_id", existing.get("ashby_application_id", "")),
            "payload": json.dumps(r, ensure_ascii=False),
            "updated_at": ts, "updated_by": OWNER,
        })
        row.setdefault("sourced_by", OWNER)
        row.setdefault("sourced_date", (r.get("source") or {}).get("date", ts[:10]))
        _ = cur  # current title/company live inside payload
        if (key, role) not in by_key and "--no-events" not in argv:
            new_events.append([ts, OWNER, key, role, "sourced",
                               json.dumps({"name": r.get("name"), "status": r.get("status"), "score": r.get("score")}, ensure_ascii=False)])
        upserts.append(row)
    if new_events:
        for i in range(0, len(new_events), 500):
            append_rows("events", new_events[i:i + 500])
    if upserts:
        upsert_candidates(upserts, index)
    print(json.dumps({"pushed": len(upserts), "new_sourced_events": len(new_events),
                      "skipped_other_owner": skipped}))


def cmd_reconcile(argv):
    """Merge Sheet truth into the local longlist file (session-start sync).

    Sheet wins for: owner, contact/queue state (contacted/replied/unresponsive/
    interview-scheduled/rejected-by-tim/suppressed-ashby). Local wins for
    everything else (scores, evidence — this install's workbench).
    Sheet rows missing locally (e.g. sourced by the other owner) are inserted
    from their payload so dedupe and crossrole checks see them.
    """
    if "--file" not in argv or "--role" not in argv:
        die("reconcile needs --file <longlist.jsonl> --role <slug>")
    path = argv[argv.index("--file") + 1]
    role = argv[argv.index("--role") + 1]
    sheet_wins = {"contacted", "replied", "in-conversation", "interview-scheduled",
                  "unresponsive", "rejected-by-candidate", "rejected-by-tim", "suppressed-ashby"}
    local = {}
    try:
        for line in open(path):
            if line.strip():
                r = json.loads(line)
                local[r.get("id") or normalize(r.get("linkedin_url")) or ""] = r
    except FileNotFoundError:
        pass
    cands, _ = load_candidates()
    changed = inserted = 0
    for c in cands:
        if c.get("role") != role:
            continue
        key = c["candidate_key"]
        rec = local.get(key)
        if rec is None:
            try:
                rec = json.loads(c.get("payload") or "{}")
            except ValueError:
                rec = {}
            rec.setdefault("name", c.get("name"))
            rec.setdefault("linkedin_url", c.get("linkedin_url"))
            rec["id"] = key
            rec.setdefault("status", c.get("status") or "harvested")
            if c.get("owner"):
                rec["owner"] = c["owner"]
            rec["registry_inserted"] = c.get("updated_at", "")[:10]
            local[key] = rec
            inserted += 1
            continue
        dirty = False
        if c.get("owner") and rec.get("owner") != c["owner"]:
            rec["owner"] = c["owner"]
            dirty = True
        if c.get("status") in sheet_wins and rec.get("status") != c["status"]:
            rec["status"] = c["status"]
            dirty = True
        if c.get("queue_state") and rec.get("queue_state") != c["queue_state"]:
            rec["queue_state"] = c["queue_state"]
            dirty = True
        changed += dirty
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        for r in local.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)
    print(json.dumps({"role": role, "updated": changed, "inserted_from_sheet": inserted, "total_local": len(local)}))


def cmd_pull(argv):
    role = argv[argv.index("--role") + 1] if "--role" in argv else None
    cands, _ = load_candidates()
    n = 0
    for c in cands:
        if role and c.get("role") != role:
            continue
        print(json.dumps(c, ensure_ascii=False))
        n += 1
    print(f"pulled {n} rows", file=sys.stderr)


def cmd_queue(argv):
    owner = argv[argv.index("--owner") + 1] if "--owner" in argv else OWNER
    cands, _ = load_candidates()
    out = [c for c in cands if c.get("queue_state") == "queued" and (not owner or c.get("owner") == owner)]
    for c in sorted(out, key=lambda c: -(float(c.get("score") or 0))):
        print(json.dumps({k: c.get(k, "") for k in ("candidate_key", "name", "role", "score", "owner", "variant", "last_action_date")}))
    print(f"{len(out)} queued for owner={owner or 'any'}", file=sys.stderr)


def cmd_cadence(argv):
    owner = argv[argv.index("--owner") + 1] if "--owner" in argv else OWNER
    evs = read_events()
    per = {}
    for e in evs:
        if e["action"] != "sent":
            continue
        try:
            p = json.loads(e["payload"] or "{}")
        except ValueError:
            p = {}
        if owner and e["actor"] != owner:
            continue
        t = p.get("type", "initial")
        per.setdefault((e["candidate_key"], e["role"]), {})[t] = e["ts"]
    for (key, role), sends in per.items():
        print(json.dumps({"candidate_key": key, "role": role, "sends": sends}))
    print(f"{len(per)} candidates with sends (owner={owner or 'any'})", file=sys.stderr)


def cmd_rebuild_row(argv):
    require_owner()
    key = keyify(argv[0])
    role = argv[argv.index("--role") + 1]
    evs = [e for e in read_events(candidate_key=key, role=role)]
    if not evs:
        die(f"no events for {key} / {role}")
    row = {}
    for e in evs:
        merge_event_into_row(row, e)
    upsert_candidates([row])
    print(json.dumps(row, indent=2))


def cmd_init(argv):
    global SID, BASE
    if REG is not None:
        die(f"{REG_PATH} already exists (spreadsheet {SID}) — registry already initialized")
    title = "Recruiting — Shared Candidate Registry"
    if "--title" in argv:
        title = argv[argv.index("--title") + 1]
    r = requests.post(
        f"{PROXY}/{ACCT}/sheets.googleapis.com/v4/spreadsheets",
        headers=H, timeout=120,
        json={"properties": {"title": title},
              "sheets": [{"properties": {"title": "events"}},
                         {"properties": {"title": "candidates"}}]},
    )
    if not r.ok:
        die(f"sheets api {r.status_code}: {r.text[:500]}")
    data = r.json()
    SID = data["spreadsheetId"]
    url = data.get("spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{SID}")
    BASE = f"{PROXY}/{ACCT}/sheets.googleapis.com/v4/spreadsheets/{SID}"
    batch_update_values([
        {"range": "events!A1", "values": [EVENT_COLS]},
        {"range": "candidates!A1", "values": [CAND_COLS]},
    ])
    with open(REG_PATH, "w") as f:
        json.dump({"spreadsheet_id": SID, "url": url, "created": now()}, f, indent=2)
        f.write("\n")
    print(f"created: {url}")
    print(f"wrote {REG_PATH}")


def cmd_stats(argv):
    cands, _ = load_candidates()
    by = {}
    for c in cands:
        k = (c.get("role", "?"), c.get("status", "?"), c.get("owner") or "-")
        by[k] = by.get(k, 0) + 1
    for (role, status, owner), n in sorted(by.items()):
        print(f"{role:30s} {status:25s} owner={owner:6s} {n}")
    print(f"total {len(cands)}")


def main():
    args = sys.argv[1:]
    if not args:
        die(__doc__)
    cmd, rest = args[0], args[1:]
    if not ACCT:
        die("GSHEETS_ACCOUNT_ID env var not set — connect a Google Sheets account and add it to /workspace/.env")
    if cmd != "init" and REG is None:
        die(f"no {REG_PATH} — run `registry.py init` first (creates the shared Sheet) or restore the file")
    fn = {
        "init": cmd_init,
        "event": lambda r: cmd_event(r),
        "events": lambda r: cmd_event(r, bulk=True),
        "check": cmd_check,
        "push": cmd_push,
        "pull": cmd_pull,
        "reconcile": cmd_reconcile,
        "queue": cmd_queue,
        "cadence": cmd_cadence,
        "rebuild-row": cmd_rebuild_row,
        "stats": cmd_stats,
    }.get(cmd)
    if not fn:
        die(f"unknown command {cmd}\n\n{__doc__}")
    fn(rest)


if __name__ == "__main__":
    main()
