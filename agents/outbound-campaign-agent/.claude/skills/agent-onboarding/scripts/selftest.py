#!/usr/bin/env python3
"""Walk fixture prospects through the entire motion. Sends nothing.

  uv run --with pyyaml selftest.py [--keep]

Exercises: config load, adapter resolution, identity matching, ICP
qualification, suppression fail-closed behaviour, cap enforcement, the copy
linter, and the DB write path. Runs against a THROWAWAY database so it can
never touch real campaign state.

A pass means the wiring is correct. It says nothing about whether the copy or
the ICP are any good; only a human can judge those.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters, caps, config as cfgmod, db, icp, identity, linter  # noqa: E402

PASS, FAIL, SKIP = "PASS", "FAIL", "SKIP"
results: list[tuple[str, str, str]] = []


def check(name: str, fn):
    try:
        ok, detail = fn()
        status = ok if isinstance(ok, str) else (PASS if ok else FAIL)
        results.append((status, name, detail))
    except Exception as e:
        results.append((FAIL, name, f"{type(e).__name__}: {e}"))


FIXTURES = [
    {"name": "Dana Whitfield", "title": "Head of Operations",
     "company": "Kestrel Freight", "company_domain": "kestrelfreight.example",
     "email": "dana@kestrelfreight.example", "employee_count": 80,
     "country": "US", "linkedin_url": "https://linkedin.com/in/dana-whitfield",
     "signals": ["founder_led", "has_ops_function"]},
    {"name": "Priya Raman", "title": "Chief Executive Officer",
     "company": "Vantage Health", "company_domain": "vantagehealth.example",
     "email": "priya@vantagehealth.example", "employee_count": 4200,
     "country": "US", "linkedin_url": "https://linkedin.com/in/priya-raman"},
    {"name": "Tom Ek", "title": "Owner", "company": "Ek Plumbing",
     "company_domain": "ekplumbing.example", "email": "tom@ekplumbing.example",
     "employee_count": 6, "country": "US"},
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="keep the temp database")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    print("Outbound self-test (nothing will be sent)\n")

    # "Did the template install correctly" is a different question from "is my
    # config right", and a fresh importer asks the first one first. Falling back
    # to the example lets the wiring be verified before the interview happens.
    pre_onboarding = False
    try:
        cfg = cfgmod.load(args.config)
    except Exception as e:
        if args.config or not cfgmod.EXAMPLE_CONFIG.exists():
            print(f"FAIL  config: {e}")
            return 1
        pre_onboarding = True
        cfg = cfgmod.load(cfgmod.EXAMPLE_CONFIG)
    print(f"  config   {cfg.config_path.name}  ({cfg.get('company.name')})")
    if pre_onboarding:
        print("  NOTE: no config/outbound.yaml yet, so this is testing the template's")
        print("        wiring against the shipped example. It says nothing about your")
        print("        ICP or your copy. Run the agent-onboarding skill next.")

    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix="outbound-selftest-"))
    conn = db.init(tmpdir / "selftest.db")
    print(f"  database {tmpdir/'selftest.db'} (throwaway)\n")

    # -- config surface ---------------------------------------------------
    check("config: brand resolves", lambda: (bool(cfg.brand), f"brand={cfg.brand!r}"))
    check("config: timezone valid", lambda: (cfg.now() is not None, str(cfg.tz)))
    check("config: senders present",
          lambda: (len(cfg.senders) > 0, f"{len(cfg.senders)} sender(s), "
                                         f"capacity {cfg.total_daily_capacity}/day"))
    check("config: signature renders",
          lambda: (bool(cfg.signature), repr(cfg.signature[:60])))

    # -- adapters ----------------------------------------------------------
    for slot in ("sourcing", "sender", "crm"):
        check(f"adapter: {slot} resolves", lambda s=slot: _resolve(cfg, s))
    for slot in ("enrichment", "suppression"):
        check(f"adapter: {slot} chain resolves", lambda s=slot: _resolve_chain(cfg, s))

    # -- identity ----------------------------------------------------------
    check("identity: rejects a same-company different-person match", lambda: (
        not identity.verify_match(
            {"name": "Nathalia Silva", "linkedin_url": "linkedin.com/in/nathalia-silva"},
            {"name": "Nathalia Costa", "linkedin_url": "linkedin.com/in/nathalia-costa"},
        )[0], "coworker swap blocked"))
    check("identity: accepts a nickname match", lambda: (
        identity.names_compatible("Bob Smith", "Robert Smith"), "Bob == Robert"))
    check("identity: never overwrites a seed value", lambda: (
        "title" not in identity.merge_enrichment(
            {"title": "Head of Ops"}, {"title": "Intern"}), "seed title preserved"))

    # -- ICP ---------------------------------------------------------------
    verdicts = [(f, icp.evaluate(cfg, f)) for f in FIXTURES]
    check("icp: evaluates every fixture with a reason",
          lambda: (all(v.reason for _, v in verdicts),
                   "; ".join(f"{f['name']}={'Y' if v else 'N'}({v.tier})"
                             for f, v in verdicts)))
    check("icp: rejects out-of-band size", lambda: (
        any(not v and "employee" in v.reason.lower() or
            (not v and "warm-intro" in v.reason) for _, v in verdicts),
        next((v.reason for _, v in verdicts if not v), "no rejection produced")))

    # -- suppression fail-closed ------------------------------------------
    check("suppression: fail_closed is enabled", lambda: (
        cfg.get("suppression.fail_closed") is True,
        f"fail_closed={cfg.get('suppression.fail_closed')}"))

    # -- caps --------------------------------------------------------------
    sid = cfg.senders[0]["id"] if cfg.senders else None
    if sid:
        check("caps: enforces the daily ceiling", lambda: _cap_test(cfg, conn, sid))
        check("caps: governor catches stacked campaign rates",
              lambda: _governor_test(cfg, sid))
        check("caps: send window is evaluated", lambda: (
            isinstance(cfg.in_send_window()[0], bool), cfg.in_send_window()[1]))
        check("caps: linkedin invite cap is enforced",
              lambda: _li_cap_test(cfg, conn, sid))

    # -- linter ------------------------------------------------------------
    check("linter: blocks an em dash", lambda: _lint_blocks(
        cfg, "Quick note", "<p>We help teams — a lot — every day. Worth a look?</p>",
        "em dash"))
    check("linter: blocks a tracking pixel", lambda: _lint_blocks(
        cfg, "Quick note",
        '<p>Hello there, worth a look?</p><img src="http://t/x.gif" width="1" height="1">',
        "pixel"))
    check("linter: blocks an unfilled placeholder", lambda: _lint_blocks(
        cfg, "Quick note", "<p>Hi {first_name}, worth a look?</p>", "placeholder"))
    check("linter: blocks a forbidden brand name", lambda: _forbidden_test(cfg))
    check("linter: passes clean copy", lambda: _clean_test(cfg))
    check("linter: blocks another sender's booking link",
          lambda: _wrong_calendar_test(cfg))
    check("linter: blocks a linkedin invite over 300 chars", lambda: _lint_blocks(
        cfg, "", "<p>" + "This note runs long. " * 20 + "</p>", "truncates",
        channel="linkedin_invite"))
    check("linter: linkedin invite skips email-shaped rules", lambda: _li_clean_test(cfg))

    # -- interview spec ------------------------------------------------------
    check("interview: interview.yaml is well-formed", _interview_test)
    check("interview: vendor-knowledge.yaml is well-formed", _vendor_knowledge_test)

    # -- db write path -----------------------------------------------------
    check("db: upsert is idempotent", lambda: _upsert_test(conn))
    check("db: decisions are auditable", lambda: _decision_test(conn))

    # -- approval queue ------------------------------------------------------
    check("queue: approved copy cannot be silently replaced",
          lambda: _queue_test(conn))

    # -- report ------------------------------------------------------------
    conn.close()
    if not args.keep:
        import shutil
        shutil.rmtree(tmpdir, ignore_errors=True)

    width = max(len(n) for _, n, _ in results) + 2
    for status, name, detail in results:
        print(f"  {status:<5} {name:<{width}} {detail}")

    failed = [r for r in results if r[0] == FAIL]
    skipped = [r for r in results if r[0] == SKIP]
    print()
    if failed:
        print(f"FAILED: {len(failed)} of {len(results)} checks")
        print("\nThe motion is not correctly wired. Fix these before drafting.")
        return 1
    print(f"OK: {len(results) - len(skipped)} passed, {len(skipped)} skipped")
    if UNPROVISIONED:
        print("\nNot provisioned yet (wiring is fine, credentials are missing):")
        for u in UNPROVISIONED:
            print(f"  - {u}")
        print("  Add these to .env before a live run. Ask the operator; never invent one.")
    print("\nWiring is correct. This does NOT validate your ICP or your copy.")
    if cfg.get("adapters.sender") == "dryrun":
        print("Sender is 'dryrun': you can safely run a full batch end to end now.")
    return 0


_INVENTORY = adapters.discover()
UNPROVISIONED: list[str] = []


def _missing_env(slot: str, name: str) -> list[str]:
    for meta in _INVENTORY.get(slot, []):
        if meta["name"] == name:
            return [v for v in meta.get("requires_env", []) if v not in __import__("os").environ]
    return []


def _is_scaffold(slot: str, name: str) -> bool:
    return any(m["name"] == name and m.get("scaffold")
               for m in _INVENTORY.get(slot, []))


def _resolve_one(cfg, slot, name):
    """(status, detail). A missing vendor secret is SKIP, not FAIL: the wiring
    is sound, the workspace is simply not provisioned yet. A scaffold is SKIP
    for the same reason, and reporting it PASS would tell the operator a stub
    that raises on every call is ready."""
    if _is_scaffold(slot, name):
        UNPROVISIONED.append(
            f"{slot}:{name} is a scaffold: implement adapters/{slot}/{name}.py")
        return SKIP, f"{name} scaffolded, not implemented"
    missing = _missing_env(slot, name)
    if missing:
        UNPROVISIONED.append(f"{slot}:{name} needs {', '.join('$' + m for m in missing)}")
        return SKIP, f"{name} not provisioned: {', '.join('$' + m for m in missing)}"
    adapters.load(cfg, slot, name)
    return PASS, name


def _resolve(cfg, slot):
    name = cfg.get(f"adapters.{slot}")
    if name in (None, "none"):
        return PASS, "none (disabled)"
    return _resolve_one(cfg, slot, name)


def _resolve_chain(cfg, slot):
    configured = cfg.get(f"adapters.{slot}")
    configured = configured if isinstance(configured, list) else [configured]
    real = [c for c in configured if c not in (None, "none")]
    if not real:
        return PASS, "none (disabled)"
    statuses = [_resolve_one(cfg, slot, n) for n in real]
    worst = FAIL if FAIL in [s for s, _ in statuses] else (
        SKIP if SKIP in [s for s, _ in statuses] else PASS)
    return worst, " then ".join(d for _, d in statuses)


def _cap_test(cfg, conn, sid):
    cap = cfg.effective_cap(sid)
    pid = db.upsert_prospect(conn, {"linkedin_url": "https://linkedin.com/in/cap-test",
                                    "name": "Cap Test", "email": "cap@test.example"})
    for i in range(cap):
        conn.execute("INSERT INTO sends (prospect_id, step_index, channel, sender_id,"
                     " subject, body) VALUES (?,?,?,?,?,?)",
                     (pid, i, "email", sid, "s", "b"))
    conn.commit()
    when = _next_send_moment(cfg)
    d = caps.check_send(cfg, conn, sid, when=when)
    conn.execute("DELETE FROM sends WHERE prospect_id = ?", (pid,))
    conn.execute("DELETE FROM prospects WHERE id = ?", (pid,))
    conn.commit()
    return (not d.allowed and "cap" in d.reason), f"at {cap}/{cap}: {d.reason}"


def _governor_test(cfg, sid):
    cap = cfg.effective_cap(sid)
    planned = {"campaign-a": {sid: cap}, "campaign-b": {sid: cap}}
    report = caps.audit_planned_rates(cfg, planned)
    return (not report["ok"] and bool(report["rebalance_plan"])), (
        f"2 campaigns x {cap}/day -> breach detected, rebalanced to "
        f"{[v.get(sid) for v in report['rebalance_plan'].values()]}")


def _next_send_moment(cfg) -> dt.datetime:
    """First moment inside the configured send window, so cap tests are
    not masked by a window refusal."""
    now = cfg.now()
    window = str(cfg.get("limits.send_window_local", "09:00-11:00"))
    hh, mm = window.split("-")[0].split(":")
    for delta in range(0, 8):
        cand = (now + dt.timedelta(days=delta)).replace(
            hour=int(hh), minute=int(mm) + 1, second=0, microsecond=0)
        if cfg.in_send_window(cand)[0]:
            return cand
    return now


def _lint_blocks(cfg, subject, body, kind, channel="email"):
    r = linter.lint(subject, body, cfg, channel=channel)
    return (not r.ok), f"{kind} rejected: {r.errors[0][:70] if r.errors else 'NOT BLOCKED'}"


def _li_clean_test(cfg):
    """A good invite note has no subject, no CTA link, no paragraphs. Under
    email rules that is three errors; under invite rules it is clean."""
    body = "<p>Your dispatch team caught my eye. Building something for exactly that handoff pain.</p>"
    r = linter.lint("", body, cfg, channel="linkedin_invite")
    return r.ok, (f"invite note accepted ({r.stats.get('chars')} chars)"
                  if r.ok else f"REJECTED: {r.errors}")


def _interview_test():
    """The interview is data; malformed data silently degrades to prose
    questions, which is the exact failure the file exists to prevent."""
    import yaml
    path = ROOT / ".claude" / "skills" / "agent-onboarding" / "interview.yaml"
    if not path.exists():
        return FAIL, "interview.yaml is missing"
    spec = yaml.safe_load(path.read_text())
    sections = spec.get("sections") or []
    if not sections:
        return FAIL, "no sections"
    problems = []
    n_q = 0
    for s in sections:
        if not s.get("id") or not s.get("questions"):
            problems.append(f"section {s.get('id', '?')}: missing id or questions")
            continue
        for q in s["questions"]:
            n_q += 1
            t = q.get("type")
            if not q.get("key") or not q.get("ask") or t not in ("choice", "multi", "text"):
                problems.append(f"{s['id']}/{q.get('key', '?')}: bad key/ask/type")
            if t in ("choice", "multi"):
                opts = q.get("options")
                if opts is None and not q.get("options_from"):
                    problems.append(f"{s['id']}/{q['key']}: {t} with no options")
                elif opts is not None and not 2 <= len(opts) <= 4:
                    problems.append(f"{s['id']}/{q['key']}: {len(opts)} options "
                                    f"(AskUserQuestion takes 2 to 4)")
    if problems:
        return FAIL, "; ".join(problems[:3])
    return PASS, f"{len(sections)} sections, {n_q} questions, all typed"


def _vendor_knowledge_test():
    import yaml
    path = ROOT / "adapters" / "vendor-knowledge.yaml"
    if not path.exists():
        return FAIL, "vendor-knowledge.yaml is missing"
    kb = yaml.safe_load(path.read_text())
    if not kb.get("as_of"):
        return FAIL, "no as_of stamp; the trust/verify split depends on it"
    problems, n = [], 0
    for cat, entries in kb.items():
        if cat == "as_of":
            continue
        for e in entries or []:
            n += 1
            if not e.get("name") or not e.get("is"):
                problems.append(f"{cat}: entry missing name or is")
    if problems:
        return FAIL, "; ".join(problems[:3])
    return PASS, f"{n} vendors across {len(kb) - 1} categories, as of {kb['as_of']}"


def _li_cap_test(cfg, conn, sid):
    cap = int(cfg.sender(sid).get("daily_linkedin_invite_cap", 20) or 0)
    if cap <= 0:
        return True, "invite cap is 0 (nothing to test)"
    pid = db.upsert_prospect(conn, {"linkedin_url": "https://linkedin.com/in/li-cap-test",
                                    "name": "LI Cap Test", "email": "licap@test.example"})
    for i in range(cap):
        conn.execute("INSERT INTO sends (prospect_id, step_index, channel, sender_id,"
                     " provider, body) VALUES (?,?,?,?,?,?)",
                     (pid, i, "linkedin_invite", sid, "manual", "b"))
    conn.commit()
    d = caps.check_linkedin_invite(cfg, conn, sid)
    conn.execute("DELETE FROM sends WHERE prospect_id = ?", (pid,))
    conn.execute("DELETE FROM prospects WHERE id = ?", (pid,))
    conn.commit()
    return (not d.allowed and "invite cap" in d.reason), f"at {cap}/{cap}: {d.reason}"


def _forbidden_test(cfg):
    names = list(cfg.forbidden_names or [])
    if not names:
        return True, "no forbidden names configured (nothing to test)"
    r = linter.lint("Quick note", f"<p>We use {names[0]} daily. Worth a look?</p>", cfg)
    return (not r.ok), f"{names[0]!r} rejected"


def _clean_test(cfg):
    body = (f"<p>Saw you run ops for a growing team.</p>"
            f"<p>Teams your size lose real hours on cross system handoffs.</p>"
            f"<p>Worth a look?</p><p>{cfg.signature}</p>")
    r = linter.lint("Ops handoffs", body, cfg, signature=cfg.signature)
    return r.ok, (f"clean copy accepted ({r.stats.get('words')} words)"
                  if r.ok else f"REJECTED: {r.errors}")


def _wrong_calendar_test(cfg):
    """Offering a colleague's booking link is only discoverable by the prospect
    after they have already committed to a slot, so the linter must catch it."""
    linked = [s for s in (cfg.senders or []) if s.get("calendar_link")]
    if len(linked) < 2:
        return SKIP, "needs two senders with calendar_link to test"
    me, them = linked[0], linked[1]
    body = (f"<p>Saw you run ops for a growing team.</p>"
            f"<p>Teams your size lose real hours on cross system handoffs.</p>"
            f"<p>Grab a slot: {them['calendar_link']}</p>")
    r = linter.lint("Ops handoffs", body, cfg, signature=cfg.signature,
                    sender_id=me.get("id"))
    hit = any("booking link" in e for e in r.errors)
    return hit, (f"{them['id']}'s link rejected when sending as {me['id']}"
                 if hit else f"NOT CAUGHT: {r.errors}")


def _upsert_test(conn):
    row = {"linkedin_url": "https://linkedin.com/in/idem-test", "name": "Idem Test",
           "email": "idem@test.example", "title": "Head of Ops"}
    a = db.upsert_prospect(conn, row)
    b = db.upsert_prospect(conn, {**row, "title": "Should Not Overwrite"})
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM prospects WHERE linkedin_url = ?",
                     (row["linkedin_url"],)).fetchone()[0]
    return (a == b and n == 1), f"same id {a}, {n} row"


def _decision_test(conn):
    db.log_decision(conn, "selftest", "drop", "fixture reason", layer="local")
    conn.commit()
    r = conn.execute("SELECT stage, decision, reason, layer FROM decisions "
                     "ORDER BY id DESC LIMIT 1").fetchone()
    return (r["reason"] == "fixture reason"), f"{r['stage']}/{r['decision']} logged"


def _queue_test(conn):
    """Stage, approve, then try to re-stage: the approved copy must survive.

    Swapping copy under an approval a human already gave is the queue's one
    unforgivable failure, so it is the thing the selftest exercises.
    """
    pid = db.upsert_prospect(conn, {"name": "Queue Fixture", "company": "QT Co",
                                    "email": "qf@qtco.example", "status": "new"})
    did = db.stage_draft(conn, {"prospect_id": pid, "step_index": 9,
                                "subject": "v1", "body": "<p>v1</p>"})
    row = db.draft_for(conn, pid, 9)
    if row["status"] != "pending":
        return FAIL, f"fresh draft is {row['status']}, expected pending"
    # Re-staging a pending draft replaces it (copy was revised): allowed.
    did = db.stage_draft(conn, {"prospect_id": pid, "step_index": 9,
                                "subject": "v2", "body": "<p>v2</p>"})
    conn.execute("UPDATE drafts SET status = 'approved' WHERE id = ?", (did,))
    conn.commit()
    try:
        db.stage_draft(conn, {"prospect_id": pid, "step_index": 9,
                              "subject": "v3", "body": "<p>v3</p>"})
        return FAIL, "re-staging over an approved draft was allowed"
    except ValueError:
        pass
    row = db.draft_for(conn, pid, 9)
    return (row["subject"] == "v2" and row["status"] == "approved",
            "approved copy preserved; pending re-stage allowed")


if __name__ == "__main__":
    sys.exit(main())
