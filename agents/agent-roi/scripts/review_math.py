#!/usr/bin/env python3
"""Every number in the review, for one of the Gamut Platform usage page's ranges: wtd, mtd, last7, last14, last30.
Worth counts outcomes delivered in the range. Cost is the page's spend for the same range.

Same inputs, same numbers. A missing input is unknown, never zero.
"""
import argparse, datetime, json, os, sys

HARD = ("money_saved", "money_made")
KINDS = ("time_saved",) + HARD
CARD_FIELDS = ("agent_id", "agent_name", "purpose", "confirmed_at", "confirmed_by")
TYPE_FIELDS = ("id", "name", "counts_when", "receipt", "value_kind", "price_reason", "price_anchor", "counts_on")
ANCHORS = ("owner", "market_rate", "real_cost", "estimate")
PEOPLE_TIME_DEFAULTS = {"first_message_min": 2, "gap_cap_min": 10, "in_cost": False}
ALWAYS_EXCLUDED = ["Usage on people's own AI subscriptions or API keys",
                   "Time people spend on an agent's work outside its sessions"]


def r2(x):
    return None if x is None else round(x + 0.0, 2)


def validate(cards, coverage):
    problems = []
    for a in coverage.get("agents", []):
        if not isinstance(a.get("agent_id"), str):
            problems.append(f"coverage.json: each agent needs agent_id (text): {a}")
        elif a.get("in_scope") and a.get("readable") not in (True, False, None):
            problems.append(f"coverage.json: readable is true, false, or null until tried: {a}")
    for c in cards.get("agents", []):
        if not c.get("confirmed_at"):
            continue
        problems += [f"{c.get('agent_id')}: missing {f}" for f in CARD_FIELDS if not c.get(f)]
        if not isinstance(c.get("outcome_types"), list):
            problems.append(f"{c.get('agent_id')}: outcome_types must be a list, empty when none were found")
        for t in c.get("outcome_types") or []:
            problems += [f"{c.get('agent_id')}.{t.get('id')}: missing {f}" for f in TYPE_FIELDS if not t.get(f)]
            if t.get("value_kind") not in KINDS:
                problems.append(f"{c.get('agent_id')}.{t.get('id')}: value_kind must be one of {KINDS}")
            if t.get("price_anchor") not in ANCHORS:
                problems.append(f"{c.get('agent_id')}.{t.get('id')}: price_anchor must be one of {ANCHORS}")
            if t.get("counts_on") not in ("delivery", "use"):
                problems.append(f"{c.get('agent_id')}.{t.get('id')}: counts_on must be delivery or use")
    if problems:
        raise SystemExit("review files are not valid:\n" + "\n".join(problems))


def outcome_value(otype, rate, low=False):
    """The stated price, or with low=True the low end of its range (the stated price when no range is given)."""
    if otype["value_kind"] == "time_saved":
        r = otype.get("rate_usd") if otype.get("rate_usd") is not None else rate
        hours = otype.get("hours_low", otype.get("hours")) if low else otype.get("hours")
        return None if hours is None or r is None else hours * r
    return otype.get("price_usd_low", otype.get("price_usd")) if low else otype.get("price_usd")


def scan_minutes(scan, pt):
    return sum(pt["first_message_min"] if m["gap_min"] is None else min(m["gap_min"], pt["gap_cap_min"])
               for m in scan["person_messages"])


def priced_outcomes(cards, outcomes, rate):
    types = {(c["agent_id"], t["id"]): t for c in cards for t in c["outcome_types"]}
    out = []
    for o in outcomes:
        t = types.get((o["agent"], o["type"]))
        out.append({**o, "value": None if t is None else outcome_value(t, rate),
                    "value_low": None if t is None else outcome_value(t, rate, low=True),
                    "value_kind": None if t is None else t["value_kind"],
                    "price_anchor": None if t is None else t.get("price_anchor")})
    return out




