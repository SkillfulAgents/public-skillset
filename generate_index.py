# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Scan the skills and agents directories and generate index.json."""

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

FRONTMATTER_START_RE = re.compile(r"\A---[ \t]*(?:\r?\n)")
FRONTMATTER_RE = re.compile(
    r"\A---[ \t]*\r?\n(?P<frontmatter>.*?)^---[ \t]*(?:\r?\n|\Z)",
    re.DOTALL | re.MULTILINE,
)
WORKS_WITH_TYPES = {"api_account", "mcp"}
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
ICON_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class UniqueKeyBaseLoader(yaml.BaseLoader):
    """BaseLoader variant that rejects ambiguous duplicate mapping keys."""

    def construct_mapping(self, node: MappingNode, deep: bool = False) -> dict[Any, Any]:
        if not isinstance(node, MappingNode):
            raise ConstructorError(None, None, f"expected a mapping node, but found {node.id}", node.start_mark)

        mapping: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                duplicate = key in mapping
            except TypeError as exc:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    "found an unhashable key",
                    key_node.start_mark,
                ) from exc
            if duplicate:
                raise ConstructorError(
                    "while constructing a mapping",
                    node.start_mark,
                    f"found duplicate key ({key!r})",
                    key_node.start_mark,
                )
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def parse_document(text: str, source: str = "<document>") -> tuple[dict[str, Any], str]:
    """Return YAML frontmatter and the Markdown body from a document.

    BaseLoader intentionally keeps every scalar as a string. That prevents values
    such as timestamps, versions, and tags like ``on`` from being coerced into
    dates, floats, or booleans while still supporting nested maps and lists.
    """
    text = text.removeprefix("\ufeff")
    if not FRONTMATTER_START_RE.match(text):
        return {}, text.strip("\r\n")

    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"{source}: opening frontmatter delimiter has no closing '---'")

    try:
        metadata = yaml.load(match.group("frontmatter"), Loader=UniqueKeyBaseLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"{source}: invalid YAML frontmatter: {exc}") from exc

    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{source}: frontmatter must be a YAML mapping")

    return metadata, text[match.end() :].strip("\r\n")


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Parse YAML frontmatter while preserving the generator's public helper."""
    return parse_document(text)[0]


def read_document(path: Path) -> tuple[dict[str, Any], str]:
    """Read and parse a Markdown document with path-aware errors."""
    return parse_document(path.read_text(encoding="utf-8"), str(path))


def _resolve_repo_file(root: Path, path: Path) -> Path:
    """Resolve a regular source file and reject symlinks or outside targets."""
    resolved_root = root.resolve()
    resolved_path = path.resolve(strict=True)
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(f"{path}: resolves outside repository root {resolved_root}") from exc

    # Reject symlinks below the selected root rather than silently changing an
    # entry's discovered path or reading a different agent's sibling README.
    current = path
    while current.resolve() != resolved_root:
        if current.is_symlink():
            raise ValueError(f"{path}: symlinked metadata sources are not supported")
        parent = current.parent
        if parent == current:
            raise ValueError(f"{path}: could not establish repository containment")
        current = parent
    return resolved_path


def _string_field(metadata: dict[str, Any], key: str, default: str, source: str) -> str:
    value = metadata.get(key, default)
    if not isinstance(value, str):
        raise ValueError(f"{source}: '{key}' must be a string")
    return value


def _tags_field(metadata: dict[str, Any], source: str) -> list[str]:
    value = metadata.get("tags", [])
    if not isinstance(value, list) or any(not isinstance(tag, str) or not tag.strip() for tag in value):
        raise ValueError(f"{source}: 'tags' must be a list of non-empty strings")
    return value


def _icon_field(metadata: dict[str, Any], source: str) -> str:
    value = _string_field(metadata, "icon", "", source)
    if value and not ICON_RE.fullmatch(value):
        raise ValueError(f"{source}: 'icon' must be a lowercase kebab-case Lucide icon name")
    return value


def _works_with_field(metadata: dict[str, Any], source: str) -> list[dict[str, str]]:
    value = metadata.get("works_with", [])
    if not isinstance(value, list):
        raise ValueError(f"{source}: 'works_with' must be a list")

    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(value):
        location = f"{source}: works_with[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{location} must be an object")
        if set(item) != {"type", "slug"}:
            raise ValueError(f"{location} must contain exactly 'type' and 'slug'")

        entry_type = item.get("type")
        slug = item.get("slug")
        if not isinstance(entry_type, str) or entry_type not in WORKS_WITH_TYPES:
            allowed = ", ".join(sorted(WORKS_WITH_TYPES))
            raise ValueError(f"{location}.type must be one of: {allowed}")
        if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
            raise ValueError(f"{location}.slug must be an exact lowercase registry slug")

        key = (entry_type, slug)
        if key in seen:
            raise ValueError(f"{location} duplicates '{entry_type}:{slug}'")
        seen.add(key)
        result.append({"type": entry_type, "slug": slug})

    return result


