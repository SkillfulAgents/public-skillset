#!/usr/bin/env python3
"""Feedback-queue helper: list pending the hiring lead-verdict events, mark them handled.

Append-only design (no rewrites, no locks):
  feedback-queue.jsonl      events appended by the dashboard server
  feedback-processed.jsonl  {id, status, processed_at, result} appended here
Pending = queue events whose id has no marker in the processed file.
"""
import argparse
import datetime
import json
import pathlib

QUEUE = pathlib.Path("/workspace/pipeline/feedback-queue.jsonl")
PROCESSED = pathlib.Path("/workspace/pipeline/feedback-processed.jsonl")


def read_jsonl(p):
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def cand_key(e):
    c = e.get("candidate") or {}
    return (
        e.get("source"),
        c.get("application_id") or c.get("id") or c.get("linkedin_url") or c.get("name"),
    )


def pending_events():
    done = {r.get("id") for r in read_jsonl(PROCESSED)}
    return [e for e in read_jsonl(QUEUE) if e.get("id") not in done]


def cmd_list(args):
    pending = pending_events()
    if args.all:
        for e in pending:
            print(json.dumps(e))
        return
    latest = {}
    for e in pending:  # file order is chronological (append-only)
        latest[cand_key(e)] = e
    superseded = [e["id"] for e in pending if latest[cand_key(e)] is not e]
    for e in latest.values():
        print(json.dumps(e))
    if superseded:
        print(json.dumps({"_superseded_ids": superseded,
                          "_note": "older click on same candidate; mark with --status superseded"}))


def cmd_mark(args):
    rec = {
        "id": args.id,
        "status": args.status,
        "processed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "result": args.result,
    }
    with PROCESSED.open("a") as f:
        f.write(json.dumps(rec) + "\n")
    print(f"marked {args.id} -> {args.status}")


def cmd_stats(args):
    q = read_jsonl(QUEUE)
    n_pending = len(pending_events())
    print(json.dumps({"pending": n_pending, "processed": len(q) - n_pending, "total": len(q)}))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="print pending events (latest per candidate)")
    p.add_argument("--all", action="store_true", help="include superseded duplicates")
    p.set_defaults(fn=cmd_list)

    p = sub.add_parser("mark", help="record an event as handled")
    p.add_argument("id")
    p.add_argument("--status", default="processed",
                   choices=["processed", "error", "superseded", "skipped"])
    p.add_argument("--result", default="", help="one line: what was done")
    p.set_defaults(fn=cmd_mark)

    p = sub.add_parser("stats", help="pending/processed counts as JSON")
    p.set_defaults(fn=cmd_stats)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
