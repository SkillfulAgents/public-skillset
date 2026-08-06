"""Bootstrap the nutrition SQLite database. Safe to re-run (idempotent)."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from db import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS meals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- ISO-8601 timestamp WITH timezone offset, recorded in America/Los_Angeles
    ts TEXT NOT NULL,
    -- local date (YYYY-MM-DD) in America/Los_Angeles, denormalized for fast grouping
    local_day TEXT NOT NULL,
    -- breakfast | lunch | dinner | snack
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_meals_day ON meals(local_day);
CREATE INDEX IF NOT EXISTS idx_meals_ts ON meals(ts);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- effective_from is local date the goal becomes active; current goal = latest row
    effective_from TEXT NOT NULL,
    calories REAL NOT NULL,
    protein_g REAL NOT NULL,
    fat_g REAL NOT NULL,
    carbs_g REAL NOT NULL,
    rationale TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS weights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    -- local date (YYYY-MM-DD) in America/Los_Angeles; one weight per day (latest wins)
    local_day TEXT NOT NULL UNIQUE,
    weight_lbs REAL NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weights_day ON weights(local_day);
"""


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
    print(f"Initialized DB at {DB_PATH}")


if __name__ == "__main__":
    main()
