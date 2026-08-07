#!/usr/bin/env python3
"""Validate an outbound config: structure, then non-negotiable safety invariants.

Usage:
  uv run --with pyyaml validate_config.py config/outbound.yaml [--strict]

Exit codes: 0 ok (warnings allowed), 1 errors found, 2 file/parse problem.
`--strict` promotes warnings to errors.
"""
import argparse
import datetime as dt
import pathlib
import re
import sys

import yaml

ERRORS: list[str] = []
WARNINGS: list[str] = []


def err(path: str, msg: str) -> None:
    ERRORS.append(f"{path}: {msg}")


def warn(path: str, msg: str) -> None:
    WARNINGS.append(f"{path}: {msg}")


def get(cfg, dotted: str, default=None):
    node = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def require(cfg, dotted: str, kind=None) -> None:
    val = get(cfg, dotted, _MISSING)
    if val is _MISSING:
        err(dotted, "REQUIRED but missing")
        return
    if val is None or (isinstance(val, str) and not val.strip()):
        err(dotted, "REQUIRED but empty")
        return
    if kind and not isinstance(val, kind):
        err(dotted, f"expected {kind.__name__}, got {type(val).__name__}")


_MISSING = object()

# Invariants that exist because violating them damages sending reputation,
# leaks spend, or contacts people who already said no. These are not style.
HARD_TRUE = {
    "cadence.stop_on_reply": "a reply must always halt the sequence",
    "suppression.fail_closed": "an unreachable suppression source must halt the run, never pass it",
    "message_standards.forbid_tracking_pixels": "tracking pixels wreck primary-domain deliverability",
    "approval_gates.first_batch_of_campaign": "the first batch of any campaign requires a human",
    "first_run.require_operator_review": "the first run must be read by a human before anything ships",
}
HARD_FALSE = {
    "reporting.track_opens": "open tracking is unreliable and hurts deliverability",
}

VALID_DAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}
SLOTS = ["sourcing", "enrichment", "sender", "crm", "calendar", "suppression", "notify"]

# Slots added after the original set. A config written before they existed is
# not broken, it just predates them, so absence is a warning and the runtime
# treats a missing slot as `none`.
OPTIONAL_SLOTS = {"calendar"}

# Triggers whose absence is a supervision gap, not a preference.
EXPECTED_ESCALATIONS = {
    "positive_reply": "a person who wants to talk should get a human, not the next cadence step",
    "suppression_unavailable": "a fail-closed halt nobody hears about is an outage that looks like a quiet day",
}
DO_NOT_TOUCH_LISTS = ("companies", "domains", "people", "geos")


def check_identity(cfg):
    for p in ("company.name", "company.product_name",
              "operator.name", "operator.email", "operator.timezone"):
        require(cfg, p, str)

    email = get(cfg, "operator.email", "")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        err("operator.email", f"not a valid address: {email!r}")

    tz = get(cfg, "operator.timezone", "")
    if tz:
        try:
            from zoneinfo import ZoneInfo
            ZoneInfo(tz)
        except Exception:
            err("operator.timezone", f"unknown IANA timezone: {tz!r}")

    launch = get(cfg, "company.brand_public_from")
    product = get(cfg, "company.product_name")
    if isinstance(launch, dt.date) and launch > dt.date.today():
        warn("company.brand_public_from",
             f"{product!r} is embargoed until {launch}; drafting will fall back to company.name")

    forbidden = get(cfg, "company.forbidden_names", []) or []
    if product and product in forbidden:
        err("company.forbidden_names", f"product_name {product!r} is also listed as forbidden")


