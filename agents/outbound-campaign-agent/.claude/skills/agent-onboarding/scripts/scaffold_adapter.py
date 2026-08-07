#!/usr/bin/env python3
"""Create a stub adapter for a vendor this template does not ship.

  uv run --with pyyaml scaffold_adapter.py --slot sender --name outlook \
      [--env GRAPH_TOKEN ...] [--description "..."]

Onboarding asks which tools the team uses, not which adapters are installed.
When the answer is a vendor with no builtin, this writes the module so the
config can name the team's real stack immediately. The stub satisfies the slot
contract, declares itself a scaffold, and raises on every call: fail-closed,
like everything else in this template. A wrong adapter silently corrupts data;
a stub that halts with instructions does not.

The slug becomes `adapters.<slot>: <name>` in config. Implement the functions
when the team is ready to go live on that vendor; until then, selftest and
validate_config report the slot as scaffolded rather than ready.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from lib import adapters  # noqa: E402

# Per-slot contract: (signature, return contract shown in the stub docstring).
CONTRACTS = {
    "sourcing": [(
        "fetch(ctx, limit)",
        "return a list of prospect dicts (linkedin_url, name, title, company,\n"
        "    company_domain, email, employee_count, industry, country)")],
    "enrichment": [(
        "enrich(ctx, prospect)",
        "return a dict of fields to merge onto the prospect, or {} for no hit.\n"
        "    Never fabricate; identity-gate matches before returning them")],
    "sender": [(
        "send(ctx, message)",
        "message has to_email, subject, body_html, sender (id/email/display_name).\n"
        "    return {'status': 'sent', 'message_id': ..., 'thread_id': ...}")],
    "crm": [
        ("lookup(ctx, prospect)",
         "return the CRM record dict for this person/company, or None"),
        ("record(ctx, event)",
         "write an engagement event (send, reply, meeting) to the CRM"),
    ],
    "calendar": [(
        "events(ctx, sender_email, since, until)",
        "ISO8601 UTC bounds. return normalized events: {provider_event_id,\n"
        "    title, starts_at, ends_at, attendees: [email, ...], organizer,\n"
        "    status, cancelled: bool}")],
    "suppression": [(
        "is_suppressed(ctx, prospect)",
        "return (hit: bool, reason: str). Raise on backend unreachable so the\n"
        "    fail-closed chain halts the run rather than proceeding blind")],
    "notify": [(
        "post(ctx, text)",
        "deliver text to the configured destination. Raise on failure")],
}

TEMPLATE = '''"""{title}: SCAFFOLD, not implemented.

Written by scaffold_adapter.py during onboarding because the team uses
{vendor} for the {slot} slot and no builtin ships for it.

Every function below raises until implemented. That is deliberate: the config
can already name the team's real stack, and nothing can silently no-op.

To implement:
  1. Read the slot contract at the top of lib/adapters.py.
  2. Look at a shipped adapter in adapters/{slot}/ for the conventions
     (ctx.settings for the adapter_config block, ctx.secret() for env vars,
     stdlib urllib for HTTP, no third-party deps).
  3. Replace the raise in each function. Delete the "scaffold" flag from
     ADAPTER when it is real.
  4. Re-run selftest.py and validate_config.py.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib.adapters import AdapterError  # noqa: E402

ADAPTER = {{
    "slot": "{slot}",
    "name": "{name}",
    "requires_env": {env!r},
    "description": "{description}",
    "scaffold": True,
}}

_MSG = ("adapter {slot}:{name} is a scaffold and is not implemented yet. "
        "Implement adapters/{slot}/{name}.py per the contract in "
        "lib/adapters.py, or switch adapters.{slot} to another adapter.")

'''

FUNC = '''
def {sig}:
    """{doc}"""
    raise AdapterError(_MSG)

'''


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=sorted(adapters.SLOTS))
    ap.add_argument("--name", required=True,
                    help="vendor slug, lowercase, becomes adapters.<slot>: <name>")
    ap.add_argument("--env", action="append", default=[],
                    help="env var NAME the vendor needs (repeatable). "
                         "Values go in .env, never in config.")
    ap.add_argument("--description", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    name = args.name.strip().lower().replace("-", "_")
    if not name.isidentifier():
        print(f"--name {args.name!r} must be a lowercase slug (letters, digits, "
              f"underscores)", file=sys.stderr)
        return 1

    path = adapters.ADAPTER_DIR / args.slot / f"{name}.py"
    if path.exists() and not args.force:
        print(f"{path.relative_to(ROOT)} already exists. It may be a real "
              f"implementation; refusing to overwrite without --force.",
              file=sys.stderr)
        return 1

    vendor = args.name.replace("_", " ").replace("-", " ").title()
    desc = args.description or f"{vendor} ({args.slot}). Scaffold: not implemented yet."

    body = TEMPLATE.format(title=f"{vendor} {args.slot} adapter", vendor=vendor,
                           slot=args.slot, name=name, env=args.env,
                           description=desc.replace('"', "'"))
    for sig, doc in CONTRACTS[args.slot]:
        fn = sig.split("(")[0]
        body += FUNC.format(sig=sig, doc=f"{doc}.")
        assert fn  # keeps the loop honest if CONTRACTS grows a malformed row

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)

    print(f"scaffolded {path.relative_to(ROOT)}")
    print(f"  config:   adapters.{args.slot}: {name}")
    if args.env:
        print(f"  secrets:  {', '.join(args.env)} (request via "
              f"mcp__user-input__request_secret; values live in .env)")
    print(f"  settings: add an `adapter_config.{name}` block if the vendor "
          f"needs configuration")
    print(f"  status:   fail-closed until implemented; selftest reports it "
          f"as scaffolded, not ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())
