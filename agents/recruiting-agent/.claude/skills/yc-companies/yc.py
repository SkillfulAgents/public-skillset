#!/usr/bin/env python3
"""Filter the public YC companies directory. See SKILL.md for usage."""
# /// script
# dependencies = ["requests"]
# ///
import argparse
import csv
import json
import os
import sys
import time

import requests

API = "https://yc-oss.github.io/api/companies/all.json"
CACHE = "/workspace/.cache/yc-companies.json"
DEFAULT_FIELDS = ["name", "batch", "team_size", "status", "one_liner", "website", "yc_url"]


def load(refresh):
    if not refresh and os.path.exists(CACHE) and time.time() - os.path.getmtime(CACHE) < 86400:
        with open(CACHE) as f:
            return json.load(f)
    data = requests.get(API, timeout=120).json()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(data, f)
    return data


def batch_year(batch):
    for tok in str(batch or "").split():
        if tok.isdigit() and len(tok) == 4:
            return int(tok)
    return 0


def matches(c, a):
    blob = " ".join([
        c.get("name") or "", c.get("one_liner") or "",
        c.get("long_description") or "", " ".join(c.get("tags") or []),
    ]).lower()
    tags = [t.lower() for t in (c.get("tags") or [])]
    industries = " ".join([c.get("industry") or "", c.get("subindustry") or ""]).lower()
    regions = (" ".join(c.get("regions") or []) + " " + (c.get("all_locations") or "")).lower()
    team = c.get("team_size")

    if a.keyword and a.keyword.lower() not in blob:
        return False
    if a.tags and not any(t.strip().lower() in tags for t in a.tags.split(",")):
        return False
    if a.industry and a.industry.lower() not in industries:
        return False
    if a.batch and (c.get("batch") or "").lower() not in [b.strip().lower() for b in a.batch.split(",")]:
        return False
    if a.batch_since and batch_year(c.get("batch")) < a.batch_since:
        return False
    if a.min_team is not None and (team is None or team < a.min_team):
        return False
    if a.max_team is not None and (team is None or team > a.max_team):
        return False
    if a.region and a.region.lower() not in regions:
        return False
    if a.status and (c.get("status") or "").lower() != a.status.lower():
        return False
    if a.hiring and not c.get("isHiring"):
        return False
    if a.top and not c.get("top_company"):
        return False
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--keyword")
    p.add_argument("--tags")
    p.add_argument("--industry")
    p.add_argument("--batch")
    p.add_argument("--batch-since", type=int, dest="batch_since")
    p.add_argument("--min-team", type=int, dest="min_team")
    p.add_argument("--max-team", type=int, dest="max_team")
    p.add_argument("--region")
    p.add_argument("--status")
    p.add_argument("--hiring", action="store_true")
    p.add_argument("--top", action="store_true")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--sort", choices=["batch", "team_size"], default="batch")
    p.add_argument("--format", choices=["table", "csv", "json"], default="table")
    p.add_argument("--fields", default=",".join(DEFAULT_FIELDS))
    p.add_argument("--refresh", action="store_true")
    a = p.parse_args()

    companies = load(a.refresh)
    for c in companies:
        c["yc_url"] = f"https://www.ycombinator.com/companies/{c.get('slug', '')}"

    hits = [c for c in companies if matches(c, a)]
    if a.sort == "batch":
        hits.sort(key=lambda c: batch_year(c.get("batch")), reverse=True)
    else:
        hits.sort(key=lambda c: (c.get("team_size") is None, c.get("team_size") or 0))
    total = len(hits)
    if a.limit:
        hits = hits[: a.limit]

    fields = [f.strip() for f in a.fields.split(",")]
    rows = [{f: c.get(f) for f in fields} for c in hits]

    if a.format == "json":
        print(json.dumps(rows, indent=2))
    elif a.format == "csv":
        w = csv.DictWriter(sys.stdout, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    else:
        for r in rows:
            vals = []
            for f in fields:
                v = str(r.get(f) if r.get(f) is not None else "-")
                vals.append(v[:60] + "…" if len(v) > 61 else v)
            print(" | ".join(vals))
    print(f"\n[{total} matches, showing {len(rows)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