def agent_numbers(card, outs, scans, listed, cost, rate, readable, pt):
    aid = card["agent_id"]
    outs = [o for o in outs if o["agent"] == aid and o["status"] != "rejected"]
    scans = [s for s in scans if s["agent"] == aid]
    value = {k: 0.0 for k in KINDS}
    verified, unpriced, by_type, low, by_anchor = 0.0, 0, {}, 0.0, {}
    low_kind = {k: 0.0 for k in KINDS}
    verified_count = 0
    types = {t["id"]: t for t in card["outcome_types"]}
    for o in outs:
        t = types.get(o["type"], {})
        row = by_type.setdefault(o["type"], {"name": t.get("name", o["type"]), "unit": t.get("unit") or t.get("name", o["type"]),
                                             "unit_one": t.get("unit_one"), "value_kind": o["value_kind"], "count": 0, "value": 0.0,
                                             "unit_price_low": r2(outcome_value(t, rate, low=True)) if t else None,
                                             "unit_price": r2(outcome_value(t, rate)) if t else None,
                                             "price_anchor": t.get("price_anchor"), "value_low": 0.0, "checked": 0})
        row["count"] += 1
        if o["value"] is None:
            unpriced += 1
            continue
        row["value"] += o["value"]
        value[o["value_kind"]] += o["value"]
        lo = o["value"] if o.get("value_low") is None else o["value_low"]
        row["value_low"] += lo
        low += lo
        low_kind[o["value_kind"]] += lo
        by_anchor[o.get("price_anchor")] = by_anchor.get(o.get("price_anchor"), 0.0) + o["value"]
        if o["status"] == "verified":
            row["checked"] += 1
            verified += o["value"]
            verified_count += 1

    mins = {s["session"]: scan_minutes(s, pt) for s in scans}
    people_min = sum(mins.values())
    setup_min = sum(mins[s["session"]] for s in scans if s["kind"] == "setup")
    people = None if rate is None else people_min / 60 * rate
    work = [s for s in scans if s["kind"] == "work"]
    total_value = sum(value.values())
    hard = sum(value[k] for k in HARD)
    in_cost = pt["in_cost"]
    if cost is None or (in_cost and people is None):
        ai = tools = total_cost = setup_cost = None
    else:
        # Cost is spend (AI + tools). People's time joins it only when the view asks for it.
        ai, tools = cost["ai_usd"], cost["tools_usd"]
        total_cost = ai + tools + (people if in_cost else 0.0)
        spend = cost.get("sessions") or {}
        complete = (spend and set(spend) <= set(mins) and abs(sum(spend.values()) - (ai + tools)) <= 0.01 * max(ai + tools, 1)
                    and listed is not None and listed["unread"] == 0)
        setup_cost = (sum(spend.get(s["session"], 0.0) for s in scans if s["kind"] == "setup")
                      + (setup_min / 60 * rate if in_cost else 0.0)) if complete else None
    work_cost = None if total_cost is None or setup_cost is None else total_cost - setup_cost
    priced = [k for k, v in by_type.items() if v["count"]]
    for row in by_type.values():
        base = work_cost if work_cost is not None else total_cost
        row["cost_per_outcome"] = r2(base / row["count"]) if base is not None and row["count"] else None
        row["cost_per_outcome_upper_bound"] = len(priced) > 1 or work_cost is None
        row["value"] = r2(row["value"])
        row["value_low"] = r2(row["value_low"])
    flags = []
    if (listed is not None and listed["count"] == 0 and not listed["unread"] and not outs
            and not (cost and (cost["ai_usd"] or cost["tools_usd"]))):
        flags.append("inactive")
    elif not readable:
        flags.append("no_access")
    if cost is None and "inactive" not in flags:
        flags.append("cost_unknown")
    if "inactive" in flags:
        pass
    elif listed is None:
        flags.append("not_counted")
    elif listed["unread"] or len(scans) < listed["count"]:
        flags.append("partial_count")
    if unpriced:
        flags.append("unpriced_outcomes")
    # Idle: nothing delivered in the range, once every session in it was read. A partly read agent stays incomplete.
    idle = "inactive" in flags or (readable and not outs and listed is not None and listed["unread"] == 0)
    return {
        "agent_id": aid, "agent_name": card.get("agent_name"), "owner": card.get("owner"), "team": card.get("team"),
        "flags": flags, "idle": idle, "complete": not flags,
        "outcomes": len(outs), "unpriced_outcomes": unpriced, "by_type": by_type,
        "value": {k: r2(v) for k, v in value.items()}, "total_value": r2(total_value), "hard_value": r2(hard),
        "value_low": r2(low), "cash_low": r2(sum(low_kind[k] for k in HARD)), "time_low": r2(low_kind["time_saved"]),
        "receipts": len(outs), "receipts_checked": verified_count,
        "delivered": [{"count": r["count"], "unit": r["unit_one"] if r["count"] == 1 and r["unit_one"] else r["unit"],
                       "unit_price_low": r["unit_price_low"], "unit_price": r["unit_price"], "price_anchor": r["price_anchor"]}
                      for r in sorted(by_type.values(), key=lambda r: -r["value"])],
        "verified_value": r2(verified), "value_by_anchor": {k: r2(v) for k, v in by_anchor.items()},
        "net_value_low": r2(low - total_cost) if total_cost is not None and not flags else None,
        "soft_value": r2(value["time_saved"]), "verified_share": r2(verified / total_value) if total_value > 0 else None,
        "cost": {"ai": r2(ai), "tools": r2(tools), "people": r2(people), "total": r2(total_cost)},
        "people_minutes": r2(people_min), "setup_cost": r2(setup_cost), "work_cost": r2(work_cost),
        "setup_share_of_people_time": r2(setup_min / people_min) if people_min else None,
        "sessions_alone": r2(sum(1 for s in work if not s["person_messages"]) / len(work)) if work else None,
        "net_value": r2(total_value - total_cost) if total_cost is not None and not flags else None,
        "net_hard_value": r2(hard - total_cost) if total_cost is not None and not flags else None,
        "roi": r2((total_value - total_cost) / total_cost) if total_cost and not flags else None,
        "return_low": r2(low / total_cost) if total_cost and not flags else None,
        "return_high": r2(total_value / total_cost) if total_cost and not flags else None,
        "sessions_read": len(scans), "sessions_listed": None if listed is None else listed["count"],
        "sessions": sorted(({"session": s["session"], "started_at": s["started_at"], "kind": s["kind"],
                             "kind_reason": s["kind_reason"], "kind_by": s.get("kind_by"),
                             "people_minutes": r2(mins[s["session"]]), "person_messages": len(s["person_messages"])}
                            for s in scans), key=lambda s: s["started_at"]),
    }


