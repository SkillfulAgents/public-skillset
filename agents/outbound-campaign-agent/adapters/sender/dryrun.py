"""Dry-run sender. Renders what would have been sent, sends nothing.

This is the default sender so a team can exercise the entire motion (sourcing,
enrichment, suppression, drafting, caps, cadence, reporting) before a single
real email leaves a mailbox. It makes no network call of any kind.

Message contract (shared by every sender adapter):

    {
      "to": "person@example.com",        required
      "subject": "...",                  required
      "body_html": "<p>...</p>",         required (inner HTML)
      "body_text": "...",                optional; derived from HTML if absent
      "from_email": "...", "from_name": "...", "reply_to": "...",
      "thread_id": None,                 provider thread to reply into
      "sender_id": "jane",
      "prospect_id": 12, "step_index": 0, "variant": "A", "channel": "email",
    }

Returns {"status", "provider", "message_id", "thread_id"}.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADAPTER = {
    "slot": "sender",
    "name": "dryrun",
    "description": "Writes the rendered message to a run log. Never touches the network.",
}

RUN_LOG = "run.jsonl"
_TAG = re.compile(r"<[^>]+>")
_PARA_BREAK = re.compile(r"</(p|div|h[1-6]|tr|ul|ol)>", re.I)
_LINE_BREAK = re.compile(r"<br\s*/?>|</li>", re.I)


def _out_dir(ctx) -> pathlib.Path:
    raw = ctx.settings.get("out_dir", "data/dry-runs")
    p = pathlib.Path(str(raw))
    if not p.is_absolute():
        p = ROOT / p
    p.mkdir(parents=True, exist_ok=True)
    return p


def _to_text(html: str) -> str:
    if not html:
        return ""
    text = _PARA_BREAK.sub("\n\n", html)
    text = _LINE_BREAK.sub("\n", text)
    text = _TAG.sub("", text)
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _next_seq(log_path: pathlib.Path) -> int:
    if not log_path.exists():
        return 1
    with log_path.open("r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip()) + 1


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(value or "unknown").lower()).strip("-")[:48]


def _render(message: dict, seq: int, at: str) -> str:
    body_html = message.get("body_html") or message.get("body") or ""
    body_text = message.get("body_text") or _to_text(body_html)
    from_email = message.get("from_email") or ""
    from_name = message.get("from_name") or ""
    sender_line = f"{from_name} <{from_email}>".strip() if from_name else from_email
    header_keys = [
        ("To", message.get("to")),
        ("From", sender_line),
        ("Reply-To", message.get("reply_to")),
        ("Subject", message.get("subject")),
        ("Thread-Id", message.get("thread_id")),
        ("Sender-Id", message.get("sender_id")),
        ("Prospect-Id", message.get("prospect_id")),
        ("Step-Index", message.get("step_index")),
        ("Variant", message.get("variant")),
        ("Channel", message.get("channel", "email")),
        ("Dry-Run-Seq", seq),
        ("Rendered-At", at),
    ]
    head = "\n".join(f"{k}: {v}" for k, v in header_keys if v not in (None, ""))
    return (
        f"{head}\n"
        f"{'=' * 72}\n"
        f"--- text/plain ---\n{body_text}\n\n"
        f"--- text/html ---\n{body_html}\n"
    )


def send(ctx, message: dict) -> dict:
    """Write the fully rendered message to disk and report a dry-run result."""
    out = _out_dir(ctx)
    log_path = out / RUN_LOG
    seq = _next_seq(log_path)
    at = dt.datetime.now(dt.timezone.utc).isoformat()

    rendered = _render(message, seq, at)
    txt_name = f"{seq:04d}_{_slug(message.get('to'))}.txt"
    (out / txt_name).write_text(rendered, encoding="utf-8")

    record = {
        "seq": seq,
        "rendered_at": at,
        "status": "dry_run",
        "provider": "dryrun",
        "message_id": f"dry-{seq}",
        "thread_id": None,
        "to": message.get("to"),
        "subject": message.get("subject"),
        "body_html": message.get("body_html") or message.get("body"),
        "body_text": message.get("body_text") or _to_text(
            message.get("body_html") or message.get("body") or ""),
        "sender_id": message.get("sender_id"),
        "prospect_id": message.get("prospect_id"),
        "step_index": message.get("step_index"),
        "variant": message.get("variant"),
        "channel": message.get("channel", "email"),
        "file": str(out / txt_name),
    }
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    return {
        "status": "dry_run",
        "provider": "dryrun",
        "message_id": f"dry-{seq}",
        "thread_id": None,
    }


def check_replies(ctx, since=None) -> list[dict]:
    """No mailbox exists in a dry run, so there is never a reply."""
    return []
