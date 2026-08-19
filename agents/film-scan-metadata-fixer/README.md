---
category: "Personal"
icon: video
tags:
  - "Personal"
  - "Film Scan Metadata Fixer"
  - "Scanned-image folder"
  - "ExifTool"
  - "Workflow Automation"
works_with: []
developer:
  name: "@benln"
  url: "https://x.com/benln"
---

# Film Scan Metadata Fixer

Inspect scanned photos for correct capture dates and locations; repair EXIF date and GPS metadata without altering image content.

## What it does

- Act as the Film Scan Metadata Fixer: inspect scanned photos for correct capture dates and locations; repair EXIF date and GPS metadata without altering image content.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Scanned-image folder** — local tool or resource; no connection slug.
- **ExifTool** — local tool or resource; no connection slug.

## Sample use cases

- Inspect scanned photos for correct capture dates and locations.
- Repair EXIF date and GPS metadata without altering image content.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Dry run the metadata fix on a small sample of scans
- Repair the capture dates and GPS on this folder of scans
- Report which files were changed, uncertain, or skipped

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@benln](https://x.com/benln) on [Bot Directory](https://botdirectory.ai/bots/film-scan-metadata-fixer/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
