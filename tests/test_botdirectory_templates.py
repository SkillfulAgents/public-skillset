# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Validate completeness, provenance, and metadata for Bot Directory imports."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_index import build_agent_entry, read_document  # noqa: E402


SOURCE_ROOT = ROOT / "sources" / "botdirectory"
CATALOG_PATH = SOURCE_ROOT / "catalog.json"
CROSSWALK_PATH = SOURCE_ROOT / "connect-first.json"
MAPPED_KINDS = {"api_account", "mcp"}
UNMAPPED_KINDS = {"browser", "builtin", "external", "local", "raw_api"}
DIRECT_API_KINDS = {"external", "raw_api"}
BUILTIN_SEARCH_LABELS = {"Google Search", "Web Search"}
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9._-]*\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def section(body: str, heading: str) -> str:
    marker = f"## {heading}"
    if marker not in body:
        return ""
    return body.split(marker, 1)[1].split("\n## ", 1)[0]


class BotDirectoryTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = read_json(CATALOG_PATH)
        cls.crosswalk = read_json(CROSSWALK_PATH)
        cls.templates = cls.catalog["templates"]
        cls.mapping_list = cls.crosswalk["labels"]
        cls.mappings = {entry["name"]: entry for entry in cls.mapping_list}

    def test_snapshot_and_crosswalk_are_well_formed(self) -> None:
        self.assertEqual(self.catalog["schemaVersion"], 1)
        self.assertEqual(self.crosswalk["schemaVersion"], 1)
        self.assertRegex(self.catalog["sourceCommit"], COMMIT_RE)
        self.assertRegex(self.crosswalk["superagentCommit"], COMMIT_RE)
        self.assertEqual(self.catalog["license"], "MIT")
        self.assertEqual(self.catalog["templateCount"], len(self.templates))
        self.assertGreater(len(self.templates), 0)

        slugs = [template["slug"] for template in self.templates]
        self.assertEqual(len(slugs), len(set(slugs)), "duplicate source template slugs")
        mapping_names = [entry["name"] for entry in self.mapping_list]
        self.assertEqual(len(mapping_names), len(set(mapping_names)), "duplicate Connect First labels")

        used_labels = {
            label for template in self.templates for label in template["connectFirst"]
        }
        self.assertEqual(set(mapping_names), used_labels)

        for entry in self.mapping_list:
            with self.subTest(label=entry["name"]):
                kind = entry.get("kind")
                self.assertIn(kind, MAPPED_KINDS | UNMAPPED_KINDS)
                self.assertIsInstance(entry.get("reason"), str)
                self.assertTrue(entry["reason"].strip())
                if kind in MAPPED_KINDS:
                    self.assertIsInstance(entry.get("slug"), str)
                    self.assertRegex(entry["slug"], SLUG_RE)
                else:
                    self.assertNotIn("slug", entry)

    def test_manifest_matches_all_prompt_directories(self) -> None:
        expected = {template["slug"] for template in self.templates}
        discovered = {
            prompt_file.parent.name
            for prompt_file in (ROOT / "agents").glob("*/PROMPT.md")
        }
        self.assertEqual(discovered, expected)

    def test_every_template_is_complete_and_consistent(self) -> None:
        for template in self.templates:
            slug = template["slug"]
            with self.subTest(slug=slug):
                directory = ROOT / "agents" / slug
                claude_path = directory / "CLAUDE.md"
                prompt_path = directory / "PROMPT.md"
                readme_path = directory / "README.md"
                for path in (claude_path, prompt_path, readme_path):
                    self.assertTrue(path.is_file(), f"missing {path}")

                prompt_text = prompt_path.read_text(encoding="utf-8")
                self.assertFalse(prompt_text.startswith("---"), f"{prompt_path}: prompt has frontmatter")
                self.assertTrue(prompt_text.endswith("\n"), f"{prompt_path}: missing final newline")
                self.assertFalse(prompt_text.endswith("\n\n"), f"{prompt_path}: extra final newline")
                prompt_hash = hashlib.sha256(prompt_text[:-1].encode("utf-8")).hexdigest()
                self.assertEqual(prompt_hash, template["promptSha256"])

                claude_metadata, claude_body = read_document(claude_path)
                self.assertEqual(
                    set(claude_metadata),
                    {"name", "description", "createdAt", "version"},
                )
                self.assertEqual(claude_metadata.get("name"), template["name"])
                self.assertEqual(claude_metadata.get("description"), template["description"])
                self.assertEqual(claude_metadata.get("createdAt"), template["addedAt"])
                self.assertEqual(claude_metadata.get("version"), "1.0.0")
                self.assertNotIn("\n", claude_metadata["description"])

                readme_metadata, readme_body = read_document(readme_path)
                self.assertEqual(
                    set(readme_metadata),
                    {"category", "icon", "tags", "works_with", "developer"},
                )
                self.assertEqual(readme_metadata.get("category"), template["category"])
                self.assertEqual(readme_metadata.get("icon"), template["icon"])
                self.assertEqual(readme_metadata.get("tags"), template["tags"])
                self.assertGreaterEqual(len(readme_metadata["tags"]), 4)
                self.assertLessEqual(len(readme_metadata["tags"]), 7)
                self.assertEqual(len(readme_metadata["tags"]), len(set(readme_metadata["tags"])))
                self.assertEqual(readme_metadata.get("developer"), template["creator"])

                expected_connections: list[dict[str, str]] = []
                seen: set[tuple[str, str]] = set()
                for label in template["connectFirst"]:
                    mapping = self.mappings[label]
                    if mapping["kind"] not in MAPPED_KINDS:
                        continue
                    key = (mapping["kind"], mapping["slug"])
                    if key in seen:
                        continue
                    seen.add(key)
                    expected_connections.append({"type": key[0], "slug": key[1]})
                self.assertEqual(readme_metadata.get("works_with"), expected_connections)
                self.assertEqual(template["worksWith"], expected_connections)

                effective = build_agent_entry(ROOT, claude_path)
                self.assertEqual(effective["name"], template["name"])
                self.assertEqual(effective["description"], template["description"])
                self.assertEqual(effective["createdAt"], template["addedAt"])
                self.assertEqual(effective["version"], "1.0.0")
                self.assertEqual(effective["category"], template["category"])
                self.assertEqual(effective["icon"], template["icon"])
                self.assertEqual(effective["tags"], template["tags"])
                self.assertEqual(effective["works_with"], expected_connections)
                self.assertEqual(effective["developer"], template["creator"])

                first_run = section(claude_body, "First run")
                connection_methods = section(claude_body, "Connection methods")
                method_lines = connection_methods.splitlines()
                connect_first = section(readme_body, "Connect first")
                self.assertTrue(first_run)
                self.assertTrue(connect_first)
                for label in template["connectFirst"]:
                    self.assertIn(label, first_run)
                    self.assertIn(label, connect_first)
                    mapping = self.mappings[label]
                    if mapping["kind"] in MAPPED_KINDS:
                        token = f"`{mapping['kind']}:{mapping['slug']}`"
                        self.assertIn(token, first_run)
                        self.assertIn(f"`{mapping['slug']}`", connect_first)

                    if mapping["kind"] == "browser":
                        browser_lines = [
                            line
                            for line in method_lines
                            if line.startswith("- For browser-based connections (")
                            and f"`{label}`" in line
                        ]
                        self.assertEqual(len(browser_lines), 1)
                        self.assertIn("`mcp__browser__browser_open`", browser_lines[0])
                        self.assertIn('subagent_type="web-browser"', browser_lines[0])

                    if label == "Apple Messages":
                        apple_lines = [
                            line
                            for line in method_lines
                            if line.startswith("- For Apple Messages,")
                        ]
                        self.assertEqual(len(apple_lines), 1)
                        self.assertIn("iMessage chat integration", apple_lines[0])
                        self.assertIn(
                            "`mcp__chat__list_available_chat_providers`",
                            apple_lines[0],
                        )
                        self.assertIn(
                            "`mcp__chat__add_chat_integration`", apple_lines[0]
                        )
                        self.assertIn("provider `imessage`", apple_lines[0])

                    if label in BUILTIN_SEARCH_LABELS:
                        search_lines = [
                            line
                            for line in method_lines
                            if line.startswith("- For built-in search (")
                            and f"`{label}`" in line
                        ]
                        self.assertEqual(len(search_lines), 1)
                        self.assertIn("`mcp__web__web_search`", search_lines[0])
                        self.assertIn("`WebSearch`", search_lines[0])

                    if mapping["kind"] in DIRECT_API_KINDS:
                        direct_api_lines = [
                            line
                            for line in method_lines
                            if line.startswith(f"- For the {label} connection,")
                        ]
                        self.assertEqual(len(direct_api_lines), 1)
                        self.assertIn("API key", direct_api_lines[0])
                        self.assertIn(
                            "`mcp__user-input__request_secret`", direct_api_lines[0]
                        )
                        self.assertIn("direct API calls", direct_api_lines[0])

                self.assertIn(template["detailUrl"], readme_body)
                self.assertIn(template["creator"]["url"], readme_body)
                self.assertIn("`PROMPT.md`", readme_body)

                if template["sourceCategory"] == "Success":
                    self.assertEqual(template["category"], "Customer Success")
                else:
                    self.assertEqual(template["category"], template["sourceCategory"])


if __name__ == "__main__":
    unittest.main()
