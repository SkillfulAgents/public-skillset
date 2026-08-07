"""CRM suppression: ask the system of record before mailing anyone.

Whatever fills the `crm` slot answers this layer, so a team switching from local
SQLite to a real CRM changes one config line and keeps the same gate.

Fail-closed by design: a lookup that errors raises `SuppressionUnavailable`
instead of returning "not suppressed". Halting the run costs a day. Mailing a
customer, an open deal, or someone who already signed up costs the relationship.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import adapters as adapter_registry  # noqa: E402
from lib import db  # noqa: E402

ADAPTER = {
    "slot": "suppression",
    "name": "crm",
    "description": "Delegates to the configured CRM adapter. Fails closed if it errors.",
}

DEFAULT_COMPANY_STATES = ["signup", "open_deal", "meeting_held", "customer"]


class SuppressionUnavailable(RuntimeError):
    """The CRM could not be consulted. Callers must halt, not proceed."""


def _crm(ctx):
    try:
        return adapter_registry.load(ctx.config, "crm")
    except Exception as e:
        raise SuppressionUnavailable(
            f"crm suppression layer cannot load the crm adapter: {e}"
        ) from e


def is_suppressed(ctx, prospect: dict) -> tuple[bool, str]:
    crm = _crm(ctx)
    if crm is None:
        return False, "crm slot is disabled (adapters.crm: none), nothing to check"

    crm_ctx = adapter_registry.context(ctx.config, crm)
    try:
        record = crm.lookup(crm_ctx, prospect)
    except Exception as e:
        raise SuppressionUnavailable(
            f"crm lookup via {crm.name} failed for "
            f"{prospect.get('email') or prospect.get('linkedin_url') or prospect.get('name')!r}: "
            f"{e}. Halting: an unchecked send risks mailing an existing "
            f"customer or open deal."
        ) from e

    if not record:
        return False, f"no record in crm:{crm.name}"

    states = set(ctx.config.get("suppression.suppress_company_states")
                 or DEFAULT_COMPANY_STATES)

    status = (record.get("status") or record.get("state") or "")
    if status and status in states:
        return True, f"crm:{crm.name} record status {status!r} is a suppressing state"

    if status and status in db.TERMINAL_STATUSES:
        return True, f"crm:{crm.name} record is terminal (status={status!r})"

    company_states = record.get("company_states") or []
    if isinstance(company_states, str):
        company_states = [company_states]
    hit = sorted(states.intersection(company_states))
    if hit:
        domain = record.get("company_domain") or prospect.get("company_domain") or "company"
        return True, (f"crm:{crm.name} has {domain} in state(s) "
                      f"{', '.join(hit)}; whole account is suppressed")

    if record.get("engaged"):
        return True, f"crm:{crm.name} record is already engaged"

    return False, f"crm:{crm.name} record found, no suppressing state"
