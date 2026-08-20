# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.2,<7"]
# ///
"""Compare imported templates with the pinned Bot Directory source checkout."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from generate_index import read_document  # noqa: E402


def checkout_commit(checkout_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(checkout_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()
def validate(source_root: Path) -> None:
    catalog_path = ROOT / "sources" / "botdirectory" / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    expected_commit = catalog["sourceCommit"]
    actual_commit = checkout_commit(source_root)
    if actual_commit != expected_commit:
        raise ValueError(
            f"Bot Directory checkout is {actual_commit}, expected {expected_commit}"
        )

    templates = catalog["templates"]
    expected_source_files = {template["sourceFile"] for template in templates}
    actual_source_files = {
        path.relative_to(source_root).as_posix()
        for path in (source_root / "bots").glob("*.md")
    }
    if actual_source_files != expected_source_files:
        missing = sorted(expected_source_files - actual_source_files)
        extra = sorted(actual_source_files - expected_source_files)
        raise ValueError(f"Bot Directory source-set mismatch; missing={missing}, extra={extra}")

    errors: list[str] = []
    for template in templates:
        slug = template["slug"]
        source_slug = template.get("sourceSlug", slug)
        expected_source_file = f"bots/{source_slug}.md"
        if template.get("sourceFile") != expected_source_file:
            errors.append(
                f"{slug}: sourceFile={template.get('sourceFile')!r}, "
                f"expected {expected_source_file!r}"
            )
        source_file = source_root / expected_source_file
        metadata, source_prompt = read_document(source_file)
        prompt = source_prompt.encode("utf-8") + b"\n"
        imported_prompt = (ROOT / "agents" / slug / "PROMPT.md").read_bytes()

        contributor = metadata.get("contributor")
        expected_creator = {
            "name": f"@{contributor}",
            "url": metadata.get("contributor_url")
            or f"https://github.com/{contributor}",
        }
        source_name = template.get("sourceName", template["name"])
        if source_name != metadata.get("name"):
            errors.append(
                f"{slug}: catalog source name={source_name!r}, "
                f"source expects {metadata.get('name')!r}"
            )
        expected = {
            "sourceCategory": metadata.get("category"),
            "addedAt": metadata.get("added_at"),
            "connectFirst": metadata.get("integrations", []),
            "creator": expected_creator,
            "detailUrl": f"https://botdirectory.ai/bots/{source_slug}/",
        }
        for key, value in expected.items():
            if template.get(key) != value:
                errors.append(
                    f"{slug}: catalog {key}={template.get(key)!r}, source expects {value!r}"
                )
        if imported_prompt != prompt:
            errors.append(f"{slug}: PROMPT.md is not byte-identical to the source body")
        source_hash = hashlib.sha256(source_prompt.encode("utf-8")).hexdigest()
        if template.get("promptSha256") != source_hash:
            errors.append(f"{slug}: promptSha256 does not match pinned source")

    license_bytes = (source_root / "LICENSE").read_bytes()
    notice_bytes = (ROOT / "sources" / "botdirectory" / "NOTICE.md").read_bytes()
    if license_bytes not in notice_bytes:
        errors.append("NOTICE.md does not embed the pinned Bot Directory LICENSE verbatim")
    if expected_commit.encode() not in notice_bytes:
        errors.append("NOTICE.md does not identify the pinned Bot Directory commit")

    if errors:
        raise ValueError("\n".join(errors))
    print(
        f"Validated {len(templates)} templates byte-for-byte against "
        f"Bot Directory {actual_commit}."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-root",
        type=Path,
        required=True,
        help="Checkout of elie222/botdirectory.ai at the catalog's recorded commit",
    )
    args = parser.parse_args()
    validate(args.source_root.resolve())


if __name__ == "__main__":
    main()
