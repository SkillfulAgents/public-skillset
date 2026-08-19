# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Check an agent README against this repository's marketplace conventions.

Usage:
    uv run .claude/skills/agent-readme/scripts/check_agent_readme.py agents/<slug>
    uv run .claude/skills/agent-readme/scripts/check_agent_readme.py --all

Reports `error:` lines (block the commit) and `warning:` lines (justify or fix).
Exits non-zero when any error is found.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from generate_index import (  # noqa: E402
    _developer_field,
    _icon_field,
    _tags_field,
    _works_with_field,
    read_document,
)

README_KEYS = ["category", "icon", "tags", "works_with", "developer"]
CLAUDE_ONLY_KEYS = {"name", "description", "createdAt", "version"}
GENERATED_KEYS = {"path", "details"}

KNOWN_CATEGORIES = {
    "Agent Creation",
    "Customer Success",
    "Design & Creative",
    "Email & Communication",
    "Health & Fitness",
    "Human Resources",
    "Marketing",
    "Operations",
    "Ops",
    "Personal",
    "Productivity",
    "Sales",
}

LIGHT_SECTIONS = [
    "What it does",
    "Connect first",
    "Sample use cases",
    "Getting started",
    "Example prompts",
    "Files",
    "Credits",
]
# Shape of a README written before the starter-chip section existed. Every
# agent in the repo has been backfilled; this is kept so a stale or externally
# authored README is flagged as needing chips rather than rejected as malformed.
LIGHT_SECTIONS_PRE_CHIPS = [s for s in LIGHT_SECTIONS if s != "Example prompts"]
FULL_SECTIONS = {
    "What it does",
    "What you'll need",
    "What it needs",
    "Getting started",
    "Example prompts",
    "What's inside",
    "Layout",
    "Notes",
    "Privacy",
    "Credits",
}

# The platform's default chips. A template that ships these has not replaced
# the fallback, which is the only reason the section exists.
FALLBACK_PROMPTS = {
    "help me get started",
    "what can you do",
    "walk me through your first run",
    "what do you do",
    "get started",
}
PROMPT_MIN_CHARS = 25
PROMPT_MAX_CHARS = 80

CONNECT_SUFFIXES = [
    re.compile(r"SuperAgent API account `[a-z0-9][a-z0-9._-]*`\.\Z"),
    re.compile(r"SuperAgent MCP `[a-z0-9][a-z0-9._-]*`\.\Z"),
    re.compile(r"browser session; no registry slug\.\Z"),
    re.compile(r"local tool or resource; no connection slug\.\Z"),
    re.compile(r"built-in capability; no connection slug\.\Z"),
    re.compile(r"built-in iMessage chat integration; no registry slug\.\Z"),
    re.compile(r"external connection; no canonical registry slug\.\Z"),
    re.compile(r"direct API, feed, or required credentials; no canonical registry slug\.\Z"),
]

# READMEs that predate the convention. Listed so the checker stays useful
# instead of crying wolf; do not extend this set.
LEGACY_H1_DRIFT = {
    "open-slide-studio",
    "outbound-campaign-agent",
    "recruiting-agent",
    "seo-agent",
}
LEGACY_NO_HOOK = {"outbound-campaign-agent", "recruiting-agent", "seo-agent"}


class Report:
    def __init__(self, slug: str) -> None:
        self.slug = slug
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def emit(self) -> None:
        for message in self.errors:
            print(f"error:   {self.slug}: {message}")
        for message in self.warnings:
            print(f"warning: {self.slug}: {message}")
        if not self.errors and not self.warnings:
            print(f"ok:      {self.slug}")


def headings(body: str) -> list[str]:
    return [line[3:].strip() for line in body.splitlines() if line.startswith("## ")]


