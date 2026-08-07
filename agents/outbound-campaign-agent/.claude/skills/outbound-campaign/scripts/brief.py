#!/usr/bin/env python3
"""Assemble everything the agent needs to draft one message. Writes no copy.

  uv run --with pyyaml brief.py --prospect 12 [--step 0] [--json]

Drafting is the one step in this motion that a script must not do. A template
that generates the sentence produces the same sentence for everyone, which is
the failure mode the whole personalization argument rests on. So this gathers
the raw material, states the constraints, and hands it to the agent to write.

What it gathers: the prospect record and why they qualified, the use case they
would plausibly own, the operator's voice samples, the exact copy rules the
linter will enforce, and the history of what has already been said to this
person. That last one matters most on follow-ups: a bump that repeats the
opener's angle is worse than no bump.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import config as cfgmod, db  # noqa: E402


def load_use_cases(cfg) -> list[dict]:
    p = ROOT / "positioning" / "use-cases.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as e:
        raise SystemExit(f"positioning/use-cases.json is not valid JSON: {e}")
    return data.get("use_cases", data) if isinstance(data, dict) else data


def rank_use_cases(cases: list[dict], prospect) -> list[dict]:
    """Cheap keyword overlap. Deliberately not clever: this narrows the field
    for the agent, it does not make the choice."""
    title = (prospect["title"] or "").casefold()
    industry = (prospect["industry"] or "").casefold()
    scored = []
    for c in cases:
        score = 0
        for role in c.get("personas", []) + c.get("roles", []):
            r = role.casefold()
            if r and (r in title or title in r):
                score += 3
        for ind in c.get("industries", []):
            i = ind.casefold()
            # "*" means the use case is horizontal and fits any industry.
            if i == "*" or (industry and (i in industry or industry in i)):
                score += 2
        for kw in c.get("keywords", []):
            if kw.casefold() in title or kw.casefold() in industry:
                score += 1
        if score:
            scored.append((score, c))
    scored.sort(key=lambda t: -t[0])
    return [c for _, c in scored[:3]]


def voice_samples() -> str:
    p = ROOT / "positioning" / "voice-samples.md"
    if not p.exists():
        return ""
    text = p.read_text().strip()
    # A file that is still the unfilled template is worse than an empty one,
    # because it reads as though voice was captured when it was not. The
    # template's sample slots are empty fenced blocks, so an unfilled copy has
    # nothing between any pair of fences.
    body = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith(">"))
    filled = [b.strip() for b in body.split("```")[1::2] if b.strip()]
    if not filled:
        return ""
    return text


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prospect", type=int, required=True)
    ap.add_argument("--step", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    p = conn.execute("SELECT * FROM prospects WHERE id = ?", (args.prospect,)).fetchone()
    if p is None:
        print(f"no prospect with id {args.prospect}", file=sys.stderr)
        return 1
    if db.has_replied(conn, args.prospect):
        print(f"prospect {args.prospect} has replied; the cadence is stopped. "
              f"Do not draft. The operator decides whether to re-engage.",
              file=sys.stderr)
        return 1

    steps = cfg.get("cadence.steps", []) or []
    if not 0 <= args.step < len(steps):
        print(f"step {args.step} out of range (0..{len(steps)-1})", file=sys.stderr)
        return 1
    step = steps[args.step]

    history = conn.execute(
        "SELECT step_index, channel, subject, body, sent_at FROM sends "
        "WHERE prospect_id = ? ORDER BY step_index", (args.prospect,)).fetchall()

    samples = voice_samples()
    cases = rank_use_cases(load_use_cases(cfg), p)

    # The link must belong to whoever is sending. The linter rejects a draft
    # that offers a colleague's calendar, so surface the right one up front.
    sender_id = p["sender_id"] or (cfg.senders[0].get("id") if cfg.senders else None)
    booking_link = next((s.get("calendar_link") for s in (cfg.senders or [])
                         if s.get("id") == sender_id), None)

    brief = {
        "prospect": {
            "id": p["id"], "name": p["name"], "first_name": p["first_name"],
            "title": p["title"], "company": p["company"],
            "company_domain": p["company_domain"], "industry": p["industry"],
            "employee_count": p["employee_count"], "linkedin_url": p["linkedin_url"],
            "icp_tier": p["icp_tier"], "buyer_tier": p["buyer_tier"],
            "qualified_because": p["icp_reason"],
        },
        "step": {"index": args.step, **step},
        "positioning": cfg.get("positioning", {}),
        "candidate_use_cases": cases,
        "voice": {
            "samples": samples,
            "notes": cfg.get("voice.notes", ""),
            "banned_phrases": cfg.get("voice.banned_phrases", []),
        },
        "constraints": {
            "max_words": cfg.get("message_standards.max_words"),
            "max_subject_chars": cfg.get("message_standards.max_subject_chars"),
            "cta": cfg.get("message_standards.cta", {}),
            "booking_link": booking_link,
            "brand": cfg.brand,
            "forbidden_names": list(cfg.forbidden_names or []),
            "no_em_dashes": True,
            "no_tracking": True,
            "signature": cfg.signature,
        },
        "already_said": [
            {"step": h["step_index"], "channel": h["channel"],
             "subject": h["subject"], "sent_at": h["sent_at"],
             "body": h["body"]} for h in history
        ],
    }

    if args.json:
        print(json.dumps(brief, indent=2, default=str))
        return 0

    b = brief["prospect"]
    print(f"DRAFTING BRIEF: prospect {b['id']}, cadence step {args.step} "
          f"({step.get('channel')}, {step.get('intent', '?')})\n")
    print(f"  {b['name']}, {b['title']}")
    print(f"  {b['company']} ({b['employee_count']} emp, {b['industry']})")
    print(f"  {b['linkedin_url'] or 'no LinkedIn on file'}")
    print(f"  qualified as {b['icp_tier']}/{b['buyer_tier']}: {b['qualified_because']}\n")

    print("POSITIONING")
    for k, v in (brief["positioning"] or {}).items():
        if isinstance(v, (str, int, float)):
            print(f"  {k}: {v}")
    print()

    print("CANDIDATE USE CASES (pick ONE they would plausibly own)")
    if cases:
        for c in cases:
            print(f"  - {c.get('name', '?')}")
            if c.get("overview"):
                print(f"      {c['overview']}")
            if c.get("spotlight"):
                print(f"      spotlight: {c['spotlight']}")
            if c.get("hours_saved_per_week"):
                print(f"      saves: {c['hours_saved_per_week']} hrs/week")
    else:
        print("  NONE MATCHED. Do not invent one and do not fall back to generic")
        print("  praise. Either add a use case to positioning/use-cases.json or")
        print("  tell the operator this prospect has no mapped workflow.")
    print()

    print("VOICE")
    if samples:
        print(f"  {len(samples.split())} words of real samples in "
              f"positioning/voice-samples.md. Read them before writing.")
    else:
        print("  NO SAMPLES. positioning/voice-samples.md is empty or still the")
        print("  template. Copy written without them reads like copy. Ask the")
        print("  operator for one to three emails they actually sent.")
    if brief["voice"]["notes"]:
        print(f"  notes: {brief['voice']['notes']}")
    if brief["voice"]["banned_phrases"]:
        print(f"  banned: {', '.join(brief['voice']['banned_phrases'])}")
    print()

    if history:
        print("ALREADY SAID TO THIS PERSON (do not repeat the angle)")
        for h in history:
            print(f"  step {h['step_index']} ({h['sent_at']}): {h['subject']}")
        print()

    c = brief["constraints"]
    print("CONSTRAINTS (the linter enforces these; a failing draft does not send)")
    print(f"  under {c['max_words']} words, subject under {c['max_subject_chars']} chars")
    print(f"  brand: {c['brand']}"
          + (f"  |  never write: {', '.join(c['forbidden_names'])}"
             if c['forbidden_names'] else ""))
    print(f"  single CTA: {c['cta'].get('type')} {c['cta'].get('url', '')}")
    if c["booking_link"]:
        print(f"  booking link for {sender_id}: {c['booking_link']}")
        print("    use this one only; another sender's link fails the linter")
    print("  no em dashes, no en dashes, no tracking pixels, no link wrappers")
    print("  short paragraphs, one blank line between them, never one dense block")
    return 0


if __name__ == "__main__":
    sys.exit(main())
