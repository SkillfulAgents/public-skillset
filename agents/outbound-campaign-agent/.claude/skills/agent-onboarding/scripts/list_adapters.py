#!/usr/bin/env python3
"""Orient on the adapter layer: installed modules, and the interview menu.

  uv run --with pyyaml list_adapters.py [--json]

Run this at the START of onboarding, for YOUR orientation only. Do not read
the installed list to the operator as "what's available": the shipped modules
are reference implementations, not the menu. The interview asks which tools
the TEAM uses (the `common choices` below, plus Other), and a vendor with no
builtin gets a stub via scaffold_adapter.py rather than a steer toward
whatever happens to ship.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from lib import adapters  # noqa: E402

CATALOG = ROOT / "adapters" / "catalog.yaml"

BLURB = {
    "sourcing": "where net-new prospects come from",
    "enrichment": "fills missing email / firmographics (ordered waterfall, first hit wins)",
    "sender": "delivers the message",
    "crm": "system of record for engagement",
    "calendar": "reads booked meetings off the sender's calendar (the outcome metric)",
    "suppression": "decides who must NOT be contacted (ordered, fail-closed)",
    "notify": "operator notifications",
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    found = adapters.discover()
    catalog = yaml.safe_load(CATALOG.read_text()) if CATALOG.exists() else {}

    if args.json:
        print(json.dumps({"installed": found, "catalog": catalog}, indent=2))
        return 0

    current = {}
    try:
        from lib import config as cfgmod
        cfg = cfgmod.load()
        current = cfg.get("adapters", {}) or {}
        print(f"Config: {cfg.config_path.name}\n")
    except Exception:
        print("Config: none yet (this workspace has not been onboarded)\n")

    blocked = 0
    for slot in adapters.SLOTS:
        entries = found.get(slot, [])
        sel = current.get(slot)
        sel_list = sel if isinstance(sel, list) else ([sel] if sel else [])
        print(f"{slot.upper():<12} {BLURB.get(slot, '')}")

        print("  installed:")
        if not entries:
            print("    (none)")
        for e in entries:
            mark = "*" if e["name"] in sel_list else " "
            if e["broken"]:
                state = "BROKEN"
            elif e["scaffold"]:
                state = "scaffold (not implemented)"
            elif not e["env_ready"]:
                missing = [k for k in e["requires_env"]
                           if k not in __import__("os").environ]
                state = f"needs ${', $'.join(missing)}"
                blocked += 1
            else:
                state = "ready"
            print(f"  {mark} {e['name']:<14} {state:<28} {e['description']}")

        common = catalog.get(slot) or []
        if common:
            installed_names = {e["name"] for e in entries}
            print("  common choices to offer the operator:")
            for c in common:
                tag = ("builtin" if c.get("builtin")
                       else "installed" if c["name"] in installed_names
                       else "scaffold on choice")
                note = c.get("note", "")
                print(f"    {c['label']:<38} [{tag}]  {note}")
        if sel_list:
            print(f"  selected: {' then '.join(str(s) for s in sel_list)}")
        print()

    print("  * = currently selected in config")
    print("  Any vendor not listed: scaffold_adapter.py --slot <slot> --name <slug> "
          "creates the stub; the operator's answer is never limited to this file.")
    if blocked:
        print(f"\n{blocked} adapter(s) need credentials. Add them to .env, or request "
              f"them with mcp__user-input__request_secret.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
