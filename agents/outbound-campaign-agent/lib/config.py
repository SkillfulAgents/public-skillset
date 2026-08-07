"""Config loading and resolution.

Every skill script starts here. Nothing in this template reads a company name,
a cap, an ICP rule, or a vendor choice from anywhere else.
"""
from __future__ import annotations

import datetime as dt
import html
import os
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "outbound.yaml"
EXAMPLE_CONFIG = ROOT / "config" / "outbound.example.yaml"


class ConfigError(RuntimeError):
    pass


class Config:
    """Dotted-path read-only view over the config file."""

    def __init__(self, data: dict, path: pathlib.Path):
        self._d = data
        self.config_path = path

    def get(self, dotted: str, default=None):
        node = self._d
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def require(self, dotted: str):
        val = self.get(dotted, _MISSING)
        if val is _MISSING or val is None or (isinstance(val, str) and not val.strip()):
            raise ConfigError(
                f"{dotted} is required but missing/empty in {self.config_path.name}. "
                f"Run the agent-onboarding skill, or edit the file directly."
            )
        return val

    def __repr__(self) -> str:
        return f"<Config {self.config_path.name} company={self.get('company.name')!r}>"

    # -- identity -------------------------------------------------------

    @property
    def brand(self) -> str:
        """The name safe to use in prospect-facing copy right now.

        Falls back to the legal entity while the product brand is embargoed,
        so a pre-launch team cannot leak an unannounced name into a cold email.
        """
        launch = self.get("company.brand_public_from")
        product = self.require("company.product_name")
        if isinstance(launch, dt.date) and launch > dt.date.today():
            return self.require("company.name")
        return product

    @property
    def brand_is_public(self) -> bool:
        launch = self.get("company.brand_public_from")
        return not (isinstance(launch, dt.date) and launch > dt.date.today())

    @property
    def forbidden_names(self) -> list[str]:
        names = list(self.get("company.forbidden_names", []) or [])
        if not self.brand_is_public:
            names.append(self.require("company.product_name"))
        return names

    @property
    def tz(self):
        from zoneinfo import ZoneInfo
        return ZoneInfo(self.require("operator.timezone"))

    def now(self) -> dt.datetime:
        return dt.datetime.now(self.tz)

    # -- senders --------------------------------------------------------

    @property
    def senders(self) -> list[dict]:
        return list(self.get("senders", []) or [])

    def sender(self, sender_id: str) -> dict:
        for s in self.senders:
            if s.get("id") == sender_id:
                return s
        raise ConfigError(
            f"unknown sender {sender_id!r}; configured: "
            f"{[s.get('id') for s in self.senders]}"
        )

    def effective_cap(self, sender_id: str, weeks_live: int = 0) -> int:
        """Daily cap for a sender, honouring an in-progress ramp.

        A warming mailbox opened at full volume is the fastest way to land a
        new domain in spam, so the ramp floor wins until it reaches the cap.
        """
        s = self.sender(sender_id)
        cap = int(s.get("daily_email_cap", 0))
        if s.get("status") == "paused":
            return 0
        ramp = s.get("ramp")
        if s.get("status") == "warming" and isinstance(ramp, dict):
            start = int(ramp.get("start_cap", cap))
            step = int(ramp.get("increment_per_week", 0))
            target = min(int(ramp.get("target_cap", cap)), cap)
            return max(0, min(target, start + step * max(0, weeks_live)))
        return cap

    @property
    def total_daily_capacity(self) -> int:
        return sum(self.effective_cap(s["id"]) for s in self.senders if s.get("id"))

    # -- schedule -------------------------------------------------------

    @property
    def send_days(self) -> set[str]:
        return {str(d).lower()[:3] for d in (self.get("limits.send_days") or [])}

    def in_send_window(self, when: dt.datetime | None = None) -> tuple[bool, str]:
        """(allowed, human reason). Reason is always populated, for logging."""
        when = when or self.now()
        day = when.strftime("%a").lower()
        if day not in self.send_days:
            return False, f"{day} is not a send day ({sorted(self.send_days)})"

        window = self.get("limits.send_window_local")
        if window:
            start_s, end_s = str(window).split("-")
            hhmm = when.strftime("%H:%M")
            if not (start_s <= hhmm <= end_s):
                return False, f"{hhmm} is outside the send window {window}"
        return True, "in window"

    # -- paths ----------------------------------------------------------

    def path(self, dotted: str, default: str | None = None) -> pathlib.Path:
        """Resolve a config path value against the template root."""
        val = self.get(dotted, default)
        if not val:
            raise ConfigError(f"{dotted} is not set and has no default")
        p = pathlib.Path(str(val))
        return p if p.is_absolute() else (ROOT / p)

    def secret(self, dotted_env_key: str) -> str:
        """Read a secret by the NAME stored in config. Values never live here."""
        env_name = self.get(dotted_env_key)
        if not env_name:
            raise ConfigError(f"{dotted_env_key} is not set")
        val = os.environ.get(str(env_name))
        if not val:
            raise ConfigError(
                f"${env_name} is not set in the environment "
                f"(required by {dotted_env_key}). Add it to .env."
            )
        return val

    # -- rendering ------------------------------------------------------

    _TOKEN = re.compile(r"\{([a-z_]+(?:\.[a-z_]+)*)\}")

    def render(self, text: str) -> str:
        """Expand {dotted.path} tokens, e.g. in signature lines."""
        def sub(m):
            val = self.get(m.group(1), _MISSING)
            if val is _MISSING:
                raise ConfigError(f"unknown token {{{m.group(1)}}} in template text")
            return "" if val is None else str(val)
        return self._TOKEN.sub(sub, text)

    @property
    def signature(self) -> str:
        lines = self.get("message_standards.signature.lines", []) or []
        return "\n".join(self.render(str(l)) for l in lines).strip()

    @property
    def signature_html(self) -> str:
        """The signature as its own paragraph, which is what produces the one
        blank line before it that every client renders consistently."""
        lines = [self.render(str(l)) for l in
                 (self.get("message_standards.signature.lines", []) or [])]
        lines = [html.escape(l) for l in lines if l.strip()]
        return f"<p>{'<br>'.join(lines)}</p>" if lines else ""


_MISSING = object()


def load(path: str | pathlib.Path | None = None) -> Config:
    p = pathlib.Path(path) if path else DEFAULT_CONFIG
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        raise ConfigError(
            f"No config at {p}.\n"
            f"This workspace has not been onboarded yet. Either:\n"
            f"  1. Run the `agent-onboarding` skill (recommended), or\n"
            f"  2. cp {EXAMPLE_CONFIG.relative_to(ROOT)} {p.relative_to(ROOT) if not p.is_absolute() else p} and edit it."
        )
    data = yaml.safe_load(p.read_text())
    if not isinstance(data, dict):
        raise ConfigError(f"{p}: top level must be a mapping")
    return Config(data, p)
