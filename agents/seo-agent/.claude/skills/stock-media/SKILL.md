---
name: Stock Media
description: Search and download free, license-clear stock images for blog posts from Unsplash (needs UNSPLASH_ACCESS_KEY) and Openverse (keyless, CC-licensed). Returns image URLs + attribution + license, and downloads files locally for upload to Sanity.
metadata:
  version: "1.0.0"
---

# Stock Media

Find royalty-free images for articles. Two backends:
- **Unsplash** — high-quality stock. Needs `UNSPLASH_ACCESS_KEY` in `/workspace/.env`.
  Unsplash License (free, commercial OK, no attribution required but nice to include).
- **Openverse** — keyless, aggregates CC-licensed images (Flickr, Wikimedia, etc.).
  Always filter to commercial-use licenses; attribution usually required.

## Usage

```bash
# Search Unsplash (JSON: url, download_url, author, link, alt)
uv run --env-file .env /workspace/.claude/skills/stock-media/media.py unsplash "ai agent payments" --n 8

# Search Openverse (JSON: url, author, license, source, foreign_landing_url)
uv run /workspace/.claude/skills/stock-media/media.py openverse "stripe payments api" --n 8 --license commercial

# Download a specific image URL to /workspace/downloads/media/<name>
uv run /workspace/.claude/skills/stock-media/media.py download "https://images...." hero.jpg
```

## Notes
- Always record author + source URL + license for attribution in the post caption.
- After downloading, upload via the sanity-draft skill's `upload-image`, set `alt` + `caption`.
- Unsplash guideline: when using their API, trigger the `download_location` endpoint on
  use — this script's `unsplash` action returns it as `download_trigger`.
