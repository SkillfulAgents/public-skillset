"""ICP qualification, driven entirely by config.

In the pipeline this was extracted from, tier rules were hardcoded in three
different files that had already drifted apart. Here there is one evaluator and
one config block. Every verdict carries a reason so a rejected prospect can be
explained a month later.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from . import identity


@dataclass
class Verdict:
    qualified: bool
    tier: str | None
    reason: str
    buyer_tier: str | None = None
    warnings: list[str] | None = None

    def __bool__(self) -> bool:
        return self.qualified


def _employees(p: dict) -> int | None:
    v = p.get("employee_count")
    if v in (None, ""):
        return None
    try:
        return int(str(v).replace(",", "").split("-")[0].split("+")[0].strip())
    except (ValueError, TypeError):
        return None


def buyer_tier(config, title: str) -> str | None:
    """Map a job title to a configured buyer tier (A/B/C). Longest match wins.

    Longest-first matching stops 'Head of Operations' being classified by a
    bare 'Operations' entry in a different tier.
    """
    if not title:
        return None
    folded = identity.fold(title)
    best = (0, None)
    for tier in config.get("icp.buyer_tiers", []) or []:
        for t in tier.get("titles", []) or []:
            ft = identity.fold(t)
            if not ft:
                continue
            if re.search(rf"\b{re.escape(ft)}\b", folded) and len(ft) > best[0]:
                best = (len(ft), tier.get("id"))
    return best[1]


def _tier_matches(tier: dict, prospect: dict, emp: int | None) -> tuple[bool, str]:
    crit = tier.get("criteria") or {}

    rng = crit.get("employee_range")
    if rng and emp is not None:
        if not (int(rng[0]) <= emp <= int(rng[1])):
            return False, f"{emp} employees outside {rng}"

    signals = set(crit.get("signals") or [])
    if signals:
        have = {identity.fold(s) for s in (prospect.get("signals") or [])}
        have |= {identity.fold(s) for s in (prospect.get("tags") or [])}
        wanted = {identity.fold(s) for s in signals}
        if not (wanted & have):
            return False, f"no matching signal from {sorted(signals)}"

    # Industry is how most ICP frameworks actually tier, and it is the one
    # field sourcing reliably provides. Substring both ways so "freight
    # brokerage" matches a "freight" rule without an exact-match taxonomy.
    industry = identity.fold(prospect.get("industry") or "")
    excluded = crit.get("exclude_industries") or []
    if industry:
        for bad in excluded:
            b = identity.fold(bad)
            if b and (b in industry or industry in b):
                return False, f"industry {prospect['industry']!r} is excluded from this tier"

    wanted_ind = crit.get("industries") or []
    if wanted_ind:
        if not industry:
            return False, f"no industry on the record; this tier requires one of {wanted_ind}"
        if not any(identity.fold(w) in industry or industry in identity.fold(w)
                   for w in wanted_ind):
            return False, f"industry {prospect['industry']!r} not in {wanted_ind}"

    stages = crit.get("funding_stage")
    if stages and prospect.get("funding_stage"):
        if identity.fold(prospect["funding_stage"]) not in {identity.fold(s) for s in stages}:
            return False, f"stage {prospect['funding_stage']!r} not in {stages}"

    return True, "criteria met"


def evaluate(config, prospect: dict) -> Verdict:
    """Qualify one prospect. Disqualifiers first, then first-matching tier."""
    warnings: list[str] = []
    emp = _employees(prospect)
    bt = buyer_tier(config, prospect.get("title", ""))

    # -- global size band -------------------------------------------------
    band = config.get("icp.employee_range")
    if band and emp is not None and not (int(band[0]) <= emp <= int(band[1])):
        # Above the band may still be a valid warm-intro tier, so fall through
        # to tier matching rather than rejecting outright.
        if emp < int(band[0]):
            return Verdict(False, None,
                           f"{emp} employees is below the outbound floor of {band[0]}")
        warnings.append(f"{emp} employees is above the outbound ceiling of {band[1]}")
    elif emp is None:
        warnings.append("employee_count unknown; size rules not applied")

    # -- geo ---------------------------------------------------------------
    geos = config.get("icp.geos") or []
    country = prospect.get("country")
    if geos and country and identity.fold(country) not in {identity.fold(g) for g in geos}:
        aliases = {"us", "usa", "united states", "united states of america"}
        if not (identity.fold(country) in aliases and
                {identity.fold(g) for g in geos} & aliases):
            return Verdict(False, None, f"country {country!r} not in target geos {geos}")

    # -- hard disqualifiers ------------------------------------------------
    for dq in config.get("icp.disqualifiers", []) or []:
        dq_id = dq.get("id")
        if dq_id and prospect.get(f"dq_{dq_id}"):
            return Verdict(False, None, f"disqualified: {dq_id} ({dq.get('rule','')})")
    for flag in (prospect.get("disqualifiers") or []):
        return Verdict(False, None, f"disqualified: {flag}")

    # -- tier assignment ---------------------------------------------------
    tiers = config.get("icp.tiers") or []
    if not tiers:
        return Verdict(True, None, "no tiers configured; accepting by default",
                       buyer_tier=bt, warnings=warnings)

    tried = []
    for tier in tiers:
        ok, why = _tier_matches(tier, prospect, emp)
        if not ok:
            tried.append(f"{tier.get('id')}: {why}")
            continue
        if tier.get("outbound_allowed", True) is False:
            return Verdict(
                False, tier.get("id"),
                f"tier {tier.get('id')} ({tier.get('name')}) is warm-intro only, "
                f"not outbound",
                buyer_tier=bt, warnings=warnings)
        if bt is None:
            warnings.append(
                f"title {prospect.get('title')!r} does not map to a buyer tier")
        return Verdict(True, tier.get("id"), f"matched {tier.get('id')}: {why}",
                       buyer_tier=bt, warnings=warnings)

    return Verdict(False, None, "no tier matched: " + "; ".join(tried),
                   buyer_tier=bt, warnings=warnings)


def mix_drift(config, counts: dict[str, int]) -> list[str]:
    """Compare actual tier mix against target mix_pct. Reporting only.

    Never used to gate sourcing: a good prospect in an over-weight tier is
    still a good prospect.
    """
    total = sum(counts.values())
    if not total:
        return []
    out = []
    for tier in config.get("icp.tiers") or []:
        target = tier.get("mix_pct")
        if target is None:
            continue
        actual = 100.0 * counts.get(tier.get("id"), 0) / total
        if abs(actual - target) >= 15:
            out.append(f"{tier.get('id')}: {actual:.0f}% actual vs {target}% target "
                       f"(n={counts.get(tier.get('id'), 0)}/{total})")
    return out