def in_scope(cost, coverage, scope):
    """With scope "listed", only agents in coverage.json marked in_scope count anywhere, cost included."""
    if scope != "listed":
        return cost
    keep = {a["agent_id"] for a in coverage["agents"] if a.get("in_scope")}
    return {**cost, "agents": {k: v for k, v in cost["agents"].items() if k in keep}}


def price_text(t, rate):
    if t["value_kind"] == "time_saved":
        r = t.get("rate_usd") if t.get("rate_usd") is not None else rate
        h = f"{t['hours_low']}–{t['hours']}" if t.get("hours_low") is not None else f"{t.get('hours')}"
        return f"{h} h × ${r:,.0f}/h" if r is not None else f"{h} h"
    lo = t.get("price_usd_low")
    return (f"${lo:,.0f}–" if lo is not None else "$") + f"{t.get('price_usd', 0):,.0f}"


def compute(period, cards, outs, scans, listed, cost, coverage, rate, pt, exclusions=()):
    """cards: confirmed cards. outs: priced outcomes. cost: the range's cost file, already scoped, or None when the
    range hasn't been read: cost is then unknown everywhere. Value from agents counted from a sample shows in the value
    totals. Cost, net and return count only fully counted agents."""
    unreadable = {a["agent_id"] for a in coverage["agents"] if a["readable"] is False}
    spend = cost["agents"] if cost else {}
    agents = [agent_numbers(c, outs, scans, listed.get(c["agent_id"]), spend.get(c["agent_id"]),
                            rate, c["agent_id"] not in unreadable, pt) for c in cards]
    carded = {a["agent_id"] for a in agents}
    not_covered = [{"agent_id": k, "agent_name": v.get("name"), "spend": r2(v["ai_usd"] + v["tools_usd"])}
                   for k, v in spend.items() if k not in carded]
    counted = [a for a in agents if a["complete"]]
    value_ok = {"cost_unknown", "partial_count"}
    valued = [a for a in agents if a["complete"] or (a["flags"] and set(a["flags"]) <= value_ok)]
    un = cost["unattributed"] if cost else None
    tv = sum(a["total_value"] for a in valued)
    vv = sum((a["verified_share"] or 0) * a["total_value"] for a in valued)
    lv = sum(a["value_low"] for a in valued)
    est = sum(a["value_by_anchor"].get("estimate", 0) or 0 for a in valued)
    types = [(a["agent_name"], row["name"], row["value"], next((t.get("price_anchor") for c in cards if c["agent_id"] == a["agent_id"]
              for t in c["outcome_types"] if t["name"] == row["name"]), None)) for a in valued for row in a["by_type"].values()]
    drivers = [{"agent": n, "outcome": t, "value": v, "share": r2(v / tv) if tv else None, "price_anchor": an}
               for n, t, v, an in sorted(types, key=lambda x: -(x[2] or 0))[:3]]
    hv = sum(a["hard_value"] for a in valued)
    ccv = sum(a["total_value"] for a in counted)
    clv = sum(a["value_low"] for a in counted)
    chv = sum(a["hard_value"] for a in counted)
    tc = sum(a["cost"]["total"] for a in counted) if counted else None
    part = lambda k: r2(sum(a["cost"][k] for a in counted)) if counted else None
    split_known = bool(counted) and all(a["setup_cost"] is not None for a in counted)
    all_spend = (sum(v["ai_usd"] + v["tools_usd"] for v in spend.values()) + un["ai_usd"] + un["tools_usd"]) if cost else None
    prices = []
    for a in valued:
        card = next(c for c in cards if c["agent_id"] == a["agent_id"])
        for t in card["outcome_types"]:
            row = a["by_type"].get(t["id"])
            if row and row["count"]:
                prices.append({"agent": a["agent_name"], "outcome": t["name"], "price": price_text(t, rate),
                               "anchor": t.get("price_anchor"), "reason": t.get("price_reason"),
                               "count": row["count"], "value": row["value"]})
    prices.sort(key=lambda p: -(p["value"] or 0))
    left_out = [dict(e) for e in exclusions]
    if cost is None:
        left_out.append({"label": "Cost: this range hasn't been read from the usage page yet", "amount": "unknown",
                         "effect": "unknown"})
    elif un["tools_usd"] or un["ai_usd"]:
        left_out.append({"label": "Spend tied to no agent", "amount": f"${un['ai_usd'] + un['tools_usd']:,.0f}", "effect": "cost_low"})
    if not_covered:
        left_out.append({"label": f"Agents in scope that the review can't read ({len(not_covered)})",
                         "amount": f"${sum(n['spend'] for n in not_covered):,.0f}", "effect": "cost_low"})
    for a in agents:
        if a in counted or "inactive" in a["flags"] or (cost is None and set(a["flags"]) <= {"cost_unknown", "partial_count"}):
            continue
        cost_gap = a in valued and "cost_unknown" in a["flags"]
        left_out.append({"label": f"{a['agent_name']}: {', '.join(f.replace('_', ' ') for f in a['flags'])}",
                         "amount": f"${a['total_value']:,.0f} value {'counted' if a in valued else 'seen'}",
                         "effect": "cost_low" if cost_gap else "value_low"})
    lead = {
        "period": period, "agents_counted": len(counted), "agents_carded": len(agents),
        "idle_agents": [a["agent_name"] for a in agents if a["idle"]],
        "inactive": [a["agent_name"] for a in agents if "inactive" in a["flags"]],
        "cost_known": cost is not None,
        "cost_parts": {"ai": part("ai"), "tools": part("tools"), "people": part("people")},
        "cash_low": r2(sum(a["cash_low"] for a in valued)),
        "time_low": r2(sum(a["time_low"] for a in valued)),
        "receipts": sum(a["receipts"] for a in valued), "receipts_checked": sum(a["receipts_checked"] for a in valued),
        "prices": prices, "left_out": left_out,
        "agents_not_counted": [{"agent_id": a["agent_id"], "agent_name": a["agent_name"], "flags": a["flags"],
                                "value_so_far": a["total_value"]} for a in agents if a not in counted and "inactive" not in a["flags"]],
        "total_value": r2(tv), "hard_value": r2(hv), "soft_value": r2(tv - hv),
        "counted_value": r2(ccv), "counted_value_low": r2(clv),
        "counted_hard_value": r2(chv), "counted_time_low": r2(sum(a["time_low"] for a in counted)),
        "counted_soft_value": r2(sum(a["value"]["time_saved"] for a in counted)),
        "total_cost": r2(tc), "net_value": r2(ccv - tc) if tc is not None else None,
        "net_hard_value": r2(chv - tc) if tc is not None else None,
        "roi": r2((ccv - tc) / tc) if tc else None,
        "return_low": r2(clv / tc) if tc else None, "return_high": r2(ccv / tc) if tc else None,
        "verified_share": r2(vv / tv) if tv > 0 else None,
        "verified_value": r2(vv), "total_value_low": r2(lv),
        "net_value_low": r2(clv - tc) if tc is not None else None,
        "value_from_estimates_share": r2(est / tv) if tv > 0 else None,
        "drivers": drivers,
        "investment_cost": r2(sum(a["setup_cost"] for a in counted)) if split_known else None,
        "operating_cost": r2(sum(a["work_cost"] for a in counted)) if split_known else None,
        "workspace_spend": r2(all_spend), "not_reviewed_spend": r2(sum(n["spend"] for n in not_covered)),
        "unattributed_spend": r2(un["ai_usd"] + un["tools_usd"]) if cost else None,
        "cost_source": cost.get("source") if cost else "unknown", "cost_read_at": cost.get("read_at") if cost else None,
        "excludes": ALWAYS_EXCLUDED + [x for x in (cost or {}).get("excludes", []) if x not in ALWAYS_EXCLUDED],
        "people_in_cost": pt["in_cost"],
    }
    return {"leadership": lead, "agents": agents, "not_covered": not_covered}


