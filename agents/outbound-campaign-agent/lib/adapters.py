"""Adapter registry: the portability seam.

Every vendor touchpoint is a capability SLOT. The motion (ICP rules, cadence,
copy standards, caps, suppression order, reporting) is vendor-neutral and lives
in this template. Vendors are swappable modules under `adapters/<slot>/<name>.py`.

Contract: an adapter module declares:

    ADAPTER = {
        "slot": "enrichment",
        "name": "apollo",
        "requires_env": ["APOLLO_API_KEY"],   # optional
        "description": "one line, shown by list_adapters.py",
    }

and implements the functions its slot requires:

    sourcing     fetch(ctx, limit) -> list[dict]      prospect dicts
    enrichment   enrich(ctx, prospect) -> dict        fields to merge (may be {})
    sender       send(ctx, message) -> dict           {status, message_id, thread_id}
                 check_replies(ctx, since) -> list[dict]   optional
    crm          lookup(ctx, prospect) -> dict|None
                 record(ctx, event) -> None
    calendar     events(ctx, sender_email, since, until) -> list[dict]
    suppression  is_suppressed(ctx, prospect) -> tuple[bool, str]   (hit, reason)
    notify       post(ctx, text) -> None

`ctx` is an AdapterContext: `.config` (full Config), `.settings` (that adapter's
block from `adapter_config`), `.name`, `.slot`.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
from dataclasses import dataclass, field

ROOT = pathlib.Path(__file__).resolve().parents[1]
ADAPTER_DIR = ROOT / "adapters"

SLOTS = {
    "sourcing":    ["fetch"],
    "enrichment":  ["enrich"],
    "sender":      ["send"],
    "crm":         ["lookup", "record"],
    "calendar":    ["events"],
    "suppression": ["is_suppressed"],
    "notify":      ["post"],
}

# Only `none` is built in; every other slot value must resolve to a module.
PSEUDO = {"none"}


class AdapterError(RuntimeError):
    pass


@dataclass
class AdapterContext:
    config: object
    slot: str
    name: str
    settings: dict = field(default_factory=dict)

    def secret(self, env_name: str) -> str:
        val = os.environ.get(env_name)
        if not val:
            raise AdapterError(
                f"[{self.slot}:{self.name}] ${env_name} is not set in the environment"
            )
        return val


@dataclass
class Adapter:
    slot: str
    name: str
    module: object
    meta: dict

    def __getattr__(self, item):
        fn = getattr(self.module, item, None)
        if fn is None:
            raise AdapterError(
                f"adapter {self.slot}:{self.name} does not implement {item}()"
            )
        return fn

    def supports(self, fn_name: str) -> bool:
        return callable(getattr(self.module, fn_name, None))


def _load_module(slot: str, name: str):
    path = ADAPTER_DIR / slot / f"{name}.py"
    if not path.exists():
        available = sorted(
            p.stem for p in (ADAPTER_DIR / slot).glob("*.py")
            if not p.stem.startswith("_")
        ) if (ADAPTER_DIR / slot).exists() else []
        raise AdapterError(
            f"no {slot} adapter named {name!r} (looked in {path}).\n"
            f"Installed {slot} adapters: {available or 'none'}"
        )
    spec = importlib.util.spec_from_file_location(f"adapters.{slot}.{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(config, slot: str, name: str | None = None) -> Adapter | None:
    """Resolve one adapter for a slot. Returns None for disabled slots."""
    if slot not in SLOTS:
        raise AdapterError(f"unknown slot {slot!r}; valid: {sorted(SLOTS)}")

    if name is None:
        name = config.get(f"adapters.{slot}")
        if isinstance(name, list):
            raise AdapterError(
                f"adapters.{slot} is a list; use load_chain() for ordered slots"
            )
    if name in (None, "none"):
        return None

    mod = _load_module(slot, name)
    meta = getattr(mod, "ADAPTER", {}) or {}

    missing = [fn for fn in SLOTS[slot] if not callable(getattr(mod, fn, None))]
    if missing:
        raise AdapterError(
            f"adapter {slot}:{name} is missing required function(s): {missing}"
        )

    for env_name in meta.get("requires_env", []):
        if env_name not in os.environ:
            raise AdapterError(
                f"adapter {slot}:{name} requires ${env_name}, which is not set. "
                f"Add it to .env, or switch adapters.{slot} to another adapter."
            )
    return Adapter(slot, name, mod, meta)


def load_chain(config, slot: str) -> list[Adapter]:
    """Resolve an ordered slot (enrichment waterfall, suppression layers).

    Pseudo-names are preserved by the caller, not loaded here.
    """
    names = config.get(f"adapters.{slot}")
    names = names if isinstance(names, list) else [names]
    out = []
    for n in names:
        if n in PSEUDO or n is None:
            continue
        a = load(config, slot, n)
        if a:
            out.append(a)
    return out


def context(config, adapter: Adapter) -> AdapterContext:
    """Resolve one adapter's settings block.

    A bare vendor name collides across slots: Google is both a mailbox and a
    calendar, and they need different account ids. `<name>_<slot>` wins over
    `<name>` so a vendor can be configured per slot without renaming either.
    """
    blocks = config.get("adapter_config") or {}
    settings = (blocks.get(f"{adapter.name}_{adapter.slot}")
                or blocks.get(adapter.name) or {})
    return AdapterContext(config=config, slot=adapter.slot,
                          name=adapter.name, settings=settings)


def discover() -> dict[str, list[dict]]:
    """Every installed adapter, for `list_adapters.py` and onboarding."""
    found: dict[str, list[dict]] = {}
    for slot in SLOTS:
        d = ADAPTER_DIR / slot
        if not d.exists():
            found[slot] = []
            continue
        entries = []
        for p in sorted(d.glob("*.py")):
            if p.stem.startswith("_"):
                continue
            try:
                meta = getattr(_load_module(slot, p.stem), "ADAPTER", {}) or {}
            except Exception as e:
                meta = {"description": f"(failed to import: {e})", "broken": True}
            entries.append({
                "name": p.stem,
                "description": meta.get("description", ""),
                "requires_env": meta.get("requires_env", []),
                "broken": meta.get("broken", False),
                # Declared by scaffold_adapter.py stubs: the module loads and
                # satisfies the contract, but every call raises until someone
                # implements it. Selftest and validation report it as such
                # instead of calling it ready.
                "scaffold": bool(meta.get("scaffold", False)),
                "env_ready": all(k in os.environ for k in meta.get("requires_env", [])),
            })
        found[slot] = entries
    return found
