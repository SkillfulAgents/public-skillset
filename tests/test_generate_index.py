# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Tests for the skillset index generator."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from generate_index import build_agent_entry, build_index, parse_document  # noqa: E402


class ParseDocumentTests(unittest.TestCase):
    def test_parses_rich_yaml_and_removes_frontmatter_from_body(self) -> None:
        metadata, body = parse_document(
            """---
description: >-
  A description: with punctuation
createdAt: 2026-08-18T00:00:00.000Z
version: 2.0.0
icon: sparkles
tags:
  - on
  - automation
works_with:
  - type: api_account
    slug: gmail
  - type: mcp
    slug: linear
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# Long-form details

---

The Markdown body stays intact.
""",
            "fixture.md",
        )

        self.assertEqual(metadata["createdAt"], "2026-08-18T00:00:00.000Z")
        self.assertEqual(metadata["version"], "2.0.0")
        self.assertEqual(metadata["icon"], "sparkles")
        self.assertEqual(metadata["tags"], ["on", "automation"])
        self.assertEqual(
            metadata["works_with"],
            [
                {"type": "api_account", "slug": "gmail"},
                {"type": "mcp", "slug": "linear"},
            ],
        )
        self.assertEqual(metadata["developer"]["name"], "SkillfulAgents")
        self.assertEqual(body, "# Long-form details\n\n---\n\nThe Markdown body stays intact.")

    def test_document_without_frontmatter_is_all_body(self) -> None:
        self.assertEqual(parse_document("\n# Details\n\nHello.\n"), ({}, "# Details\n\nHello."))

    def test_body_trimming_preserves_markdown_indentation_and_hard_breaks(self) -> None:
        _, body = parse_document("---\nname: Example\n---\n    indented code\nHard break  \n\n")
        self.assertEqual(body, "    indented code\nHard break  ")

    def test_empty_frontmatter_and_crlf_are_supported(self) -> None:
        self.assertEqual(parse_document("---\r\n---\r\n# Details\r\n"), ({}, "# Details"))

    def test_utf8_bom_before_frontmatter_is_supported(self) -> None:
        self.assertEqual(
            parse_document("\ufeff---\nname: Example\n---\n# Details\n"),
            ({"name": "Example"}, "# Details"),
        )

    def test_rejects_unclosed_or_non_mapping_frontmatter(self) -> None:
        with self.assertRaisesRegex(ValueError, "fixture.md.*no closing"):
            parse_document("---\nname: Broken\n", "fixture.md")
        with self.assertRaisesRegex(ValueError, "fixture.md.*mapping"):
            parse_document("---\n- not\n- a\n- mapping\n---\nBody", "fixture.md")

    def test_rejects_duplicate_yaml_keys_at_any_depth(self) -> None:
        fixtures = (
            "---\nname: First\nname: Second\n---\n",
            "---\ndeveloper:\n  name: First\n  name: Second\n---\n",
        )
        for fixture in fixtures:
            with self.subTest(fixture=fixture), self.assertRaisesRegex(ValueError, "duplicate key"):
                parse_document(fixture, "fixture.md")


