"""Identity matching: the guard against enriching the wrong human.

Extracted from a production pipeline where the failure this prevents was real:
an enrichment provider, asked to match "Nathalia Silva at doola", returned a
*different* Nathalia at the same company and the pipeline happily overwrote the
seed LinkedIn URL. The prospect got an email addressed to someone else.

Rules, in order of authority:
  1. A seed LinkedIn slug is ground truth. If the candidate carries a different
     slug, reject outright, no matter how good the name looks.
  2. Names must be compatible (accent- and case-insensitive, nickname-aware).
  3. On a name+domain fallback match (no LinkedIn on either side), the title
     must also be compatible, because name+domain collides at large companies.
Never overwrite a non-empty seed field with provider data.
"""
from __future__ import annotations

import re
import unicodedata

PERSONAL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "ymail.com", "hotmail.com",
    "outlook.com", "live.com", "msn.com", "aol.com", "icloud.com", "me.com",
    "mac.com", "proton.me", "protonmail.com", "gmx.com", "mail.com", "zoho.com",
    "yandex.com", "fastmail.com", "hey.com",
}

# Post-nominals to strip from a display name. Generational suffixes are kept:
# "Jr" is part of the name, "MBA" is not.
CREDENTIALS = {
    "mba", "phd", "md", "do", "rn", "np", "pa", "esq", "jd", "cpa", "cfa",
    "cfp", "pmp", "cissp", "pe", "ma", "ms", "msc", "bsc", "ba", "bs", "edd",
    "dds", "dvm", "pharmd", "lcsw", "lmft", "sphr", "phr", "shrm", "cscp",
    "ccp", "cpc", "cissp", "cism", "citp", "mph", "mfa", "llm",
}
GENERATIONAL = {"jr", "sr", "ii", "iii", "iv", "v"}

NICKNAMES = {
    "bill": "william", "will": "william", "billy": "william",
    "bob": "robert", "rob": "robert", "bobby": "robert",
    "dick": "richard", "rick": "richard", "rich": "richard",
    "jim": "james", "jimmy": "james", "jamie": "james",
    "joe": "joseph", "joey": "joseph",
    "mike": "michael", "mikey": "michael",
    "dave": "david", "davey": "david",
    "chris": "christopher", "kit": "christopher",
    "tom": "thomas", "tommy": "thomas",
    "dan": "daniel", "danny": "daniel",
    "matt": "matthew", "steve": "stephen", "steven": "stephen",
    "tony": "anthony", "nick": "nicholas", "alex": "alexander",
    "ben": "benjamin", "sam": "samuel", "ed": "edward", "ted": "edward",
    "kate": "katherine", "katie": "katherine", "kathy": "katherine",
    "liz": "elizabeth", "beth": "elizabeth", "betty": "elizabeth",
    "sue": "susan", "suzy": "susan", "peggy": "margaret", "meg": "margaret",
    "maggie": "margaret", "jen": "jennifer", "jenny": "jennifer",
    "becky": "rebecca", "cathy": "catherine", "pat": "patricia",
    "trish": "patricia", "andy": "andrew", "greg": "gregory",
    "jeff": "jeffrey", "larry": "lawrence", "ron": "ronald", "ken": "kenneth",
}

_EMOJI = re.compile(
    "[" "\U0001F300-\U0001FAFF" "\U00002600-\U000027BF"
    "\U0001F1E6-\U0001F1FF" "\U00002190-\U000021FF" "\U00002B00-\U00002BFF" "]+"
)
_PUNCT = re.compile(r"[^\w\s'-]", re.UNICODE)


def fold(s: str) -> str:
    """Lowercase, strip accents and punctuation. 'José M. Álvarez' -> 'jose m alvarez'."""
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _EMOJI.sub(" ", s)
    s = _PUNCT.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def canonical_first(token: str) -> str:
    t = fold(token)
    return NICKNAMES.get(t, t)


def split_name(display: str) -> tuple[str, str]:
    """('Dr. María-José Ruiz Gómez, PhD') -> ('María-José', 'Ruiz Gómez').

    Keeps original casing/accents in the output; only the analysis is folded.
    """
    if not display:
        return "", ""

    s = _EMOJI.sub(" ", str(display))
    s = s.split("(")[0]
    # Split on commas, then drop any trailing chunk that is purely credentials.
    chunks = [c.strip() for c in s.split(",") if c.strip()]
    if chunks:
        kept = [chunks[0]]
        for c in chunks[1:]:
            toks = [fold(t) for t in c.split() if t.strip()]
            if toks and not all(t in CREDENTIALS or not t for t in toks):
                kept.append(c)
        s = " ".join(kept)

    tokens = [t for t in re.split(r"\s+", s.strip()) if t]
    tokens = [t for t in tokens if fold(t) not in {"dr", "mr", "mrs", "ms", "prof", "sir"}]
    # Trailing credential tokens without a comma, e.g. "Jane Doe MBA"
    while len(tokens) > 2 and fold(tokens[-1]).strip(".") in CREDENTIALS:
        tokens.pop()

    if not tokens:
        return "", ""
    if len(tokens) == 1:
        return tokens[0], ""

    # Keep a generational suffix attached to the last name.
    if fold(tokens[-1]).strip(".") in GENERATIONAL and len(tokens) > 2:
        return tokens[0], " ".join(tokens[1:])
    return tokens[0], " ".join(tokens[1:])


