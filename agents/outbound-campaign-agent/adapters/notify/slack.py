"""Slack notifications.

Two auth paths, in order:
  1. `adapter_config.slack.token_env` names an env var holding a bot token, used
     directly against slack.com.
  2. Otherwise the connected-account proxy:
     {PROXY_BASE_URL}/{account_id}/slack.com/api/chat.postMessage

Em and en dashes are stripped before posting so channel copy matches the same
standard the message linter enforces on prospect-facing text.
"""
from __future__ import annotations

import json
import os
import pathlib
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "notify",
    "name": "slack",
    "description": "Posts to a Slack channel via bot token or the connected-account proxy.",
}

SLACK_HOST = "slack.com"
TOOLKIT = "slack"
DEFAULT_TIMEOUT = 30


class NotifyError(RuntimeError):
    pass


def strip_dashes(text: str) -> str:
    return (text or "").replace("—", "-").replace("–", "-")


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
    for acct in _connected_accounts().get(TOOLKIT) or []:
        if isinstance(acct, dict) and acct.get("id"):
            return acct["id"]
        if isinstance(acct, str) and acct:
            return acct
    raise NotifyError(
        "no Slack credentials. Set adapter_config.slack.token_env to an env var "
        f"holding a bot token, or connect a '{TOOLKIT}' account so it appears in "
        "CONNECTED_ACCOUNTS."
    )


def _request(url: str, token: str, body: dict, timeout: int) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise NotifyError(f"slack post failed ({e.code}): {detail}") from e
    except urllib.error.URLError as e:
        raise NotifyError(f"slack unreachable: {e.reason}") from e


def post(ctx, text: str) -> None:
    channel = ctx.settings.get("channel")
    if not channel:
        raise NotifyError("adapter_config.slack.channel is not set")

    body = {
        "channel": channel,
        "text": strip_dashes(text),
        "unfurl_links": False,
        "unfurl_media": False,
    }
    timeout = int(ctx.settings.get("timeout_seconds", DEFAULT_TIMEOUT))

    token_env = ctx.settings.get("token_env")
    bot_token = os.environ.get(str(token_env)) if token_env else None
    if bot_token:
        url = f"https://{SLACK_HOST}/api/chat.postMessage"
        token = bot_token
    else:
        base = ctx.secret("PROXY_BASE_URL").rstrip("/")
        token = ctx.secret("PROXY_TOKEN")
        url = f"{base}/{_account_id(ctx)}/{SLACK_HOST}/api/chat.postMessage"

    resp = _request(url, token, body, timeout)
    if not resp.get("ok"):
        raise NotifyError(
            f"slack rejected the post to {channel}: {resp.get('error') or resp}"
        )
