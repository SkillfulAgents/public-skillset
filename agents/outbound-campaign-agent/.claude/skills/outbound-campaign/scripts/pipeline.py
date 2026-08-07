#!/usr/bin/env python3
"""Intake: source -> enrich -> qualify -> suppress -> store.

  uv run --with pyyaml pipeline.py [--limit N] [--dry-run] [--campaign KEY]

Every prospect that enters the system passes through this in order. Each stage
writes a row to the `decisions` table, so "why was this person dropped" is
answerable weeks later without rerunning anything.

Suppression is fail-closed: if a suppression source raises, the run HALTS
before storing anything. Contacting a current customer as a cold prospect is a
worse outcome than a delayed batch.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters, caps, config as cfgmod, db, gates, icp, identity  # noqa: E402


class Halt(RuntimeError):
    """Fail-closed stop. Nothing further is stored."""


def norm(row: dict) -> dict:
    """Canonicalize a sourced row before any gate looks at it."""
    out = dict(row)

    if out.get("linkedin_url"):
        slug = identity.linkedin_slug(out["linkedin_url"])
        out["linkedin_url"] = f"https://linkedin.com/in/{slug}" if slug else None

    if not out.get("first_name") and out.get("name"):
        first, last = identity.split_name(out["name"])
        out["first_name"], out["last_name"] = first, last
    if not out.get("name"):
        joined = f"{out.get('first_name','')} {out.get('last_name','')}".strip()
        out["name"] = joined or None

    if not out.get("company_domain") and out.get("email"):
        dom = identity.email_domain(out["email"])
        if dom and not identity.is_personal_email(out["email"]):
            out["company_domain"] = dom

    if out.get("email") and identity.is_personal_email(out["email"]):
        out.setdefault("personal_email", out["email"])
        out["email"] = None

    return out


def enrich_row(cfg, row: dict, chain: list, conn) -> dict:
    """Run the waterfall. Stops at the first adapter that yields a work email."""
    for ad in chain:
        if row.get("email"):
            break
        ctx = adapters.context(cfg, ad)
        try:
            result = ad.enrich(ctx, row) or {}
        except Exception as e:
            db.log_decision(conn, "enrich", "error", f"{ad.name}: {e}",
                            layer=ad.name, ref=row.get("linkedin_url", ""))
            continue

        meta = result.pop("_meta", {}) if isinstance(result, dict) else {}
        if meta and not meta.get("accepted", True):
            db.log_decision(conn, "enrich", "rejected", meta.get("reason", ""),
                            layer=ad.name, ref=row.get("linkedin_url", ""))
            continue
        if result:
            row.update(result)
            db.log_decision(conn, "enrich", "hit", f"fields={sorted(result)}",
                            layer=ad.name, ref=row.get("linkedin_url", ""))
    return row


def check_suppression(cfg, row: dict, chain: list, conn) -> tuple[bool, str, str]:
    """(suppressed, reason, layer). Raises Halt if a source is unavailable."""
    fail_closed = bool(cfg.get("suppression.fail_closed", True))
    for ad in chain:
        ctx = adapters.context(cfg, ad)
        try:
            hit, reason = ad.is_suppressed(ctx, row)
        except Exception as e:
            if fail_closed:
                raise Halt(
                    f"suppression layer {ad.name!r} is unavailable ({e}). "
                    f"suppression.fail_closed is true, so the run stops here rather "
                    f"than risk contacting someone who already engaged."
                ) from e
            db.log_decision(conn, "suppress", "error", f"{ad.name}: {e}", layer=ad.name)
            continue
        if hit:
            return True, reason, ad.name
    return False, "", ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--campaign", default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="evaluate every gate but write no prospects")
    ap.add_argument("--config", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cfg = cfgmod.load(args.config)
    conn = db.init(cfg.path("adapter_config.sqlite.path", "data/campaigns.db"))

    src = adapters.load(cfg, "sourcing")
    if src is None:
        print("adapters.sourcing is 'none'; nothing to intake.", file=sys.stderr)
        return 0
    enrich_chain = adapters.load_chain(cfg, "enrichment")
    supp_chain = adapters.load_chain(cfg, "suppression")

    intake = caps.check_intake(cfg, conn)
    budget = min(args.limit, intake.remaining if intake.allowed else 0)
    if not intake.allowed:
        print(f"intake blocked: {intake.reason}", file=sys.stderr)
        return 1

    rows = src.fetch(adapters.context(cfg, src), budget) or []
    stats = {"sourced": len(rows), "stored": 0, "disqualified": 0,
             "suppressed": 0, "no_contact": 0, "duplicate": 0,
             "do_not_touch": 0}
    dropped: list[dict] = []

    with db.transaction(conn):
        for raw in rows:
            if stats["stored"] >= budget:
                break
            row = norm(raw)
            ref = row.get("linkedin_url") or row.get("email") or row.get("name") or "?"

            # Runs before suppression and before enrichment: there is no point
            # spending an enrichment credit on someone we may never contact.
            # send.py gates again, because a prospect can be added to the list
            # after intake.
            block = gates.check_do_not_touch(cfg, row)
            if block:
                stats["do_not_touch"] += 1
                dropped.append({"ref": ref, "stage": "do_not_touch",
                                "reason": block.reason, "layer": block.matched})
                db.log_decision(conn, "do_not_touch", "drop", block.reason,
                                layer=block.matched, ref=ref)
                continue

            suppressed, reason, layer = check_suppression(cfg, row, supp_chain, conn)
            if suppressed:
                stats["suppressed"] += 1
                dropped.append({"ref": ref, "stage": "suppress", "reason": reason,
                                "layer": layer})
                db.log_decision(conn, "suppress", "drop", reason, layer=layer, ref=ref)
                continue

            row = enrich_row(cfg, row, enrich_chain, conn)

            verdict = icp.evaluate(cfg, row)
            if not verdict.qualified:
                stats["disqualified"] += 1
                dropped.append({"ref": ref, "stage": "icp", "reason": verdict.reason})
                db.log_decision(conn, "icp", "drop", verdict.reason, ref=ref)
                continue

            if not row.get("email"):
                stats["no_contact"] += 1
                dropped.append({"ref": ref, "stage": "contact",
                                "reason": "no work email after enrichment"})
                db.log_decision(conn, "contact", "drop",
                                "no work email after enrichment", ref=ref)
                continue

            pacing = caps.check_company_contact_limit(
                cfg, conn, row.get("company_domain", ""))
            if not pacing.allowed:
                stats["duplicate"] += 1
                dropped.append({"ref": ref, "stage": "pacing", "reason": pacing.reason})
                db.log_decision(conn, "pacing", "drop", pacing.reason, ref=ref)
                continue

            row["icp_tier"] = verdict.tier
            row["icp_reason"] = verdict.reason
            row["buyer_tier"] = verdict.buyer_tier
            row["status"] = "new"
            if row.get("enrichment_json") is None:
                row["enrichment_json"] = json.dumps(
                    {k: v for k, v in raw.items() if k not in row})

            if args.dry_run:
                stats["stored"] += 1
                continue

            pid = db.upsert_prospect(conn, row)
            db.log_decision(conn, "intake", "store", verdict.reason,
                            prospect_id=pid, ref=ref)
            stats["stored"] += 1

    if args.json:
        print(json.dumps({"stats": stats, "dropped": dropped}, indent=2))
    else:
        print(("DRY RUN, nothing written\n" if args.dry_run else "") +
              f"sourced {stats['sourced']} -> stored {stats['stored']}")
        for k in ("do_not_touch", "suppressed", "disqualified", "no_contact", "duplicate"):
            if stats[k]:
                print(f"  dropped {stats[k]:>3} at {k}")
        for d in dropped[:10]:
            print(f"    {d['stage']:<9} {d['ref'][:44]:<46} {d['reason'][:60]}")
        if len(dropped) > 10:
            print(f"    ... and {len(dropped) - 10} more (use --json for all)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Halt as e:
        print(f"\nHALTED: {e}", file=sys.stderr)
        sys.exit(2)
