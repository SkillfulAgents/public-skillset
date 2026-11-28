#!/usr/bin/env python3
"""The Gamut Platform org usage page as the cost source, one reading per range.

  save   store one reading of the page (JSON on stdin), keeping only in-scope agents. Written by the read-usage-page skill.
         --kind is one of the page's ranges (wtd, mtd, 7d, 14d, 30d). It lands in usage-page/rolling/<kind>/<read date>.json
         and prices the matching dashboard view (wtd, mtd, last7, last14, last30).
  cost   print the cost JSON for the view in $PERIOD from its newest reading. Run by cost.py through cost-source.json.
  js     print the browser_eval script that reads a loaded usage page into the save shape, in-scope rows only.

Reading on stdin:
  {"kind": "30d", "read_at": "2026-11-27T10:05:00-08:00", "tz": "America/Los_Angeles",
   "ranges": {"total_range": "30d", "llm_range": "30d", "service_range": "30d"},
   "agents": [{"agent_id": "...", "name": "...", "ai_usd": 12.3}],      in-scope rows; any other row is folded away
   "out_of_scope": {"count": 210, "ai_usd": 3001.2},                     rows dropped before they left the page
   "ai_total_usd": 4100.5, "tools_total_usd": 870.1}
"""
import argparse, datetime, json, os, sys
from zoneinfo import ZoneInfo

REVIEW = os.environ.get("REVIEW_DIR", os.path.join(os.getcwd(), "review"))
DAY = datetime.timedelta(days=1)
RANGES = ("total_range", "llm_range", "service_range")
VIEWS = {"wtd": "wtd", "mtd": "mtd", "last7": "7d", "last14": "14d", "last30": "30d"}
RANGE_KINDS = tuple(VIEWS.values())
RANGE_NAMES = {"wtd": "week to date", "mtd": "month to date", "7d": "last 7 days", "14d": "last 14 days", "30d": "last 30 days"}


def review_tz():
    return ZoneInfo(json.load(open(os.path.join(REVIEW, "cards.json"))).get("timezone") or "UTC")


def midnight(d, tz):
    return datetime.datetime.combine(d, datetime.time(0), tzinfo=tz)


def amount(x, where):
    if not isinstance(x, (int, float)) or isinstance(x, bool) or x < 0:
        raise SystemExit(f"bad amount at {where}: {x!r}")
    return float(x)


def in_scope():
    cov = json.load(open(os.path.join(REVIEW, "coverage.json")))["agents"]
    out = {}
    for c in cov:
        if c.get("in_scope", True):
            out[c["agent_id"]] = c
            out[c["agent_id"].rsplit("-", 1)[-1]] = c
    return out


def window_for(kind, read_local, tz):
    """The days a range reading covers, as the page counts them: up to tomorrow's midnight, from the week's Monday,
    the month's first, or exact 24-hour blocks back."""
    end = midnight(read_local.date() + DAY, tz)
    if kind == "wtd":
        return midnight(read_local.date() - datetime.timedelta(days=read_local.weekday()), tz), end
    if kind == "mtd":
        return midnight(read_local.date().replace(day=1), tz), end
    hours = 24 * int(kind[:-1])
    return (end.astimezone(datetime.timezone.utc) - datetime.timedelta(hours=hours)).astimezone(tz), end


def rolling_dir(kind):
    return os.path.join(REVIEW, "exports", "usage-page", "rolling", kind)


def latest(kind):
    d = rolling_dir(kind)
    files = sorted(f for f in os.listdir(d) if f.endswith(".json")) if os.path.isdir(d) else []
    return json.load(open(os.path.join(d, files[-1]))) if files else None