def check_senders(cfg):
    senders = get(cfg, "senders")
    if not isinstance(senders, list) or not senders:
        err("senders", "REQUIRED: at least one sender")
        return

    seen_ids, seen_emails = set(), set()
    for i, s in enumerate(senders):
        p = f"senders[{i}]"
        if not isinstance(s, dict):
            err(p, "must be a mapping")
            continue
        for k in ("id", "email", "daily_email_cap"):
            if not s.get(k) and s.get(k) != 0:
                err(f"{p}.{k}", "REQUIRED")

        sid, email = s.get("id"), s.get("email")
        if sid in seen_ids:
            err(f"{p}.id", f"duplicate sender id {sid!r}")
        seen_ids.add(sid)
        if email in seen_emails:
            err(f"{p}.email", f"duplicate sender email {email!r}")
        seen_emails.add(email)

        cap = s.get("daily_email_cap")
        if isinstance(cap, int):
            if cap <= 0:
                err(f"{p}.daily_email_cap", "must be > 0")
            elif cap > 50:
                warn(f"{p}.daily_email_cap",
                     f"{cap}/day is aggressive for a primary domain; 25 is the safe ceiling")

        # A booking link that 404s or points at a colleague is discovered by the
        # prospect, after they have already decided to say yes.
        link = s.get("calendar_link")
        if link is not None and not str(link).startswith(("http://", "https://")):
            err(f"{p}.calendar_link", f"expected a booking URL, got {link!r}")

        status = s.get("status", "live")
        if status not in {"live", "warming", "paused"}:
            err(f"{p}.status", f"must be live|warming|paused, got {status!r}")

        ramp = s.get("ramp")
        if isinstance(ramp, dict):
            start, target = ramp.get("start_cap"), ramp.get("target_cap")
            if isinstance(start, int) and isinstance(target, int) and start > target:
                err(f"{p}.ramp", f"start_cap {start} exceeds target_cap {target}")
            if isinstance(target, int) and isinstance(cap, int) and target > cap:
                err(f"{p}.ramp.target_cap",
                    f"{target} exceeds daily_email_cap {cap}; the cap is the hard ceiling")


def check_limits(cfg):
    require(cfg, "limits.new_prospects_per_day")

    days = get(cfg, "limits.send_days")
    if not isinstance(days, list) or not days:
        err("limits.send_days", "REQUIRED: at least one weekday")
    else:
        for d in days:
            if str(d).lower() not in VALID_DAYS:
                err("limits.send_days", f"invalid weekday {d!r}")
        if {"sat", "sun"} & {str(d).lower() for d in days}:
            warn("limits.send_days", "weekend sends typically underperform B2B")

    window = get(cfg, "limits.send_window_local", "")
    if window and not re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", str(window)):
        err("limits.send_window_local", f"expected HH:MM-HH:MM, got {window!r}")
    elif window:
        start, end = str(window).split("-")
        if start >= end:
            err("limits.send_window_local", f"window start {start} is not before end {end}")

    # The governor is the only thing standing between stacked per-campaign
    # rates and a blown sender reputation.
    intake = get(cfg, "limits.new_prospects_per_day")
    senders = get(cfg, "senders") or []
    total_cap = sum(s.get("daily_email_cap", 0) for s in senders if isinstance(s, dict))
    if isinstance(intake, int) and total_cap and intake > total_cap:
        err("limits.new_prospects_per_day",
            f"intake {intake}/day exceeds combined sender capacity {total_cap}/day")

    if not get(cfg, "limits.enforce_global_governor", False):
        warn("limits.enforce_global_governor",
             "disabled: per-campaign rates stack and can silently exceed a sender's daily cap")


def check_adapters(cfg, root: pathlib.Path):
    adapters = get(cfg, "adapters")
    if not isinstance(adapters, dict):
        err("adapters", "REQUIRED mapping of capability slot to adapter")
        return

    for slot in SLOTS:
        if slot not in adapters:
            if slot in OPTIONAL_SLOTS:
                warn(f"adapters.{slot}",
                     "not set; it will behave as 'none'. Add it explicitly so the "
                     "choice is on the record rather than inherited by omission")
            else:
                err(f"adapters.{slot}", "REQUIRED (use 'none' to disable)")
            continue

        names = adapters[slot]
        names = names if isinstance(names, list) else [names]
        for name in names:
            if name == "none":
                continue
            impl = root / "adapters" / slot / f"{name}.py"
            if not impl.exists():
                err(f"adapters.{slot}",
                    f"no adapter {name!r} at adapters/{slot}/{name}.py. If the "
                    f"team uses a vendor this template does not ship, create the "
                    f"stub: scaffold_adapter.py --slot {slot} --name {name}")
            # Scaffolds declare themselves in ADAPTER meta. A text check is
            # enough because scaffold_adapter.py is the only writer and a
            # hand-authored module claiming "scaffold": True means it too.
            elif '"scaffold": True' in impl.read_text():
                warn(f"adapters.{slot}",
                     f"{name!r} is a scaffold: config names the team's real "
                     f"vendor, but every call fails closed until "
                     f"adapters/{slot}/{name}.py is implemented")

    if adapters.get("sender") == "dryrun":
        warn("adapters.sender", "dryrun: drafts are produced and logged but NOTHING is sent")

    enrichment = adapters.get("enrichment")
    if isinstance(enrichment, list) and len(enrichment) != len(set(enrichment)):
        err("adapters.enrichment", "duplicate adapters in the waterfall")

    # A secret named in config must actually be present in the environment.
    import os
    for name, block in (get(cfg, "adapter_config") or {}).items():
        if not isinstance(block, dict):
            continue
        for key, val in block.items():
            if key.endswith("_env") and isinstance(val, str) and val not in os.environ:
                warn(f"adapter_config.{name}.{key}",
                     f"${val} is not set in the environment; {name} will fail at runtime")


