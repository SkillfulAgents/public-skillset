#!/usr/bin/env python3
"""Find link-building prospects: pages that link to competitors and look like
listicles / reviews / comparisons / "alternatives" posts where our product could
plausibly be added.

Pulls competitor backlinks from Ahrefs Site Explorer (all-backlinks), keeps one
link per referring domain, filters referring-page titles to listicle signals,
then dedupes across all competitors so domains that mention MULTIPLE competitors
(the hottest prospects) bubble to the top.

Usage:
  uv run --env-file .env --with requests prospect.py \
      --domains gumloop.com,vellum.ai,dust.tt,zo.computer \
      --out /workspace/output/link-prospects \
      [--limit 150] [--min-dr 20]
"""
import argparse, csv, json, os, sys, time
from collections import defaultdict
import requests

API = "https://api.ahrefs.com/v3/site-explorer/all-backlinks"

# Listicle / review / comparison signals we look for in the referring page title.
SIGNALS = [
    "best", "top ", "alternative", "review", "comparison", "compare",
    "vs ", "vs.", " vs", "tools", "platforms", "roundup", "guide to",
]

SELECT = ",".join([
    "url_from", "url_to", "title", "anchor",
    "domain_rating_source", "traffic_domain", "is_dofollow",
    "first_seen", "last_seen", "link_type",
])


TITLE_OR = {"or": [{"field": "title", "is": ["substring", s]} for s in SIGNALS]}

# Domain-rating bands for pagination — each is a separate <=100-row call, which
# breaks the Lite plan's 100-row-per-call cap. Disjoint ranges => clean dedup.
BANDS = [(90, 101), (80, 90), (70, 80), (60, 70), (50, 60),
         (40, 50), (30, 40), (20, 30)]


def _call(domain, key, where, limit, mode):
    params = {
        "target": domain,
        "mode": mode,
        "aggregation": "1_per_domain",
        "limit": str(limit),
        "select": SELECT,
        "order_by": "domain_rating_source:desc",
        "where": json.dumps(where),
        "history": "live",
    }
    r = requests.get(API, params=params,
                     headers={"Authorization": f"Bearer {key}"}, timeout=120)
    if r.status_code != 200:
        print(f"  ! {domain}: HTTP {r.status_code} {r.text[:200]}", file=sys.stderr)
        return []
    return r.json().get("backlinks", [])


def fetch(domain, key, limit, date, mode="domain", banded=False, min_dr=20):
    if not banded:
        return _call(domain, key, TITLE_OR, limit, mode)
    rows = []
    for lo, hi in BANDS:
        if hi <= min_dr:
            continue
        where = {"and": [TITLE_OR,
                         {"field": "domain_rating_source", "is": ["gte", lo]},
                         {"field": "domain_rating_source", "is": ["lt", hi]}]}
        band = _call(domain, key, where, limit, mode)
        print(f"    DR[{lo},{hi}): {len(band)}", file=sys.stderr)
        rows.extend(band)
        time.sleep(0.2)
    return rows


def refdomain(url):
    try:
        host = url.split("//", 1)[1].split("/", 1)[0].lower()
        return host[4:] if host.startswith("www.") else host
    except Exception:
        return url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--domains", required=True, help="comma-separated competitor domains")
    ap.add_argument("--out", required=True, help="output path prefix (no extension)")
    ap.add_argument("--limit", type=int, default=150)
    ap.add_argument("--min-dr", type=float, default=20.0)
    ap.add_argument("--mode", default="domain", help="domain|subdomains|prefix|exact")
    ap.add_argument("--banded", action="store_true",
                    help="paginate by DR bands to exceed the 100-row/call cap")
    ap.add_argument("--date", default="2026-06-15")
    args = ap.parse_args()

    key = os.environ["AHREFS_API_KEY"]
    domains = [d.strip() for d in args.domains.split(",") if d.strip()]

    # prospect keyed by referring page URL
    by_page = {}
    for d in domains:
        print(f"Fetching {d} ...", file=sys.stderr)
        rows = fetch(d, key, args.limit, args.date, args.mode,
                     banded=args.banded, min_dr=args.min_dr)
        print(f"  {len(rows)} filtered backlinks", file=sys.stderr)
        for b in rows:
            dr = b.get("domain_rating_source") or 0
            if dr < args.min_dr:
                continue
            url = b.get("url_from")
            if not url:
                continue
            p = by_page.setdefault(url, {
                "url_from": url,
                "refdomain": refdomain(url),
                "title": b.get("title", ""),
                "domain_rating": dr,
                "traffic_domain": b.get("traffic_domain") or 0,
                "is_dofollow": b.get("is_dofollow"),
                "first_seen": b.get("first_seen", ""),
                "last_seen": b.get("last_seen", ""),
                "competitors": set(),
            })
            p["competitors"].add(d)
        time.sleep(0.3)

    prospects = list(by_page.values())
    # Hotness: # competitors mentioned (desc), then DR (desc), then traffic (desc)
    prospects.sort(key=lambda x: (len(x["competitors"]), x["domain_rating"],
                                  x["traffic_domain"]), reverse=True)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    csv_path = args.out + ".csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["rank", "refdomain", "url_from", "title", "domain_rating",
                    "traffic_domain", "is_dofollow", "competitors_mentioned",
                    "n_competitors", "first_seen", "last_seen"])
        for i, p in enumerate(prospects, 1):
            w.writerow([i, p["refdomain"], p["url_from"], p["title"],
                        p["domain_rating"], p["traffic_domain"], p["is_dofollow"],
                        "|".join(sorted(p["competitors"])), len(p["competitors"]),
                        p["first_seen"], p["last_seen"]])

    multi = [p for p in prospects if len(p["competitors"]) > 1]
    print(json.dumps({
        "total_prospects": len(prospects),
        "multi_competitor_prospects": len(multi),
        "competitors": domains,
        "csv": csv_path,
    }, indent=2))


if __name__ == "__main__":
    main()
