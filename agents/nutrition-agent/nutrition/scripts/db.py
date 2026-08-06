"""Shared DB helpers for nutrition tracking. All day boundaries use America/Los_Angeles."""
from __future__ import annotations
import sqlite3
from datetime import datetime, date
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "nutrition.db"
GOAL_PATH = ROOT / "data" / "goal.json"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now_local() -> datetime:
    return datetime.now(TZ)


def today_local() -> date:
    return now_local().date()


def local_day(ts_iso: str) -> str:
    """Convert a stored ISO timestamp to local YYYY-MM-DD."""
    dt = datetime.fromisoformat(ts_iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ).date().isoformat()
