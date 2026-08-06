#!/usr/bin/env python3
"""Query Google Search Console (property from seo/config.json `gsc_property`).

Usage:
  uv run --env-file .env --with google-auth,requests \
    .claude/skills/seo-weekly-strategy/gsc_query.py \
    --start 2026-07-13 --end 2026-07-19 --dimensions query,page --limit 100
  # dims: any of date,query,page,country,device (comma-sep). Output: TSV to stdout.
  # --filter 'query notContains <brand>' for non-brand views (op: contains|notContains|equals)
"""
import argparse, json, os, pathlib, sys
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

PROPERTY = json.loads(pathlib.Path("/workspace/seo/config.json").read_text())["gsc_property"]

def token():
    info = json.loads(os.environ["GSC_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    creds.refresh(Request())
    return creds.token

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--dimensions", default="query")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--filter", action="append", default=[],
                    help="'<dimension> <operator> <expression>' e.g. 'query notContains acme'")
    args = ap.parse_args()

    body = {"startDate": args.start, "endDate": args.end,
            "dimensions": args.dimensions.split(","), "rowLimit": args.limit}
    if args.filter:
        filters = []
        for f in args.filter:
            dim, op, expr = f.split(" ", 2)
            filters.append({"dimension": dim, "operator": op, "expression": expr})
        body["dimensionFilterGroups"] = [{"filters": filters}]

    url = (f"https://www.googleapis.com/webmasters/v3/sites/"
           f"{requests.utils.quote(PROPERTY, safe='')}/searchAnalytics/query")
    r = requests.post(url, headers={"Authorization": f"Bearer {token()}"}, json=body)
    r.raise_for_status()
    rows = r.json().get("rows", [])
    print("\t".join(body["dimensions"] + ["clicks", "impressions", "ctr", "position"]))
    for row in rows:
        print("\t".join([*map(str, row["keys"]),
                         str(row["clicks"]), str(row["impressions"]),
                         f"{row['ctr']:.4f}", f"{row['position']:.1f}"]))
    print(f"# {len(rows)} rows", file=sys.stderr)

if __name__ == "__main__":
    main()
