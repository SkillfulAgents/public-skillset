"""Local suppression: the layer that works with no vendor at all.

Three checks, cheapest first:
  1. Blocklist domains file (competitors, partners, existing customers, anyone
     legal told you never to mail).
  2. The `seen` table, which holds every row this workspace has ever pulled.
  3. Per-company send recency, so two contacts at one account are not hit inside
     `icp.min_days_between_same_company_touches`.

Domain matching is deliberately NOT applied to the `seen` table: a domain
appearing there only means a colleague was sourced once, and blocking on that
would make `icp.max_contacts_per_company` unreachable.
"""
from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import db, identity  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "suppression",
    "name": "local",
    "description": "Blocklist domains, the local seen-set, and per-company send recency.",
}

DEFAULT_DB = "data/campaigns.db"


class SuppressionUnavailable(RuntimeError):
    """A suppression source could not be read. Fail closed rather than send."""


def _db_path(ctx) -> pathlib.Path:
    raw = (ctx.settings.get("path")
           or ctx.config.get("adapter_config.sqlite.path")
           or DEFAULT_DB)
    p = pathlib.Path(str(raw))
    return p if p.is_absolute() else ROOT / p


def _blocklist(ctx) -> set[str]:
    raw = (ctx.settings.get("blocklist_domains_file")
           or ctx.config.get("suppression.blocklist_domains_file"))
    if not raw:
        return set()
    p = pathlib.Path(str(raw))
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return set()

    text = p.read_text(encoding="utf-8").strip()
    if not text:
        return set()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = [line.strip() for line in text.splitlines()
                if line.strip() and not line.startswith("#")]
    if isinstance(data, dict):
        data = data.get("domains") or data.get("blocklist") or list(data.keys())
    if not isinstance(data, list):
        raise SuppressionUnavailable(
            f"{p} is not a JSON list of domains, a {{\"domains\": [...]}} object, "
            "or a newline-delimited list"
        )
    return {str(d).strip().lower().lstrip("@") for d in data if str(d).strip()}


def _domains(prospect: dict) -> set[str]:
    out = set()
    for value in (prospect.get("company_domain"),
                  identity.email_domain(prospect.get("email", "")),
                  identity.email_domain(prospect.get("personal_email", ""))):
        if value:
            out.add(str(value).strip().lower().lstrip("@"))
    return out


def _seen_hit(conn, prospect: dict, match_on: set[str]):
    if "linkedin_url" in match_on:
        slug = identity.linkedin_slug(prospect.get("linkedin_url", ""))
        if slug:
            row = conn.execute(
                "SELECT source_key, status, first_seen_at FROM seen "
                "WHERE linkedin_slug = ? LIMIT 1", (slug,)
            ).fetchone()
            if row:
                return row, f"linkedin slug {slug!r}"
    if "email" in match_on:
        email = (prospect.get("email") or "").strip().lower()
        if email:
            row = conn.execute(
                "SELECT source_key, status, first_seen_at FROM seen "
                "WHERE lower(email) = ? LIMIT 1", (email,)
            ).fetchone()
            if row:
                return row, f"email {email}"
    return None, ""


def is_suppressed(ctx, prospect: dict) -> tuple[bool, str]:
    match_on = set(ctx.config.get("suppression.match_on")
                   or ["email", "linkedin_url", "company_domain"])
    blocked = _blocklist(ctx)
    if "company_domain" in match_on:
        for domain in _domains(prospect):
            if domain in blocked:
                return True, f"blocklist domain: {domain}"

    try:
        conn = db.init(_db_path(ctx))
    except Exception as e:
        raise SuppressionUnavailable(
            f"local suppression db {_db_path(ctx)} is unreadable: {e}"
        ) from e

    try:
        row, how = _seen_hit(conn, prospect, match_on)
        if row is not None:
            status = row["status"] or "seen"
            return True, (f"already in local seen-set by {how} "
                          f"(status={status}, source={row['source_key']}, "
                          f"first seen {row['first_seen_at']})")

        days = int(ctx.config.get("icp.min_days_between_same_company_touches", 0) or 0)
        if days > 0:
            for domain in _domains(prospect):
                if db.company_touched_recently(conn, domain, days):
                    return True, (f"company {domain} was emailed within the last "
                                  f"{days} day(s)")
    finally:
        conn.close()

    return False, "no local suppression hit"