def linkedin_slug(url: str) -> str:
    """Normalize a LinkedIn profile URL to its slug. Returns '' if not a profile."""
    if not url:
        return ""
    m = re.search(r"linkedin\.com/in/([^/?#\s]+)", str(url), re.I)
    return m.group(1).rstrip("/").lower() if m else ""


def is_personal_email(email: str) -> bool:
    if not email or "@" not in str(email):
        return False
    return str(email).rsplit("@", 1)[-1].strip().lower() in PERSONAL_DOMAINS


def email_domain(email: str) -> str:
    if not email or "@" not in str(email):
        return ""
    return str(email).rsplit("@", 1)[-1].strip().lower()


def names_compatible(seed: str, candidate: str) -> bool:
    """Same human? Requires first-name compatibility AND a shared surname token.

    Deliberately strict: a false accept sends mail to the wrong person, while a
    false reject only costs one unenriched row.
    """
    sf, sl = split_name(seed)
    cf, cl = split_name(candidate)
    if not sf or not cf:
        return False

    a, b = canonical_first(sf), canonical_first(cf)
    first_ok = (
        a == b
        # initial vs full name: "J. Smith" vs "John Smith"
        or (len(a) == 1 and b.startswith(a))
        or (len(b) == 1 and a.startswith(b))
    )
    if not first_ok:
        return False

    # Surnames: any shared token handles maiden/compound names
    # ("Ruiz Gomez" vs "Gomez").
    st = {t for t in fold(sl).split() if len(t) > 1}
    ct = {t for t in fold(cl).split() if len(t) > 1}
    if not st or not ct:
        return True  # one side has no surname; first-name match is all we have
    return bool(st & ct)


TITLE_STOPWORDS = {
    "of", "the", "and", "for", "to", "a", "an", "at", "in", "on",
    "senior", "sr", "junior", "jr", "global", "regional", "group", "lead",
}


def titles_compatible(seed: str, candidate: str) -> bool:
    """Loose overlap check. Empty on either side passes (no evidence, no veto)."""
    if not seed or not candidate:
        return True
    st = {t for t in fold(seed).split() if t not in TITLE_STOPWORDS and len(t) > 2}
    ct = {t for t in fold(candidate).split() if t not in TITLE_STOPWORDS and len(t) > 2}
    if not st or not ct:
        return True
    return bool(st & ct)


def verify_match(seed: dict, candidate: dict, *, require_title: bool | None = None
                 ) -> tuple[bool, str]:
    """Gate a provider result against the seed row.

    Returns (accepted, reason). `reason` is always populated so rejections can
    be logged and audited rather than silently dropped.
    """
    seed_slug = linkedin_slug(seed.get("linkedin_url", ""))
    cand_slug = linkedin_slug(candidate.get("linkedin_url", ""))

    # Rule 1: the seed slug is ground truth.
    if seed_slug and cand_slug and seed_slug != cand_slug:
        return False, f"linkedin slug mismatch: seed={seed_slug!r} candidate={cand_slug!r}"

    seed_name = seed.get("name") or f"{seed.get('first_name','')} {seed.get('last_name','')}"
    cand_name = candidate.get("name") or f"{candidate.get('first_name','')} {candidate.get('last_name','')}"

    if seed_slug and cand_slug and seed_slug == cand_slug:
        return True, "linkedin slug exact match"

    # Rule 2: names must be compatible.
    if not names_compatible(seed_name, cand_name):
        return False, f"name mismatch: seed={seed_name.strip()!r} candidate={cand_name.strip()!r}"

    # Rule 3: with no LinkedIn on either side, name+domain alone is not enough.
    if require_title is None:
        require_title = not (seed_slug or cand_slug)
    if require_title and not titles_compatible(seed.get("title", ""), candidate.get("title", "")):
        return False, (f"title mismatch on name+domain match: "
                       f"seed={seed.get('title')!r} candidate={candidate.get('title')!r}")

    return True, "name compatible"


def merge_enrichment(seed: dict, candidate: dict, fields: list[str] | None = None) -> dict:
    """Fill gaps in `seed` from `candidate`. Never overwrites a non-empty seed value.

    Returns only the fields that changed, so callers can log what a provider
    actually contributed.
    """
    fields = fields or [
        "email", "personal_email", "first_name", "last_name", "name", "title",
        "company", "company_domain", "industry", "employee_count", "linkedin_url",
        "country", "city", "phone",
    ]
    out = {}
    for f in fields:
        seed_val = seed.get(f)
        if seed_val not in (None, "", 0):
            continue
        new_val = candidate.get(f)
        if new_val in (None, ""):
            continue
        out[f] = new_val
    return out
