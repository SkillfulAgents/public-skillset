#!/usr/bin/env python3
"""Search/download free stock images from Unsplash + Openverse."""
import argparse
import json
import os
import urllib.parse
import urllib.request

UA = "seo-agent/1.0 (blog media sourcing)"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())


def unsplash(q, n):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        return {"error": "UNSPLASH_ACCESS_KEY not set"}
    url = "https://api.unsplash.com/search/photos?" + urllib.parse.urlencode(
        {"query": q, "per_page": n, "orientation": "landscape"})
    data = _get(url, {"Authorization": f"Client-ID {key}"})
    out = []
    for p in data.get("results", []):
        out.append({
            "id": p["id"],
            "url": p["urls"]["regular"],
            "full": p["urls"]["full"],
            "download_trigger": p["links"]["download_location"],
            "author": p["user"]["name"],
            "author_url": p["user"]["links"]["html"],
            "link": p["links"]["html"],
            "alt": p.get("alt_description") or p.get("description") or q,
            "license": "Unsplash License",
        })
    return {"query": q, "source": "unsplash", "results": out}


def openverse(q, n, license_type):
    params = {"q": q, "page_size": n}
    if license_type:
        params["license_type"] = license_type  # commercial / modification
    url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)
    data = _get(url)
    out = []
    for p in data.get("results", []):
        out.append({
            "id": p.get("id"),
            "url": p.get("url"),
            "author": p.get("creator"),
            "author_url": p.get("creator_url"),
            "license": f"{p.get('license')} {p.get('license_version','')}".strip(),
            "source": p.get("source"),
            "foreign_landing_url": p.get("foreign_landing_url"),
            "alt": p.get("title") or q,
        })
    return {"query": q, "source": "openverse", "results": out}


def download(url, name):
    d = "/workspace/downloads/media"
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req) as r, open(path, "wb") as f:
        f.write(r.read())
    return {"saved": path, "bytes": os.path.getsize(path)}


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("unsplash", "openverse"):
        s = sub.add_parser(name)
        s.add_argument("query")
        s.add_argument("--n", type=int, default=8)
        if name == "openverse":
            s.add_argument("--license", default="commercial")
    d = sub.add_parser("download")
    d.add_argument("url")
    d.add_argument("name")
    a = p.parse_args()
    if a.cmd == "unsplash":
        out = unsplash(a.query, a.n)
    elif a.cmd == "openverse":
        out = openverse(a.query, a.n, a.license)
    else:
        out = download(a.url, a.name)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