def check_icp(cfg):
    rng = get(cfg, "icp.employee_range")
    if not (isinstance(rng, list) and len(rng) == 2 and all(isinstance(n, int) for n in rng)):
        err("icp.employee_range", "REQUIRED: [min, max] integers")
    elif rng[0] > rng[1]:
        err("icp.employee_range", f"min {rng[0]} exceeds max {rng[1]}")

    tiers = get(cfg, "icp.tiers")
    if not isinstance(tiers, list) or not tiers:
        err("icp.tiers", "REQUIRED: at least one tier")
        return

    ids = [t.get("id") for t in tiers if isinstance(t, dict)]
    if len(ids) != len(set(ids)):
        err("icp.tiers", "duplicate tier ids")

    total = sum(t.get("mix_pct", 0) for t in tiers if isinstance(t, dict))
    if total and abs(total - 100) > 1:
        warn("icp.tiers", f"mix_pct sums to {total}, not 100")

    buyer_ids = {t.get("id") for t in (get(cfg, "icp.buyer_tiers") or []) if isinstance(t, dict)}
    lead = get(cfg, "icp.lead_with_tier")
    if lead and buyer_ids and lead not in buyer_ids:
        err("icp.lead_with_tier", f"{lead!r} is not one of the buyer_tiers {sorted(buyer_ids)}")


def check_cadence(cfg):
    steps = get(cfg, "cadence.steps")
    if not isinstance(steps, list) or not steps:
        err("cadence.steps", "REQUIRED: at least one step")
        return

    days = []
    for i, s in enumerate(steps):
        p = f"cadence.steps[{i}]"
        if not isinstance(s, dict):
            err(p, "must be a mapping")
            continue
        if not isinstance(s.get("day"), int):
            err(f"{p}.day", "REQUIRED integer (days from day 0)")
        else:
            days.append(s["day"])
        if not s.get("channel"):
            err(f"{p}.channel", "REQUIRED")

    if days and days != sorted(days):
        err("cadence.steps", f"steps are out of chronological order: {days}")
    if days and days[0] != 0:
        warn("cadence.steps", f"first step is day {days[0]}, not day 0")

    emails = [s for s in steps if isinstance(s, dict) and s.get("channel") == "email"]
    if len(emails) > 5:
        warn("cadence.steps", f"{len(emails)} emails per prospect is above the 3-4 norm")


def check_standards(cfg):
    words = get(cfg, "message_standards.max_words")
    if isinstance(words, int) and words > 150:
        warn("message_standards.max_words", f"{words} words is long for a cold opener")

    subj = get(cfg, "message_standards.max_subject_chars")
    if isinstance(subj, int) and subj > 60:
        warn("message_standards.max_subject_chars", f"{subj} chars will truncate in most clients")

    conf = get(cfg, "message_standards.min_confidence_to_autosend")
    if isinstance(conf, (int, float)) and not 0 <= conf <= 1:
        err("message_standards.min_confidence_to_autosend", f"must be 0..1, got {conf}")

    cta = get(cfg, "message_standards.cta.type")
    if cta not in ("self_serve", "meeting", None):
        err("message_standards.cta.type", f"must be self_serve|meeting, got {cta!r}")
    if cta == "self_serve" and not get(cfg, "message_standards.cta.url"):
        err("message_standards.cta.url", "REQUIRED when cta.type is self_serve")


