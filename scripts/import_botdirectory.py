#!/usr/bin/env python3
"""Generate lightweight agent templates from a reviewed Bot Directory snapshot.

The script intentionally does not fetch the network. Its inputs are a captured catalog
and a human-reviewed connector crosswalk so imports are reproducible and cannot invent
SuperAgent registry slugs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any


CATEGORY_ICONS = {
    "Customer Success": "life-buoy",
    "Marketing": "megaphone",
    "Ops": "workflow",
    "Personal": "sparkles",
    "Productivity": "list-checks",
    "Sales": "badge-dollar-sign",
}
ICON_RULES = (
    (("support", "ticket", "customer"), "life-buoy"),
    (("email", "inbox", "mail"), "mail"),
    (("calendar", "appointment", "meeting", "schedule"), "calendar-check"),
    (("flight", "trip", "travel", "itinerary"), "plane"),
    (("youtube", "video", "clip", "film"), "video"),
    (("podcast", "voice"), "mic"),
    (("github", "codebase", "development", "repository"), "code-2"),
    (("security", "threat", "hardening"), "shield-check"),
    (("sales", "prospect", "crm", "deal"), "badge-dollar-sign"),
    (("content", "article", "writing", "writer"), "pen-line"),
    (("seo", "search", "signal", "research"), "search"),
    (("social", "tweet", "linkedin", "community"), "messages-square"),
    (("finance", "accounting", "bookkeeping", "ledger", "cfo"), "calculator"),
    (("home", "household", "grocery", "recipe"), "house"),
    (("recruit", "applicant", "hire"), "user-search"),
    (("docs", "notion", "wiki", "knowledge"), "book-open"),
    (("deck", "slide", "presentation"), "presentation"),
)
MAPPED_KINDS = {"api_account", "mcp"}
UNMAPPED_KINDS = {"browser", "builtin", "external", "local", "raw_api"}
ALL_KINDS = MAPPED_KINDS | UNMAPPED_KINDS
DIRECT_API_KINDS = {"external", "raw_api"}
BUILTIN_SEARCH_LABELS = {"Google Search", "Web Search"}
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
TEMPLATE_SLUG_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def yaml_string_list(key: str, values: list[str]) -> list[str]:
    if not values:
        return [f"{key}: []"]
    return [f"{key}:", *(f"  - {yaml_string(value)}" for value in values)]


def choose_icon(name: str, category: str) -> str:
    lowered = name.lower()
    for needles, icon in ICON_RULES:
        if any(needle in lowered for needle in needles):
            return icon
    return CATEGORY_ICONS[category]


def normalize_category(category: str) -> str:
    return "Customer Success" if category == "Success" else category


def mapping_sentence(label: str, mapping: dict[str, str]) -> str:
    kind = mapping["kind"]
    if kind == "api_account":
        return (
            f"{label} through the SuperAgent API account `{mapping['slug']}` "
            f"(`api_account:{mapping['slug']}`)"
        )
    if kind == "mcp":
        return (
            f"{label} through the SuperAgent MCP `{mapping['slug']}` "
            f"(`mcp:{mapping['slug']}`)"
        )
    if kind == "browser":
        return f"{label} through a browser session (no SuperAgent registry slug)"
    if kind == "builtin":
        if label == "Apple Messages":
            return (
                "Apple Messages through SuperAgent's iMessage chat integration "
                "(no registry slug required)"
            )
        return f"{label} as a built-in capability (no connection slug required)"
    if kind == "local":
        return f"{label} as a local tool or resource (no connection slug required)"
    if kind == "raw_api":
        return (
            f"{label} through its direct API, feed, or required credentials "
            "(no canonical SuperAgent registry slug)"
        )
    return (
        f"{label} through the connection method available to the user "
        "(no canonical SuperAgent registry slug)"
    )


def readme_mapping_line(label: str, mapping: dict[str, str]) -> str:
    kind = mapping["kind"]
    if kind == "api_account":
        return f"- **{label}** — SuperAgent API account `{mapping['slug']}`."
    if kind == "mcp":
        return f"- **{label}** — SuperAgent MCP `{mapping['slug']}`."
    if kind == "browser":
        return f"- **{label}** — browser session; no registry slug."
    if kind == "builtin":
        if label == "Apple Messages":
            return "- **Apple Messages** — built-in iMessage chat integration; no registry slug."
        return f"- **{label}** — built-in capability; no connection slug."
    if kind == "local":
        return f"- **{label}** — local tool or resource; no connection slug."
    if kind == "raw_api":
        return f"- **{label}** — direct API, feed, or required credentials; no canonical registry slug."
    return f"- **{label}** — external connection; no canonical registry slug."


def connection_method_lines(
    template: dict[str, Any], mappings: dict[str, dict[str, str]]
) -> list[str]:
    labels = template["connectFirst"]
    browser_labels = [label for label in labels if mappings[label]["kind"] == "browser"]
    direct_api_labels = [
        label for label in labels if mappings[label]["kind"] in DIRECT_API_KINDS
    ]
    search_labels = [
        label
        for label in labels
        if label in BUILTIN_SEARCH_LABELS and mappings[label]["kind"] == "builtin"
    ]
    lines: list[str] = []

    if browser_labels:
        display_labels = ", ".join(f"`{label}`" for label in browser_labels)
        lines.append(
            f"- For browser-based connections ({display_labels}), use SuperAgent's dedicated "
            "`mcp__browser__browser_*` tools, starting with "
            "`mcp__browser__browser_open`. For multi-step browsing, delegate with "
            "`Agent(subagent_type=\"web-browser\", prompt=\"<task>\")`."
        )

    if (
        "Apple Messages" in labels
        and mappings["Apple Messages"]["kind"] == "builtin"
    ):
        lines.append(
            "- For Apple Messages, use the iMessage chat integration: call "
            "`mcp__chat__list_available_chat_providers`, collect the required setup "
            "details, then call `mcp__chat__add_chat_integration` with provider `imessage`."
        )

    if search_labels:
        display_labels = ", ".join(f"`{label}`" for label in search_labels)
        lines.append(
            f"- For built-in search ({display_labels}), use `mcp__web__web_search` when "
            "configured, otherwise native `WebSearch`; do not request an API key."
        )

    for label in direct_api_labels:
        lines.append(
            f"- For the {label} connection, ask the user for an API key with "
            "`mcp__user-input__request_secret` and use direct API calls."
        )

    return lines


def render_claude(template: dict[str, Any], mappings: dict[str, dict[str, str]]) -> str:
    name = template["name"]
    category = normalize_category(template["sourceCategory"])
    first_run = "; ".join(
        mapping_sentence(label, mappings[label]) for label in template["connectFirst"]
    )
    if not first_run:
        first_run = "no external account or MCP is required"
    method_lines = connection_method_lines(template, mappings)

    lines = [
        "---",
        f"name: {yaml_string(name)}",
        f"description: {yaml_string(template['description'])}",
        "version: 1.0.0",
        f"createdAt: {yaml_string(template['addedAt'])}",
        "---",
        "",
        f"# {name}",
        "",
        template["roleSentence"].rstrip(".") + ".",
        "",
        "## First run",
        "",
        "Before doing any work on the first run, connect each applicable listed account or "
        "service, following `PROMPT.md` when alternatives are offered: "
        + first_run
        + ".",
        "",
        "Then read `PROMPT.md` as the canonical setup brief. Gather the requested "
        "preferences and boundaries, complete the supervised first run, and save the "
        "resulting workflow or cadence for later use.",
        "",
        *(
            ["## Connection methods", "", *method_lines, ""]
            if method_lines
            else []
        ),
        "## Operating rules",
        "",
        "- Follow `PROMPT.md` faithfully; do not silently broaden the workflow.",
        "- Ask for missing context instead of inventing user preferences, access, or policy.",
        "- Keep the first execution supervised and show the result before enabling a cadence.",
        "- Require explicit approval before external communication, spending, booking, "
        "publishing, deployment, or destructive changes.",
        "- Record durable preferences, boundaries, and cadence decisions in Project Notes.",
        "",
        "## Preferences",
        "",
        "<!-- Add user-specific preferences learned during setup. -->",
        "",
        "## Project Notes",
        "",
        f"<!-- Keep durable {category.lower()} context and decisions here. -->",
        "",
    ]
    return "\n".join(lines)


def render_readme(
    template: dict[str, Any],
    mappings: dict[str, dict[str, str]],
    works_with: list[dict[str, str]],
    icon: str,
) -> str:
    category = normalize_category(template["sourceCategory"])
    creator_name = template["creatorCredit"]
    creator_url = template["creatorUrl"]

    frontmatter = [
        "---",
        f"category: {yaml_string(category)}",
        f"icon: {icon}",
        *yaml_string_list("tags", template["tags"]),
    ]
    if works_with:
        frontmatter.append("works_with:")
        for connection in works_with:
            frontmatter.extend(
                [
                    f"  - type: {connection['type']}",
                    f"    slug: {connection['slug']}",
                ]
            )
    else:
        frontmatter.append("works_with: []")
    frontmatter.extend(
        [
            "developer:",
            f"  name: {yaml_string(creator_name)}",
            f"  url: {yaml_string(creator_url)}",
            "---",
            "",
        ]
    )

    connection_lines = [
        readme_mapping_line(label, mappings[label]) for label in template["connectFirst"]
    ] or ["- No external connection is required."]
    use_case_lines = [f"- {item.rstrip('.')}." for item in template["sampleUseCases"]]

    body = [
        f"# {template['name']}",
        "",
        template["description"].rstrip(".") + ".",
        "",
        "## What it does",
        "",
        f"- {template['roleSentence'].rstrip('.')}.",
        "- Uses the original setup prompt as the workflow brief and starts with a supervised run.",
        "- Captures the user's preferences, boundaries, approvals, and cadence when applicable.",
        "",
        "## Connect first",
        "",
        *connection_lines,
        "",
        "## Sample use cases",
        "",
        *use_case_lines,
        "",
        "## Getting started",
        "",
        "1. Import this directory as an agent template.",
        "2. Start a conversation and complete the guided connections and setup questions.",
        "3. Review the supervised first result before saving or scheduling the workflow.",
        "",
        "## Files",
        "",
        "- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.",
        "- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.",
        "- `README.md` — marketplace metadata, examples, connection mapping, and credits.",
        "",
        "## Credits",
        "",
        f"Original prompt credited to [{creator_name}]({creator_url}) on "
        f"[Bot Directory]({template['detailUrl']}). Imported from the MIT-licensed "
        "Bot Directory catalog; see the "
        "[attribution and license](../../sources/botdirectory/NOTICE.md).",
        "",
    ]
    return "\n".join([*frontmatter, *body])


def validate_inputs(
    templates: list[dict[str, Any]], mappings: dict[str, dict[str, str]]
) -> None:
    required = {
        "name",
        "slug",
        "detailUrl",
        "sourceCategory",
        "creatorCredit",
        "creatorAccount",
        "creatorUrl",
        "connectFirst",
        "prompt",
        "addedAt",
        "description",
        "tags",
        "sampleUseCases",
        "roleSentence",
    }
    seen_slugs: set[str] = set()
    used_labels: set[str] = set()
    for template in templates:
        missing = sorted(required - set(template))
        if missing:
            raise ValueError(f"{template.get('slug', '<unknown>')}: missing {', '.join(missing)}")
        slug = template["slug"]
        if not isinstance(slug, str) or not TEMPLATE_SLUG_RE.fullmatch(slug):
            raise ValueError(f"invalid template directory slug: {slug!r}")
        if slug in seen_slugs:
            raise ValueError(f"duplicate template slug: {slug}")
        seen_slugs.add(slug)
        if normalize_category(template["sourceCategory"]) not in CATEGORY_ICONS:
            raise ValueError(f"{slug}: unsupported category {template['sourceCategory']!r}")
        if not template["prompt"].strip():
            raise ValueError(f"{slug}: empty prompt")
        if not 4 <= len(template["tags"]) <= 7:
            raise ValueError(f"{slug}: expected 4-7 tags")
        if not 2 <= len(template["sampleUseCases"]) <= 3:
            raise ValueError(f"{slug}: expected 2-3 sample use cases")
        used_labels.update(template["connectFirst"])

    missing_mappings = sorted(used_labels - set(mappings))
    extra_mappings = sorted(set(mappings) - used_labels)
    if missing_mappings:
        raise ValueError(f"unmapped Connect First labels: {', '.join(missing_mappings)}")
    if extra_mappings:
        raise ValueError(f"unused Connect First mappings: {', '.join(extra_mappings)}")

    for label, mapping in mappings.items():
        kind = mapping.get("kind")
        if kind not in ALL_KINDS:
            raise ValueError(f"{label}: invalid mapping kind {kind!r}")
        slug = mapping.get("slug")
        if kind in MAPPED_KINDS:
            if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
                raise ValueError(f"{label}: mapped connection needs a canonical slug")
        elif slug is not None:
            raise ValueError(f"{label}: {kind} classifications must not invent a slug")
        if not isinstance(mapping.get("reason"), str) or not mapping["reason"].strip():
            raise ValueError(f"{label}: mapping needs a reason")


def import_templates(
    root: Path,
    inventory: dict[str, Any],
    crosswalk: dict[str, Any],
    source_commit: str,
    overwrite: bool,
) -> None:
    if inventory.get("sourceCommit") != source_commit:
        raise ValueError(
            "inventory sourceCommit does not match the requested --source-commit"
        )
    templates = inventory.get("templates")
    mapping_list = crosswalk.get("labels")
    if not isinstance(templates, list) or not isinstance(mapping_list, list):
        raise ValueError("inventory.templates and crosswalk.labels must be arrays")
    mappings = {entry["name"]: {key: value for key, value in entry.items() if key != "name"} for entry in mapping_list}
    if len(mappings) != len(mapping_list):
        raise ValueError("duplicate names in connector crosswalk")
    validate_inputs(templates, mappings)

    manifest_entries: list[dict[str, Any]] = []
    source_root = root / "sources" / "botdirectory"
    previous_catalog_path = source_root / "catalog.json"
    previous_slugs: set[str] = set()
    if previous_catalog_path.is_file():
        previous_catalog = load_json(previous_catalog_path)
        previous_slugs = {
            entry["slug"] for entry in previous_catalog.get("templates", [])
        }
    agents_root = root / "agents"
    resolved_agents_root = agents_root.resolve()
    sorted_templates = sorted(templates, key=lambda item: item["slug"])
    incoming_slugs = {template["slug"] for template in sorted_templates}
    stale_slugs = sorted(previous_slugs - incoming_slugs)
    if stale_slugs:
        raise ValueError(
            "inventory omits previously imported templates; remove them explicitly first: "
            + ", ".join(stale_slugs)
        )

    targets: list[tuple[dict[str, Any], Path]] = []
    for template in sorted_templates:
        slug = template["slug"]
        target = agents_root / slug
        if target.parent.resolve() != resolved_agents_root:
            raise ValueError(f"refusing to write outside the agents directory: {target}")
        if target.is_symlink():
            raise ValueError(f"refusing to write through a symlink: {target}")
        if target.exists():
            if not overwrite:
                raise ValueError(f"refusing to overwrite existing directory: {target}")
            if slug not in previous_slugs:
                raise ValueError(f"refusing to overwrite a non-imported agent: {target}")
        for filename in ("CLAUDE.md", "PROMPT.md", "README.md"):
            if (target / filename).is_symlink():
                raise ValueError(f"refusing to write through a symlink: {target / filename}")
        targets.append((template, target))

    for template, target in targets:
        slug = template["slug"]
        target.mkdir(parents=True, exist_ok=True)
        works_with: list[dict[str, str]] = []
        seen_connections: set[tuple[str, str]] = set()
        for label in template["connectFirst"]:
            mapping = mappings[label]
            if mapping["kind"] not in MAPPED_KINDS:
                continue
            connection = (mapping["kind"], mapping["slug"])
            if connection in seen_connections:
                continue
            seen_connections.add(connection)
            works_with.append({"type": connection[0], "slug": connection[1]})

        icon = choose_icon(template["name"], normalize_category(template["sourceCategory"]))
        prompt = template["prompt"]
        (target / "CLAUDE.md").write_text(render_claude(template, mappings), encoding="utf-8")
        (target / "PROMPT.md").write_text(prompt + "\n", encoding="utf-8")
        (target / "README.md").write_text(
            render_readme(template, mappings, works_with, icon), encoding="utf-8"
        )

        manifest_entries.append(
            {
                "slug": slug,
                "name": template["name"],
                "description": template["description"],
                "category": normalize_category(template["sourceCategory"]),
                "sourceCategory": template["sourceCategory"],
                "addedAt": template["addedAt"],
                "creator": {
                    "name": template["creatorCredit"],
                    "url": template["creatorUrl"],
                },
                "connectFirst": template["connectFirst"],
                "worksWith": works_with,
                "icon": icon,
                "tags": template["tags"],
                "detailUrl": template["detailUrl"],
                "sourceFile": f"bots/{slug}.md",
                "promptSha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            }
        )

    source_root.mkdir(parents=True, exist_ok=True)
    (source_root / "inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    source_metadata = {
        "schemaVersion": 1,
        "fetchedAt": inventory["fetchedAt"],
        "catalogUrl": inventory["catalogSource"],
        "websiteUrl": inventory["directorySource"],
        "sourceRepository": "https://github.com/elie222/botdirectory.ai",
        "sourceCommit": source_commit,
        "license": "MIT",
        "templateCount": len(manifest_entries),
        "templates": manifest_entries,
    }
    (source_root / "catalog.json").write_text(
        json.dumps(source_metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    canonical_crosswalk = {
        "schemaVersion": 1,
        "superagentRepository": "https://github.com/SkillfulAgents/SuperAgent",
        "superagentCommit": crosswalk["superagentCommit"],
        "providerRegistry": "src/shared/lib/account-providers/service-catalog.ts",
        "mcpRegistry": "src/shared/lib/mcp/common-servers.ts",
        "labels": sorted(mapping_list, key=lambda item: item["name"].casefold()),
    }
    (source_root / "connect-first.json").write_text(
        json.dumps(canonical_crosswalk, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        f"Imported {len(manifest_entries)} Bot Directory templates and "
        f"{len(mapping_list)} Connect First classifications."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--crosswalk", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    import_templates(
        args.root.resolve(),
        load_json(args.inventory),
        load_json(args.crosswalk),
        args.source_commit,
        args.overwrite,
    )


if __name__ == "__main__":
    main()
