#!/usr/bin/env python3
"""Ashby crosscheck for would-be shortlisters (the hiring lead 2026-07-24: crosscheck at SHORTLIST
time, so people already in Ashby never reach the sourced list -- narrowed 2026-07-27 to
records showing REAL contact; see contact_depth below).

Usage: uv run ashby_crosscheck.py <in.json> <out.json>
  in.json:  [{"name","linkedin_url","score","tier"}, ...]
  out.json: same rows + ashby_hits + verdict
    clear | agent-created-reuse | stale-touch-review | suppressed-ashby
    | possible-collision-review | search-failed

candidate.search is an exact-name matcher, so a single query on the harvested name misses
records filed under a name variant (Ashby held "Shaoru Huang"; the longlist had "Shaoru Ian
Huang" -> crosscheck said clear on someone already at Reached Out). Every name is therefore
searched as several variants and identity is settled on the LinkedIn slug.

A matched non-agent record is then probed for CONTACT DEPTH (Eric Zhang override, the hiring lead
2026-07-27: "we were never really in conversation with him"). Suppressing on the mere
existence of a record was silently deleting the top of the funnel -- a "Reached Out" stage
stamped on a record's own creation date, with no notes and no reply, is a bulk-touch marker
and not a conversation. Bare touches surface for the hiring lead's call; real contact stays suppressed.
"""
import json, subprocess, sys
from datetime import datetime, timezone

AGENT_TAG = "{{AGENT_SOURCED_TAG_ID}}"
ASHBY = "/workspace/.claude/skills/ashby/ashby.py"
AGENT_API_USER = "customer-api-and-automation@ashbyhq.com"
# stages at or below these are still "no conversation happened"
BARE_STAGES = {"New Lead", "Reached Out"}


def call(endpoint, payload):
    r = subprocess.run(
        ["uv", "run", "--env-file", "/workspace/.env", "--with", "requests",
         ASHBY, endpoint, json.dumps(payload)],
        capture_output=True, text=True, cwd="/workspace")
    if r.returncode != 0:
        return None, r.stderr.strip()[:200]
    try:
        return json.loads(r.stdout).get("results", []), None
    except Exception as e:
        return None, f"parse: {e}"


def search(name):
    return call("candidate.search", {"name": name})


def contact_depth(candidate_id, app_ids):
    """-> (has_real_contact, detail). Bare = no notes, nothing past Reached Out, not archived."""
    notes, err = call("candidate.listNotes", {"candidateId": candidate_id})
    if err:
        return True, {"probe_error": err}          # fail closed: unknown depth = do not send
    # the agent's own notes are not evidence that a human ever talked to them
    notes = [n for n in (notes or [])
             if (n.get("author") or {}).get("email") != AGENT_API_USER]
    stages, statuses = [], []
    for aid in app_ids or []:
        info, err = call("application.info", {"applicationId": aid})
        if err or not isinstance(info, dict):
            return True, {"probe_error": err or "bad application.info"}
        stages.append((info.get("currentInterviewStage") or {}).get("title"))
        statuses.append(info.get("status"))
    detail = {"n_notes": len(notes or []), "stages": stages, "statuses": statuses}
    real = bool(notes) or any(s not in BARE_STAGES for s in stages) \
        or any(st and st != "Lead" for st in statuses)
    return real, detail


def days_since(iso):
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - d).days
    except Exception:
        return None


def name_variants(name):
    parts = [p for p in name.replace(",", " ").split() if p]
    out = [name]
    if len(parts) > 2:
        out.append(f"{parts[0]} {parts[-1]}")          # drop middle names/initials
        out.append(f"{parts[1]} {parts[-1]}")          # middle name used as the given name
    if len(parts) >= 2:
        out.append(parts[-1])                          # surname sweep, filtered by slug below
    seen, uniq = set(), []
    for v in out:
        k = v.lower()
        if k not in seen:
            seen.add(k)
            uniq.append(v)
    return uniq


def norm_li(u):
    u = (u or "").lower().rstrip("/")
    return u.split("/in/", 1)[1] if "/in/" in u else ""


def main():
    rows = json.load(open(sys.argv[1]))
    out = []
    for c in rows:
        want = norm_li(c.get("linkedin_url"))
        rec = {"name": c["name"], "linkedin_url": c.get("linkedin_url"), "score": c.get("score"),
               "tier": c.get("tier"), "ashby_error": None, "ashby_hits": [], "verdict": "clear"}
        seen_ids, errs = set(), []
        for vi, variant in enumerate(name_variants(c["name"])):
            res, err = search(variant)
            if err:
                errs.append(err)
                continue
            for r in res or []:
                if r["id"] in seen_ids:
                    continue
                li = next((s.get("url", "") for s in (r.get("socialLinks") or [])
                           if s.get("type") == "LinkedIn"), "")
                li_match = bool(want) and norm_li(li) == want
                # surname-only sweep is noisy: keep those hits only on a slug match
                if vi and variant.count(" ") == 0 and not li_match:
                    continue
                seen_ids.add(r["id"])
                hit = {
                    "candidate_id": r["id"], "name": r["name"], "matched_on": variant,
                    "created": r.get("createdAt", "")[:10],
                    "agent_sourced": AGENT_TAG in [t.get("id") for t in (r.get("tags") or [])],
                    "linkedin": li, "li_match": li_match,
                    "n_apps": len(r.get("applicationIds") or []), "source": r.get("source"),
                }
                if li_match and not hit["agent_sourced"]:
                    real, detail = contact_depth(r["id"], r.get("applicationIds"))
                    hit["real_contact"] = real
                    hit["contact_detail"] = detail
                    hit["days_since_touch"] = days_since(r.get("updatedAt") or r.get("createdAt", ""))
                rec["ashby_hits"].append(hit)
        if errs and not rec["ashby_hits"]:
            rec["ashby_error"], rec["verdict"] = errs[0], "search-failed"
        hits = rec["ashby_hits"]
        if hits:
            non_agent = [h for h in hits if not h["agent_sourced"]]
            if any(h["agent_sourced"] for h in hits):
                rec["verdict"] = "agent-created-reuse"
            elif non_agent:
                matched = [h for h in non_agent if h["li_match"]]
                if not matched:
                    rec["verdict"] = "possible-collision-review"
                elif any(h.get("real_contact", True) for h in matched):
                    rec["verdict"] = "suppressed-ashby"
                else:
                    # record exists but nobody ever actually talked to them: the hiring lead's call, not ours
                    rec["verdict"] = "stale-touch-review"
        out.append(rec)
        print(f"{rec['verdict']:26s} {c['name']}", flush=True)

    json.dump(out, open(sys.argv[2], "w"), indent=1)
    tally = {}
    for r in out:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print(json.dumps(tally, indent=1))


if __name__ == "__main__":
    main()
