#!/usr/bin/env python3
"""Deduped JSONL store for sourcing longlists. See SKILL.md for usage."""
import argparse
import glob as globmod
import json
import os
import sys
import tempfile
from urllib.parse import urlparse

PIPELINE_DIR = "/workspace/pipeline"
# Actively-pursued statuses: a person in one of these in ANY role is locked to
# that role (the hiring lead, 2026-07-22: never source the same person into two roles).
LOCK_STATUSES = {"shortlisted", "contacted", "replied", "in-conversation", "interview-scheduled"}


def normalize(url):
    p = urlparse(url.strip())
    path = p.path.rstrip("/").lower()
    if "/in/" in path:
        return "in/" + path.split("/in/", 1)[1]
    return (p.netloc.lower().removeprefix("www.") + path) or url.lower()


def is_linkedin_profile(url):
    """LinkedIn is a HARD condition (the hiring lead, 2026-07-24): a candidate cannot be
    shortlisted/advanced without a real linkedin.com/in/ profile URL. GitHub,
    personal sites, and pending-enrich:// placeholders do NOT qualify — they must
    be resolved to a LinkedIn profile first (resolve-then-DQ).

    Sentinel slugs like /in/UNKNOWN-rich-harris are placeholders wearing a
    linkedin.com/in/ costume: they passed the substring gate and put people with
    no resolvable profile (Rich Harris, William Fu-Hinthorn) in front of the hiring lead,
    who rejected them with "no linkedin" (2026-07-27)."""
    u = (url or "").strip().lower()
    if not (u.startswith("http") and "linkedin.com/in/" in u):
        return False
    slug = u.split("linkedin.com/in/", 1)[1].strip("/")
    return bool(slug) and not slug.startswith(("unknown", "tbd", "placeholder", "pending"))


def fingerprint(rec):
    name = (rec.get("name") or "").strip().lower()
    company = ((rec.get("current") or {}).get("company") or "").strip().lower()
    return f"{name}|{company}" if name and company else None


def load(path):
    recs = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    recs[r["id"]] = r
    return recs


def save(path, recs):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".")
    with os.fdopen(fd, "w") as f:
        for r in recs.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def role_slug(path):
    base = os.path.basename(path)
    return base[len("longlist-"):-len(".jsonl")] if base.startswith("longlist-") else base


def scan_other_roles(rid, fp, exclude_path):
    """Find this person in OTHER roles' longlists (by id, then name+company)."""
    hits = []
    for path in sorted(globmod.glob(f"{PIPELINE_DIR}/longlist-*.jsonl")):
        if os.path.abspath(path) == os.path.abspath(exclude_path or ""):
            continue
        try:
            others = load(path)
        except Exception:
            continue
        hit = others.get(rid)
        if hit is None and fp:
            hit = next((o for o in others.values() if fingerprint(o) == fp), None)
        if hit is not None:
            hits.append({"role": role_slug(path), "id": hit.get("id"), "name": hit.get("name"),
                         "status": hit.get("status"), "score": hit.get("score")})
    return hits


def crossrole_conflict(hits):
    return next((h for h in hits if h.get("status") in LOCK_STATUSES), None)


