"""No CRM. Every lookup misses and every event is discarded.

Selecting this slot is a deliberate statement that no system of record exists.
Note the consequence: `suppression/crm.py` then has nothing to check, so the
local seen-set and blocklist are the only layers standing between the motion and
a person you already closed.
"""
from __future__ import annotations

ADAPTER = {
    "slot": "crm",
    "name": "none",
    "description": "Disabled CRM slot. No lookups, no writes.",
}


def lookup(ctx, prospect: dict) -> dict | None:
    return None


def record(ctx, event: dict) -> None:
    return None
