#!/usr/bin/env python3
"""Spend per agent for one dashboard view (wtd, mtd, last7, last14, last30), from the source in review/cost-source.json.

Sources:
  {"type": "command", "command": "..."}            the default: usage_page.py cost. PERIOD is set in its env
  {"type": "file", "path": "review/exports/{period}.json"}   a file someone provides, if the admin changes the source

Either source yields, for example:
  {"period": "last30", "source": "Usage page, last 30 days, read 2026-11-27 10:05 PST",
   "agents": [{"agent_id": "sales-research-1a2b", "name": "Sales Research", "ai_usd": 412.80, "tools_usd": 18.00,
               "sessions": {"<session id>": 3.10}}],
   "unattributed": {"ai_usd": 0, "tools_usd": 42.00},
   "excludes": ["Usage on people's own AI subscriptions or API keys"]}
agent_id must be the id the agent-to-agent tools use. Every amount is required, 0 when there was none.
"sessions" (spend per session) is optional: without it, the setup and work split of spend is unknown.
"read_at" and "window" (optional) say when the page was read and which days it covers.
Writes review/costs/<period>.json. It is the only source of spend.
"""
import argparse, datetime, json, os, subprocess, sys

REVIEW = os.environ.get("REVIEW_DIR", os.path.join(os.getcwd(), "review"))


def num(x, where):
    if not isinstance(x, (int, float)) or x < 0:
        raise SystemExit(f"bad amount at {where}: {x!r}")
    return float(x)


def normalize(raw, period, source_label):
    if raw.get("period") not in (None, period):
        raise SystemExit(f"source is for {raw['period']}, not {period}")
    agents = {}
    for i, a in enumerate(raw.get("agents", [])):
        aid = a.get("agent_id")
        if not aid:
            raise SystemExit(f"agents[{i}] has no agent_id")
        if aid in agents:
            raise SystemExit(f"agent {aid} appears twice")
        for k in ("ai_usd", "tools_usd"):
            if k not in a:
                raise SystemExit(f"{aid} has no {k}: give 0 explicitly when there was none")
        entry = {"name": a.get("name"), "ai_usd": num(a["ai_usd"], f"{aid}.ai_usd"),
                 "tools_usd": num(a["tools_usd"], f"{aid}.tools_usd")}
        if a.get("sessions"):
            entry["sessions"] = {k: num(v, f"{aid}.sessions.{k}") for k, v in a["sessions"].items()}
        agents[aid] = entry
    un = raw.get("unattributed")
    if un is None or "ai_usd" not in un or "tools_usd" not in un:
        raise SystemExit("unattributed.ai_usd and unattributed.tools_usd are required: give 0 when there was none")
    return {"period": period, "source": raw.get("source") or source_label,
            "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "agents": agents,
            "unattributed": {"ai_usd": num(un["ai_usd"], "unattributed.ai_usd"),
                             "tools_usd": num(un["tools_usd"], "unattributed.tools_usd")},
            "excludes": raw.get("excludes", []),
            **{k: raw[k] for k in ("read_at", "window") if k in raw}}


def fetch(src, period):
    if src["type"] == "file":
        path = src["path"].format(period=period)
        with open(path) as f:
            return json.load(f), f"file {path}"
    if src["type"] == "command":
        out = subprocess.run(src["command"], shell=True, capture_output=True, text=True,
                             env={**os.environ, "PERIOD": period}, timeout=300)
        if out.returncode != 0:
            raise SystemExit(f"cost command failed: {out.stderr.strip()[:500]}")
        return json.loads(out.stdout), "command"
    raise SystemExit(f"unknown cost source type: {src['type']}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--period", required=True, choices=("wtd", "mtd", "last7", "last14", "last30"))
    args = p.parse_args(argv)
    with open(os.path.join(REVIEW, "cost-source.json")) as f:
        src = json.load(f)
    try:
        raw, label = fetch(src, args.period)
    except (SystemExit, OSError, ValueError) as e:
        raise SystemExit(f"cost blocked: {e}")
    result = normalize(raw, args.period, label)
    os.makedirs(os.path.join(REVIEW, "costs"), exist_ok=True)
    dest = os.path.join(REVIEW, "costs", f"{args.period}.json")
    with open(dest, "w") as f:
        json.dump(result, f, indent=1, sort_keys=True)
    print(f"{dest}: {len(result['agents'])} agents, source: {result['source']}")


if __name__ == "__main__":
    main()
