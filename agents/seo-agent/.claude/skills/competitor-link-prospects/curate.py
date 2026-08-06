#!/usr/bin/env python3
"""Curate a raw prospect CSV (from prospect.py) down to a vetted, editorial-only
outreach shortlist. Strips PBN/SEO-spam, AI-tool directories, programmatic
"alternatives" pages, social/video/app stores, and obvious title false-positives.
Classifies survivors by outreach format (roundup vs comparison vs review).

Usage:
  uv run curate.py --in /workspace/output/link-prospects.csv \
                   --out /workspace/output/link-prospects-shortlist \
                   [--min-dr 30]
"""
import argparse, csv, os, re

# --- blocklists -------------------------------------------------------------
# PBN / paid-link / spam network signals (substring match on refdomain)
SPAM = [".shop", "seolink", "linkseo", "linkrank", "ranklink", "ranklink",
        "seolinks", "backlink", "pbn", "rank-top", "premiumseo", "fiverr",
        "boostrank", "buy-backlink", ".site", "scam-detector"]

# Aggregators / AI-tool directories / app catalogs — rarely accept manual adds
DIRECTORY = ["toolify.ai", "creati.ai", "webcatalog.io", "aitooltrek", "dang.ai",
             "stork.ai", "glarity", "saasworthy", "slashdot", "sourceforge",
             "getapp", "capterra", "g2.com", "futurepedia", "theresanaiforthat",
             "aimojo", "producthunt.com", "f6s.com", "cbinsights.com",
             "crunchbase", "tracxn", "aiagentstore", "uptodown", "alternativeto",
             "diigo.com", "openrouter.ai", "rumahweb", "ecosyste.ms",
             "allaiwebsite", "deepnlp.org", "saastrac", "selecthub",
             "poddtoppen", "allainsingle", "aitoolsdirectory"]

# Social / video / code / app stores — not editorial
SOCIAL = ["youtube", "chromewebstore", "play.google", "apps.apple", "linkedin",
          "facebook", "twitter", "x.com", "reddit", "t.me", "instagram",
          "github.com", "github.io", "tiktok", "pinterest", "medium.com",
          "substack.com", "buzzsprout", "pocketcasts", "vercel.app", ".netlify.app"]

# Title patterns that are clearly NOT a tool listicle/comparison
TITLE_NOISE = [r"\bpeptide\b", r"\bgym bro\b", r"top 100 b2b", r"teaching",
               r"assessment", r"robotics use cases", r"review articles in the age",
               r"leaderboard", r"springer"]

# Competitor-owned domains (self-links — not outreach targets). Substring match.
# Loaded from seo/config.json `link_prospecting.self_domains` — keep it in sync with
# the competitor set you prospect (agent-onboarding seeds it; weekly strategy extends it).
import json as _json, pathlib as _pathlib
_CFG = {}
try:
    _CFG = _json.loads(_pathlib.Path("/workspace/seo/config.json").read_text()) \
        .get("link_prospecting", {})
except Exception:
    pass
SELF = _CFG.get("self_domains", [])

# Content-farm / auto-generated subdomain signals
FARM = ["bestarticleworld", "99bestsite", "aicavo", "premieralts", "explinks",
        "skillsmp", "respan.ai", "employbl"]
FARM_RE = re.compile(r"-\d{5,}")  # random-hyphen-number generated subdomains

# A page is on-topic only if its title touches your category. Loaded from
# seo/config.json `link_prospecting.topic_terms` — set these to your niche's
# category vocabulary or the TOPIC gate passes everything / nothing useful.
TOPIC = _CFG.get("topic_terms", [])

def blocked(rd, lst):
    return any(s in rd for s in lst)

def classify(title):
    t = title.lower()
    if " vs" in t or "vs " in t or "vs." in t or "comparison" in t or "compare" in t:
        return "comparison"
    if "alternative" in t:
        return "alternatives"
    if "review" in t or "reviews" in t or "pricing" in t:
        return "review"
    if "best" in t or "top " in t or "tools" in t or "platforms" in t:
        return "roundup"
    return "other"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-dr", type=float, default=30.0)
    args = ap.parse_args()

    rows = list(csv.DictReader(open(args.inp)))
    kept, dropped = [], {"spam": 0, "directory": 0, "social": 0, "self": 0,
                         "farm": 0, "off_topic": 0,
                         "nofollow": 0, "low_dr": 0, "title_noise": 0}
    for r in rows:
        rd = r["refdomain"].lower()
        title = r["title"]
        tl = title.lower()
        multi = int(r["n_competitors"]) > 1
        if r["is_dofollow"] != "True":
            dropped["nofollow"] += 1; continue
        if float(r["domain_rating"]) < args.min_dr:
            dropped["low_dr"] += 1; continue
        if blocked(rd, SPAM):
            dropped["spam"] += 1; continue
        if blocked(rd, SELF):
            dropped["self"] += 1; continue
        if blocked(rd, DIRECTORY):
            dropped["directory"] += 1; continue
        if blocked(rd, SOCIAL):
            dropped["social"] += 1; continue
        if blocked(rd, FARM) or FARM_RE.search(rd):
            dropped["farm"] += 1; continue
        if any(re.search(p, tl) for p in TITLE_NOISE):
            dropped["title_noise"] += 1; continue
        # on-topic gate: skip unless title touches the category or it's multi-competitor
        if TOPIC and not multi and not any(t in tl for t in TOPIC):
            dropped["off_topic"] += 1; continue
        r["format"] = classify(title)
        kept.append(r)

    # rank: multi-competitor first, then format priority, then DR
    fmt_rank = {"comparison": 0, "roundup": 1, "alternatives": 2, "review": 3, "other": 4}
    kept.sort(key=lambda x: (int(x["n_competitors"]), -fmt_rank[x["format"]],
                             float(x["domain_rating"])), reverse=True)

    out_csv = args.out + ".csv"
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    cols = ["rank", "refdomain", "format", "url_from", "title", "domain_rating",
            "traffic_domain", "competitors_mentioned", "n_competitors", "last_seen"]
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for i, r in enumerate(kept, 1):
            w.writerow([i, r["refdomain"], r["format"], r["url_from"], r["title"],
                        r["domain_rating"], r["traffic_domain"],
                        r["competitors_mentioned"], r["n_competitors"], r["last_seen"]])

    print(f"kept {len(kept)} of {len(rows)}")
    print("dropped:", dropped)
    from collections import Counter
    print("by format:", dict(Counter(r["format"] for r in kept)))
    print("csv:", out_csv)

if __name__ == "__main__":
    main()
