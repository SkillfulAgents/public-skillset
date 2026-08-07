"""Sourcing disabled.

Select this when prospects arrive by some path the template does not own:
hand-curated rows written straight to the database, an upstream list tool that
already pushes into your CRM, or a paused intake. The rest of the motion
(enrichment, suppression, cadence, reporting) still runs on whatever is there.
"""
from __future__ import annotations

ADAPTER = {
    "slot": "sourcing",
    "name": "none",
    "description": "No automated sourcing. Prospects are added manually or by an upstream system.",
}


def fetch(ctx, limit: int | None = None) -> list[dict]:
    """Always returns an empty list. Intake is handled outside the template."""
    return []