def _developer_field(metadata: dict[str, Any], source: str) -> dict[str, str]:
    value = metadata.get("developer", {})
    if not isinstance(value, dict):
        raise ValueError(f"{source}: 'developer' must be an object")
    if not value:
        return {}
    if set(value) - {"name", "url"}:
        raise ValueError(f"{source}: 'developer' may only contain 'name' and 'url'")

    name = value.get("name")
    url = value.get("url")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{source}: 'developer.name' must be a non-empty string")
    if url is not None and (not isinstance(url, str) or not url.strip()):
        raise ValueError(f"{source}: 'developer.url' must be a non-empty string when present")
    if url is not None:
        parsed_url = urlparse(url)
        if url != url.strip() or parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError(f"{source}: 'developer.url' must be an absolute http(s) URL")

    return {"name": name, **({"url": url} if url is not None else {})}


def build_agent_entry(root: Path, agent_file: Path) -> dict[str, Any]:
    """Build one index entry, merging README metadata beneath CLAUDE metadata."""
    root = root.resolve()
    agent_file = _resolve_repo_file(root, agent_file)
    claude_metadata, _ = read_document(agent_file)
    readme_file = agent_file.parent / "README.md"
    if readme_file.exists():
        readme_file = _resolve_repo_file(root, readme_file)
        readme_metadata, details = read_document(readme_file)
    else:
        readme_metadata, details = {}, ""

    # This is deliberately shallow: the complete CLAUDE value wins whenever a
    # top-level key occurs in both documents, including falsey values.
    metadata = {**readme_metadata, **claude_metadata}
    source = f"merged metadata for {agent_file.parent}"

    return {
        "name": _string_field(metadata, "name", agent_file.parent.name, source),
        "path": agent_file.parent.relative_to(root).as_posix() + "/",
        "description": _string_field(metadata, "description", "", source),
        "details": details,
        "createdAt": _string_field(metadata, "createdAt", "", source),
        "version": _string_field(metadata, "version", "1.0.0", source),
        "category": _string_field(metadata, "category", "", source),
        "icon": _icon_field(metadata, source),
        "tags": _tags_field(metadata, source),
        "works_with": _works_with_field(metadata, source),
        "developer": _developer_field(metadata, source),
    }


def build_index(root: Path, name: str, description: str, version: str) -> dict[str, Any]:
    """Build a complete skillset index without writing it."""
    root = root.resolve()

    skills = []
    skills_dir = root / "skills"
    if skills_dir.exists():
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            skill_file = _resolve_repo_file(root, skill_file)
            frontmatter, _ = read_document(skill_file)
            source = f"frontmatter for {skill_file}"
            skill_metadata = frontmatter.get("metadata", {})
            if not isinstance(skill_metadata, dict):
                raise ValueError(f"{skill_file}: 'metadata' must be an object")
            skills.append(
                {
                    "name": _string_field(frontmatter, "name", skill_file.parent.name, source),
                    "path": skill_file.relative_to(root).as_posix(),
                    "description": _string_field(frontmatter, "description", "", source),
                    "version": _string_field(skill_metadata, "version", "0.0.0", source),
                }
            )

    agents = []
    agents_dir = root / "agents"
    if agents_dir.exists():
        for agent_file in sorted(agents_dir.glob("*/CLAUDE.md")):
            agents.append(build_agent_entry(root, agent_file))

    return {
        "skillset_name": name,
        "description": description,
        "version": version,
        "skills": skills,
        "agents": agents,
    }


def write_index(root: Path, index: dict[str, Any]) -> Path:
    """Write index.json with deterministic formatting and a final newline."""
    out = root.resolve() / "index.json"
    out.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate index.json for a skillset repo.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Root of the skillset repo (default: cwd)")
    parser.add_argument("--name", default="Gamut Public Skillset", help="Skillset name")
    parser.add_argument("--description", default="A public collection of agent templates for the Gamut app.", help="Skillset description")
    parser.add_argument("--version", default="1.0.0", help="Skillset version")
    args = parser.parse_args()

    index = build_index(args.root, args.name, args.description, args.version)
    out = write_index(args.root, index)
    print(f"Wrote {out} with {len(index['skills'])} skill(s) and {len(index['agents'])} agent(s).")


if __name__ == "__main__":
    main()
