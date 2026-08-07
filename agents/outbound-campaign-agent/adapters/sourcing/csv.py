"""Sourcing from a local CSV file.

The zero-dependency starting point: export a list from anywhere, drop it in,
run the motion. Headers are matched loosely so an untouched export from a
sales tool usually works without editing.
"""
from __future__ import annotations

import csv
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import identity  # noqa: E402

ADAPTER = {
    "slot": "sourcing",
    "name": "csv",
    "description": "Read prospects from a local CSV. Flexible headers, no credentials.",
}

ROOT = pathlib.Path(__file__).resolve().parents[2]

ALIASES = {
    "linkedin_url": ["linkedin", "linkedin_url", "li", "li_url", "linkedin_profile",
                     "linkedinprofileurl", "profile_url", "person_linkedin_url"],
    "email": ["email", "work_email", "email_address", "business_email",
              "primary_email", "corporate_email"],
    "personal_email": ["personal_email", "personal_email_address"],
    "name": ["name", "full_name", "contact_name", "person", "person_name",
             "display_name"],
    "first_name": ["first_name", "firstname", "first", "given_name"],
    "last_name": ["last_name", "lastname", "last", "surname", "family_name"],
    "title": ["title", "job_title", "position", "role", "headline"],
    "company": ["company", "organization", "organisation", "company_name",
                "account", "account_name", "employer", "org"],
    "company_domain": ["domain", "company_domain", "website", "company_website",
                       "url", "site", "primary_domain"],
    "industry": ["industry", "vertical", "sector", "segment"],
    "employee_count": ["employees", "employee_count", "headcount", "num_employees",
                       "company_size", "size", "estimated_num_employees"],
    "country": ["country", "company_country"],
    "city": ["city", "location", "company_city"],
    "state": ["state", "region", "province"],
    "phone": ["phone", "phone_number", "mobile", "direct_dial"],
    "external_id": ["external_id", "id", "record_id", "crm_id"],
}

_HEADER_TO_FIELD = {alias: field for field, aliases in ALIASES.items() for alias in aliases}

_SLUG_CHARS = re.compile(r"^[a-z0-9][a-z0-9\-_%]{2,}$", re.I)


def _norm_header(h: str) -> str:
    h = str(h or "").replace("﻿", "").strip().lower()
    h = re.sub(r"[\s\-./]+", "_", h)
    return re.sub(r"[^a-z0-9_]", "", h).strip("_")


def _clean(v) -> str:
    if v is None:
        return ""
    if isinstance(v, list):
        v = next((x for x in v if x), "")
    return str(v).replace("﻿", "").strip()


def _canonical_linkedin(raw: str) -> str:
    slug = identity.linkedin_slug(raw)
    if not slug:
        # Exports sometimes carry a bare slug ("jane-doe-1a2b") or "in/jane-doe"
        # rather than a full URL. Anything with a scheme or a dot is a real URL
        # that simply is not a /in/ profile, so it stays rejected.
        bare = raw.strip().strip("/")
        if bare.lower().startswith("in/"):
            bare = bare[3:]
        if bare and "." not in bare and "/" not in bare and _SLUG_CHARS.match(bare):
            slug = bare.lower()
    return f"https://linkedin.com/in/{slug}" if slug else ""


def _canonical_domain(raw: str) -> str:
    d = raw.strip().lower()
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("@")[-1]
    if d.startswith("www."):
        d = d[4:]
    return d if "." in d else ""


def _to_int(raw: str):
    m = re.search(r"\d[\d,]*", raw)
    if not m:
        return None
    try:
        return int(m.group(0).replace(",", ""))
    except ValueError:
        return None


def _map_row(row: dict) -> dict:
    out: dict = {}
    for key, val in row.items():
        field = _HEADER_TO_FIELD.get(_norm_header(key))
        cleaned = _clean(val)
        if not cleaned:
            continue
        if field:
            out.setdefault(field, cleaned)
        else:
            passthrough = _norm_header(key)
            if passthrough and passthrough not in ("extra",):
                out.setdefault(passthrough, cleaned)

    out["linkedin_url"] = _canonical_linkedin(out.get("linkedin_url", ""))
    out["company_domain"] = _canonical_domain(out.get("company_domain", ""))

    email = out.get("email", "").lower()
    if email and identity.is_personal_email(email):
        out["personal_email"] = out.get("personal_email") or email
        out["email"] = ""
    else:
        out["email"] = email

    if not out.get("first_name") or not out.get("last_name"):
        display = out.get("name") or f"{out.get('first_name', '')} {out.get('last_name', '')}"
        first, last = identity.split_name(display)
        out["first_name"] = out.get("first_name") or first
        out["last_name"] = out.get("last_name") or last
    if not out.get("name"):
        out["name"] = " ".join(x for x in [out.get("first_name"), out.get("last_name")] if x)

    if out.get("employee_count"):
        out["employee_count"] = _to_int(str(out["employee_count"]))
    if not out.get("company_domain") and out.get("email"):
        out["company_domain"] = _canonical_domain(identity.email_domain(out["email"]))

    out["source"] = "csv"
    return {k: v for k, v in out.items() if v not in (None, "")}


def fetch(ctx, limit: int | None = None) -> list[dict]:
    """Read prospect rows from `adapter_config.csv.input_path`.

    Rows carrying neither a LinkedIn URL nor any email are dropped, since
    nothing downstream can suppress, enrich, or send to them.
    """
    raw_path = ctx.settings.get("input_path")
    if not raw_path:
        raise ValueError("adapter_config.csv.input_path is not set")
    path = pathlib.Path(raw_path)
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        raise FileNotFoundError(f"[sourcing:csv] no such file: {path}")

    rows: list[dict] = []
    skipped_blank = 0
    skipped_unidentified = 0

    with path.open(newline="", encoding="utf-8-sig", errors="replace") as fh:
        reader = csv.DictReader(fh, restkey="_extra", restval="")
        if not reader.fieldnames:
            print(f"[sourcing:csv] {path.name} has no header row", file=sys.stderr)
            return []
        for row in reader:
            row.pop("_extra", None)
            row.pop(None, None)
            if not any(_clean(v) for v in row.values()):
                skipped_blank += 1
                continue
            mapped = _map_row(row)
            # A personal-domain address still identifies the row well enough to
            # suppress and enrich against, so it counts here even though it is
            # not a sendable work email.
            if not any(mapped.get(k) for k in ("linkedin_url", "email", "personal_email")):
                skipped_unidentified += 1
                continue
            rows.append(mapped)
            if limit and len(rows) >= limit:
                break

    print(
        f"[sourcing:csv] {path.name}: {len(rows)} usable, "
        f"{skipped_unidentified} skipped (no linkedin and no work email), "
        f"{skipped_blank} blank",
        file=sys.stderr,
    )
    return rows
