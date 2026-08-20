# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Validate connector slugs and built-in capability names against SuperAgent."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_index import build_agent_entry  # noqa: E402


REGISTRIES = {
    "api_account": (
        Path("src/shared/lib/account-providers/service-catalog.ts"),
        "SUPPORTED_PROVIDERS",
    ),
    "mcp": (
        Path("src/shared/lib/mcp/common-servers.ts"),
        "COMMON_MCP_SERVERS",
    ),
}
CAPABILITY_PATTERNS = {
    Path("agent-container/src/tools/browser.ts"): (
        ("browser_open tool declaration", r"\btool\s*\(\s*['\"]browser_open['\"]"),
        (
            "browser_get_state tool declaration",
            r"\btool\s*\(\s*['\"]browser_get_state['\"]",
        ),
    ),
    Path("agent-container/src/system-prompt.md"): (
        (
            "conditional web-browser delegation guidance",
            r"<%#subagentsEnabled%>"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"### Web Browser Agent\b"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"\bdelegate\b"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"\bweb-browser (?:agent|specialist)\b"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"<%/subagentsEnabled%>",
        ),
        (
            "direct-browsing fallback when subagents are disabled",
            r"<%\^subagentsEnabled%>"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"### Browsing Workflow\b"
            r"(?:(?!<%/subagentsEnabled%>)[\s\S])*?"
            r"<%/subagentsEnabled%>",
        ),
    ),
    Path("agent-container/src/claude-code.ts"): (
        (
            "MCP wire-ID construction",
            r"`mcp__\$\{serverName\}__\$\{t\.name\}`",
        ),
        ("web-browser agent registration", r"['\"]web-browser['\"]\s*:\s*\{"),
        (
            "browser MCP tools bound to web-browser",
            r"mcpToolNames\s*\(\s*['\"]browser['\"]\s*,\s*browserMcpTools\s*\)",
        ),
        ("host web-search wire ID", r"['\"]mcp__web__web_search['\"]"),
        ("native WebSearch tool ID", r"['\"]WebSearch['\"]"),
        (
            "browser MCP server registration",
            r"['\"]browser['\"]\s*:\s*createBrowserMcpServer\s*\(",
        ),
        (
            "chat MCP server registration",
            r"['\"]chat['\"]\s*:\s*createChatMcpServer\s*\(",
        ),
        (
            "user-input MCP server registration",
            r"['\"]user-input['\"]\s*:\s*createUserInputMcpServer\s*\(",
        ),
        (
            "web MCP server registration",
            r"['\"]web['\"]\s*:\s*createWebMcpServer\s*\(",
        ),
    ),
    Path("agent-container/src/mcp-server.ts"): (
        (
            "browser MCP server name",
            r"\bfunction\s+createBrowserMcpServer\b[\s\S]*?"
            r"\bname\s*:\s*['\"]browser['\"]",
        ),
        (
            "chat MCP server name",
            r"\bfunction\s+createChatMcpServer\b[\s\S]*?"
            r"\bname\s*:\s*['\"]chat['\"]",
        ),
        (
            "user-input MCP server name",
            r"\bfunction\s+createUserInputMcpServer\b[\s\S]*?"
            r"\bname\s*:\s*['\"]user-input['\"]",
        ),
        (
            "web MCP server name",
            r"\bfunction\s+createWebMcpServer\b[\s\S]*?"
            r"\bname\s*:\s*['\"]web['\"]",
        ),
    ),
    Path("agent-container/src/tools/chat/add-chat-integration.ts"): (
        (
            "add_chat_integration tool declaration",
            r"\btool\s*\(\s*['\"]add_chat_integration['\"]",
        ),
        ("iMessage provider", r"z\.enum\s*\([^)]*['\"]imessage['\"]"),
    ),
    Path("agent-container/src/tools/chat/list-available-chat-providers.ts"): (
        (
            "list_available_chat_providers tool declaration",
            r"\btool\s*\(\s*['\"]list_available_chat_providers['\"]",
        ),
    ),
    Path("agent-container/src/tools/request-secret.ts"): (
        (
            "request_secret tool declaration",
            r"\btool\s*\(\s*['\"]request_secret['\"]",
        ),
    ),
    Path("agent-container/src/tools/web/web-search.ts"): (
        ("web_search tool declaration", r"\btool\s*\(\s*['\"]web_search['\"]"),
    ),
    Path("src/shared/lib/llm-provider/model-prompt-hints.ts"): (
        ("recommended browser-open wire ID", r"mcp__browser__browser_open"),
        ("recommended web-browser agent", r"web-browser agent"),
    ),
}