def read_json(path, fallback=None):
    return json.load(open(path)) if os.path.exists(path) else fallback


VIEWS = ("wtd", "mtd", "last7", "last14", "last30")
STALE_AFTER_HOURS = 24


def window_bounds(review_dir, view, tz):
    """A view's days: the window of its usage page reading when there is one, so value and cost cover the same days.
    Otherwise the same range counted to tomorrow's midnight in the review's timezone, as the page counts it."""
    cost = read_json(os.path.join(review_dir, "costs", f"{view}.json"))
    if cost and cost.get("window"):
        return tuple(datetime.datetime.fromisoformat(cost["window"][k]) for k in ("start", "end"))
    import usage_page
    return usage_page.window_for(usage_page.VIEWS[view], datetime.datetime.now(tz), tz)


def in_window(at, start, end):
    t = datetime.datetime.fromisoformat(str(at).replace("Z", "+00:00"))
    if t.tzinfo is None:
        t = t.replace(tzinfo=start.tzinfo)
    return start <= t < end


def load_view(review_dir, view="last30", people_in_cost=None):
    """One of the usage page's ranges, from the drafts of every month it touches and the page's reading of that range.
    It moves every day. Months are only the unit of storage underneath."""
    import ledger
    from zoneinfo import ZoneInfo
    ledger.REVIEW = review_dir
    cards = read_json(os.path.join(review_dir, "cards.json"), {"agents": []})
    coverage = read_json(os.path.join(review_dir, "coverage.json"), {"agents": []})
    validate(cards, coverage)
    config = ledger.config_snapshot()
    tz = ZoneInfo(config["timezone"])
    start, end = window_bounds(review_dir, view, tz)
    first, last = f"{start.astimezone(tz):%Y-%m}", f"{(end - datetime.timedelta(seconds=1)).astimezone(tz):%Y-%m}"
    months = ledger.months_between(first, last) + [last]
    confirmed, rate = config["cards"], config["cost_of_an_hour_usd"]
    pt = {**PEOPLE_TIME_DEFAULTS, **(config["people_time"] or {})}
    if people_in_cost is not None:  # a view option from the dashboard; the saved setting is unchanged
        pt["in_cost"] = people_in_cost
    outs, scans, exclusions, listed_by = [], [], [], {}
    read_until = None
    for m in months:
        evts = ledger.events(m)
        # The newest month decides how fresh the count is: new sessions land there.
        read_until = max([""] + [e["at"] for e in evts if e["event"] in ("scan", "listed", "outcome")]) or None
        st = ledger.state(evts)
        outs += [o for o in st["outcomes"].values() if in_window(o["delivered_at"], start, end)]
        scans += [s for s in st["scans"].values() if in_window(s["started_at"], start, end)]
        exclusions += [e for e in st["exclusions"] if e not in exclusions]
        for aid, l in st["listed"].items():
            listed_by.setdefault(aid, {})[m] = l
    # A month's session list can't be cut to the window, so the window counts as read only when every month it
    # touches was listed for the agent with nothing left unread.
    listed = {}
    for c in confirmed:
        aid, per = c["agent_id"], listed_by.get(c["agent_id"], {})
        n = sum(1 for s in scans if s["agent"] == aid)
        if not per:
            continue
        unread = sum(l["unread"] for l in per.values()) + sum(1 for m in months if m not in per)
        listed[aid] = {"count": n, "unread": unread}
    cost = read_json(os.path.join(review_dir, "costs", f"{view}.json"))
    if cost is not None:
        cost = in_scope(cost, coverage, cards.get("scope", "listed"))
    priced = priced_outcomes(confirmed, outs, rate)
    last_day = (end - datetime.timedelta(seconds=1)).astimezone(tz)
    label = f"{start.astimezone(tz):%b %-d} to {last_day:%b %-d}"
    numbers = compute(view, confirmed, priced, scans, listed, cost, coverage, rate, pt, exclusions)
    L = numbers["leadership"]
    L["window"] = {"start": start.isoformat(), "end": end.isoformat(), "label": label, "months": months, "timezone": tz.key}
    # How far to trust the page: how much of the work was read, and how much of the worth is checked or estimated.
    A = numbers["agents"]
    status = lambda a: ("idle" if a["idle"] else "counted" if a["complete"]
                        else "cost_unknown" if "cost_unknown" in a["flags"] else "partial")
    by_anchor = {}
    for a in A:
        for an, v in a["value_by_anchor"].items():
            by_anchor[an or "unknown"] = r2(by_anchor.get(an or "unknown", 0) + (v or 0))
    L["trust"] = {"agents": {k: sum(1 for a in A if status(a) == k) for k in ("counted", "partial", "cost_unknown", "idle")},
                  "partial_agents": [a["agent_name"] for a in A if status(a) == "partial"],
                  "sessions_read": sum(a["sessions_read"] for a in A),
                  "sessions_unread": sum(l["unread"] for l in listed.values()),
                  "value_checked": L["verified_value"], "value_unchecked": r2(L["total_value"] - L["verified_value"]),
                  "value_by_anchor": by_anchor}
    # Fresh as of the older of the two reads: sessions counted, and the usage page.
    now = datetime.datetime.now(datetime.timezone.utc)
    stamps = [datetime.datetime.fromisoformat(x.replace("Z", "+00:00")) for x in (read_until, (cost or {}).get("read_at")) if x]
    as_of = min(stamps) if stamps else None
    L["freshness"] = {"sessions_read_until": read_until, "cost_read_at": (cost or {}).get("read_at"),
                      "as_of": as_of.isoformat() if as_of else None,
                      "hours_old": r2((now - as_of).total_seconds() / 3600) if as_of else None,
                      "stale": as_of is None or (now - as_of).total_seconds() > STALE_AFTER_HOURS * 3600}
    if cards.get("scope", "listed") == "listed":
        L["excludes"].append("Agents outside the review's scope, such as people's private agents")
    numbers["inputs"] = {"cost_of_an_hour_usd": rate, "cards_confirmed": len(confirmed), "people_time": pt}
    return {"period": view, "window": L["window"], "numbers": numbers, "cards": confirmed, "outcomes": priced}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", required=True, choices=VIEWS, help="which usage page range")
    p.add_argument("--people-in-cost", choices=("yes", "no"), help="show cost with or without people's time, "
                   "overriding the saved setting for this view only")
    args = p.parse_args(argv)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import ledger
    pic = None if args.people_in_cost is None else args.people_in_cost == "yes"
    print(json.dumps(load_view(ledger.REVIEW, args.period, pic), indent=1, default=list))


if __name__ == "__main__":
    main()
