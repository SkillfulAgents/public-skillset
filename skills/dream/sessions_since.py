#!/usr/bin/env python3
"""List the sessions a dream should read: active after the cursor, not dreams themselves."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone

LIST_SESSIONS = "/opt/gamut/bin/list-sessions.py"
DREAM_RUN_RE = re.compile(r"run the dream skill", re.IGNORECASE)


def parse_ts(value: str) -> datetime:
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", required=True, help="ISO timestamp cursor (last_run_at)")
    args = parser.parse_args()
    cursor = parse_ts(args.since)

    out = subprocess.run(
        [sys.executable, LIST_SESSIONS, "--json", "--limit", "0", "--since", cursor.date().isoformat()],
        check=True, capture_output=True, text=True,
    ).stdout
    sessions = [s for s in json.loads(out) if parse_ts(s["last_activity"]) > cursor]

    picked, dreams = [], 0
    for s in sessions:
        if DREAM_RUN_RE.search(s.get("first_user_message") or ""):
            dreams += 1
            continue
        picked.append({k: s[k] for k in ("session_id", "started", "last_activity", "bytes", "name")})

    picked.sort(key=lambda s: s["last_activity"])
    latest = max((s["last_activity"] for s in sessions), default=None)
    json.dump({"sessions": picked, "skipped_dream_runs": dreams, "latest_activity": latest}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