class AgentEntryTests(unittest.TestCase):
    def _agent_dir(self, root: Path, slug: str = "example") -> Path:
        agent_dir = root / "agents" / slug
        agent_dir.mkdir(parents=True)
        return agent_dir

    def test_readme_metadata_merges_beneath_claude_and_details_exclude_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agent_dir = self._agent_dir(root)
            (agent_dir / "README.md").write_text(
                """---
name: README Name
description: README description
version: 1.0.0
category: Productivity
icon: inbox
tags:
  - readme-tag
works_with:
  - type: api_account
    slug: gmail
developer:
  name: README Developer
  url: https://example.com/readme
---

# Marketplace details
""",
                encoding="utf-8",
            )
            claude_file = agent_dir / "CLAUDE.md"
            claude_file.write_text(
                """---
name: CLAUDE Name
description: ""
createdAt: "2026-08-18T00:00:00.000Z"
version: 2.0.0
icon: presentation
tags: []
developer:
  name: CLAUDE Developer
---

# Operating instructions
""",
                encoding="utf-8",
            )

            entry = build_agent_entry(root.resolve(), claude_file)

        self.assertEqual(entry["name"], "CLAUDE Name")
        self.assertEqual(entry["description"], "")
        self.assertEqual(entry["details"], "# Marketplace details")
        self.assertEqual(entry["createdAt"], "2026-08-18T00:00:00.000Z")
        self.assertEqual(entry["version"], "2.0.0")
        self.assertEqual(entry["category"], "Productivity")
        self.assertEqual(entry["icon"], "presentation")
        self.assertEqual(entry["tags"], [])
        self.assertEqual(entry["works_with"], [{"type": "api_account", "slug": "gmail"}])
        self.assertEqual(entry["developer"], {"name": "CLAUDE Developer"})
        self.assertEqual(entry["path"], "agents/example/")

    def test_missing_readme_and_metadata_use_backward_compatible_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            agent_dir = self._agent_dir(root, "legacy-agent")
            claude_file = agent_dir / "CLAUDE.md"
            claude_file.write_text("# Instructions\n", encoding="utf-8")

            entry = build_agent_entry(root.resolve(), claude_file)

        self.assertEqual(
            entry,
            {
                "name": "legacy-agent",
                "path": "agents/legacy-agent/",
                "description": "",
                "details": "",
                "createdAt": "",
                "version": "1.0.0",
                "category": "",
                "icon": "",
                "tags": [],
                "works_with": [],
                "developer": {},
            },
        )

    def test_rejects_invalid_marketing_metadata_with_source_path(self) -> None:
        invalid_fragments = {
            "tags: one": "tags",
            "works_with:\n  - gmail": "works_with\\[0\\]",
            "works_with:\n  - type: oauth\n    slug: gmail": "works_with\\[0\\].type",
            "works_with:\n  - type: api_account\n    slug: GMAIL": "works_with\\[0\\].slug",
            'works_with:\n  - type: api_account\n    slug: " gmail "': "works_with\\[0\\].slug",
            "icon: Sparkles": "icon",
            'icon: "inbox "': "icon",
            "icon:\n  - inbox": "icon",
            "developer:\n  url: https://example.com": "developer.name",
            "developer:\n  name: Example\n  url: 'javascript:alert(1)'": "developer.url",
        }
        for fragment, error_pattern in invalid_fragments.items():
            with self.subTest(fragment=fragment), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                agent_dir = self._agent_dir(root)
                claude_file = agent_dir / "CLAUDE.md"
                claude_file.write_text(f"---\n{fragment}\n---\n# Instructions\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, f"example.*{error_pattern}"):
                    build_agent_entry(root.resolve(), claude_file)

    def test_rejects_readme_symlink_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            root = base / "repo"
            agent_dir = self._agent_dir(root)
            claude_file = agent_dir / "CLAUDE.md"
            claude_file.write_text("# Instructions\n", encoding="utf-8")
            secret = base / "outside.md"
            secret.write_text("private contents\n", encoding="utf-8")
            try:
                (agent_dir / "README.md").symlink_to(secret)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with self.assertRaisesRegex(ValueError, "README.md.*outside repository root"):
                build_agent_entry(root, claude_file)

    def test_rejects_in_repository_metadata_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real_dir = self._agent_dir(root, "real")
            real_file = real_dir / "CLAUDE.md"
            real_file.write_text("---\nname: Real\n---\n", encoding="utf-8")
            alias_dir = self._agent_dir(root, "alias")
            alias_file = alias_dir / "CLAUDE.md"
            try:
                alias_file.symlink_to(real_file)
            except OSError as exc:
                self.skipTest(f"symlinks unavailable: {exc}")

            with self.assertRaisesRegex(ValueError, "symlinked metadata sources"):
                build_agent_entry(root, alias_file)


class IndexTests(unittest.TestCase):
    def test_builds_sorted_agents_and_preserves_nested_skill_version(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for slug in ("zeta", "alpha"):
                agent_dir = root / "agents" / slug
                agent_dir.mkdir(parents=True)
                (agent_dir / "CLAUDE.md").write_text(f"---\nname: {slug}\n---\n", encoding="utf-8")
            skill_dir = root / "skills" / "example-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: Example Skill
description: Does useful work
metadata:
  version: 3.2.1
---
""",
                encoding="utf-8",
            )

            index = build_index(root, "Test", "Description", "9.0.0")

        self.assertEqual([agent["name"] for agent in index["agents"]], ["alpha", "zeta"])
        self.assertEqual(index["skills"][0]["version"], "3.2.1")
        self.assertEqual(index["version"], "9.0.0")

    def test_rejects_non_string_skill_fields(self) -> None:
        fixtures = {
            "name:\n  - Example": "name",
            "description:\n  nested: value": "description",
            "metadata:\n  version:\n    - 1.0.0": "version",
        }
        for fragment, field in fixtures.items():
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                skill_dir = root / "skills" / "example-skill"
                skill_dir.mkdir(parents=True)
                (skill_dir / "SKILL.md").write_text(
                    f"---\n{fragment}\n---\n# Instructions\n",
                    encoding="utf-8",
                )

                with self.assertRaisesRegex(ValueError, f"'{field}'.*string"):
                    build_index(root, "Test", "Description", "1.0.0")

    def test_checked_in_index_is_current_and_every_agent_has_marketing_metadata(self) -> None:
        expected = build_index(
            REPO_ROOT,
            "Gamut Public Skillset",
            "A public collection of agent templates for the Gamut app.",
            "1.0.0",
        )
        actual = json.loads((REPO_ROOT / "index.json").read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

        self.assertTrue(expected["agents"])
        for agent in expected["agents"]:
            with self.subTest(agent=agent["path"]):
                self.assertTrue((REPO_ROOT / agent["path"] / "README.md").is_file())
                self.assertTrue(agent["description"])
                self.assertTrue(agent["details"])
                self.assertTrue(agent["createdAt"])
                self.assertTrue(agent["version"])
                self.assertTrue(agent["category"])
                self.assertTrue(agent["icon"])
                self.assertTrue(agent["tags"])
                self.assertTrue(agent["developer"].get("name"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
