#!/usr/bin/env python3
"""Ahrefs v3 Keywords Explorer helper."""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = "https://api.ahrefs.com/v3/keywords-explorer"
TOKEN = os.environ["AHREFS_API_KEY"]

OVERVIEW_SELECT = "keyword,volume,global_volume,difficulty,cpc,clicks,cps,parent_topic,traffic_potential,intents,serp_features"
EXPAND_SELECT = "keyword,volume,difficulty,cpc"


def _get(path, params):
    url = f"{BASE}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "body": e.read().decode()}


def overview(kws, country):
    return _get("overview", {"keywords": kws, "country": country, "select": OVERVIEW_SELECT})


def expand(endpoint, seed, country, limit):
    return _get(endpoint, {"keywords": seed, "country": country,
                           "select": EXPAND_SELECT, "limit": limit})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["overview", "matching", "related", "suggestions"])
    p.add_argument("keywords")
    p.add_argument("--country", default="us")
    p.add_argument("--limit", type=int, default=50)
    a = p.parse_args()
    if a.cmd == "overview":
        out = overview(a.keywords, a.country)
    else:
        ep = {"matching": "matching-terms", "related": "related-terms",
              "suggestions": "search-suggestions"}[a.cmd]
        out = expand(ep, a.keywords, a.country, a.limit)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