def check_reporting(cfg):
    floor = get(cfg, "reporting.n_floor")
    if not isinstance(floor, int) or floor < 1:
        err("reporting.n_floor", "REQUIRED integer >= 1 (suppresses rates on thin denominators)")
    elif floor < 10:
        warn("reporting.n_floor", f"{floor} is low; rates below n=10 are noise")

    # Most prospects book from a link and never reply, so with no calendar the
    # meetings number measures how often someone remembered to flag one.
    metrics = get(cfg, "reporting.primary_metrics") or []
    booked = {"meetings_booked", "meetings_held"} & {str(m) for m in metrics}
    if booked and get(cfg, "adapters.calendar", "none") in ("none", None):
        warn("reporting.primary_metrics",
             f"{sorted(booked)} is a primary metric but adapters.calendar is 'none'; "
             f"meetings will only be counted when a human flags one by hand")

    for key in ("reporting.schedule.weekly_report_cron", "reporting.schedule.cadence_tick_cron"):
        cron = get(cfg, key)
        if cron and len(str(cron).split()) != 5:
            err(key, f"expected 5-field cron, got {cron!r}")


def check_escalation(cfg):
    """An agent that cannot reach a human is an agent running unsupervised."""
    require(cfg, "escalation.escalate_to", str)

    triggers = get(cfg, "escalation.escalate_on")
    if not isinstance(triggers, list) or not triggers:
        err("escalation.escalate_on", "REQUIRED: at least one trigger that interrupts a human")
    else:
        listed = {str(t) for t in triggers}
        for name, why in EXPECTED_ESCALATIONS.items():
            if name not in listed:
                warn("escalation.escalate_on", f"{name!r} is not escalated: {why}")

    quiet = get(cfg, "escalation.quiet_hours_local")
    if quiet and not re.fullmatch(r"\d{2}:\d{2}-\d{2}:\d{2}", str(quiet)):
        err("escalation.quiet_hours_local", f"expected HH:MM-HH:MM, got {quiet!r}")

    # A destination with no transport is a destination that does not exist, and
    # silence on a broken channel is indistinguishable from a healthy quiet day.
    # Requiring a destination AND rejecting one when notify is 'none' would
    # leave no valid value, so the requirement is conditional on a transport.
    digest = get(cfg, "escalation.digest_to")
    if get(cfg, "adapters.notify") == "none":
        if digest:
            err("escalation.digest_to",
                f"{digest!r} is configured but adapters.notify is 'none'; there is "
                f"no transport that can reach it and every notification is silent")
        else:
            warn("escalation.digest_to",
                 "no destination and no notify adapter: routine output goes nowhere "
                 "and the operator only sees this agent when they come looking")
    else:
        require(cfg, "escalation.digest_to", str)


def check_voice(cfg, root: pathlib.Path):
    """The linter enforces mechanics. Only real samples enforce voice."""
    samples = get(cfg, "voice.samples_file")
    if not samples:
        warn("voice.samples_file",
             "not set: drafting has nothing to imitate and the copy will read like copy")
    elif not (root / str(samples)).exists():
        # A warning, not an error: this file is filled in during onboarding.
        warn("voice.samples_file",
             f"{samples} does not exist yet; paste 1-3 emails the operator has actually "
             f"sent and was happy with into it before the first draft")

    banned = get(cfg, "voice.banned_phrases", [])
    if banned is None:
        banned = []
    if not isinstance(banned, list):
        err("voice.banned_phrases",
            f"expected a list of strings, got {type(banned).__name__}")
        return
    for i, phrase in enumerate(banned):
        p = f"voice.banned_phrases[{i}]"
        if not isinstance(phrase, str):
            err(p, f"expected a string, got {type(phrase).__name__}")
        elif not phrase.strip():
            err(p, "empty string: it would match every draft ever written")


def check_do_not_touch(cfg):
    """Distinct from ICP (not a fit) and suppression (already engaged)."""
    entries: list[str] = []
    for key in DO_NOT_TOUCH_LISTS:
        path = f"do_not_touch.{key}"
        val = get(cfg, path, _MISSING)
        if val is _MISSING or val is None:
            continue
        if isinstance(val, str):
            err(path, f"expected a list, got the bare string {val!r}; "
                      f"a string here matches nothing and fails silently")
            continue
        if not isinstance(val, list):
            err(path, f"expected a list, got {type(val).__name__}")
            continue
        entries.extend(str(v) for v in val)

    if not entries:
        warn("do_not_touch",
             "every exclusion list is empty; confirm with the operator that there is "
             "genuinely no company, domain, person, or geo this agent must never contact")

    if get(cfg, "do_not_touch.reason_required", False) is True:
        notes = get(cfg, "do_not_touch.notes")
        if notes is None:
            notes = {}
        if not isinstance(notes, dict):
            err("do_not_touch.notes",
                f"expected a mapping of entry to reason, got {type(notes).__name__}")
            return
        for entry in entries:
            if entry not in notes:
                warn("do_not_touch.notes",
                     f"{entry!r} has no reason and reason_required is true; an unexplained "
                     f"exclusion gets deleted by whoever inherits this config")


