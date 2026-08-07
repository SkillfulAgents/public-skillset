#!/usr/bin/env python3
"""Thin CLI for the Ashby ATS RPC API. Usage: ashby.py <endpoint> ['<json-payload>'] [--all]"""
# /// script
# dependencies = ["requests"]
# ///
import json
import os
import sys

import requests

BASE = "https://api.ashbyhq.com"


def call(endpoint, payload, key):
    r = requests.post(
        f"{BASE}/{endpoint}",
        json=payload,
        auth=(key, ""),
        headers={"Accept": "application/json"},
        timeout=60,
    )
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, {"success": False, "raw": r.text[:2000]}


def main():
    fetch_all = "--all" in sys.argv[1:]
    args = [a for a in sys.argv[1:] if a != "--all"]
    if not args:
        sys.exit("usage: ashby.py <endpoint> ['<json-payload>'] [--all]")
    endpoint = args[0]
    payload = json.loads(args[1]) if len(args) > 1 else {}
    key = os.environ.get("ASHBY_API_KEY")
    if not key:
        sys.exit("ASHBY_API_KEY not set (run with: uv run --env-file /workspace/.env ...)")

    status, data = call(endpoint, payload, key)
    if fetch_all and data.get("success") and isinstance(data.get("results"), list):
        results = data["results"]
        while data.get("moreDataAvailable") and data.get("nextCursor"):
            payload["cursor"] = data["nextCursor"]
            status, data = call(endpoint, payload, key)
            if not data.get("success"):
                break
            results.extend(data.get("results", []))
        data["results"] = results
        data.pop("moreDataAvailable", None)
        data.pop("nextCursor", None)

    print(json.dumps(data, indent=2))
    if status >= 400 or not data.get("success", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
