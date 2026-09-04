---
name: Ads Tracker Sheet
description: 'Manage the LIVE Google Sheets ad-performance tracker + cloud masters folder (Google Drive or Dropbox), organized Family > Argument > Video. Two operations - (1) push a finished ad into the tracker (upload masters + append sheet rows) ONLY when the user explicitly says to push; (2) build/rebuild the tracker workbook. Set up during onboarding step 6.'
metadata:
  version: "4.0.0"
---

# Ads Tracker Sheet

The LIVE tracker: a Google Sheet "<Company> Ads Tracker" plus a cloud folder of final masters (Google Drive folder or Dropbox folder). It tracks ads with real ad spend (TikTok / Meta). IDs and account IDs live in `/workspace/ads/tracker.json` (see `tracker.json.example` next to it).

## Taxonomy

Videos are organized **Family → Argument → Video**. Arguments are the company's positioning angles from `/workspace/ads/arguments.json` (written in onboarding step 2 from the ICP work, extended by `ideate-ads`). Key format `<family>-<argument>` e.g. `outcome-save_time`, `feature-live_sync`, `audience-agencies`, `usecase-invoice_chasing`. The family is ALWAYS derived from the key prefix (formula in the sheet — never entered by hand). One primary argument key per video; secondary angles go in Notes. Hooks / presenters / music are flat execution axes (analyzed in the Axes tab), not nesting levels.

- Machine copy: `arguments_data.py` loads `arguments.json` — keep it in sync with the sheet's Arguments tab. New argument = add to BOTH before pushing to it.
- Presenter slugs are read from the roster table in `/workspace/ads/assets/presenters.md` (first column).

## Push an ad (the main operation — EXPLICIT user call only)

**NEVER push automatically.** Producing, delivering, or QC-passing an ad does NOT push it. Only push when the user explicitly says so ("push it", "push <ad-id>", "ship it to the tracker"). One invocation per ad:

```bash
cd /workspace/.claude/skills/ads-tracker-sheet
uv run --env-file /workspace/.env --with requests push_ad.py \
  --ad-id invoices-hpain-f1-maya --arg usecase-invoice_chasing --hook hpain \
  --hook-title "Stop chasing / invoices by hand" --presenter maya --len 13 --cost 1.12 \
  [--notes "..."]
```

What it does:
1. Validates `--presenter` against the roster and `--arg` against `arguments.json` (aborts on unknown values — spelling splits the Axes slices).
2. Requires both masters in `/workspace/ads/studio/out/<ad-id>-{music,nomusic}-master.mp4`.
3. Uploads them to `<root>/<argument-key>/<ad-id>/` on the configured storage (`"storage": "drive"` or `"dropbox"` in tracker.json). Uploads are chunked at 512 KiB because the proxy caps binary bodies (512–768 KiB); same-name files are overwritten.
4. Appends TWO rows to the Videos tab (music / no music), status **Produced**, blank metrics, folder link, Family + rate columns as formulas.
5. Rebuilds the Rollups + Axes tabs (fully regenerated from Videos — never hand-edit them).
6. Aborts if the ad-id is already in the sheet (edit the sheet directly for changes).
7. Rows go through the atomic `values:append` endpoint — safe when several sessions push concurrently. Never revert to a fixed-range write at "next empty row" (that silently overwrote rows once).

The user owns: flipping Status → Published, publish dates, and all spend/metric entry.

## Build / rebuild the workbook

```bash
uv run --env-file /workspace/.env --with requests build_sheet.py --title "<Company> Ads Tracker" [--dummy] [--account <googlesheets-account-id>]
```

- Default: empty tracker (Videos headers/formats/dropdowns pre-applied to ~1000 rows; Arguments tab seeded from `arguments.json`; empty Rollups/Axes).
- `--dummy`: seeds three fake rows with fake metrics so the user can preview the layout (build a separate SAMPLE sheet for this; never push real ads to it).
- After building the real tracker, write the `spreadsheet_id` into `/workspace/ads/tracker.json`.
- `--account` when `CONNECTED_ACCOUNTS` is stale.

## Storage setup (onboarding step 6)

- **Google Drive**: request the `googledrive` connected account, create the root folder (`POST drive/v3/files` with folder mimeType, name "<Company> Ads"), store `drive_account` + `drive_root_id` + `drive_root_name`.
- **Dropbox**: request the `dropbox` connected account, create the root folder (`POST api.dropboxapi.com/2/files/create_folder_v2` `{"path": "/<Company> Ads"}`), store `dropbox_account` + `dropbox_root`. The Dropbox path was written against the public API but has not been exercised in production — on the first push, watch the output and fix as needed.
- **Sheets**: request the `googlesheets` connected account, run `build_sheet.py`, store `sheets_account` + `spreadsheet_id`.

## Structure

- **Videos** = flat source of truth, one row per ad-id × music/no-music. Raw counts only; Family, CTR/CPC/CPA/hook-rate are formulas. Argument column is a dropdown fed by the Arguments tab. Rows with combined spend < $20 grey out.
- **Rollups** = Family → Argument → video leaves with native collapsible row groups; all SUMIFS from Videos, ratios recomputed from sums.
- **Arguments** = the full taxonomy with live coverage stats (# vids, spend, signups, CPA per argument) — shows which arguments have no ads yet. Use it when ideating the next batch.
- **Axes** = SUMIFS slices by family / presenter / music / hook type.
- Code: `arguments_data.py` (taxonomy loader), `common.py` (shared structure + `rebuild_views`), `build_sheet.py`, `push_ad.py`.