def check_first_run(cfg):
    batch = get(cfg, "first_run.batch_size", _MISSING)
    if batch is _MISSING or batch is None:
        err("first_run.batch_size", "REQUIRED: how many prospects the first dry run walks")
        return
    if isinstance(batch, bool) or not isinstance(batch, int):
        err("first_run.batch_size",
            f"expected a positive integer, got {type(batch).__name__}")
        return
    if batch <= 0:
        err("first_run.batch_size", f"must be > 0, got {batch}")
        return

    intake = get(cfg, "limits.new_prospects_per_day")
    if isinstance(intake, int) and batch > intake:
        err("first_run.batch_size",
            f"{batch} exceeds the intake ceiling limits.new_prospects_per_day ({intake}/day)")


def check_leftovers(cfg, example: dict | None):
    """Flag values still identical to the shipped example.

    The failure mode this catches is silent and embarrassing: onboarding fills
    in the company name but misses the CTA url, and every opener ships a link
    to the example domain.
    """
    if not example:
        return

    watch = [
        ("company.name", "error"),
        ("company.product_name", "error"),
        ("company.website", "warn"),
        ("operator.name", "error"),
        ("operator.email", "error"),
        ("message_standards.cta.url", "error"),
        ("positioning.wedge", "warn"),
        ("positioning.pain", "warn"),
        ("positioning.proof_metric", "warn"),
        ("adapter_config.csv.input_path", "warn"),
        ("escalation.escalate_to", "error"),
        ("voice.notes", "warn"),
        ("first_run.goal", "warn"),
    ]
    for path, severity in watch:
        actual, sample = get(cfg, path), get(example, path)
        if sample in (None, "") or actual != sample:
            continue
        msg = f"still set to the example value {sample!r}; replace it with the team's own"
        (err if severity == "error" else warn)(path, msg)

    for i, s in enumerate(get(cfg, "senders", []) or []):
        if isinstance(s, dict) and str(s.get("email", "")).endswith("@acme.example"):
            err(f"senders[{i}].email", f"example address {s['email']!r} will not send")

    for path in ("escalation.digest_to", "escalation.escalate_to"):
        val = str(get(cfg, path, "") or "")
        if val.endswith("@acme.example"):
            err(path, f"example address {val!r} will never reach a human")


def check_invariants(cfg):
    for path, why in HARD_TRUE.items():
        if get(cfg, path) is not True:
            err(path, f"must be true: {why}")
    for path, why in HARD_FALSE.items():
        if get(cfg, path) is not False:
            err(path, f"must be false: {why}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--strict", action="store_true",
                    help="treat warnings as errors")
    args = ap.parse_args()

    path = pathlib.Path(args.config).resolve()
    if not path.exists():
        print(f"config not found: {path}", file=sys.stderr)
        return 2
    try:
        cfg = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        print(f"YAML parse error in {path}:\n{e}", file=sys.stderr)
        return 2
    if not isinstance(cfg, dict):
        print(f"{path}: top level must be a mapping", file=sys.stderr)
        return 2

    # template root = .../skills/agent-onboarding/scripts/ -> up 3
    root = pathlib.Path(__file__).resolve().parents[4]

    check_identity(cfg)
    check_senders(cfg)
    check_limits(cfg)
    check_adapters(cfg, root)
    check_icp(cfg)
    check_cadence(cfg)
    check_standards(cfg)
    check_reporting(cfg)
    check_escalation(cfg)
    check_voice(cfg, root)
    check_do_not_touch(cfg)
    check_first_run(cfg)

    example_path = root / "config" / "outbound.example.yaml"
    example = None
    if example_path.exists() and example_path.resolve() != path:
        try:
            example = yaml.safe_load(example_path.read_text())
        except yaml.YAMLError:
            example = None
    check_leftovers(cfg, example)

    check_invariants(cfg)

    if args.strict:
        ERRORS.extend(WARNINGS)
        WARNINGS.clear()

    for w in WARNINGS:
        print(f"  WARN  {w}")
    for e in ERRORS:
        print(f"  ERROR {e}")

    print()
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s) in {path.name}")
        return 1
    print(f"OK: {path.name} valid ({len(WARNINGS)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
