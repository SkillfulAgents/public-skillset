#!/usr/bin/env python3
"""The approval queue. Drafts staged for a human, decided by a human.

  uv run --with pyyaml queue.py add --prospect 12 --step 1 \
      --subject "..." --body-file draft.html [--confidence 0.8] [--variant A]
  uv run --with pyyaml queue.py list [--status pending] [--json]
  uv run --with pyyaml queue.py show 3
  uv run --with pyyaml queue.py approve 3 [4 5 ...] [--via chat]
  uv run --with pyyaml queue.py reject 3 --reason "wrong angle" [--via chat]

Staging is the agent's move; deciding is the operator's. The live dashboard
(slug `outbound` under /workspace/artifacts/) reads this queue and offers
Approve / Reject buttons, so the operator can review from the dashboard
instead of chat; both paths land in the same table and the same audit log.

`add` lints the copy first: a draft that cannot pass the linter has no
business asking for a human's time. Approving is NOT sending. send.py still
runs every gate (do-not-touch, caps, window, pacing, deliverability); the
approval only satisfies the human-review requirement.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import config as cfgmod, db, linter  # noqa: E402


def _open(args):
    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))
    return cfg, conn


def _row_summary(r) -> str:
    conf = f"{r['confidence']:.2f}" if r["confidence"] is not None else "  - "
    subj = (r["subject"] or "(no subject)")[:44]
    return (f"  #{r['id']:<4} {r['status']:<9} p{r['prospect_id']:<5} "
            f"step {r['step_index']} {r['channel']:<16} conf {conf}  {subj}")


def cmd_add(args) -> int:
    cfg, conn = _open(args)
    p = conn.execute("SELECT * FROM prospects WHERE id = ?",
                     (args.prospect,)).fetchone()
    if p is None:
        print(f"no prospect with id {args.prospect}", file=sys.stderr)
        return 1
    body = pathlib.Path(args.body_file).read_text()
    sender_id = args.sender or p["sender_id"] or (
        cfg.senders[0].get("id") if cfg.senders else None)

    lint = linter.lint(args.subject, body, cfg, signature=cfg.signature,
                       sender_id=sender_id, channel=args.channel)
    if not lint.ok:
        print("draft failed the linter; fix it before asking a human to read it:",
              file=sys.stderr)
        print(lint.report(), file=sys.stderr)
        return 3

    with db.transaction(conn):
        try:
            did = db.stage_draft(conn, {
                "prospect_id": args.prospect, "step_index": args.step,
                "channel": args.channel, "sender_id": sender_id,
                "subject": args.subject or None, "body": body,
                "variant": args.variant, "confidence": args.confidence,
            })
        except ValueError as e:
            print(f"REFUSED: {e}", file=sys.stderr)
            return 4
        db.log_decision(conn, "approval", "staged",
                        f"step {args.step} {args.channel} staged for review",
                        prospect_id=args.prospect, ref=f"draft:{did}")
    print(f"staged draft #{did} for prospect {args.prospect} "
          f"({p['name']}, {p['company']}), step {args.step} {args.channel}")
    print("  awaiting operator approval: dashboard queue or queue.py approve")
    return 0


def cmd_list(args) -> int:
    _, conn = _open(args)
    q, params = "SELECT * FROM drafts", []
    if args.status:
        q += " WHERE status = ?"
        params.append(args.status)
    q += " ORDER BY created_at DESC"
    rows = conn.execute(q, params).fetchall()
    if args.json:
        print(json.dumps([dict(r) for r in rows], indent=2))
        return 0
    if not rows:
        print("queue is empty" + (f" (status={args.status})" if args.status else ""))
        return 0
    for r in rows:
        print(_row_summary(r))
    pending = sum(1 for r in rows if r["status"] == "pending")
    if pending:
        print(f"\n{pending} draft(s) awaiting a decision.")
    return 0


def cmd_show(args) -> int:
    _, conn = _open(args)
    r = conn.execute(
        "SELECT d.*, p.name, p.title, p.company, p.icp_tier FROM drafts d"
        " JOIN prospects p ON p.id = d.prospect_id WHERE d.id = ?",
        (args.id,)).fetchone()
    if r is None:
        print(f"no draft #{args.id}", file=sys.stderr)
        return 1
    print(f"draft #{r['id']}  [{r['status']}]")
    print(f"  to      {r['name']}, {r['title']} at {r['company']} "
          f"(tier {r['icp_tier']})")
    print(f"  step    {r['step_index']} {r['channel']}  sender {r['sender_id']}")
    if r["confidence"] is not None:
        print(f"  conf    {r['confidence']:.2f}")
    if r["decided_at"]:
        print(f"  decided {r['decided_at']} via {r['decided_via']}"
              + (f": {r['decision_reason']}" if r["decision_reason"] else ""))
    print(f"  subject {r['subject'] or '(none)'}")
    print("  body:")
    for line in (r["body"] or "").splitlines():
        print(f"    {line}")
    return 0


def _decide(args, new_status: str) -> int:
    _, conn = _open(args)
    rc = 0
    for did in args.ids:
        r = conn.execute("SELECT * FROM drafts WHERE id = ?", (did,)).fetchone()
        if r is None:
            print(f"no draft #{did}", file=sys.stderr)
            rc = 1
            continue
        if r["status"] != "pending":
            print(f"draft #{did} is already {r['status']}; only pending drafts "
                  f"can be decided", file=sys.stderr)
            rc = 1
            continue
        with db.transaction(conn):
            conn.execute(
                "UPDATE drafts SET status = ?, decided_at = datetime('now'),"
                " decided_via = ?, decision_reason = ? WHERE id = ?",
                (new_status, args.via, args.reason or None, did))
            db.log_decision(conn, "approval", new_status,
                            args.reason or f"via {args.via}",
                            prospect_id=r["prospect_id"], ref=f"draft:{did}")
        print(f"draft #{did} {new_status} (via {args.via})")
    return rc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=None)
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add", help="stage a draft for operator review")
    a.add_argument("--prospect", type=int, required=True)
    a.add_argument("--step", type=int, required=True)
    a.add_argument("--channel", default="email")
    a.add_argument("--subject", default="")
    a.add_argument("--body-file", required=True)
    a.add_argument("--sender", default=None)
    a.add_argument("--variant", default=None)
    a.add_argument("--confidence", type=float, default=None)
    a.set_defaults(fn=cmd_add)

    ls = sub.add_parser("list")
    ls.add_argument("--status", default=None,
                    choices=sorted(db.DRAFT_STATUSES))
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(fn=cmd_list)

    sh = sub.add_parser("show")
    sh.add_argument("id", type=int)
    sh.set_defaults(fn=cmd_show)

    apv = sub.add_parser("approve")
    apv.add_argument("ids", type=int, nargs="+")
    apv.add_argument("--via", default="chat")
    apv.add_argument("--reason", default=None)
    apv.set_defaults(fn=lambda a: _decide(a, "approved"))

    rj = sub.add_parser("reject")
    rj.add_argument("ids", type=int, nargs="+")
    rj.add_argument("--via", default="chat")
    rj.add_argument("--reason", required=True,
                    help="a rejection with no reason teaches the drafter nothing")
    rj.set_defaults(fn=lambda a: _decide(a, "rejected"))

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
