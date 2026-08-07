"""Enrichment disabled.

Select this when the sourcing list already carries verified emails, or when you
want to exercise the motion without spending provider credits. Prospects pass
through untouched, so anything missing an email is filtered out later by the
send gate rather than being guessed at here.
"""
from __future__ import annotations

ADAPTER = {
    "slot": "enrichment",
    "name": "none",
    "description": "No-op enrichment. Prospect fields are used exactly as sourced.",
}


def enrich(ctx, prospect: dict) -> dict:
    """Always returns an empty dict, so nothing is merged."""
    return {}
