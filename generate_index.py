# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Scan the skills directory and generate index.json."""

import argparse
import json
import re
from pathlib import Path

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter with one level of nesting support."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result: dict = {}
    current_section: str | None = None
    for line in match.group(1).splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Indented line — belongs to current section (if any)
        if line[0] in (" ", "\t"):
            if current_section is not None:
                stripped = line.strip()
                if stripped.startswith("-"):
                    continue
                key, _, value = stripped.partition(":")
                if value:
                    result.setdefault(current_section, {})[key.strip()] = value.strip()
            continue
        if line[0] == "-":
            continue
        key, _, value = line.partition(":")
        if value.strip():
            result[key.strip()] = value.strip()
            current_section = None
        else:
            # Section header (e.g. "metadata:")
            current_section = key.strip()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate index.json for a skillset repo.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Root of the skillset repo (default: cwd)")
    parser.add_argument("--name", default="Super Agent Public Skillset", help="Skillset name")
    parser.add_argument("--description", default="A public collection of agent templates for the Super Agent app.", help="Skillset description")
    parser.add_argument("--version", default="1.0.0", help="Skillset version")
    args = parser.parse_args()

    root = args.root.resolve()
    skills_dir = root / "skills"
    skills = []

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        fm = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        skills.append({
            "name": fm.get("name", skill_file.parent.name),
            "path": str(skill_file.relative_to(root)),
            "description": fm.get("description", ""),
            "version": fm.get("metadata", {}).get("version", "0.0.0"),
        })

    index = {
        "skillset_name": args.name,
        "description": args.description,
        "version": args.version,
        "skills": skills,
    }

    out = root / "index.json"
    out.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out} with {len(skills)} skill(s).")


if __name__ == "__main__":
    main()
