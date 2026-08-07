"""Gmail sender via the connected-account proxy.

The proxy signs requests with the workspace OAuth grant, so no Google client
library and no refresh-token handling live here. Every call is:

    {PROXY_BASE_URL}/{account_id}/gmail.googleapis.com/{path}
    Authorization: Bearer {PROXY_TOKEN}

Account resolution order:
  1. `adapter_config.gmail.connected_account_id_env` names an env var holding
     the account id.
  2. Otherwise the first account under toolkit "gmail" in CONNECTED_ACCOUNTS.

Message contract is the one documented in `sender/dryrun.py`.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import identity  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "sender",
    "name": "gmail",
    "requires_env": ["PROXY_BASE_URL", "PROXY_TOKEN"],
    "description": "Sends and polls replies through a connected Gmail account (proxy, stdlib only).",
}

GMAIL_HOST = "gmail.googleapis.com"
TOOLKIT = "gmail"
DEFAULT_TIMEOUT = 30

_TAG = re.compile(r"<[^>]+>")
_PARA_BREAK = re.compile(r"</(p|div|h[1-6]|tr|ul|ol)>", re.I)
_LINE_BREAK = re.compile(r"<br\s*/?>|</li>", re.I)

PIXEL_PATTERN = re.compile(
    r"<img[^>]*(?:width\s*=\s*[\"']?1[\"']?|height\s*=\s*[\"']?1[\"']?)[^>]*>", re.I)
TRACKER_PATTERNS = [
    r"utm_[a-z]+=", r"\bmailtrack\b", r"\bhubspotlinks?\.com\b", r"\bsendgrid\.net\b",
    r"\bmailchi\.mp\b", r"\bclick\.[a-z0-9-]+\.com\b", r"\btrk\.", r"\bt\.co/",
    r"\blnkd\.in\b", r"\bbit\.ly\b", r"\btinyurl\.com\b", r"\bmailgun\b",
    r"\bcustomeriomail\b", r"\bsparkpostmail\b", r"open\.gif", r"pixel\.(png|gif)",
]
_TRACKERS = [re.compile(p, re.I) for p in TRACKER_PATTERNS]


class GmailError(RuntimeError):
    pass


class TrackingArtifactError(GmailError):
    """Raised instead of silently rewriting the body. The draft must be fixed upstream."""


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
    accounts = _connected_accounts().get(TOOLKIT) or []
    for acct in accounts:
        if isinstance(acct, dict) and acct.get("id"):
            return acct["id"]
        if isinstance(acct, str) and acct:
            return acct
    raise GmailError(
        "no Gmail account available. Set "
        f"{env_name or 'adapter_config.gmail.connected_account_id_env'} to an env var "
        f"holding the account id, or connect a '{TOOLKIT}' account so it appears in "
        "CONNECTED_ACCOUNTS."
    )


def _proxy(ctx, path: str, method: str = "GET", body: dict | None = None,
           params: dict | None = None) -> dict:
    base = ctx.secret("PROXY_BASE_URL").rstrip("/")
    token = ctx.secret("PROXY_TOKEN")
    url = f"{base}/{_account_id(ctx)}/{GMAIL_HOST}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    timeout = int(ctx.settings.get("timeout_seconds", DEFAULT_TIMEOUT))
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise GmailError(f"gmail {method} {path} failed ({e.code}): {detail}") from e
    except urllib.error.URLError as e:
        raise GmailError(f"gmail {method} {path} unreachable: {e.reason}") from e
    return json.loads(payload) if payload else {}


def _to_text(html: str) -> str:
    if not html:
        return ""
    text = _PARA_BREAK.sub("\n\n", html)
    text = _LINE_BREAK.sub("\n", text)
    text = _TAG.sub("", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def assert_no_tracking(subject: str, body: str) -> None:
    """Last-line defence. Detect and refuse; never silently mutate a draft."""
    if PIXEL_PATTERN.search(body or ""):
        raise TrackingArtifactError(
            "refusing to send: body contains a 1x1 tracking pixel. "
            "Remove it from the draft; open tracking is not used by this motion."
        )
    blob = f"{subject or ''}\n{body or ''}"
    for pat in _TRACKERS:
        m = pat.search(blob)
        if m:
            raise TrackingArtifactError(
                f"refusing to send: wrapped or tracked link detected ({m.group(0)!r}). "
                "Use the bare destination URL."
            )


def _build_raw(message: dict) -> str:
    to = message.get("to")
    if not to:
        raise GmailError("message has no 'to' address")
    subject = message.get("subject") or ""
    body_html = message.get("body_html") or message.get("body") or ""
    body_text = message.get("body_text") or _to_text(body_html)

    assert_no_tracking(subject, body_html)

    mime = MIMEMultipart("alternative")
    mime["To"] = to
    mime["Subject"] = subject
    if message.get("from_email"):
        mime["From"] = formataddr(
            (message.get("from_name") or "", message["from_email"]))
    if message.get("reply_to"):
        mime["Reply-To"] = message["reply_to"]
    if message.get("cc"):
        mime["Cc"] = message["cc"]
    if message.get("in_reply_to"):
        mime["In-Reply-To"] = message["in_reply_to"]
        mime["References"] = message.get("references") or message["in_reply_to"]
    mime.attach(MIMEText(body_text, "plain", "utf-8"))
    mime.attach(MIMEText(body_html or body_text, "html", "utf-8"))
    return base64.urlsafe_b64encode(mime.as_bytes()).decode()


def send(ctx, message: dict) -> dict:
    payload: dict = {"raw": _build_raw(message)}
    if message.get("thread_id"):
        payload["threadId"] = message["thread_id"]
    resp = _proxy(ctx, "/gmail/v1/users/me/messages/send", method="POST", body=payload)
    return {
        "status": "sent",
        "provider": "gmail",
        "message_id": resp.get("id"),
        "thread_id": resp.get("threadId"),
    }


def _as_datetime(since) -> dt.datetime | None:
    if since in (None, ""):
        return None
    if isinstance(since, dt.datetime):
        return since if since.tzinfo else since.replace(tzinfo=dt.timezone.utc)
    if isinstance(since, dt.date):
        return dt.datetime(since.year, since.month, since.day, tzinfo=dt.timezone.utc)
    if isinstance(since, (int, float)):
        return dt.datetime.fromtimestamp(float(since), dt.timezone.utc)
    text = str(since).replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def _is_from_me(msg: dict) -> bool:
    return "SENT" in (msg.get("labelIds") or [])


def check_replies(ctx, since=None) -> list[dict]:
    """Inbound messages on threads this mailbox started, newer than `since`.

    A thread with a single message is the opener sitting unanswered, so only
    threads whose last message is not ours count as a reply.
    """
    cutoff = _as_datetime(since)
    query = ["from:me", "-in:chats"]
    if cutoff:
        query.append(f"after:{cutoff.astimezone(dt.timezone.utc):%Y/%m/%d}")
    extra = ctx.settings.get("reply_query_extra")
    if extra:
        query.append(str(extra))

    out: list[dict] = []
    page_token = None
    max_pages = int(ctx.settings.get("reply_max_pages", 5))
    for _ in range(max_pages):
        params = {"q": " ".join(query), "maxResults": "100"}
        if page_token:
            params["pageToken"] = page_token
        listing = _proxy(ctx, "/gmail/v1/users/me/threads", params=params)
        for stub in listing.get("threads") or []:
            thread = _proxy(
                ctx,
                f"/gmail/v1/users/me/threads/{stub['id']}",
                params={
                    "format": "metadata",
                    "metadataHeaders": "From",
                },
            )
            messages = thread.get("messages") or []
            if len(messages) <= 1 or not _is_from_me(messages[0]):
                continue
            last = messages[-1]
            if _is_from_me(last):
                continue
            received = dt.datetime.fromtimestamp(
                int(last.get("internalDate", 0)) / 1000, dt.timezone.utc)
            if cutoff and received < cutoff:
                continue
            headers = {h["name"].lower(): h["value"]
                       for h in (last.get("payload") or {}).get("headers") or []}
            sender = headers.get("from", "")
            out.append({
                "thread_id": thread.get("id") or stub["id"],
                "from": sender,
                "from_domain": identity.email_domain(
                    sender.split("<")[-1].strip(" <>")),
                "snippet": last.get("snippet") or "",
                "received_at": received.isoformat(),
            })
        page_token = listing.get("nextPageToken")
        if not page_token:
            break
    return out
