"""Calendar reading disabled. No meeting is ever detected automatically.

This is the default, because a calendar grant is a real permission decision and
nothing should read one until the operator has agreed to it.

The cost of leaving it here is worth stating plainly: most booked meetings never
produce a reply, so with this adapter selected the meetings number reflects only
what a human flagged by hand. A low number means nothing is watching, not that
nothing is booking.
"""
from __future__ import annotations

ADAPTER = {
    "slot": "calendar",
    "name": "none",
    "description": "Disabled calendar slot. Meetings must be recorded by hand.",
}


def events(ctx, sender_email: str, since: str, until: str) -> list[dict]:
    """Always returns an empty list, so nothing is ever matched or written."""
    return []