def lexical_mask(text: str, *, blank_strings: bool) -> str:
    """Blank comments and optionally strings without changing source positions."""
    output: list[str] = []
    index = 0
    quote: str | None = None
    while index < len(text):
        char = text[index]
        following = text[index + 1] if index + 1 < len(text) else ""
        if quote:
            output.append(char if not blank_strings or char in "\r\n" else " ")
            if char == "\\" and index + 1 < len(text):
                index += 1
                escaped = text[index]
                output.append(
                    escaped if not blank_strings or escaped in "\r\n" else " "
                )
            elif char == quote:
                quote = None
        elif char in {"'", '"', "`"}:
            quote = char
            output.append(" " if blank_strings else char)
        elif char == "/" and following == "/":
            output.extend((" ", " "))
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                output.append(" ")
                index += 1
            if index < len(text):
                output.append(text[index])
        elif char == "/" and following == "*":
            output.extend((" ", " "))
            index += 2
            while index + 1 < len(text) and text[index : index + 2] != "*/":
                output.append(text[index] if text[index] in "\r\n" else " ")
                index += 1
            if index + 1 >= len(text):
                raise ValueError("unterminated block comment in TypeScript registry")
            output.extend((" ", " "))
            index += 1
        else:
            output.append(char)
        index += 1
    if quote:
        raise ValueError("unterminated string in TypeScript registry")
    return "".join(output)


def strip_typescript_comments(text: str) -> str:
    return lexical_mask(text, blank_strings=False)


def typescript_code_mask(text: str) -> str:
    return lexical_mask(text, blank_strings=True)


