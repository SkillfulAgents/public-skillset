"""Google Calendar reader via the connected-account proxy.

Read-only. Nothing here creates, moves, or deletes an event.

The proxy signs requests with the workspace OAuth grant, so no Google client
library and no refresh-token handling live here. Every call is:

    {PROXY_BASE_URL}/{account_id}/www.googleapis.com/{path}
    Authorization: Bearer {PROXY_TOKEN}

Account resolution matches `sender/gmail.py`:
  1. `adapter_config.google_calendar.connected_account_id_env` names an env var
     holding the account id.
  2. Otherwise the first account under a Google toolkit in CONNECTED_ACCOUNTS.

Cancelled events are requested deliberately (`showDeleted`). A meeting that was
booked and then called off is a different outcome from one that was never
booked, and the only place that distinction survives is the calendar.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "calendar",
    "name": "google",
    "requires_env": ["PROXY_BASE_URL", "PROXY_TOKEN"],
    "description": "Reads booked meetings from a connected Google Calendar (proxy, stdlib only).",
}

GOOGLE_HOST = "www.googleapis.com"
# The same Google grant usually carries both scopes, so a plain gmail account is
# the last resort rather than a missing-credential error.
TOOLKITS = ("googlecalendar", "google_calendar", "gmail")
DEFAULT_TIMEOUT = 30
DEFAULT_MAX_RESULTS = 250
DEFAULT_MAX_PAGES = 10


class CalendarError(RuntimeError):
    pass


def _connected_accounts() -> dict:
    """Read CONNECTED_ACCOUNTS, tolerating the double-JSON-encoded .env form.

    Some runners inject an empty `{}` into the environment that wins over
    `--env-file`, so fall back to parsing the file, whose value is a JSON string
    containing JSON.
    """
    raw = os.environ.get("CONNECTED_ACCOUNTS", "") or ""
    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        parsed = {}
    if isinstance(parsed, str):
        try:
            parsed = json.loads(parsed)
        except json.JSONDecodeError:
            parsed = {}
    if isinstance(parsed, dict) and parsed:
        return parsed

    for env_path in (ROOT / ".env", pathlib.Path.cwd() / ".env"):
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("CONNECTED_ACCOUNTS="):
                continue
            val = line.split("=", 1)[1].strip()
            try:
                inner = json.loads(val)
                out = json.loads(inner) if isinstance(inner, str) else inner
            except json.JSONDecodeError:
                continue
            if isinstance(out, dict) and out:
                return out
    return {}


def _account_id(ctx) -> str:
    env_name = ctx.settings.get("connected_account_id_env")
    if env_name:
        val = os.environ.get(str(env_name))
        if val:
            return val
    accounts = _connected_accounts()
    for toolkit in TOOLKITS:
        for acct in accounts.get(toolkit) or []:
            if isinstance(acct, dict) and acct.get("id"):
                return acct["id"]
            if isinstance(acct, str) and acct:
                return acct
    raise CalendarError(
        "no Google Calendar account available. Set "
        f"{env_name or 'adapter_config.google_calendar.connected_account_id_env'} "
        f"to an env var holding the account id, or connect one of {list(TOOLKITS)} "
        "so it appears in CONNECTED_ACCOUNTS."
    )


def _proxy(ctx, path: str, params: dict, calendar_id: str) -> dict:
    base = ctx.secret("PROXY_BASE_URL").rstrip("/")
    token = ctx.secret("PROXY_TOKEN")
    url = f"{base}/{_account_id(ctx)}/{GOOGLE_HOST}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}"}, method="GET")
    timeout = int(ctx.settings.get("timeout_seconds", DEFAULT_TIMEOUT))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise CalendarError(
            f"calendar {calendar_id!r}: events request failed ({e.code}): {detail}"
        ) from e
    except urllib.error.URLError as e:
        raise CalendarError(
            f"calendar {calendar_id!r}: Google is unreachable: {e.reason}") from e
    return json.loads(payload) if payload else {}


def _utc(value: str | None) -> str | None:
    """ISO8601 in UTC. Google mixes offset timestamps and all-day dates."""
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        try:
            parsed = dt.datetime.fromisoformat(f"{text}T00:00:00")
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).isoformat()


def _when(node: dict | None) -> str | None:
    node = node or {}
    return _utc(node.get("dateTime") or node.get("date"))


def _normalize(ev: dict) -> dict:
    status = ev.get("status") or "confirmed"
    return {
        "provider_event_id": ev.get("id"),
        "title": ev.get("summary") or "",
        "starts_at": _when(ev.get("start")),
        "ends_at": _when(ev.get("end")),
        "attendees": [a["email"] for a in (ev.get("attendees") or [])
                      if isinstance(a, dict) and a.get("email")],
        "organizer": (ev.get("organizer") or {}).get("email"),
        "status": status,
        "cancelled": status == "cancelled",
    }


def events(ctx, sender_email: str, since: str, until: str) -> list[dict]:
    """Normalized events on one calendar between two ISO8601 UTC bounds."""
    calendar_id = str(sender_email or ctx.settings.get("calendar_id") or "primary")
    path = f"/calendar/v3/calendars/{urllib.parse.quote(calendar_id, safe='')}/events"

    params = {
        "timeMin": _utc(since) or since,
        "timeMax": _utc(until) or until,
        # A weekly recurring series is not one meeting, so expand it.
        "singleEvents": "true",
        "orderBy": "startTime",   # only accepted alongside singleEvents
        "showDeleted": "true",
        "maxResults": str(int(ctx.settings.get("max_results", DEFAULT_MAX_RESULTS))),
    }

    out: list[dict] = []
    page_token = None
    for _ in range(int(ctx.settings.get("max_pages", DEFAULT_MAX_PAGES))):
        page = dict(params)
        if page_token:
            page["pageToken"] = page_token
        listing = _proxy(ctx, path, page, calendar_id)
        for ev in listing.get("items") or []:
            if ev.get("id"):
                out.append(_normalize(ev))
        page_token = listing.get("nextPageToken")
        if not page_token:
            break
    return out
