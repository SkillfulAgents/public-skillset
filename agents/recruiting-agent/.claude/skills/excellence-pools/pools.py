#!/usr/bin/env python3
"""Non-LinkedIn excellence-pool searchers. Subcommands: arxiv."""
import argparse, json, sys, time, urllib.parse
import xml.etree.ElementTree as ET
import requests

NS = {"a": "http://www.w3.org/2005/Atom"}
API = "http://export.arxiv.org/api/query"

def arxiv_search(query, max_results, since):
    out, start, page = [], 0, 100
    while start < max_results:
        n = min(page, max_results - start)
        params = {
            "search_query": query, "start": start, "max_results": n,
            "sortBy": "submittedDate", "sortOrder": "descending",
        }
        r = requests.get(API, params=params, timeout=30,
                         headers={"User-Agent": "gamut-recruiting-agent/1.0"})
        r.raise_for_status()
        root = ET.fromstring(r.text)
        entries = root.findall("a:entry", NS)
        if not entries:
            break
        for e in entries:
            date = (e.findtext("a:published", "", NS) or "")[:10]
            if since and date < since:
                return out
            out.append({
                "title": " ".join((e.findtext("a:title", "", NS) or "").split()),
                "date": date,
                "url": (e.findtext("a:id", "", NS) or "").strip(),
                "authors": [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
            })
        start += n
        time.sleep(3)  # arXiv API politeness delay
    return out

def cmd_arxiv(args):
    papers = arxiv_search(args.query, args.max, args.since)
    if args.by_author:
        authors = {}
        for p in papers:
            for i, name in enumerate(p["authors"]):
                a = authors.setdefault(name, {"name": name, "papers": 0,
                                              "first_author": 0, "examples": []})
                a["papers"] += 1
                if i == 0:
                    a["first_author"] += 1
                if len(a["examples"]) < 3:
                    a["examples"].append({"title": p["title"], "date": p["date"], "url": p["url"]})
        ranked = sorted(authors.values(),
                        key=lambda x: (x["first_author"], x["papers"]), reverse=True)
        if args.min_papers:
            ranked = [a for a in ranked if a["papers"] >= args.min_papers]
        print(json.dumps({"query": args.query, "papers_scanned": len(papers),
                          "authors": ranked[:args.top]}, indent=1))
    else:
        print(json.dumps({"query": args.query, "papers": papers}, indent=1))

def main():
    p = argparse.ArgumentParser(description="Excellence-pool searchers (non-LinkedIn)")
    sub = p.add_subparsers(dest="cmd", required=True)
    ax = sub.add_parser("arxiv", help="Find authors of recent papers on a topic")
    ax.add_argument("--query", required=True,
                    help='arXiv query, e.g. \'all:"agent evaluation" AND cat:cs.CL\'')
    ax.add_argument("--max", type=int, default=100, help="max papers to scan")
    ax.add_argument("--since", default=None, help="YYYY-MM-DD cutoff")
    ax.add_argument("--by-author", action="store_true", help="aggregate + rank by author")
    ax.add_argument("--min-papers", type=int, default=0)
    ax.add_argument("--top", type=int, default=50)
    ax.set_defaults(fn=cmd_arxiv)
    args = p.parse_args()
    args.fn(args)

if __name__ == "__main__":
    main()
