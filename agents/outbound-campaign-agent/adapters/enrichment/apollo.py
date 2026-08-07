"""Apollo enrichment: LinkedIn or name plus domain to a verified work email.

Every candidate Apollo returns is gated by `lib.identity.verify_match` before
any field is accepted. That gate exists because a provider asked to match a
person at a company will happily return a *different* person at that company,
and an unchecked merge sends mail addressed to the wrong human.

Return contract
---------------
`enrich()` returns a dict of fields to merge, plus a reserved `_meta` key:

    {"email": "...", "title": "...",
     "_meta": {"accepted": bool, "reason": str, "matched_via": str,
               "email_status": str, "personal_email_only": bool}}

`_meta` is always present and is never a prospect field. Callers must pop it
before persisting. When `_meta["accepted"]` is False the dict contains no other
keys, and `_meta["reason"]` explains why (no match, identity rejection, or an
Apollo record with nothing new in it).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from lib import identity  # noqa: E402

ADAPTER = {
    "slot": "enrichment",
    "name": "apollo",
    "requires_env": ["APOLLO_API_KEY"],
    "description": "Apollo people/match, identity-gated. LinkedIn first, then name plus domain.",
}

BASE = "https://api.apollo.io/api/v1"
MATCH = f"{BASE}/people/match"
SEARCH = f"{BASE}/mixed_people/api_search"

MERGE_FIELDS = [
    "email", "personal_email", "first_name", "last_name", "name", "title",
    "company", "company_domain", "industry", "employee_count", "linkedin_url",
    "country", "city", "phone",
]


class ApolloError(RuntimeError):
    pass


class ApolloAuthError(ApolloError):
    pass


class ApolloRateLimit(ApolloError):
    pass


def _post(url: str, payload: dict, key: str, *, timeout: int, retries: int) -> dict:
    body = json.dumps(payload).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": key,
        # Apollo serves stale cached matches without this, which silently
        # returns the pre-correction record for a person who changed jobs.
        "Cache-Control": "no-cache",
    }
    last: Exception | None = None
    for attempt in range(max(1, retries)):
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode(errors="replace")
            return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            if e.code in (401, 403):
                raise ApolloAuthError(
                    f"Apollo rejected the API key (HTTP {e.code}). "
                    f"Check the key named by adapter_config.apollo.api_key_env. {detail}"
                ) from e
            if e.code == 422:
                raise ApolloError(
                    f"Apollo rejected the request (HTTP 422) at {url}. "
                    f"Usually a deprecated endpoint or an unsupported filter. {detail}"
                ) from e
            if e.code == 429:
                wait = float(e.headers.get("Retry-After") or 2 ** attempt)
                last = ApolloRateLimit(f"Apollo rate limit (HTTP 429). {detail}")
                time.sleep(min(wait, 30))
                continue
            if 500 <= e.code < 600:
                last = ApolloError(f"Apollo server error (HTTP {e.code}). {detail}")
                time.sleep(min(2 ** attempt, 15))
                continue
            raise ApolloError(f"Apollo HTTP {e.code} at {url}. {detail}") from e
        except urllib.error.URLError as e:
            last = ApolloError(f"Apollo network error at {url}: {e.reason}")
            time.sleep(min(2 ** attempt, 15))
        except json.JSONDecodeError as e:
            raise ApolloError(f"Apollo returned non-JSON from {url}: {e}") from e
    raise last or ApolloError(f"Apollo request to {url} failed with no response")


def _domain(prospect: dict) -> str:
    d = str(prospect.get("company_domain") or "").strip().lower()
    if d:
        return d.replace("https://", "").replace("http://", "").split("/")[0].removeprefix("www.")
    email = prospect.get("email") or ""
    return "" if identity.is_personal_email(email) else identity.email_domain(email)


def _seed(prospect: dict) -> dict:
    first = str(prospect.get("first_name") or "").strip()
    last = str(prospect.get("last_name") or "").strip()
    full = str(prospect.get("name") or "").strip()
    if full and not first:
        first, last = identity.split_name(full)
    return {
        "first_name": first,
        "last_name": last,
        "name": full or " ".join(x for x in [first, last] if x),
        "title": str(prospect.get("title") or "").strip(),
        "company": str(prospect.get("company") or "").strip(),
        "domain": _domain(prospect),
        "linkedin_url": str(prospect.get("linkedin_url") or "").strip(),
    }


def _attempts(seed: dict, reveal_personal: bool) -> list[dict]:
    """Match payloads, richest identity first.

    Sending every signal at once is what stops two same-first-name coworkers at
    one company from cross-matching. The thinner payloads only run after the
    rich one misses.
    """
    out: list[dict] = []
    li, first, last = seed["linkedin_url"], seed["first_name"], seed["last_name"]
    domain, title, company = seed["domain"], seed["title"], seed["company"]

    if li:
        out.append({"linkedin_url": li, "first_name": first, "last_name": last,
                    "domain": domain, "title": title, "organization_name": company})
        out.append({"linkedin_url": li, "first_name": first, "last_name": last})
        out.append({"linkedin_url": li})
    if first and domain:
        out.append({"first_name": first, "last_name": last, "domain": domain,
                    "title": title, "organization_name": company})
        out.append({"first_name": first, "last_name": last, "domain": domain})

    cleaned = []
    seen = set()
    for a in out:
        a = {k: v for k, v in a.items() if v}
        if reveal_personal:
            a["reveal_personal_emails"] = True
        sig = json.dumps(a, sort_keys=True)
        if a and sig not in seen:
            seen.add(sig)
            cleaned.append(a)
    return cleaned


def _normalize(person: dict) -> dict:
    org = person.get("organization") or person.get("account") or {}
    personal = [e for e in (person.get("personal_emails") or []) if e]
    phones = person.get("phone_numbers") or []
    phone = ""
    if phones and isinstance(phones[0], dict):
        phone = phones[0].get("sanitized_number") or phones[0].get("raw_number") or ""
    domain = org.get("primary_domain") or org.get("website_url") or ""
    domain = str(domain).replace("https://", "").replace("http://", "").split("/")[0]
    return {
        "email": (person.get("email") or "").strip().lower(),
        "personal_email": (personal[0] if personal else "").strip().lower(),
        "email_status": person.get("email_status") or "",
        "first_name": person.get("first_name") or "",
        "last_name": person.get("last_name") or "",
        "name": person.get("name") or "",
        "title": person.get("title") or "",
        "company": org.get("name") or person.get("organization_name") or "",
        "company_domain": domain.removeprefix("www.").lower(),
        "industry": org.get("industry") or "",
        "employee_count": org.get("estimated_num_employees"),
        "linkedin_url": person.get("linkedin_url") or "",
        "country": person.get("country") or "",
        "city": person.get("city") or "",
        "phone": phone,
        "provider_id": person.get("id") or "",
    }


def _search_candidates(seed: dict, key: str, *, timeout: int, retries: int) -> list[dict]:
    """Two-step fallback: api_search by domain plus name, then match by id.

    `mixed_people/search` is deprecated and answers 422; `api_search` is the
    live endpoint. It returns obfuscated records, so the id must be sent back
    through people/match to reveal anything usable.
    """
    if not seed["domain"]:
        return []
    payload = {"q_organization_domains_list": [seed["domain"]], "page": 1, "per_page": 5}
    q = " ".join(x for x in [seed["first_name"], seed["last_name"]] if x).strip()
    if q:
        payload["q_keywords"] = q
    res = _post(SEARCH, payload, key, timeout=timeout, retries=retries)
    return [p for p in (res.get("people") or []) if p.get("id")][:5]


def enrich(ctx, prospect: dict) -> dict:
    """Match one prospect against Apollo. See the module docstring for `_meta`."""
    key = ctx.secret(ctx.settings.get("api_key_env", "APOLLO_API_KEY"))
    reject_personal = bool(ctx.settings.get("reject_personal_domains", True))
    timeout = int(ctx.settings.get("timeout_seconds", 45))
    retries = int(ctx.settings.get("max_retries", 4))
    pause = float(ctx.settings.get("sleep_seconds", 0.35))
    use_search = bool(ctx.settings.get("use_search_fallback", True))

    seed = _seed(prospect)
    if not seed["linkedin_url"] and not (seed["first_name"] and seed["domain"]):
        return {"_meta": {"accepted": False, "matched_via": "",
                          "reason": "no usable identity: need a linkedin url, or a first name plus a company domain"}}

    reasons: list[str] = []
    accepted: dict | None = None
    matched_via = ""

    for payload in _attempts(seed, reveal_personal=not reject_personal):
        res = _post(MATCH, payload, key, timeout=timeout, retries=retries)
        if pause:
            time.sleep(pause)
        person = res.get("person") or {}
        if not person:
            reasons.append("no match")
            continue
        cand = _normalize(person)
        ok, reason = verify(seed, cand, payload)
        if not ok:
            reasons.append(reason)
            continue
        accepted = cand
        matched_via = "linkedin" if payload.get("linkedin_url") else "name+domain"
        break

    if accepted is None and use_search:
        for hit in _search_candidates(seed, key, timeout=timeout, retries=retries):
            res = _post(MATCH, {"id": hit["id"]}, key, timeout=timeout, retries=retries)
            if pause:
                time.sleep(pause)
            person = res.get("person") or {}
            if not person:
                continue
            cand = _normalize(person)
            ok, reason = verify(seed, cand, {})
            if not ok:
                reasons.append(reason)
                continue
            accepted = cand
            matched_via = "api_search+id"
            break

    if accepted is None:
        uniq = list(dict.fromkeys(reasons))[:5]
        return {"_meta": {"accepted": False, "matched_via": "",
                          "reason": "; ".join(uniq) or "no match"}}

    personal_only = False
    if accepted["email"] and identity.is_personal_email(accepted["email"]):
        if reject_personal:
            accepted["personal_email"] = accepted["personal_email"] or accepted["email"]
            accepted["email"] = ""
            personal_only = True

    merged = identity.merge_enrichment(prospect, accepted, MERGE_FIELDS)
    if accepted.get("provider_id") and not prospect.get("apollo_person_id"):
        merged["apollo_person_id"] = accepted["provider_id"]

    return {
        **merged,
        "_meta": {
            "accepted": True,
            "matched_via": matched_via,
            "reason": "identity verified",
            "email_status": accepted.get("email_status", ""),
            "personal_email_only": personal_only,
            "fields_filled": sorted(k for k in merged if k != "_meta"),
        },
    }


def verify(seed: dict, candidate: dict, payload: dict) -> tuple[bool, str]:
    """Identity gate. Title is decisive only on a blind name plus domain match."""
    require_title = not payload.get("linkedin_url") and bool(seed["title"])
    return identity.verify_match(seed, candidate, require_title=require_title)
