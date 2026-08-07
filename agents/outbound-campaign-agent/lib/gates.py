"""Do-not-touch gate. A third question, routinely confused with the other two.

  ICP          is "not a fit".
  suppression  is "already engaged".
  do-not-touch is "never, for a reason that has nothing to do with fit": a
                 customer's competitor, an investor's portfolio company, a
                 company in an active legal matter, a former employer.

The list is short, hand-maintained, and permanent, so it is checked before
anything else and it fails closed: a malformed `do_not_touch` block raises with
the offending key rather than matching nothing. A silently-empty exclusion list
is the exact failure this gate exists to prevent.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import identity
from .config import ConfigError

RULES = ("domains", "companies", "people", "geos")

# Dropped before comparing company names, so "Acme, Inc." matches "acme".
COMPANY_SUFFIXES = {
    "inc", "llc", "ltd", "limited", "corp", "corporation", "co", "company",
    "plc", "gmbh", "ag", "bv", "nv", "sa", "sas", "srl", "spa", "oy", "ab",
    "pty", "lp", "llp", "pllc", "pc", "holdings", "the",
}

_DOMAIN_SHAPE = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


@dataclass
class Block:
    blocked: bool
    reason: str
    matched: str

    def __bool__(self) -> bool:
        return self.blocked


def check_do_not_touch(config, prospect) -> Block:
    """Is this prospect on the never-contact list? Truthy result means stop."""
    rules = _rules(config)
    for matched, how in _hits(rules, prospect):
        entry = matched.split(":", 1)[1]
        note = rules["notes"].get(_note_key(entry), "")
        if rules["reason_required"] and not note:
            note = (f"no entry for {entry!r} in do_not_touch.notes, and "
                    f"do_not_touch.reason_required is true")
        return Block(True, f"{how}. {note}" if note else how, matched)
    return Block(False, "no do-not-touch rule matched", "")


def _hits(rules: dict, prospect):
    """Yield (matched, human explanation) for every rule that fires."""
    domains = {d for d in (_domain(_field(prospect, "company_domain")),
                           _domain(_field(prospect, "email"))) if d}
    company = _company(_field(prospect, "company"))
    slug = identity.linkedin_slug(_field(prospect, "linkedin_url"))
    emails = {e.casefold() for e in (_field(prospect, "email"),
                                     _field(prospect, "personal_email")) if e}
    country = _field(prospect, "country").casefold()

    for entry in rules["people"]:
        entry_slug = identity.linkedin_slug(entry)
        if entry_slug:
            if entry_slug == slug:
                yield f"people:{entry}", f"linkedin slug {slug!r} is on the do-not-touch list"
            continue
        if entry.casefold() in emails:
            yield f"people:{entry}", f"email {entry.casefold()} is on the do-not-touch list"

    for entry in rules["domains"]:
        hit = _domain_hit(_domain(entry), domains)
        if hit:
            yield f"domains:{entry}", (f"domain {hit} falls under do-not-touch "
                                       f"domain {_domain(entry)}")

    for entry in rules["companies"]:
        if _DOMAIN_SHAPE.match(_domain(entry)):
            hit = _domain_hit(_domain(entry), domains)
            if hit:
                yield f"companies:{entry}", (f"domain {hit} falls under do-not-touch "
                                             f"company {entry}")
            continue
        if company and _company(entry) == company:
            yield f"companies:{entry}", f"company {company!r} is on the do-not-touch list"

    for entry in rules["geos"]:
        if country and entry.strip().casefold() == country:
            yield f"geos:{entry}", f"country {country.upper()} is excluded outright"


def _rules(config) -> dict:
    """Read and validate the block. Wrong shape raises; absent is empty."""
    block = config.get("do_not_touch") or {}
    if not isinstance(block, dict):
        raise ConfigError(
            f"do_not_touch must be a mapping, got {type(block).__name__}: {block!r}")

    out: dict = {}
    for key in RULES:
        val = block.get(key)
        if val is None:
            out[key] = []
            continue
        if not isinstance(val, list):
            raise ConfigError(
                f"do_not_touch.{key} must be a list, got {type(val).__name__}: "
                f"{val!r}. A do-not-touch rule that silently matches nothing is "
                f"worse than no rule, so this refuses rather than continues."
            )
        out[key] = [str(v).strip() for v in val if str(v).strip()]

    notes = block.get("notes") or {}
    if not isinstance(notes, dict):
        raise ConfigError(
            f"do_not_touch.notes must be a mapping of entry -> why, got "
            f"{type(notes).__name__}: {notes!r}")
    out["notes"] = {_note_key(k): str(v).strip() for k, v in notes.items()}
    out["reason_required"] = bool(block.get("reason_required", True))
    return out


def _field(prospect, key: str) -> str:
    """Read a column from a dict or a sqlite3.Row without caring which."""
    try:
        val = prospect[key]
    except (KeyError, IndexError):
        return ""
    return "" if val is None else str(val).strip()


def _domain(value: str) -> str:
    v = str(value or "").strip().casefold()
    if "@" in v:
        v = v.rsplit("@", 1)[-1]
    v = re.sub(r"^[a-z]+://", "", v).split("/")[0].split(":")[0]
    return v[4:] if v.startswith("www.") else v


def _domain_hit(entry: str, domains: set[str]) -> str:
    """Exact or subdomain match. 'mail.acme.example' is still acme.example."""
    if not entry:
        return ""
    for d in domains:
        if d == entry or d.endswith("." + entry):
            return d
    return ""


def _company(name: str) -> str:
    tokens = [t for t in identity.fold(name).split() if t not in COMPANY_SUFFIXES]
    return " ".join(tokens)


def _note_key(entry: str) -> str:
    return str(entry).strip().casefold()
