"""Message linter: enforces copy standards mechanically, not by prompting.

A model told "no em dashes" in a system prompt will still emit one eventually.
This runs on every draft before it can be sent, so the rule is a gate rather
than a suggestion. Rules come from `message_standards` in config.

Severity:
  error: blocks the send outright
  warn: surfaced to the operator, does not block
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

EM_DASH, EN_DASH = "—", "–"

# Common tracking/redirect hosts. Cold mail from a primary domain should carry
# bare links; wrapped ones trip spam heuristics and add nothing at low volume.
TRACKER_PATTERNS = [
    r"utm_[a-z]+=", r"\bmailtrack\b", r"\bhubspotlinks?\.com\b", r"\bsendgrid\.net\b",
    r"\bmailchi\.mp\b", r"\bclick\.[a-z0-9-]+\.com\b", r"\btrk\.", r"\bt\.co/",
    r"\blnkd\.in\b", r"\bbit\.ly\b", r"\btinyurl\.com\b", r"\bmailgun\b",
    r"\bcustomeriomail\b", r"\bsparkpostmail\b", r"open\.gif", r"pixel\.(png|gif)",
]
PIXEL_PATTERN = re.compile(
    r"<img[^>]*(?:width\s*=\s*[\"']?1[\"']?|height\s*=\s*[\"']?1[\"']?)[^>]*>", re.I)

CLICHES = [
    "i hope this email finds you well", "hope this finds you well",
    "i wanted to reach out", "just wanted to reach out", "quick question",
    "circle back", "touch base", "picking your brain", "synergy",
    "reaching out because", "i'll be brief", "per my last email",
    "at your earliest convenience", "game changer", "revolutionary",
    "cutting edge", "best in class", "world class", "seamlessly",
]

_URL = re.compile(r"https?://[^\s<>\"')]+", re.I)
_TAG = re.compile(r"<[^>]+>")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


@dataclass
class LintResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not self.errors

    def report(self) -> str:
        lines = []
        for e in self.errors:
            lines.append(f"  ERROR {e}")
        for w in self.warnings:
            lines.append(f"  WARN  {w}")
        if not lines:
            lines.append("  clean")
        return "\n".join(lines)


def strip_html(text: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", text or "", flags=re.I)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.I)
    return _TAG.sub("", text)


def word_count(text: str) -> int:
    """Words in the body, excluding URLs and the signature block."""
    plain = _URL.sub(" ", strip_html(text))
    return len([w for w in re.split(r"\s+", plain.strip()) if w])


# LinkedIn's hard ceiling on connection-request notes. Anything longer gets
# truncated by the platform, which is worse than short: the prospect sees a
# sentence that stops mid-thought.
LINKEDIN_INVITE_MAX_CHARS = 300


def lint(subject: str, body: str, config, *, signature: str = "",
         sender_id: str | None = None,
         extra_forbidden: list[str] | None = None,
         channel: str = "email") -> LintResult:
    """Lint one drafted message against the team's configured standards.

    `channel` selects which rules apply. Email gets the full set. LinkedIn
    channels have no subject, no signature, and their own length physics, so
    the email-shaped rules are skipped rather than failing every note; the
    voice rules (banned phrases, forbidden names, dashes, clichés) apply to
    every channel because they are about the team, not the medium.
    """
    r = LintResult()
    ms = lambda k, d=None: config.get(f"message_standards.{k}", d)
    is_email = channel == "email"

    plain_body = strip_html(body or "")
    # The signature is configured, not authored, so exclude it from prose checks.
    if signature and signature in plain_body:
        plain_body = plain_body.replace(signature, "")

    subject = (subject or "").strip()

    # -- subject (email only; LinkedIn has none) ------------------------------
    if is_email:
        max_subj = ms("max_subject_chars", 40)
        if not subject:
            r.errors.append("subject is empty")
        elif len(subject) > max_subj:
            r.errors.append(f"subject is {len(subject)} chars, limit is {max_subj}: {subject!r}")

        if ms("forbid_all_caps_subject", True):
            letters = [c for c in subject if c.isalpha()]
            if len(letters) >= 4 and all(c.isupper() for c in letters):
                r.errors.append(f"subject is all caps: {subject!r}")
            shouty = [w for w in subject.split() if len(w) >= 4 and w.isupper()]
            if shouty:
                r.warnings.append(f"subject has shouting word(s): {shouty}")

        if ms("forbid_emojis_in_subject", True):
            from .identity import _EMOJI
            if _EMOJI.search(subject):
                r.errors.append(f"subject contains an emoji: {subject!r}")

        if subject.endswith("!") or "!!" in subject:
            r.warnings.append("exclamation in subject reads as marketing blast")
    elif subject:
        r.warnings.append(f"{channel} has no subject line; {subject!r} will not be seen")

    # -- length ---------------------------------------------------------------
    wc = word_count(body)
    r.stats["words"] = wc
    r.stats["subject_chars"] = len(subject)
    if is_email:
        max_words = ms("max_words", 90)
        if wc > max_words:
            r.errors.append(f"body is {wc} words, limit is {max_words}")
        elif wc > max_words * 0.9:
            r.warnings.append(f"body is {wc} words, close to the {max_words} limit")
        if wc < 25:
            r.warnings.append(f"body is only {wc} words; may read as low effort")
    elif channel == "linkedin_invite":
        chars = len(plain_body.strip())
        r.stats["chars"] = chars
        if chars > LINKEDIN_INVITE_MAX_CHARS:
            r.errors.append(
                f"invite note is {chars} chars; LinkedIn truncates past "
                f"{LINKEDIN_INVITE_MAX_CHARS} and a cut-off sentence reads worse "
                f"than a short one")
        elif chars > LINKEDIN_INVITE_MAX_CHARS - 20:
            r.warnings.append(f"invite note is {chars} chars, within "
                              f"{LINKEDIN_INVITE_MAX_CHARS - chars} of the limit")

    # -- dashes -------------------------------------------------------------
    if ms("forbid_em_dashes", True):
        for label, ch in (("em dash", EM_DASH), ("en dash", EN_DASH)):
            for field_name, text in (("subject", subject), ("body", plain_body)):
                if ch in text:
                    ctx = _context(text, ch)
                    r.errors.append(f"{label} in {field_name}: ...{ctx}...")
        # " - " used as a parenthetical break reads the same way
        if re.search(r"\S\s+-\s+\S", plain_body):
            ctx = _context(plain_body, " - ")
            r.warnings.append(f"spaced hyphen used as a break: ...{ctx}...")

    # -- trackers -----------------------------------------------------------
    if ms("forbid_tracking_pixels", True) and PIXEL_PATTERN.search(body or ""):
        r.errors.append("body contains a 1x1 tracking pixel")
    if ms("forbid_link_trackers", True):
        for pat in TRACKER_PATTERNS:
            m = re.search(pat, body or "", re.I)
            if m:
                r.errors.append(f"tracked/shortened link detected: {m.group(0)!r}")
                break

    # -- forbidden brand names ---------------------------------------------
    forbidden = list(getattr(config, "forbidden_names", []) or [])
    forbidden += list(extra_forbidden or [])
    for name in forbidden:
        if not name:
            continue
        if re.search(rf"\b{re.escape(str(name))}\b", f"{subject} {plain_body}", re.I):
            r.errors.append(f"forbidden name in copy: {name!r}")

    # -- banned phrases -----------------------------------------------------
    # `voice.banned_phrases` is the operator's own kill list, not a taste call,
    # so it blocks rather than warns even where CLICHES only warns.
    for phrase in (config.get("voice.banned_phrases", []) or []):
        if not phrase:
            continue
        for field_name, text in (("subject", subject), ("body", plain_body)):
            m = re.search(re.escape(str(phrase)), text, re.I)
            if m:
                ctx = _context(text, m.group(0))
                r.errors.append(
                    f"banned phrase {str(phrase)!r} in {field_name}: ...{ctx}...")

    # -- CTA (email only: an invite note legitimately has no ask) ------------
    if is_email and ms("single_cta", True):
        urls = set(_URL.findall(body or ""))
        questions = plain_body.count("?")
        if len(urls) > 1:
            r.warnings.append(f"{len(urls)} links; a single CTA converts better: {sorted(urls)}")
        if questions > 2:
            r.warnings.append(f"{questions} questions; ask one thing")
        if not urls and questions == 0:
            r.errors.append("no CTA found: neither a link nor a question")

    cta_url = ms("cta.url")
    if is_email and ms("cta.type") == "self_serve" and cta_url \
            and cta_url not in (body or ""):
        r.warnings.append(f"self-serve CTA configured but {cta_url} is not in the body")

    # Offering a booking link that lands on a colleague's calendar is the kind
    # of error the prospect discovers only after committing, so it is an error
    # rather than a warning. Checked for every sender, not just the CTA type.
    mine = next((s.get("calendar_link") for s in (config.senders or [])
                 if s.get("id") == sender_id), None)
    for s in (config.senders or []):
        link = s.get("calendar_link")
        if link and link != mine and link in (body or ""):
            r.errors.append(
                f"body offers {s.get('id')}'s booking link ({link}) but is being "
                f"sent as {sender_id!r}; use that sender's own calendar_link")
    if is_email and ms("cta.type") == "meeting" and mine and mine not in (body or ""):
        r.warnings.append(f"meeting CTA configured but {sender_id}'s booking link "
                          f"({mine}) is not in the body, so booking needs a round trip")

    # -- formatting (email only; a 300-char note has no paragraphs) ----------
    if is_email and ms("require_blank_line_paragraphs", True):
        paras = [p.strip() for p in re.split(r"\n\s*\n", plain_body) if p.strip()]
        r.stats["paragraphs"] = len(paras)
        if len(paras) < 2 and wc > 40:
            r.errors.append("body is one dense block; split into short paragraphs "
                            "separated by a blank line")
        max_sent = ms("max_sentences_per_paragraph", 3)
        for i, p in enumerate(paras):
            n = len([s for s in _SENTENCE_SPLIT.split(p) if s.strip()])
            if n > max_sent:
                r.warnings.append(f"paragraph {i+1} has {n} sentences, limit is {max_sent}")

    # -- prose quality ------------------------------------------------------
    low = plain_body.lower()
    hits = [c for c in CLICHES if c in low]
    if hits:
        r.warnings.append(f"cliché phrasing: {hits}")

    if re.search(r"\b(we|our company|our platform)\b", low[:200]) and \
       not re.search(r"\b(you|your)\b", low[:200]):
        r.warnings.append("opening leads with 'we' and never says 'you'")

    unfilled = re.findall(r"\{\{?[a-z_.]+\}?\}", plain_body, re.I)
    if unfilled:
        r.errors.append(f"unfilled template placeholder(s): {sorted(set(unfilled))}")

    if re.search(r"\b(TODO|TBD|XXX|FIXME|LOREM IPSUM)\b", plain_body, re.I):
        r.errors.append("draft contains placeholder text (TODO/TBD/XXX)")

    return r


def _context(text: str, needle: str, width: int = 28) -> str:
    i = text.find(needle)
    if i < 0:
        return ""
    lo, hi = max(0, i - width), min(len(text), i + len(needle) + width)
    return text[lo:hi].replace("\n", " ").strip()
