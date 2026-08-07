"""Local SQLite as the CRM of record.

Good enough to run the whole motion with no external system: prior contact,
per-company state and the decision audit all live in `lib/db.py`'s schema. Swap
this slot for a real CRM adapter later without touching the motion.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import db, identity  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "crm",
    "name": "sqlite",
    "description": "Reads and writes prospect state in the local campaigns.db.",
}

DEFAULT_PATH = "data/campaigns.db"

ENGAGED_STATUSES = {"replied", "meeting", "meeting_held", "customer", "signup",
                    "open_deal", "unsubscribed"}


def _db_path(ctx) -> pathlib.Path:
    raw = ctx.settings.get("path", DEFAULT_PATH)
    p = pathlib.Path(str(raw))
    return p if p.is_absolute() else ROOT / p


def _connect(ctx):
    return db.init(_db_path(ctx))


def _row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


def _find(conn, prospect: dict):
    external_id = prospect.get("external_id")
    if external_id:
        row = conn.execute(
            "SELECT * FROM prospects WHERE external_id = ? LIMIT 1", (external_id,)
        ).fetchone()
        if row:
            return row, "external_id"

    slug = identity.linkedin_slug(prospect.get("linkedin_url", ""))
    if slug:
        row = conn.execute(
            "SELECT * FROM prospects WHERE lower(linkedin_url) LIKE ? LIMIT 1",
            (f"%/in/{slug}%",),
        ).fetchone()
        if row:
            return row, "linkedin_slug"

    email = (prospect.get("email") or "").strip().lower()
    if email:
        row = conn.execute(
            "SELECT * FROM prospects WHERE lower(email) = ? LIMIT 1", (email,)
        ).fetchone()
        if row:
            return row, "email"
    return None, ""


def _company_states(conn, domain: str, exclude_id=None) -> list[str]:
    if not domain:
        return []
    rows = conn.execute(
        "SELECT DISTINCT status FROM prospects "
        "WHERE lower(company_domain) = ? AND id IS NOT ?",
        (domain.lower(), exclude_id),
    ).fetchall()
    return sorted({r["status"] for r in rows if r["status"]})


def lookup(ctx, prospect: dict) -> dict | None:
    """Prior record for this person, or for their company if the person is new.

    A company-level hit is returned with `match="company_domain"` and no
    `prospect_id`, so a caller can distinguish "we know this human" from "we are
    already working this account".
    """
    conn = _connect(ctx)
    try:
        row, how = _find(conn, prospect)
        domain = (prospect.get("company_domain")
                  or identity.email_domain(prospect.get("email", "")))

        if row is None:
            states = _company_states(conn, domain)
            if not states:
                return None
            return {
                "match": "company_domain",
                "prospect_id": None,
                "company_domain": domain,
                "status": None,
                "company_states": states,
                "sends": 0,
                "replies": 0,
            }

        rec = _row_to_dict(row)
        rec["match"] = how
        rec["prospect_id"] = row["id"]
        rec["company_states"] = _company_states(
            conn, row["company_domain"] or domain, exclude_id=row["id"])
        rec["sends"] = conn.execute(
            "SELECT COUNT(*) FROM sends WHERE prospect_id = ?", (row["id"],)
        ).fetchone()[0]
        rec["replies"] = conn.execute(
            "SELECT COUNT(*) FROM replies WHERE prospect_id = ?", (row["id"],)
        ).fetchone()[0]
        rec["engaged"] = (rec.get("status") in ENGAGED_STATUSES) or rec["replies"] > 0
        return rec
    finally:
        conn.close()


def record(ctx, event: dict) -> None:
    """Append an audit row, and apply a status change when the event carries one.

    Recognised keys: stage, decision (or type), reason, layer, ref, prospect_id,
    status, plus linkedin_url / email / external_id for resolving the prospect.
    """
    conn = _connect(ctx)
    try:
        with db.transaction(conn):
            prospect_id = event.get("prospect_id")
            if prospect_id is None:
                row, _ = _find(conn, event)
                prospect_id = row["id"] if row else None

            status = event.get("status")
            if status and prospect_id is not None:
                conn.execute("UPDATE prospects SET status = ? WHERE id = ?",
                             (status, prospect_id))

            ref = event.get("ref")
            if ref is None and event.get("payload") is not None:
                ref = json.dumps(event["payload"], ensure_ascii=False)[:2000]

            db.log_decision(
                conn,
                stage=str(event.get("stage") or "crm"),
                decision=str(event.get("decision") or event.get("type") or "record"),
                reason=str(event.get("reason") or ""),
                layer=str(event.get("layer") or "crm:sqlite"),
                prospect_id=prospect_id,
                ref=str(ref or ""),
            )
    finally:
        conn.close()
