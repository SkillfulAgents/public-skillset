#!/usr/bin/env python3
"""The send gate. Every outbound message passes through here.

  uv run --with pyyaml send.py --prospect 12 --step 1 \
      --subject "..." --body-file draft.html [--sender alex] [--force-window]

Order of checks, all blocking:
  1. prospect exists
  2. do-not-touch gate (exit 8): never contact, for a reason unrelated to fit
  3. has a work email, has not replied, is not in a terminal state
  4. not already sent at this step (idempotent)
  5. copy passes the linter
  6. deliverability kill switch
  7. send window and per-sender daily cap
  8. per-company pacing

Do-not-touch runs first because there is no reason to lint copy, burn a cap
check, or read a draft for someone we must never contact. The block is logged
to `decisions` so it can be explained later.

Only then does it call the sender adapter, and it logs to `sends` BEFORE
reporting success. An unlogged send is a send that will be repeated.

LinkedIn steps have no automated executor, deliberately: automating LinkedIn
actions is against its terms and gets accounts restricted. They are MANUAL:
  1. run without --manual: the note is linted (300-char invite ceiling, banned
     phrases, forbidden names) and the invite cap is checked. Nothing is
     logged. Hand the note to the operator to send on LinkedIn themselves.
  2. operator confirms they sent it, re-run with --manual: the touch is
     recorded so the cadence, caps, and reporting see it.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters, caps, config as cfgmod, db, gates, linter  # noqa: E402


def refuse(msg: str, code: int = 1) -> int:
    print(f"REFUSED: {msg}", file=sys.stderr)
    return code


def with_signature(body: str, cfg) -> str:
    """Append the configured signature to an authored body.

    Composed here rather than in each sender adapter so every provider sends
    byte-identical copy, and so the linter still sees the authored body only.
    Skipped when the author already pasted the block in, which is the common
    way a signature gets duplicated.
    """
    sig_html = cfg.signature_html
    if not sig_html:
        return body
    first_line = (cfg.signature.splitlines() or [""])[0].strip()
    if first_line and first_line in body:
        return body
    return f"{body.rstrip()}\n{sig_html}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prospect", type=int, required=True)
    ap.add_argument("--step", type=int, required=True,
                    help="index into cadence.steps")
    ap.add_argument("--subject", default="",
                    help="required for email steps; LinkedIn has no subject")
    ap.add_argument("--body-file", required=True,
                    help="file containing the message body as inner HTML")
    ap.add_argument("--sender", default=None)
    ap.add_argument("--manual", action="store_true",
                    help="record a manual (non-email) touch the operator has "
                         "already performed themselves")
    ap.add_argument("--variant", default=None)
    ap.add_argument("--confidence", type=float, default=None)
    ap.add_argument("--approved", action="store_true",
                    help="operator has approved this specific draft")
    ap.add_argument("--force-window", action="store_true",
                    help="bypass the send-window check only (never the caps)")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    p = conn.execute("SELECT * FROM prospects WHERE id = ?", (args.prospect,)).fetchone()
    if p is None:
        return refuse(f"no prospect with id {args.prospect}")

    block = gates.check_do_not_touch(cfg, p)
    if block:
        with db.transaction(conn):
            db.log_decision(conn, "do_not_touch", "block", block.reason,
                            layer=block.matched, prospect_id=args.prospect)
        return refuse(f"do-not-touch [{block.matched}]: {block.reason}", 8)

    if p["status"] in db.TERMINAL_STATUSES:
        return refuse(f"prospect {args.prospect} status is {p['status']!r}")
    if db.has_replied(conn, args.prospect):
        return refuse(f"prospect {args.prospect} has replied; cadence is stopped")

    steps = cfg.get("cadence.steps", []) or []
    if not 0 <= args.step < len(steps):
        return refuse(f"step {args.step} out of range (0..{len(steps)-1})")
    step = steps[args.step]
    channel = step.get("channel", "email")

    # Channel decides which contact field is load-bearing: an email step needs
    # a work email, a LinkedIn step needs the profile, and neither should block
    # on the other's field.
    if channel == "email" and not p["email"]:
        return refuse(f"prospect {args.prospect} has no work email")
    if channel != "email" and not p["linkedin_url"]:
        return refuse(f"prospect {args.prospect} has no linkedin_url for a "
                      f"{channel} step")
    if channel == "email" and not args.subject.strip():
        return refuse("--subject is required for email steps")

    already = conn.execute(
        "SELECT id, sent_at FROM sends WHERE prospect_id = ? AND step_index = ? "
        "AND channel = ?", (args.prospect, args.step, channel)).fetchone()
    if already:
        return refuse(f"step {args.step} already sent at {already['sent_at']}")

    body = pathlib.Path(args.body_file).read_text()

    # The approval queue is binding. A draft staged for review sends only
    # after a human approved it, and only as the exact copy they approved.
    draft = db.draft_for(conn, args.prospect, args.step, channel)
    approved = args.approved
    if draft is not None:
        if draft["status"] == "pending":
            return refuse(f"draft #{draft['id']} is awaiting operator approval "
                          f"(dashboard queue or queue.py approve)", 4)
        if draft["status"] == "rejected":
            why = draft["decision_reason"] or "no reason recorded"
            return refuse(f"draft #{draft['id']} was rejected by the operator "
                          f"({why}); revise and re-stage it", 4)
        if draft["status"] == "approved":
            if (draft["body"] or "").strip() != body.strip() or \
                    (draft["subject"] or "") != (args.subject or ""):
                return refuse(f"copy differs from what the operator approved in "
                              f"draft #{draft['id']}; re-stage the revised copy", 4)
            approved = True

    sender_id = args.sender or p["sender_id"] or (
        cfg.senders[0].get("id") if cfg.senders else None)
    if not sender_id:
        return refuse("no sender configured")

    lint = linter.lint(args.subject, body, cfg, signature=cfg.signature,
                       sender_id=sender_id, channel=channel)
    if not lint.ok:
        print(f"copy failed the linter ({lint.stats}):", file=sys.stderr)
        print(lint.report(), file=sys.stderr)
        return refuse("fix the copy; the linter is a gate, not a suggestion", 3)
    if lint.warnings:
        print("linter warnings:")
        print(lint.report())

    min_conf = float(cfg.get("message_standards.min_confidence_to_autosend", 0.7))
    if args.confidence is not None and args.confidence < min_conf and not approved:
        return refuse(
            f"draft confidence {args.confidence:.2f} is below {min_conf:.2f}; "
            f"surface it to the operator and re-run with --approved", 4)

    pacing = caps.check_company_pacing(cfg, conn, p["company_domain"] or "",
                                       exclude_prospect_id=args.prospect)
    if not pacing.allowed:
        return refuse(pacing.reason, 7)

    # -- manual channels (LinkedIn): two phases, nothing automated -----------
    if channel != "email":
        if channel == "linkedin_invite":
            gate = caps.check_linkedin_invite(cfg, conn, sender_id)
            if not gate.allowed:
                return refuse(gate.reason, 6)

        if not args.manual:
            print(f"MANUAL STEP: {channel} for prospect {args.prospect} "
                  f"({p['name']}, {p['linkedin_url']})")
            print(f"  The note passes all checks"
                  + (f" ({lint.stats.get('chars', '?')} chars)"
                     if channel == "linkedin_invite" else "") + ".")
            print(f"  1. {sender_id} sends it on LinkedIn themselves "
                  f"(no automation; LinkedIn restricts accounts for it)")
            print(f"  2. once sent, record it: re-run this command with --manual")
            print("  NOTHING WAS LOGGED.")
            return 0

        with db.transaction(conn):
            conn.execute(
                "INSERT INTO sends (prospect_id, step_index, channel, sender_id,"
                " provider, subject, body, variant, confidence)"
                " VALUES (?,?,?,?,?,?,?,?,?)",
                (args.prospect, args.step, channel, sender_id, "manual",
                 args.subject or None, body, args.variant, args.confidence))
            conn.execute("UPDATE prospects SET status = ? WHERE id = ?",
                         ("contacted", args.prospect))
            if draft is not None:
                conn.execute("UPDATE drafts SET status = 'sent' WHERE id = ?",
                             (draft["id"],))
            db.log_decision(conn, "send", "manual",
                            f"step {args.step} {channel} recorded as done",
                            layer="manual", prospect_id=args.prospect)
        print(f"recorded: prospect {args.prospect} step {args.step} "
              f"({channel}) done manually by {sender_id}")
        if channel == "linkedin_invite":
            left = caps.check_linkedin_invite(cfg, conn, sender_id).remaining
            print(f"  {left} invite(s) left today for {sender_id}")
        return 0

    # -- email: automated through the sender adapter -------------------------
    health = caps.check_deliverability(cfg, conn)
    if not health.allowed:
        return refuse(health.reason, 5)
    if health.reason.startswith("WARN"):
        print(f"  {health.reason}")

    gate = caps.check_send(cfg, conn, sender_id)
    if not gate.allowed:
        window_only = gate.reason.startswith("outside send window")
        if not (window_only and args.force_window):
            return refuse(gate.reason, 6)
        print(f"  window override: {gate.reason}")

    ad = adapters.load(cfg, "sender")
    if ad is None:
        return refuse("adapters.sender is 'none'")

    sent_body = with_signature(body, cfg)

    message = {
        "to": p["email"],
        "to_name": p["name"],
        "subject": args.subject,
        "body_html": sent_body,
        "from_email": cfg.sender(sender_id).get("email"),
        "from_name": cfg.sender(sender_id).get("display_name") or cfg.get("operator.name"),
        "sender_id": sender_id,
        "prospect_id": args.prospect,
        "step_index": args.step,
        "channel": channel,
    }

    result = ad.send(adapters.context(cfg, ad), message) or {}

    with db.transaction(conn):
        conn.execute(
            "INSERT INTO sends (prospect_id, step_index, channel, sender_id, provider,"
            " provider_message_id, provider_thread_id, subject, body, variant, confidence)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (args.prospect, args.step, channel, sender_id,
             result.get("provider", ad.name), result.get("message_id"),
             result.get("thread_id"), args.subject, sent_body, args.variant,
             args.confidence),
        )
        conn.execute("UPDATE prospects SET status = ? WHERE id = ?",
                     ("contacted", args.prospect))
        if draft is not None:
            conn.execute("UPDATE drafts SET status = 'sent' WHERE id = ?",
                         (draft["id"],))
        db.log_decision(conn, "send", result.get("status", "sent"),
                        f"step {args.step} via {ad.name}",
                        layer=ad.name, prospect_id=args.prospect)

    status = result.get("status", "sent")
    remaining = caps.check_send(cfg, conn, sender_id).remaining
    print(f"{status}: prospect {args.prospect} step {args.step} "
          f"({channel}) via {ad.name} as {sender_id}")
    print(f"  to {p['email']}  |  {remaining} send(s) left today for {sender_id}")
    if status == "dry_run":
        print("  NOTHING WAS SENT (adapters.sender is 'dryrun')")
    return 0


if __name__ == "__main__":
    sys.exit(main())
