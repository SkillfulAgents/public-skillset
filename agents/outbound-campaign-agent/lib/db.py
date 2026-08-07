"""SQLite state. Vendor-neutral by design.

The reference implementation this was extracted from had Gmail-specific columns
(`gmail_message_id`, `gmail_thread_id`) added by ALTER over time. Here they are
`provider_message_id` / `provider_thread_id` plus a `provider` column, so the
same table serves Gmail, a sequencer, or a dry run.
"""
from __future__ import annotations

import contextlib
import json
import pathlib
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS campaigns (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  key           TEXT NOT NULL UNIQUE,
  name          TEXT NOT NULL,
  track         TEXT,
  enabled       INTEGER NOT NULL DEFAULT 0,
  approved_at   TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS prospects (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  external_id     TEXT,
  linkedin_url    TEXT UNIQUE,
  email           TEXT,
  personal_email  TEXT,
  first_name      TEXT,
  last_name       TEXT,
  name            TEXT,
  title           TEXT,
  buyer_tier      TEXT,
  company         TEXT,
  company_domain  TEXT,
  industry        TEXT,
  employee_count  INTEGER,
  icp_tier        TEXT,
  icp_reason      TEXT,
  country         TEXT,
  city            TEXT,
  phone           TEXT,
  enrichment_json TEXT,
  campaign_id     INTEGER REFERENCES campaigns(id),
  sender_id       TEXT,
  status          TEXT NOT NULL DEFAULT 'new',
  -- A LinkedIn connect step gates the message step that follows it. Without
  -- this the cadence would DM someone who never accepted.
  linkedin_accepted INTEGER NOT NULL DEFAULT 0,
  added_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sends (
  id                  INTEGER PRIMARY KEY AUTOINCREMENT,
  prospect_id         INTEGER NOT NULL REFERENCES prospects(id),
  step_index          INTEGER NOT NULL,
  channel             TEXT NOT NULL DEFAULT 'email',
  sender_id           TEXT,
  provider            TEXT,
  provider_message_id TEXT,
  provider_thread_id  TEXT,
  subject             TEXT,
  body                TEXT,
  variant             TEXT,
  confidence          REAL,
  bounced             INTEGER NOT NULL DEFAULT 0,
  sent_at             TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(prospect_id, step_index, channel)
);

CREATE TABLE IF NOT EXISTS replies (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  prospect_id    INTEGER NOT NULL REFERENCES prospects(id),
  replied_at     TEXT NOT NULL DEFAULT (datetime('now')),
  thread_id      TEXT,
  snippet        TEXT,
  sentiment      TEXT,
  is_positive    INTEGER,
  meeting_booked INTEGER NOT NULL DEFAULT 0,
  meeting_held   INTEGER NOT NULL DEFAULT 0,
  is_opportunity INTEGER NOT NULL DEFAULT 0,
  confidence     TEXT
);

-- Meetings are the outcome the motion exists to produce, and most of them never
-- touch `replies`: the prospect clicks a booking link and books without writing
-- back. Sourced from the sender's calendar, so they stand on their own rather
-- than as a flag on a reply that may not exist.
CREATE TABLE IF NOT EXISTS meetings (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  prospect_id       INTEGER REFERENCES prospects(id),
  sender_id         TEXT,
  provider          TEXT NOT NULL,
  provider_event_id TEXT,
  title             TEXT,
  attendee_email    TEXT,
  starts_at         TEXT,
  ends_at           TEXT,
  status            TEXT NOT NULL DEFAULT 'booked',
  source            TEXT NOT NULL DEFAULT 'calendar',
  booked_at         TEXT NOT NULL DEFAULT (datetime('now')),
  detected_at       TEXT NOT NULL DEFAULT (datetime('now')),
  notes             TEXT,
  UNIQUE(provider, provider_event_id)
);

-- Layer-3 suppression: everything this workspace has ever pulled.
CREATE TABLE IF NOT EXISTS seen (
  source_key    TEXT NOT NULL,
  row_key       TEXT NOT NULL,
  linkedin_slug TEXT,
  email         TEXT,
  domain        TEXT,
  name          TEXT,
  company       TEXT,
  status        TEXT NOT NULL DEFAULT 'seen',
  first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),
  run_dir       TEXT,
  PRIMARY KEY (source_key, row_key)
);

-- Drafts staged for operator review. This is the approval queue the dashboard
-- reads and writes: a draft the agent wants a human to see lands here as
-- 'pending', the operator approves or rejects it (dashboard or queue.py), and
-- send.py refuses to send anything staged here that a human has not approved.
-- Approving is NOT sending: the approved draft still passes every gate.
CREATE TABLE IF NOT EXISTS drafts (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  prospect_id     INTEGER NOT NULL REFERENCES prospects(id),
  step_index      INTEGER NOT NULL,
  channel         TEXT NOT NULL DEFAULT 'email',
  sender_id       TEXT,
  subject         TEXT,
  body            TEXT,
  variant         TEXT,
  confidence      REAL,
  status          TEXT NOT NULL DEFAULT 'pending',
  created_at      TEXT NOT NULL DEFAULT (datetime('now')),
  decided_at      TEXT,
  decided_via     TEXT,
  decision_reason TEXT,
  UNIQUE(prospect_id, step_index, channel)
);

-- Append-only audit of every gate decision. Without this you cannot answer
-- "why did this person get skipped" a week later.
CREATE TABLE IF NOT EXISTS decisions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  at          TEXT NOT NULL DEFAULT (datetime('now')),
  stage       TEXT NOT NULL,
  decision    TEXT NOT NULL,
  reason      TEXT,
  layer       TEXT,
  prospect_id INTEGER,
  ref         TEXT
);

