"""Send-cap governor.

The failure this exists to prevent: sending platforms commonly enforce caps
PER CAMPAIGN, with no org-level ceiling. Run six campaigns at "20/day" against
the same mailbox and that mailbox sends 120/day. Nothing in the vendor UI warns
you. The governor sums intended volume per sender across every campaign and
refuses, or proportionally rebalances, the overage.

Every check returns a Decision with a reason, so refusals are auditable.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from . import db


@dataclass
class Decision:
    allowed: bool
    reason: str
    remaining: int = 0

    def __bool__(self) -> bool:
        return self.allowed


def _local_day_utc_bounds(when: dt.datetime) -> tuple[str, str] | None:
    """UTC bounds of `when`'s local calendar day, for counting UTC-stamped
    rows against a per-operator-day cap. None for a naive datetime, where
    the caller falls back to the date-string comparison."""
    if when.tzinfo is None:
        return None
    start = when.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + dt.timedelta(days=1)
    fmt = "%Y-%m-%d %H:%M:%S"
    return (start.astimezone(dt.timezone.utc).strftime(fmt),
            end.astimezone(dt.timezone.utc).strftime(fmt))


def check_send(config, conn, sender_id: str, when: dt.datetime | None = None,
               weeks_live: int = 0) -> Decision:
    """May `sender_id` send one more email right now?"""
    when = when or config.now()

    cap = config.effective_cap(sender_id, weeks_live=weeks_live)
    if cap <= 0:
        status = config.sender(sender_id).get("status")
        return Decision(False, f"sender {sender_id!r} has cap 0 (status={status})")

    used = db.sends_today(conn, sender_id=sender_id, day=when.strftime("%Y-%m-%d"),
                          between=_local_day_utc_bounds(when))
    if used >= cap:
        return Decision(False,
                        f"sender {sender_id!r} hit its daily cap: {used}/{cap}", 0)

    # Budget is computed before the window is judged, so a refusal outside the
    # window still reports the true remaining count. Reporting 0 there reads as
    # "cap exhausted" and is the kind of number an operator acts on.
    in_window, why = config.in_send_window(when)
    if not in_window:
        return Decision(False, f"outside send window: {why}", cap - used)

    return Decision(True, f"{used}/{cap} used today", cap - used)


def check_linkedin_invite(config, conn, sender_id: str,
                          when: dt.datetime | None = None) -> Decision:
    """May `sender_id` record one more LinkedIn connection request today?

    Invites are the one LinkedIn action platforms restrict accounts over, so
    the cap counts connection requests only; messages to accepted connections
    ride free. The touches are manual (an operator clicks send on LinkedIn),
    which is exactly why the cap lives here: a human pasting notes loses count
    faster than a machine does.
    """
    when = when or config.now()
    cap = int(config.sender(sender_id).get("daily_linkedin_invite_cap", 20) or 0)
    if cap <= 0:
        return Decision(False, f"sender {sender_id!r} has linkedin invite cap 0")
    used = db.sends_today(conn, sender_id=sender_id,
                          day=when.strftime("%Y-%m-%d"),
                          channel="linkedin_invite",
                          between=_local_day_utc_bounds(when))
    if used >= cap:
        return Decision(
            False, f"sender {sender_id!r} hit its daily LinkedIn invite cap: "
                   f"{used}/{cap}. Pushing past it is how accounts get "
                   f"restricted; it resets tomorrow.", 0)
    return Decision(True, f"{used}/{cap} invites used today", cap - used)


def check_intake(config, conn, when: dt.datetime | None = None) -> Decision:
    """May another net-new prospect enter the system today?"""
    when = when or config.now()
    cap = int(config.get("limits.new_prospects_per_day", 0) or 0)
    if cap <= 0:
        return Decision(True, "no intake cap configured")

    added = conn.execute(
        "SELECT COUNT(*) FROM prospects WHERE date(added_at) = ?",
        (when.strftime("%Y-%m-%d"),),
    ).fetchone()[0]
    if added >= cap:
        return Decision(False, f"intake cap reached: {added}/{cap} new prospects today", 0)
    return Decision(True, f"{added}/{cap} intake used today", cap - added)


def check_company_pacing(config, conn, domain: str,
                         exclude_prospect_id: int | None = None) -> Decision:
    """Stop two contacts at the same company being hit on the same day."""
    days = int(config.get("icp.min_days_between_same_company_touches", 0) or 0)
    if not domain or days <= 0:
        return Decision(True, "company pacing not configured")
    if db.company_touched_recently(conn, domain, days,
                                   exclude_prospect_id=exclude_prospect_id):
        return Decision(False,
                        f"another contact at {domain} was touched within {days} day(s)")
    return Decision(True, f"no recent touch at {domain}")


def check_company_contact_limit(config, conn, domain: str) -> Decision:
    max_contacts = int(config.get("icp.max_contacts_per_company", 0) or 0)
    if not domain or max_contacts <= 0:
        return Decision(True, "no per-company contact limit")
    n = conn.execute(
        "SELECT COUNT(DISTINCT p.id) FROM prospects p JOIN sends s ON s.prospect_id = p.id "
        "WHERE p.company_domain = ?", (domain,)
    ).fetchone()[0]
    if n >= max_contacts:
        return Decision(False,
                        f"{domain} already has {n}/{max_contacts} contacts in sequence")
    return Decision(True, f"{n}/{max_contacts} contacts at {domain}")


def audit_planned_rates(config, planned: dict[str, dict[str, int]]) -> dict:
    """Detect stacked per-campaign rates that breach a sender's daily cap.

    `planned` maps campaign_key -> {sender_id: daily_rate}. Returns a report
    with per-sender totals, breaches, and a proportional rebalance plan.
    """
    totals: dict[str, int] = {}
    for rates in planned.values():
        for sid, rate in rates.items():
            totals[sid] = totals.get(sid, 0) + int(rate or 0)

    breaches, plan = [], {}
    for sid, total in sorted(totals.items()):
        try:
            cap = config.effective_cap(sid)
        except Exception:
            breaches.append({"sender_id": sid, "total": total, "cap": None,
                             "detail": "sender is not in config"})
            continue
        if total > cap:
            breaches.append({"sender_id": sid, "total": total, "cap": cap,
                             "over_by": total - cap})
            # Scale every campaign's rate for this sender down proportionally,
            # keeping at least 1/day so no campaign silently stalls.
            for ckey, rates in planned.items():
                if sid not in rates:
                    continue
                scaled = max(1, int(rates[sid] * cap / total))
                plan.setdefault(ckey, {})[sid] = scaled

    return {
        "per_sender_totals": totals,
        "caps": {sid: _safe_cap(config, sid) for sid in totals},
        "breaches": breaches,
        "rebalance_plan": plan,
        "ok": not breaches,
    }


def _safe_cap(config, sender_id: str):
    try:
        return config.effective_cap(sender_id)
    except Exception:
        return None


def check_deliverability(config, conn, trailing: int = 100) -> Decision:
    """Kill switch. A rising bounce rate means stop, not slow down."""
    rows = conn.execute(
        "SELECT bounced FROM sends WHERE channel = 'email' "
        "ORDER BY sent_at DESC LIMIT ?", (trailing,)
    ).fetchall()
    if len(rows) < 20:
        return Decision(True, f"only {len(rows)} sends, too few to judge bounce rate")

    rate = sum(r["bounced"] for r in rows) / len(rows)
    halt = float(config.get("reporting.deliverability.bounce_rate_halt", 0.05))
    warn = float(config.get("reporting.deliverability.bounce_rate_warn", 0.02))

    if rate >= halt:
        return Decision(False,
                        f"HALT: bounce rate {rate:.1%} over trailing {len(rows)} "
                        f"exceeds halt threshold {halt:.1%}")
    if rate >= warn:
        return Decision(True,
                        f"WARN: bounce rate {rate:.1%} exceeds warn threshold {warn:.1%}")
    return Decision(True, f"bounce rate {rate:.1%} healthy")
