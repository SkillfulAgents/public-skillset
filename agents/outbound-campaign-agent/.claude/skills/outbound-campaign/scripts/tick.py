#!/usr/bin/env python3
"""The daily heartbeat: check replies, then surface what is due. Sends nothing.

  uv run --with pyyaml tick.py [--dry-run] [--json]

Run on a schedule (see reporting.schedule.cadence_tick_cron). It does three
things in a fixed order, and the order is the point:

  1. Check for replies FIRST, before computing anything due. A reply that
     arrives overnight must suppress this morning's follow-up. Computing the
     due list first and checking replies second is how a cadence emails
     someone who already answered.
  2. Retire anyone who replied, bounced, or finished the cadence.
  3. Report what is due today, within caps, and stop.

It deliberately does not send. Every message goes through send.py, which is
where the linter, the caps, and the do-not-touch gate live. A tick that sends
directly would bypass all three.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters, caps, config as cfgmod, db  # noqa: E402


def check_replies(cfg, conn, lookback_days: int) -> list[dict]:
    """Ask the sender adapter what came back. Records replies against the
    prospect and halts their cadence."""
    ad = adapters.load(cfg, "sender")
    if ad is None or not ad.supports("check_replies"):
        return []
    since = cfg.now() - dt.timedelta(days=lookback_days)
    found = ad.check_replies(adapters.context(cfg, ad), since) or []

    recorded = []
    for r in found:
        row = None
        if r.get("thread_id"):
            row = conn.execute(
                "SELECT p.* FROM prospects p JOIN sends s ON s.prospect_id = p.id "
                "WHERE s.provider_thread_id = ? LIMIT 1", (r["thread_id"],)).fetchone()
        if row is None and r.get("from"):
            row = conn.execute("SELECT * FROM prospects WHERE lower(email) = ?",
                               (r["from"].casefold(),)).fetchone()
        if row is None:
            continue
        if db.has_replied(conn, row["id"]):
            continue

        with db.transaction(conn):
            conn.execute(
                "INSERT INTO replies (prospect_id, replied_at, snippet, thread_id) "
                "VALUES (?,?,?,?)",
                (row["id"], r.get("received_at") or cfg.now().isoformat(),
                 r.get("snippet", ""), r.get("thread_id")))
            conn.execute("UPDATE prospects SET status = ? WHERE id = ?",
                         ("replied", row["id"]))
            db.log_decision(conn, "reply", "stop_cadence",
                            "reply detected; remaining steps suppressed",
                            prospect_id=row["id"], layer=ad.name)
        recorded.append({"prospect_id": row["id"], "name": row["name"],
                         "email": row["email"], "snippet": r.get("snippet", "")[:140]})
    return recorded


def due_steps(cfg, conn) -> list[dict]:
    """What the cadence says should go out today, before caps are applied."""
    steps = cfg.get("cadence.steps", []) or []
    now = cfg.now()
    out = []

    rows = conn.execute(
        "SELECT * FROM prospects WHERE status NOT IN "
        f"({','.join('?' * len(db.TERMINAL_STATUSES))})",
        tuple(db.TERMINAL_STATUSES)).fetchall()

    for p in rows:
        sent = {r["step_index"]: r for r in conn.execute(
            "SELECT step_index, sent_at FROM sends WHERE prospect_id = ?",
            (p["id"],)).fetchall()}

        nxt = next((i for i in range(len(steps)) if i not in sent), None)
        if nxt is None:
            with db.transaction(conn):
                conn.execute("UPDATE prospects SET status = ? WHERE id = ?",
                             ("completed", p["id"]))
                db.log_decision(conn, "cadence", "completed",
                                "all cadence steps sent, no reply",
                                prospect_id=p["id"])
            continue

        step = steps[nxt]
        if sent:
            anchor = min(dt.datetime.fromisoformat(r["sent_at"]) for r in sent.values())
        else:
            anchor = dt.datetime.fromisoformat(p["added_at"])
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=now.tzinfo)

        due_on = anchor + dt.timedelta(days=int(step.get("day", 0)))
        if due_on > now:
            continue
        if step.get("condition") == "invite_accepted" and not p["linkedin_accepted"]:
            continue

        out.append({"prospect_id": p["id"], "name": p["name"], "email": p["email"],
                    "company": p["company"], "step": nxt,
                    "step_name": step.get("intent", ""),
                    "channel": step.get("channel", "email"),
                    "sender_id": p["sender_id"],
                    "overdue_days": (now - due_on).days})
    out.sort(key=lambda d: (-d["overdue_days"], d["step"]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lookback-days", type=int, default=7)
    ap.add_argument("--skip-reply-check", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    replies = [] if args.skip_reply_check else check_replies(cfg, conn, args.lookback_days)
    due = due_steps(cfg, conn)

    ok, window_reason = cfg.in_send_window()
    budget = {}
    for s in cfg.senders:
        gate = caps.check_send(cfg, conn, s["id"])
        budget[s["id"]] = max(0, gate.remaining)

    health = caps.check_deliverability(cfg, conn)

    li_budget = {s["id"]: caps.check_linkedin_invite(cfg, conn, s["id"]).remaining
                 for s in cfg.senders}

    scheduled, manual, deferred = [], [], []
    for d in due:
        sid = d["sender_id"] or (cfg.senders[0]["id"] if cfg.senders else None)
        if d["channel"] != "email":
            # No automated executor for LinkedIn, deliberately. These go to the
            # operator's manual queue; invites still consume a capped budget.
            if d["channel"] == "linkedin_invite" and li_budget.get(sid, 0) <= 0:
                deferred.append({**d, "why": f"{sid} has no LinkedIn invite "
                                             f"budget left today"})
            else:
                if d["channel"] == "linkedin_invite":
                    li_budget[sid] -= 1
                manual.append({**d, "sender_id": sid})
            continue
        if not health.allowed:
            deferred.append({**d, "why": health.reason})
        elif budget.get(sid, 0) <= 0:
            deferred.append({**d, "why": f"{sid} has no send budget left today"})
        else:
            budget[sid] -= 1
            scheduled.append({**d, "sender_id": sid})

    approvals = conn.execute(
        "SELECT status, COUNT(*) AS n FROM drafts GROUP BY status").fetchall()
    appr = {r["status"]: r["n"] for r in approvals}

    result = {
        "at": cfg.now().isoformat(),
        "in_send_window": ok,
        "window": window_reason,
        "deliverability": health.reason,
        "replies_detected": replies,
        "due": len(due),
        "scheduled": scheduled,
        "manual": manual,
        "deferred": deferred,
        "approvals": appr,
        "remaining_budget": budget,
        "remaining_linkedin_invites": li_budget,
    }

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0

    print(f"Cadence tick {result['at']}\n")
    if replies:
        print(f"REPLIES ({len(replies)}), cadence stopped for each:")
        for r in replies:
            print(f"  {r['name']} <{r['email']}>: {r['snippet']}")
        print("  Hand these to the operator. Do not auto-reply.\n")

    if not health.allowed:
        print(f"HALTED: {health.reason}")
        print("  Nothing will be scheduled until this clears.\n")
    elif health.reason.startswith("WARN"):
        print(f"WARNING: {health.reason}\n")

    if not ok:
        print(f"Outside the send window ({window_reason}).")
        print("  The list below is what will be due when the window opens.\n")

    print(f"DUE TODAY: {len(due)}  |  emails schedulable now: {len(scheduled)}"
          f"  |  manual LinkedIn actions: {len(manual)}")
    for d in scheduled[:20]:
        flag = f" ({d['overdue_days']}d overdue)" if d["overdue_days"] > 0 else ""
        print(f"  prospect {d['prospect_id']:>4}  step {d['step']} "
              f"{d['step_name']:<12} {d['channel']:<16} {d['name']}{flag}")
    if len(scheduled) > 20:
        print(f"  ... and {len(scheduled) - 20} more")

    if manual:
        print(f"\nMANUAL LINKEDIN QUEUE: {len(manual)} "
              f"(draft the note, the sender performs it on LinkedIn, then "
              f"record it with send.py --manual)")
        for d in manual[:20]:
            print(f"  prospect {d['prospect_id']:>4}  step {d['step']} "
                  f"{d['step_name']:<12} {d['channel']:<16} {d['name']}"
                  f"  [{d['sender_id']}]")
        if len(manual) > 20:
            print(f"  ... and {len(manual) - 20} more")

    if appr.get("pending"):
        print(f"\nAPPROVAL QUEUE: {appr['pending']} draft(s) awaiting the "
              f"operator (dashboard or queue.py). None of them can send "
              f"until decided.")
    if appr.get("approved"):
        print(f"APPROVED AND READY: {appr['approved']} draft(s) cleared for "
              f"send.py within today's caps.")

    if deferred:
        print(f"\nDEFERRED: {len(deferred)}")
        seen_reasons = {}
        for d in deferred:
            seen_reasons.setdefault(d["why"], 0)
            seen_reasons[d["why"]] += 1
        for why, n in seen_reasons.items():
            print(f"  {n:>3}  {why}")

    print(f"\nRemaining budget: " +
          ", ".join(f"{k}={v}" for k, v in budget.items()) +
          "  |  LinkedIn invites: " +
          ", ".join(f"{k}={v}" for k, v in li_budget.items()))
    print("\nNothing was sent. Draft with brief.py, then send each through send.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