def save(raw):
    tz = review_tz()
    if raw.get("tz") != tz.key:
        raise SystemExit(f"refused: the page was read with tz={raw.get('tz')}, the review's timezone is {tz.key}")
    kind = raw.get("kind")
    if kind not in RANGE_KINDS:
        raise SystemExit(f"refused: a reading is one of {', '.join(RANGE_KINDS)}")
    bad = {k: raw.get("ranges", {}).get(k) for k in RANGES if raw.get("ranges", {}).get(k) != kind}
    if bad:
        raise SystemExit(f"refused: every range must be {kind!r} for a {kind} reading, got {bad}")
    raw.setdefault("read_at", datetime.datetime.now(tz).isoformat(timespec="seconds"))
    scope = in_scope()
    agents, oos = {}, raw.get("out_of_scope") or {"count": 0, "ai_usd": 0}
    oos = {"count": int(oos.get("count", 0)), "ai_usd": amount(oos.get("ai_usd", 0), "out_of_scope.ai_usd")}
    for i, a in enumerate(raw.get("agents", [])):
        usd = amount(a.get("ai_usd"), f"agents[{i}].ai_usd")
        c = scope.get(str(a.get("agent_id")))
        if not c:
            oos["count"] += 1
            oos["ai_usd"] += usd
            continue
        if c["agent_id"] in agents:
            raise SystemExit(f"agent {c['agent_id']} appears twice")
        agents[c["agent_id"]] = {"name": c.get("name"), "ai_usd": usd}
    read_local = datetime.datetime.fromisoformat(raw["read_at"]).astimezone(tz)
    start, end = window_for(kind, read_local, tz)
    out = {"period": next(v for v, k in VIEWS.items() if k == kind), "kind": kind, "read_at": raw["read_at"], "tz": tz.key,
           "ranges": raw["ranges"], "agents": agents, "out_of_scope": oos,
           "ai_total_usd": amount(raw.get("ai_total_usd"), "ai_total_usd"),
           "tools_total_usd": amount(raw.get("tools_total_usd"), "tools_total_usd"),
           "window": {"start": start.isoformat(), "end": end.isoformat()}}
    path = os.path.join(rolling_dir(kind), f"{read_local.date()}.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    out["path"] = path
    return out


def cost(view):
    if view not in VIEWS:
        raise SystemExit(f"unknown view {view!r}: one of {', '.join(VIEWS)}")
    kind = VIEWS[view]
    r, tz = latest(kind), review_tz()
    if not r:
        raise SystemExit(f"no {RANGE_NAMES[kind]} reading of the usage page yet")
    read_local = datetime.datetime.fromisoformat(r["read_at"]).astimezone(tz)
    seen = sum(a["ai_usd"] for a in r["agents"].values()) + r["out_of_scope"]["ai_usd"]
    un_ai = r["ai_total_usd"] - seen
    if un_ai < -0.01:
        raise SystemExit(f"agent rows add up to more than the page's AI total by {-un_ai:.2f}")
    return {"period": view, "source": f"Usage page, {RANGE_NAMES[kind]}, read {read_local:%Y-%m-%d %H:%M %Z}",
            "read_at": r["read_at"], "window": r["window"],
            "agents": [{"agent_id": k, "name": a["name"], "ai_usd": a["ai_usd"], "tools_usd": 0.0}
                       for k, a in sorted(r["agents"].items())],
            "unattributed": {"ai_usd": round(max(un_ai, 0.0), 2), "tools_usd": r["tools_total_usd"]},
            "excludes": [f"Usage recorded after the read at {r['read_at']}",
                         "Paid tools called from inside agents carry no agent on the usage page, so they are all unattributed",
                         f"Spend of {r['out_of_scope']['count']} agents outside the review's scope (private agents), "
                         "by the workspace's rule"]}


PAGE_JS = r"""const IDS = new Set(__IDS__), KIND = __KIND__;
const q = new URLSearchParams(location.search);
const P = 'self.__next_f.push(';
const flight = [...document.scripts].map(s => s.textContent).filter(t => t.startsWith(P)).map(t => {
  try { const a = JSON.parse(t.slice(P.length, t.lastIndexOf(')'))); return typeof a[1] === 'string' ? a[1] : ''; }
  catch (e) { return ''; } }).join('');
function valueAt(i) {
  let d = 0, j = i;
  for (; j < flight.length; j++) {
    const c = flight[j];
    if (c === '"') { j++; while (flight[j] !== '"') { if (flight[j] === '\\') j++; j++; } }
    else if (c === '[' || c === '{') d++;
    else if (c === ']' || c === '}') { d--; if (d === 0) break; }
  }
  return JSON.parse(flight.slice(i, j + 1));
}
const hits = []; let p = -1;
while ((p = flight.indexOf('"agents":[', p + 1)) >= 0) hits.push(p);
if (hits.length !== 1) throw new Error('expected one agents array in the page data, found ' + hits.length);
const one = k => {
  const v = [...new Set([...flight.matchAll(new RegExp('"' + k + '":(-?[0-9.eE+-]+|true|false)', 'g'))].map(x => x[1]))];
  if (v.length !== 1) throw new Error(k + ' has ' + v.length + ' values in the page data');
  return JSON.parse(v[0]);
};
for (const k of ['agentsOk', 'totalLlmOk', 'totalServicesOk']) if (one(k) !== true) throw new Error(k + ' is not true: a card failed to load');
const agents = [], oos = { count: 0, ai_usd: 0 };
for (const r of valueAt(hits[0] + 9)) {
  if (!r.agent_id) continue;
  if (IDS.has(r.agent_id)) agents.push({ agent_id: r.agent_id, name: r.label, ai_usd: r.total_cost_usd });
  else { oos.count++; oos.ai_usd += r.total_cost_usd; }
}
return JSON.stringify({ kind: KIND, read_at: new Date().toISOString(), tz: q.get('tz'),
  ranges: { total_range: q.get('total_range'), llm_range: q.get('llm_range'), service_range: q.get('service_range') },
  agents, out_of_scope: oos, ai_total_usd: one('totalLlmSpendUsd'), tools_total_usd: one('totalServiceSpendUsd') });"""


def page_js(kind):
    ids = sorted({k.rsplit("-", 1)[-1] for k in in_scope()})
    return PAGE_JS.replace("__IDS__", json.dumps(ids)).replace("__KIND__", json.dumps(kind))


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=("save", "cost", "js"))
    p.add_argument("--kind", choices=RANGE_KINDS, help="for js: which range")
    args = p.parse_args(argv)
    if args.cmd == "save":
        out = save(json.load(sys.stdin))
        print(f"{out['path']}: {RANGE_NAMES[out['kind']]} reading, {len(out['agents'])} agents in scope, "
              f"{out['out_of_scope']['count']} out of scope folded away")
    elif args.cmd == "js":
        if not args.kind:
            raise SystemExit("js needs --kind")
        print(page_js(args.kind))
    else:
        json.dump(cost(os.environ["PERIOD"]), sys.stdout, indent=1)


if __name__ == "__main__":
    main()
