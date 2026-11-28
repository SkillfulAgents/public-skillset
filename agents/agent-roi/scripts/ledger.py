#!/usr/bin/env python3
"""The only writer of the review's drafts.

Outcomes and sessions are stored by the month they happened in, one draft per month: review/drafts/<period>.jsonl.
Months are storage only. The dashboard's ranges read every month they touch. Nothing closes.
"""
import argparse, datetime, glob, json, os, sys

REVIEW = os.environ.get("REVIEW_DIR", os.path.join(os.getcwd(), "review"))
KINDS = ("setup", "work")


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def norm(receipt):
    return receipt.strip().rstrip("/")


def cards():
    return json.load(open(os.path.join(REVIEW, "cards.json")))


def months_between(start, end):
    y, m = map(int, start.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" < end:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def config_snapshot():
    c = cards()
    return {"cards": [a for a in c["agents"] if a.get("confirmed_at")], "cost_of_an_hour_usd": c.get("cost_of_an_hour_usd"),
            "people_time": c.get("people_time"), "timezone": c.get("timezone") or "UTC"}


def draft_path(period):
    return os.path.join(REVIEW, "drafts", f"{period}.jsonl")


def events(period):
    path = draft_path(period)
    return [json.loads(l) for l in open(path) if l.strip()] if os.path.exists(path) else []


def append(period, event):
    path = draft_path(period)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    event["at"] = now()
    with open(path, "a") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")


def person_messages(messages):
    """messages: [("person"|"agent", iso_time)] in order, this month only. Each person message with the
    minutes since the agent's previous reply (None for the first)."""
    out, last_agent = [], None
    for role, at in messages:
        t = datetime.datetime.fromisoformat(at.replace("Z", "+00:00"))
        if role == "agent":
            last_agent = t
        else:
            out.append({"gap_min": None if last_agent is None else round(max((t - last_agent).total_seconds() / 60, 0), 2)})
    return out


def state(evts):
    """The draft as it stands. Person decisions apply last, so they survive a rescan or a clear."""
    outcomes, scans, listed, exclusions = {}, {}, {}, []
    status, corrections, kinds = {}, {}, {}
    for e in evts:
        t = e["event"]
        if t == "outcome":
            outcomes[e["receipt"]] = dict(e)
        elif t == "scan":
            scans[(e["agent"], e["session"])] = dict(e)
        elif t == "listed":
            listed[e["agent"]] = {"count": e["count"], "unread": e["unread"]}
        elif t == "exclusion":
            exclusions.append({k: e[k] for k in ("label", "amount", "effect", "agent")})
        elif t == "status":
            status[e["receipt"]] = e
        elif t == "correct":
            corrections[e["receipt"]] = e
        elif t == "kind":
            kinds[(e["agent"], e["session"])] = e
        elif t == "clear":
            decided = set(status) | set(corrections)
            for r in [r for r, o in outcomes.items() if o["agent"] == e["agent"] and r not in decided]:
                del outcomes[r]
            for k in [k for k in scans if k[0] == e["agent"]]:
                del scans[k]
            listed.pop(e["agent"], None)
    for r, c in corrections.items():
        if r in outcomes:
            outcomes[r].update(agent=c["agent"], type=c["type"], corrected_by=c["by"])
    for r, s in status.items():
        if r in outcomes:
            outcomes[r].update(status=s["status"], status_by=s["by"])
    for k, s in kinds.items():
        if k in scans:
            scans[k].update(kind=s["kind"], kind_reason=s["reason"], kind_by=s["by"])
    return {"outcomes": outcomes, "scans": scans, "listed": listed, "exclusions": exclusions}


def known_receipts(skip_period=None):
    """Receipts counted in any other month's draft, and every rejected receipt."""
    counted, rejected = set(), set()
    for p in glob.glob(os.path.join(REVIEW, "drafts", "*.jsonl")):
        period = os.path.basename(p)[:7]
        if period == skip_period:
            continue
        for o in state(events(period))["outcomes"].values():
            (rejected if o["status"] == "rejected" else counted).add(o["receipt"])
    return counted, rejected


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    def cmd(name, help, *fields):
        c = sub.add_parser(name, help=help)
        c.add_argument("--period", required=True, help="YYYY-MM, the month it happened in")
        for f in fields:
            c.add_argument("--" + f, required=True)
        return c

    a = cmd("add", "one outcome delivered this month. Refuses a receipt already counted or rejected",
            "agent", "type", "session", "delivered-at", "receipt", "quote")
    a.add_argument("--status", choices=("verified", "reported"), required=True)
    s = cmd("scan", "a session read for this month", "agent", "session", "started-at", "reason")
    s.add_argument("--kind", choices=KINDS, required=True)
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--messages", help='JSON list of ["person"|"agent", iso_time], this month only, in order')
    g.add_argument("--person-messages", type=int, help="count, when the session has no message times")
    li = cmd("listed", "sessions active this month, and how many are still unread", "agent")
    li.add_argument("--count", type=int, required=True)
    li.add_argument("--unread", type=int, required=True)
    for name in ("reject", "accept"):
        cmd(name, "a person's decision on an outcome", "receipt", "by", "reason")
    cmd("correct", "a person moves an outcome to another agent or type", "receipt", "agent", "type", "by", "reason")
    k = cmd("set-kind", "a person sets setup or work for a session", "agent", "session", "by", "reason")
    k.add_argument("--kind", choices=KINDS, required=True)
    cmd("clear", "drop this month's inferred work for an agent. Person decisions stay", "agent", "by", "reason")
    cmd("verify", "you opened an outcome's receipt and it exists", "receipt", "how")
    cmd("scan-routine", "record many sessions of one routine kind as read without opening them: work, no person",
        "agent", "kind-name", "sessions-file")
    ex = cmd("exclusion", "something real the numbers leave out, with its size and which way it skews them",
             "label", "amount")
    ex.add_argument("--agent", default=None)
    ex.add_argument("--effect", choices=("value_low", "cost_low", "value_high", "cost_high", "out_of_scope"), required=True)
    cmd("state", "print this month's draft as JSON")
    args = p.parse_args(argv)
    period = args.period
    st = state(events(period))

    if args.cmd == "add":
        rec = norm(args.receipt)
        counted, rejected = known_receipts(skip_period=period)
        if rec in st["outcomes"] or rec in counted or rec in rejected:
            print("refused: receipt already counted or rejected")
            return 3
        if not args.delivered_at.startswith(period):
            print(f"refused: delivered {args.delivered_at}, not in {period}")
            return 2
        append(period, {"event": "outcome", "agent": args.agent, "type": args.type, "session": args.session,
                        "delivered_at": args.delivered_at, "receipt": rec, "quote": args.quote, "status": args.status})
    elif args.cmd == "scan":
        entries = (person_messages(json.loads(args.messages)) if args.messages is not None
                   else [{"gap_min": None}] * args.person_messages)
        append(period, {"event": "scan", "agent": args.agent, "session": args.session, "started_at": args.started_at,
                        "kind": args.kind, "kind_reason": args.reason, "person_messages": entries})
    elif args.cmd == "listed":
        append(period, {"event": "listed", "agent": args.agent, "count": args.count, "unread": args.unread})
    elif args.cmd in ("reject", "accept", "correct", "verify"):
        rec = norm(args.receipt)
        if rec not in st["outcomes"]:
            print("unknown receipt in this month's draft")
            return 2
        if args.cmd == "correct":
            append(period, {"event": "correct", "receipt": rec, "agent": args.agent, "type": args.type,
                            "by": args.by, "reason": args.reason})
        elif args.cmd == "verify":
            append(period, {"event": "status", "receipt": rec, "status": "verified", "by": "receipt opened",
                            "reason": args.how})
        else:
            append(period, {"event": "status", "receipt": rec, "by": args.by, "reason": args.reason,
                            "status": "rejected" if args.cmd == "reject" else "verified"})
    elif args.cmd == "set-kind":
        if (args.agent, args.session) not in st["scans"]:
            print("unknown session in this month's draft")
            return 2
        append(period, {"event": "kind", "agent": args.agent, "session": args.session, "kind": args.kind,
                        "by": args.by, "reason": args.reason})
    elif args.cmd == "clear":
        append(period, {"event": "clear", "agent": args.agent, "by": args.by, "reason": args.reason})
    elif args.cmd == "scan-routine":
        rows = json.load(open(args.sessions_file))
        for row in rows:
            append(period, {"event": "scan", "agent": args.agent, "session": row["session"],
                            "started_at": row["started_at"], "kind": "work",
                            "kind_reason": f"routine: {args.kind_name}", "person_messages": []})
        print(f"{len(rows)} routine sessions recorded")
    elif args.cmd == "exclusion":
        append(period, {"event": "exclusion", "label": args.label, "amount": args.amount, "effect": args.effect,
                        "agent": args.agent})
    elif args.cmd == "state":
        print(json.dumps({**st, "outcomes": list(st["outcomes"].values()), "scans": list(st["scans"].values())},
                         indent=1, default=str))
        return 0
    print(args.cmd + ": ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
