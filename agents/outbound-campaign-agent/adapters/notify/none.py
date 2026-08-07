"""Notifications disabled. Nothing is posted anywhere.

The motion still writes every decision to the `decisions` table, so choosing
this adapter loses the ping, not the audit trail.
"""
from __future__ import annotations

ADAPTER = {
    "slot": "notify",
    "name": "none",
    "description": "Disabled notify slot. Posts nowhere.",
}


def post(ctx, text: str) -> None:
    return None