def matching_delimiter(text: str, start: int, opening: str, closing: str) -> int:
    if start >= len(text) or text[start] != opening:
        raise ValueError(f"expected {opening!r} at delimiter start")
    depth = 0
    quote: str | None = None
    index = start
    while index < len(text):
        char = text[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = None
        elif char in {"'", '"', "`"}:
            quote = char
        elif char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError(f"unbalanced {opening}{closing} delimiters in TypeScript registry")


def top_level_objects(array_body: str) -> list[str]:
    objects: list[str] = []
    index = 0
    length = len(array_body)
    while index < len(array_body):
        while index < length and array_body[index].isspace():
            index += 1
        if index >= length:
            break
        if array_body[index] != "{":
            raise ValueError("registry array contains a non-object or missing entry")
        end = matching_delimiter(array_body, index, "{", "}")
        objects.append(array_body[index : end + 1])
        index = end + 1
        while index < length and array_body[index].isspace():
            index += 1
        if index >= length:
            break
        if array_body[index] != ",":
            raise ValueError("registry array entries must be comma-separated")
        index += 1
        while index < length and array_body[index].isspace():
            index += 1
        if index >= length:
            break
        if array_body[index] != "{":
            raise ValueError("registry array contains a hole or non-object entry")
    if not objects:
        raise ValueError("registry array contains no object entries")
    return objects


def top_level_properties(source: str) -> list[str]:
    if not source.startswith("{") or matching_delimiter(source, 0, "{", "}") != len(source) - 1:
        raise ValueError("registry entry is not one complete object literal")

    properties: list[str] = []
    start = 1
    curly_depth = 0
    square_depth = 0
    paren_depth = 0
    quote: str | None = None
    index = 1
    while index < len(source) - 1:
        char = source[index]
        if quote:
            if char == "\\":
                index += 1
            elif char == quote:
                quote = None
        elif char in {"'", '"', "`"}:
            quote = char
        elif char == "{":
            curly_depth += 1
        elif char == "}":
            curly_depth -= 1
        elif char == "[":
            square_depth += 1
        elif char == "]":
            square_depth -= 1
        elif char == "(":
            paren_depth += 1
        elif char == ")":
            paren_depth -= 1
        elif char == "," and not (curly_depth or square_depth or paren_depth):
            properties.append(source[start:index])
            start = index + 1
        if curly_depth < 0 or square_depth < 0 or paren_depth < 0:
            raise ValueError("unbalanced delimiter inside registry object")
        index += 1

    if quote or curly_depth or square_depth or paren_depth:
        raise ValueError("unterminated value inside registry object")
    properties.append(source[start:-1])
    return properties


def object_field(source: str, field: str) -> str:
    pattern = re.compile(
        rf"^\s*{re.escape(field)}\s*:\s*"
        r"(?P<literal>(?P<quote>['\"])(?:\\.|(?!(?P=quote)).)*(?P=quote))\s*$",
        re.DOTALL,
    )
    matches = [
        match.group("literal")
        for prop in top_level_properties(source)
        if (match := pattern.fullmatch(prop))
    ]
    if len(matches) != 1:
        raise ValueError(
            f"registry entry must contain exactly one direct {field!r} string field"
        )
    value = ast.literal_eval(matches[0])
    if not isinstance(value, str):
        raise ValueError(f"registry {field!r} must evaluate to a string")
    return value


def extract_registry_text(text: str, export_name: str, source_name: str) -> dict[str, str]:
    """Extract display-name-to-slug entries from registry source, failing closed."""
    commentless = strip_typescript_comments(text)
    code_mask = typescript_code_mask(text)
    declaration_re = re.compile(rf"\bexport\s+const\s+{re.escape(export_name)}\b")
    declarations = list(declaration_re.finditer(code_mask))
    if len(declarations) != 1:
        raise ValueError(
            f"{source_name}: expected exactly one export declaration for {export_name}"
        )

    declaration = declarations[0]
    line_end = code_mask.find("\n", declaration.end())
    if line_end < 0:
        line_end = len(code_mask)
    declaration_tail = code_mask[declaration.end() : line_end]
    relative_assignment = declaration_tail.find("=")
    if relative_assignment < 0:
        raise ValueError(f"{source_name}: could not isolate the {export_name} array")
    assignment = declaration.end() + relative_assignment
    array_start = assignment + 1
    while array_start < len(code_mask) and code_mask[array_start].isspace():
        array_start += 1
    if array_start >= len(code_mask) or code_mask[array_start] != "[":
        raise ValueError(f"{source_name}: {export_name} must be initialized by an array")
    array_end = matching_delimiter(code_mask, array_start, "[", "]")

    closing_line_end = code_mask.find("\n", array_end + 1)
    if closing_line_end < 0:
        closing_line_end = len(code_mask)
    trailing = code_mask[array_end + 1 : closing_line_end].strip()
    if trailing not in {"", ";"}:
        raise ValueError(f"{source_name}: {export_name} has a non-array initializer")
    if trailing != ";":
        next_code = closing_line_end + 1
        while next_code < len(code_mask) and code_mask[next_code].isspace():
            next_code += 1
        if next_code < len(code_mask) and not re.match(
            r"(?:export|const|let|var|function|interface|type|class|enum|namespace|import)\b",
            code_mask[next_code:],
        ):
            raise ValueError(
                f"{source_name}: could not prove {export_name} ends after its array"
            )

    entries: dict[str, str] = {}
    slugs: list[str] = []
    for source in top_level_objects(commentless[array_start + 1 : array_end]):
        slug = object_field(source, "slug")
        display_name = object_field(source, "displayName")
        if display_name in entries:
            raise ValueError(f"{source_name}: duplicate display name {display_name!r}")
        entries[display_name] = slug
        slugs.append(slug)
    if len(slugs) != len(set(slugs)):
        duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
        raise ValueError(
            f"{source_name}: duplicate registry slugs: {', '.join(duplicates)}"
        )
    return entries


def extract_registry(path: Path, export_name: str) -> dict[str, str]:
    if not path.is_file():
        raise ValueError(f"missing SuperAgent registry: {path}")
    return extract_registry_text(path.read_text(encoding="utf-8"), export_name, str(path))


def validate_parser_fixtures() -> None:
    fixture = """
// slug: 'commented-out'
export const TEST_REGISTRY: Entry[] = [
  {
    slug: "real-entry",
    displayName: 'Real Entry',
    url: 'https://example.com/path//kept',
  },
  /* { slug: 'also-commented-out', displayName: 'Fake' }, */
]
"""
    parsed = extract_registry_text(fixture, "TEST_REGISTRY", "parser fixture")
    if parsed != {"Real Entry": "real-entry"}:
        raise ValueError(f"TypeScript parser fixture produced {parsed!r}")

    rejected = {
        "missing slug": (
            "export const TEST_REGISTRY: Entry[] = [{ displayName: 'Missing slug' }]"
        ),
        "nested fields": (
            "export const TEST_REGISTRY: Entry[] = "
            "[{ metadata: { slug: 'nested', displayName: 'Nested' } }]"
        ),
        "non-array initializer": (
            "export const TEST_REGISTRY = makeRegistry()\n"
            "const unrelated = [{ slug: 'wrong', displayName: 'Wrong' }]"
        ),
        "array hole": (
            "export const TEST_REGISTRY: Entry[] = "
            "[, { slug: 'real', displayName: 'Real' },,]"
        ),
        "declaration inside a string": (
            'const note = "export const TEST_REGISTRY = '
            "[{ slug: 'fake', displayName: 'Fake' }]\""
        ),
        "trailing initializer expression": (
            "export const TEST_REGISTRY = "
            "[{ slug: 'fake', displayName: 'Fake' }] + "
            "[{ slug: 'also-fake', displayName: 'Also Fake' }]"
        ),
    }
    for name, malformed in rejected.items():
        try:
            extract_registry_text(malformed, "TEST_REGISTRY", f"{name} fixture")
        except ValueError:
            continue
        raise ValueError(f"TypeScript parser accepted the {name} fixture")


def checkout_commit(checkout_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(checkout_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_capability_contract(superagent_root: Path) -> None:
    errors: list[str] = []
    for relative_path, required_patterns in CAPABILITY_PATTERNS.items():
        path = superagent_root / relative_path
        if not path.is_file():
            errors.append(f"missing SuperAgent capability source: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        searchable = strip_typescript_comments(text) if path.suffix == ".ts" else text
        for description, pattern in required_patterns:
            if not re.search(pattern, searchable):
                errors.append(f"{path}: missing canonical {description}")
    if errors:
        raise ValueError("\n".join(errors))


def validate(superagent_root: Path, require_recorded_commit: bool) -> None:
    validate_parser_fixtures()
    validate_capability_contract(superagent_root)
    crosswalk = json.loads(
        (ROOT / "sources" / "botdirectory" / "connect-first.json").read_text(
            encoding="utf-8"
        )
    )
    actual_commit = checkout_commit(superagent_root)
    recorded_commit = crosswalk["superagentCommit"]
    if require_recorded_commit and actual_commit != recorded_commit:
        raise ValueError(
            f"SuperAgent checkout is {actual_commit}, expected recorded commit {recorded_commit}"
        )

    registry_entries = {
        entry_type: extract_registry(superagent_root / relative_path, export_name)
        for entry_type, (relative_path, export_name) in REGISTRIES.items()
    }
    catalogs = {
        entry_type: set(entries.values())
        for entry_type, entries in registry_entries.items()
    }

    checked = 0
    errors: list[str] = []
    for claude_file in sorted((ROOT / "agents").glob("*/CLAUDE.md")):
        entry = build_agent_entry(ROOT, claude_file)
        for connection in entry["works_with"]:
            checked += 1
            entry_type = connection["type"]
            slug = connection["slug"]
            if slug not in catalogs[entry_type]:
                errors.append(
                    f"{entry['path']}README.md: unknown SuperAgent "
                    f"{entry_type} slug {slug!r}"
                )

    if errors:
        raise ValueError("\n".join(errors))

    known_display_names = {
        display_name.casefold()
        for entries in registry_entries.values()
        for display_name in entries
    }
    newly_supported = sorted(
        entry["name"]
        for entry in crosswalk["labels"]
        if entry["kind"] not in REGISTRIES
        and entry["name"].casefold() in known_display_names
    )
    if newly_supported:
        raise ValueError(
            "Connect First labels now have an exact SuperAgent registry match; "
            f"refresh their mappings: {', '.join(newly_supported)}"
        )

    counts = ", ".join(
        f"{entry_type}={len(slugs)}" for entry_type, slugs in catalogs.items()
    )
    print(
        f"Validated {checked} works_with entries against SuperAgent {actual_commit} "
        f"({counts})."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--superagent-root",
        type=Path,
        required=True,
        help="Checkout containing the canonical SkillfulAgents/SuperAgent registries",
    )
    parser.add_argument(
        "--require-recorded-commit",
        action="store_true",
        help="Require checkout HEAD to match sources/botdirectory/connect-first.json",
    )
    args = parser.parse_args()
    validate(args.superagent_root.resolve(), args.require_recorded_commit)


if __name__ == "__main__":
    main()