def section(body: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in body:
        return ""
    return body.split(marker, 1)[1].split("\n## ", 1)[0]


def check_frontmatter(metadata: dict, report: Report) -> None:
    keys = list(metadata)
    stray = CLAUDE_ONLY_KEYS.intersection(keys)
    if stray:
        report.error(
            f"README frontmatter must not define {sorted(stray)} — those belong to CLAUDE.md, which wins the merge"
        )
    generated = GENERATED_KEYS.intersection(keys)
    if generated:
        report.error(f"README frontmatter must not define generated keys {sorted(generated)}")

    missing = [key for key in README_KEYS if key not in metadata]
    if missing:
        report.error(f"missing required frontmatter keys: {missing}")

    unknown = [key for key in keys if key not in README_KEYS and key not in CLAUDE_ONLY_KEYS | GENERATED_KEYS]
    if unknown:
        report.error(f"unexpected frontmatter keys: {unknown}")

    ordered = [key for key in keys if key in README_KEYS]
    if ordered != [key for key in README_KEYS if key in ordered]:
        report.warn(f"frontmatter key order is {ordered}; convention is {README_KEYS}")

    source = "README.md"
    category = metadata.get("category", "")
    if not isinstance(category, str) or not category.strip():
        report.error("'category' must be a non-empty string")
    elif category not in KNOWN_CATEGORIES:
        report.warn(f"'category' {category!r} is new to this repo — reuse an existing value unless it is genuinely new")
    elif category == "Operations":
        report.warn("'category' 'Operations' is a legacy outlier; new agents should use 'Ops'")

    try:
        icon = _icon_field(metadata, source)
        if not icon:
            report.error("'icon' is required and must be a Lucide catalog name")
    except ValueError as exc:
        report.error(str(exc))

    try:
        tags = _tags_field(metadata, source)
        if not 4 <= len(tags) <= 7:
            report.error(f"'tags' must contain 4-7 entries, found {len(tags)}")
        if len(tags) != len(set(tags)):
            report.error("'tags' contains duplicates")
        for tag in tags:
            if tag != tag.strip():
                report.error(f"tag {tag!r} has surrounding whitespace")
            if re.fullmatch(r"[a-z0-9]+([-_][a-z0-9]+)*", tag):
                report.warn(f"tag {tag!r} looks like a slug; tags are display strings (e.g. 'Email Management')")
    except ValueError as exc:
        report.error(str(exc))

    if "works_with" not in metadata:
        report.error("'works_with' must be present, using [] when the agent needs no registry connector")
    else:
        try:
            _works_with_field(metadata, source)
        except ValueError as exc:
            report.error(str(exc))

    try:
        developer = _developer_field(metadata, source)
        if not developer.get("name"):
            report.error("'developer.name' is required")
        if "url" not in developer:
            report.warn("'developer.url' is missing; every existing agent credits an absolute http(s) URL")
    except ValueError as exc:
        report.error(str(exc))


def check_body(body: str, name: str, description: str, is_light: bool, slug: str, report: Report) -> None:
    lines = [line for line in body.splitlines() if line.strip()]
    if not lines:
        report.error("README body is empty; it becomes the agent's 'details' in index.json")
        return

    if not lines[0].startswith("# "):
        report.error("body must open with an H1 matching the agent name")
    else:
        h1 = lines[0][2:].strip()
        if h1 != name and slug not in LEGACY_H1_DRIFT:
            report.error(f"H1 {h1!r} does not match CLAUDE.md name {name!r}")

    summary = lines[1] if len(lines) > 1 else ""
    if summary.startswith("## "):
        report.error("a one-line summary must follow the H1 before the first section")
    elif is_light:
        if summary.strip() != description.strip():
            report.error("light imports must repeat the CLAUDE.md description verbatim under the H1")
    elif not summary.startswith(">") and slug not in LEGACY_NO_HOOK:
        report.warn("full templates open with a '>' blockquote hook under the H1")

    found = headings(body)
    if is_light:
        if found == LIGHT_SECTIONS_PRE_CHIPS:
            report.warn("missing '## Example prompts' — add three starter chips (see references/body-structure.md)")
        elif found != LIGHT_SECTIONS:
            report.error(f"light-import sections must be exactly {LIGHT_SECTIONS}, found {found}")
    else:
        unknown = [heading for heading in found if heading not in FULL_SECTIONS]
        if unknown:
            report.warn(f"headings outside the approved vocabulary: {unknown}")
        for required in ("What it does", "Getting started"):
            if required not in found:
                report.error(f"missing required section '## {required}'")
        if not {"What's inside", "Layout"}.intersection(found):
            report.warn("no '## What's inside' (or '## Layout') file manifest")
        if not {"What you'll need", "What it needs"}.intersection(found):
            report.warn("no '## What you'll need' requirements section")
        if "Example prompts" not in found:
            report.warn("missing '## Example prompts' — add three starter chips (see references/body-structure.md)")
        elif "Getting started" in found and found.index("Example prompts") != found.index("Getting started") + 1:
            report.warn("'## Example prompts' should follow '## Getting started' directly")

    for line in body.splitlines():
        if line.startswith("# ") and line != lines[0]:
            report.error(f"only one H1 is allowed; found {line!r}")
        if line.rstrip() != line:
            report.error(f"trailing whitespace: {line!r}")


def check_example_prompts(body: str, report: Report) -> None:
    """Validate the three starter chips rendered on the agent detail page."""
    prompts = section(body, "Example prompts")
    if not prompts.strip():
        return

    bullets = [line.strip() for line in prompts.splitlines() if line.strip().startswith("- ")]
    stray = [
        line.strip()
        for line in prompts.splitlines()
        if line.strip() and not line.strip().startswith("- ")
    ]
    if stray:
        report.error(f"'## Example prompts' must contain only bullets, found prose: {stray[0]!r}")
    if len(bullets) != 3:
        report.error(f"'## Example prompts' must contain exactly 3 bullets, found {len(bullets)}")

    seen: set[str] = set()
    for bullet in bullets:
        text = bullet[2:].strip()
        normalized = re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()

        if normalized in FALLBACK_PROMPTS:
            report.error(
                f"{text!r} is a platform fallback chip; replace it with something specific to this agent"
            )
        if normalized in seen:
            report.error(f"duplicate example prompt: {text!r}")
        seen.add(normalized)

        if text.startswith("@"):
            report.error(f"{text!r} must not lead with a mention; the page prepends '@<Name>'")
        if re.search(r"[`*_\[\]]|<[^>]+>|\{\{", text):
            report.error(f"{text!r} must be plain text — no markdown, placeholders, or template tokens")
        if text.endswith("."):
            report.error(f"{text!r} must not end with a period")
        if len(text) > PROMPT_MAX_CHARS:
            report.warn(f"{text!r} is {len(text)} chars; over {PROMPT_MAX_CHARS} wraps in the chip")
        elif len(text) < PROMPT_MIN_CHARS:
            report.warn(f"{text!r} is {len(text)} chars; under {PROMPT_MIN_CHARS} reads as a stub")


def check_connections(body: str, metadata: dict, is_light: bool, report: Report) -> None:
    if not is_light:
        return
    connect = section(body, "Connect first")
    bullets = [line.strip() for line in connect.splitlines() if line.strip().startswith("- ")]
    if not bullets:
        report.error("'## Connect first' must list at least one bullet")

    listed: set[tuple[str, str]] = set()
    for bullet in bullets:
        match = re.fullmatch(r"- \*\*(?P<label>.+?)\*\* — (?P<suffix>.+)", bullet)
        if not match:
            report.error(f"Connect first bullet is not '- **Label** — suffix': {bullet!r}")
            continue
        suffix = match.group("suffix")
        if not any(pattern.fullmatch(suffix) for pattern in CONNECT_SUFFIXES):
            report.error(f"Connect first suffix is outside the approved vocabulary: {suffix!r}")
            continue
        slug_match = re.search(r"`([a-z0-9][a-z0-9._-]*)`", suffix)
        if slug_match and "SuperAgent API account" in suffix:
            listed.add(("api_account", slug_match.group(1)))
        elif slug_match and "SuperAgent MCP" in suffix:
            listed.add(("mcp", slug_match.group(1)))

    declared = {(item["type"], item["slug"]) for item in metadata.get("works_with", []) if isinstance(item, dict)}
    for entry in sorted(declared - listed):
        report.error(f"works_with declares {entry[0]}:{entry[1]} but 'Connect first' never mentions it")
    for entry in sorted(listed - declared):
        report.error(f"'Connect first' names {entry[0]}:{entry[1]} but works_with omits it")


def check_agent(directory: Path) -> Report:
    slug = directory.name
    report = Report(slug)

    claude_path = directory / "CLAUDE.md"
    readme_path = directory / "README.md"
    if not claude_path.is_file():
        report.error("missing CLAUDE.md")
        return report
    if not readme_path.is_file():
        report.error("missing README.md — every public agent needs one")
        return report

    claude_metadata, _ = read_document(claude_path)
    for key in sorted(CLAUDE_ONLY_KEYS):
        value = claude_metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            report.error(f"CLAUDE.md frontmatter '{key}' must be a non-empty string")

    raw = readme_path.read_text(encoding="utf-8")
    if not raw.endswith("\n"):
        report.error("README.md must end with a newline")
    elif raw.endswith("\n\n"):
        report.error("README.md has more than one trailing newline")

    try:
        metadata, body = read_document(readme_path)
    except ValueError as exc:
        report.error(str(exc))
        return report

    if not metadata:
        report.error("README.md has no YAML frontmatter")
        return report

    is_light = (directory / "PROMPT.md").is_file()
    check_frontmatter(metadata, report)
    check_body(
        body,
        claude_metadata.get("name", slug),
        claude_metadata.get("description", ""),
        is_light,
        slug,
        report,
    )
    check_connections(body, metadata, is_light, report)
    check_example_prompts(body, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("paths", nargs="*", type=Path, help="agent directories to check")
    parser.add_argument("--all", action="store_true", help="check every agent under agents/")
    args = parser.parse_args()

    if args.all:
        directories = sorted(path.parent for path in (ROOT / "agents").glob("*/CLAUDE.md"))
    elif args.paths:
        directories = [path if path.is_absolute() else (Path.cwd() / path) for path in args.paths]
    else:
        parser.error("pass one or more agent directories, or --all")

    failures = 0
    warned = 0
    for directory in directories:
        report = check_agent(directory)
        report.emit()
        failures += bool(report.errors)
        warned += bool(report.warnings and not report.errors)

    print(f"\n{len(directories)} agent(s) checked, {failures} with errors, {warned} with warnings only.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