def add_record(recs, rec, file_path):
    url = rec.get("linkedin_url")
    if not url or not rec.get("name"):
        return "invalid", "record needs name and linkedin_url"
    rid = normalize(url)
    if rid in recs:
        return "skipped", rid
    li = is_linkedin_profile(url)
    if not li:
        rec["needs_linkedin"] = True
        if rec.get("status") in LOCK_STATUSES:
            return "needs-linkedin", (f"{rid} has no LinkedIn profile URL (got {url!r}) — "
                                      f"resolve to a linkedin.com/in/ profile before "
                                      f"status '{rec.get('status')}' (the hiring lead 2026-07-24)")
    fp = fingerprint(rec)
    hits = scan_other_roles(rid, fp, file_path)
    lock = crossrole_conflict(hits)
    if lock:
        return "crossrole-locked", f"{rid} is {lock['status']} in role '{lock['role']}' — one active role per person"
    warn = None
    if hits:
        rec["crossrole"] = sorted({h["role"] for h in hits})
        warn = f"{rid} also on longlist(s) {rec['crossrole']} (inactive there) — added with crossrole marker"
    if fp and not warn:
        for other in recs.values():
            if fingerprint(other) == fp:
                warn = f"soft-dupe of {other['id']} (same name+company, different URL)"
                break
    rec["id"] = rid
    rec.setdefault("status", "harvested")
    rec.setdefault("touch", "card")
    recs[rid] = rec
    return "added", warn or rid


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("record")
    sub.add_parser("bulk")
    s = sub.add_parser("update")
    s.add_argument("id")
    s.add_argument("merge")
    s = sub.add_parser("crossrole", help="find a person across ALL role longlists")
    s.add_argument("query", help="LinkedIn URL, in/<handle> id, or exact name")
    s = sub.add_parser("list")
    s.add_argument("--status")
    s.add_argument("--min-score", type=float, dest="min_score")
    s.add_argument("--limit", type=int, default=0)
    s.add_argument("--format", choices=["json", "md"], default="json")
    sub.add_parser("stats")
    a = p.parse_args()

    if a.cmd == "crossrole":
        q = a.query.strip()
        rid = normalize(q) if ("/" in q or q.startswith("in/")) else None
        results = []
        for path in sorted(globmod.glob(f"{PIPELINE_DIR}/longlist-*.jsonl")):
            for r in load(path).values():
                if (rid and r.get("id") == rid) or (not rid and (r.get("name") or "").strip().lower() == q.lower()):
                    results.append({"role": role_slug(path), "id": r.get("id"), "name": r.get("name"),
                                    "status": r.get("status"), "score": r.get("score"),
                                    "locked": r.get("status") in LOCK_STATUSES})
        print(json.dumps(results, ensure_ascii=False))
        return

    if not a.file:
        sys.exit("--file is required for this command")
    recs = load(a.file)

    if a.cmd == "add":
        outcome, detail = add_record(recs, json.loads(a.record), a.file)
        if outcome == "invalid":
            sys.exit(detail)
        if outcome == "crossrole-locked":
            print(f"{outcome}: {detail}")
            return
        save(a.file, recs)
        print(f"{outcome}: {detail}")

    elif a.cmd == "bulk":
        counts = {"added": 0, "skipped": 0, "invalid": 0, "crossrole-locked": 0, "needs-linkedin": 0}
        for line in sys.stdin:
            if not line.strip():
                continue
            outcome, detail = add_record(recs, json.loads(line), a.file)
            counts[outcome] += 1
            if outcome in ("crossrole-locked", "needs-linkedin") or (outcome == "added" and detail and "dupe" in str(detail)) \
                    or (outcome == "added" and detail and "crossrole" in str(detail)):
                print(f"warn: {detail}")
        save(a.file, recs)
        print(json.dumps(counts))

    elif a.cmd == "update":
        rid = a.id if a.id in recs else normalize(a.id)
        if rid not in recs:
            sys.exit(f"not found: {a.id}")
        merge = json.loads(a.merge)
        new_status = merge.get("status")
        # Resolve-then-DQ: a merge that supplies a real LinkedIn URL clears the flag.
        merged_url = merge.get("linkedin_url", recs[rid].get("linkedin_url"))
        if is_linkedin_profile(merged_url):
            merge.setdefault("needs_linkedin", False)
        if new_status in LOCK_STATUSES:
            if not is_linkedin_profile(merged_url):
                sys.exit(f"needs-linkedin: {rid} has no LinkedIn profile URL "
                         f"(got {merged_url!r}) — resolve to a linkedin.com/in/ profile "
                         f"before setting '{new_status}' (LinkedIn is a hard condition, the hiring lead 2026-07-24).")
            rec = recs[rid]
            lock = crossrole_conflict(scan_other_roles(rid, fingerprint(rec), a.file))
            if lock:
                sys.exit(f"crossrole-conflict: {rid} is already {lock['status']} in role "
                         f"'{lock['role']}' — refusing to set '{new_status}' here. "
                         f"One active role per person; flag to the hiring lead if this role fits better.")
        recs[rid].update(merge)
        # Re-key if a resolved LinkedIn URL changes the canonical id (dedupe integrity).
        new_rid = normalize(merged_url)
        if new_rid != rid and is_linkedin_profile(merged_url):
            if new_rid in recs and new_rid != rid:
                sys.exit(f"merge-conflict: resolved id {new_rid} already exists — merge manually.")
            recs[rid]["linkedin_url"] = merged_url
            recs[rid]["id"] = new_rid
            recs[new_rid] = recs.pop(rid)
            rid = new_rid
        save(a.file, recs)
        print(f"updated: {rid}")

    elif a.cmd == "list":
        rows = list(recs.values())
        if a.status:
            rows = [r for r in rows if r.get("status") == a.status]
        if a.min_score is not None:
            rows = [r for r in rows if (r.get("score") or 0) >= a.min_score]
        rows.sort(key=lambda r: r.get("score") or 0, reverse=True)
        if a.limit:
            rows = rows[: a.limit]
        if a.format == "md":
            print("| Name | Current | Score | Status | URL |")
            print("|---|---|---|---|---|")
            for r in rows:
                cur = r.get("current") or {}
                pos = " @ ".join(x for x in [cur.get("title"), cur.get("company")] if x) or r.get("headline", "-")
                print(f"| {r['name']} | {pos} | {r.get('score') if r.get('score') is not None else '-'} | {r.get('status')} | {r.get('linkedin_url')} |")
        else:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
        print(f"[{len(rows)} records]", file=sys.stderr)

    elif a.cmd == "stats":
        by_status, by_touch, by_source = {}, {}, {}
        for r in recs.values():
            by_status[r.get("status", "?")] = by_status.get(r.get("status", "?"), 0) + 1
            by_touch[r.get("touch", "?")] = by_touch.get(r.get("touch", "?"), 0) + 1
            src = r.get("source") or {}
            key = src.get("company") or src.get("anchor") or src.get("kind") or "?"
            s = by_source.setdefault(key, {"n": 0, "scored": 0, "score_sum": 0, "n85": 0})
            s["n"] += 1
            if r.get("score") is not None:
                s["scored"] += 1
                s["score_sum"] += r["score"]
                if r["score"] >= 85:
                    s["n85"] += 1
        for s in by_source.values():
            score_sum = s.pop("score_sum")
            s["avg_score"] = round(score_sum / s["scored"], 1) if s["scored"] else None
        print(json.dumps({"total": len(recs), "by_status": by_status, "by_touch": by_touch,
                          "stamp_precision": by_source}, indent=2))


if __name__ == "__main__":
    main()