CREATE INDEX IF NOT EXISTS idx_prospects_status   ON prospects(status);
CREATE INDEX IF NOT EXISTS idx_prospects_domain   ON prospects(company_domain);
CREATE INDEX IF NOT EXISTS idx_prospects_email    ON prospects(email);
CREATE INDEX IF NOT EXISTS idx_sends_prospect     ON sends(prospect_id);
CREATE INDEX IF NOT EXISTS idx_sends_sent_at      ON sends(sent_at);
CREATE INDEX IF NOT EXISTS idx_replies_prospect   ON replies(prospect_id);
CREATE INDEX IF NOT EXISTS idx_meetings_prospect  ON meetings(prospect_id);
CREATE INDEX IF NOT EXISTS idx_meetings_starts_at ON meetings(starts_at);
CREATE INDEX IF NOT EXISTS idx_seen_slug          ON seen(linkedin_slug);
CREATE INDEX IF NOT EXISTS idx_seen_email         ON seen(email);
CREATE INDEX IF NOT EXISTS idx_decisions_stage    ON decisions(stage);
CREATE INDEX IF NOT EXISTS idx_drafts_status      ON drafts(status);
"""

TERMINAL_STATUSES = {"replied", "meeting", "bounced", "suppressed", "unsubscribed"}
DRAFT_STATUSES = {"pending", "approved", "rejected", "sent"}


def connect(path: str | pathlib.Path) -> sqlite3.Connection:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init(path: str | pathlib.Path) -> sqlite3.Connection:
    """Idempotent create/migrate."""
    conn = connect(path)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def log_decision(conn, stage: str, decision: str, reason: str = "",
                 layer: str = "", prospect_id: int | None = None,
                 ref: str = "") -> None:
    conn.execute(
        "INSERT INTO decisions (stage, decision, reason, layer, prospect_id, ref)"
        " VALUES (?,?,?,?,?,?)",
        (stage, decision, reason, layer, prospect_id, ref),
    )


def upsert_prospect(conn, row: dict) -> int:
    """Insert or merge on linkedin_url. Never nulls out an existing value."""
    cols = {k: v for k, v in row.items() if k in _PROSPECT_COLS}
    if "enrichment_json" in cols and not isinstance(cols["enrichment_json"], str):
        cols["enrichment_json"] = json.dumps(cols["enrichment_json"])

    li = cols.get("linkedin_url")
    existing = None
    if li:
        existing = conn.execute(
            "SELECT * FROM prospects WHERE linkedin_url = ?", (li,)
        ).fetchone()
    if existing is None and cols.get("email"):
        existing = conn.execute(
            "SELECT * FROM prospects WHERE email = ?", (cols["email"],)
        ).fetchone()

    if existing:
        updates = {k: v for k, v in cols.items()
                   if v not in (None, "") and k != "linkedin_url"}
        if updates:
            sets = ", ".join(f"{k} = ?" for k in updates)
            conn.execute(f"UPDATE prospects SET {sets} WHERE id = ?",
                         (*updates.values(), existing["id"]))
        return existing["id"]

    keys = list(cols)
    cur = conn.execute(
        f"INSERT INTO prospects ({', '.join(keys)}) "
        f"VALUES ({', '.join('?' * len(keys))})",
        tuple(cols[k] for k in keys),
    )
    return cur.lastrowid


_PROSPECT_COLS = {
    "external_id", "linkedin_url", "email", "personal_email", "first_name",
    "last_name", "name", "title", "buyer_tier", "company", "company_domain",
    "industry", "employee_count", "icp_tier", "icp_reason", "country", "city",
    "phone", "enrichment_json", "campaign_id", "sender_id", "status",
}


_MEETING_COLS = {
    "prospect_id", "sender_id", "provider", "provider_event_id", "title",
    "attendee_email", "starts_at", "ends_at", "status", "source", "booked_at",
    "detected_at", "notes",
}

MEETING_STATUSES = {"booked", "held", "no_show", "cancelled"}
MEETING_SOURCES = {"calendar", "reply", "manual"}

# A calendar only ever knows an event is on the books. Attendance is decided
# here, by a human or by an outcome the calendar cannot see, so a re-sync that
# reports 'booked' must not overwrite it.
_LOCALLY_DECIDED = {"held", "no_show"}


def upsert_meeting(conn, rec: dict) -> int:
    """Insert or merge on (provider, provider_event_id). Safe to re-run."""
    cols = {k: v for k, v in rec.items() if k in _MEETING_COLS}
    provider = cols.get("provider")
    if not provider:
        raise ValueError("a meeting record must carry a provider")

    event_id = cols.get("provider_event_id")
    existing = None
    if event_id:
        existing = conn.execute(
            "SELECT * FROM meetings WHERE provider = ? AND provider_event_id = ?",
            (provider, event_id),
        ).fetchone()

    if existing is None:
        keys = list(cols)
        cur = conn.execute(
            f"INSERT INTO meetings ({', '.join(keys)}) "
            f"VALUES ({', '.join('?' * len(keys))})",
            tuple(cols[k] for k in keys),
        )
        return cur.lastrowid

    updates = {k: v for k, v in cols.items() if v not in (None, "")}
    if updates.get("status") == "booked" and existing["status"] in _LOCALLY_DECIDED:
        updates.pop("status")
    # A re-sync is not a re-booking, so the first sighting keeps the timestamp.
    updates.pop("booked_at", None)
    updates.pop("detected_at", None)

    sets = ", ".join(f"{k} = ?" for k in updates)
    sets = f"{sets}, detected_at = datetime('now')" if sets else "detected_at = datetime('now')"
    conn.execute(f"UPDATE meetings SET {sets} WHERE id = ?",
                 (*updates.values(), existing["id"]))
    return existing["id"]


def stage_draft(conn, rec: dict) -> int:
    """Insert or replace the staged draft for (prospect, step, channel).

    Re-staging a PENDING or REJECTED draft overwrites it (the copy was
    revised); an APPROVED or SENT draft is never silently replaced, because
    that would swap copy under an approval a human already gave.
    """
    existing = conn.execute(
        "SELECT id, status FROM drafts WHERE prospect_id = ? AND step_index = ?"
        " AND channel = ?",
        (rec["prospect_id"], rec["step_index"], rec.get("channel", "email")),
    ).fetchone()
    if existing and existing["status"] in ("approved", "sent"):
        raise ValueError(
            f"draft {existing['id']} is {existing['status']}; refuse to replace "
            f"copy under an approval. Reject it first if the copy must change.")
    if existing:
        conn.execute("DELETE FROM drafts WHERE id = ?", (existing["id"],))
    cur = conn.execute(
        "INSERT INTO drafts (prospect_id, step_index, channel, sender_id,"
        " subject, body, variant, confidence) VALUES (?,?,?,?,?,?,?,?)",
        (rec["prospect_id"], rec["step_index"], rec.get("channel", "email"),
         rec.get("sender_id"), rec.get("subject"), rec.get("body"),
         rec.get("variant"), rec.get("confidence")))
    return cur.lastrowid


def draft_for(conn, prospect_id: int, step_index: int, channel: str = "email"):
    return conn.execute(
        "SELECT * FROM drafts WHERE prospect_id = ? AND step_index = ?"
        " AND channel = ?", (prospect_id, step_index, channel)).fetchone()


def sends_today(conn, sender_id: str | None = None, day: str | None = None,
                channel: str = "email",
                between: tuple[str, str] | None = None) -> int:
    """Touches already recorded today on one channel, for cap enforcement.

    `sent_at` is stored in UTC, but the cap is per OPERATOR day. Callers that
    know the operator timezone pass `between` as the UTC bounds of the local
    day; comparing a UTC date against a local date string undercounts every
    send logged after 00:00 UTC but before local midnight, which is exactly
    the evening window where a cap overshoot burns the domain.
    """
    if between:
        q = ("SELECT COUNT(*) FROM sends WHERE channel = ? "
             "AND sent_at >= ? AND sent_at < ?")
        args: list = [channel, between[0], between[1]]
    else:
        q = ("SELECT COUNT(*) FROM sends WHERE channel = ? "
             "AND date(sent_at) = COALESCE(?, date('now'))")
        args = [channel, day]
    if sender_id:
        q += " AND sender_id = ?"
        args.append(sender_id)
    return conn.execute(q, args).fetchone()[0]


def has_replied(conn, prospect_id: int) -> bool:
    return conn.execute(
        "SELECT 1 FROM replies WHERE prospect_id = ? LIMIT 1", (prospect_id,)
    ).fetchone() is not None


def company_touched_recently(conn, domain: str, days: int,
                             exclude_prospect_id: int | None = None) -> bool:
    """True if any OTHER contact at this domain was touched within `days`.

    `exclude_prospect_id` exists because pacing is about not hitting two people
    at one company on the same day; a prospect's own earlier touch (the day-0
    invite before the day-0 email) must not block their own cadence.
    """
    if not domain or days <= 0:
        return False
    q = ("SELECT 1 FROM sends s JOIN prospects p ON p.id = s.prospect_id "
         "WHERE p.company_domain = ? AND s.sent_at >= datetime('now', ?)")
    args: list = [domain, f"-{int(days)} days"]
    if exclude_prospect_id is not None:
        q += " AND s.prospect_id != ?"
        args.append(exclude_prospect_id)
    return conn.execute(q + " LIMIT 1", args).fetchone() is not None


@contextlib.contextmanager
def transaction(conn):
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
