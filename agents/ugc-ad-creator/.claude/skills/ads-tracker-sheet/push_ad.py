"""Push a finished ad into the LIVE tracker: upload both masters to cloud storage
(Google Drive or Dropbox) + append rows to the Google Sheet.

ONLY run this when the user explicitly says to push. See SKILL.md.
Config: /workspace/ads/tracker.json (written by agent-onboarding):
{
  "spreadsheet_id": "...", "sheets_account": "<googlesheets account id>",
  "storage": "drive" | "dropbox",
  "drive_account": "<googledrive account id>", "drive_root_id": "<folder id>", "drive_root_name": "<Company> Ads",
  "dropbox_account": "<dropbox account id>", "dropbox_root": "/<Company> Ads"
}
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

from arguments_data import ARG_KEYS
from common import (SHEETS_HOST, DRIVE_HOST, MUSIC_VALS, PRESENTERS, api, family_formula,
                    video_formulas, rebuild_views)

CONFIG_PATH = "/workspace/ads/tracker.json"
OUT_DIR = Path("/workspace/ads/studio/out")
CHUNK = 524288  # proxy caps binary bodies between 512-768 KiB; resumable chunks must be multiples of 256 KiB


# ---------------- Google Drive ----------------

def drive_find(s, base, token, q):
    res = api(s, base, token, "GET",
              f"drive/v3/files?q={requests.utils.quote(q)}&fields=files(id,name,webViewLink)")
    return res.get("files", [])


def ensure_folder(s, base, token, name, parent):
    hits = drive_find(s, base, token,
                      f"name = '{name}' and '{parent}' in parents and "
                      f"mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    if hits:
        return hits[0]["id"]
    res = api(s, base, token, "POST", "drive/v3/files?fields=id",
              {"name": name, "parents": [parent], "mimeType": "application/vnd.google-apps.folder"})
    return res["id"]


def drive_upload(s, base, token, path, folder_id):
    """Resumable upload; overwrites an existing file of the same name in the folder."""
    name = path.name
    existing = drive_find(s, base, token,
                          f"name = '{name}' and '{folder_id}' in parents and trashed = false")
    headers = {"Authorization": f"Bearer {token}", "X-Upload-Content-Type": "video/mp4"}
    if existing:
        init = s.patch(f"{base}/upload/drive/v3/files/{existing[0]['id']}?uploadType=resumable",
                       headers=headers, json={})
    else:
        init = s.post(f"{base}/upload/drive/v3/files?uploadType=resumable", headers=headers,
                      json={"name": name, "parents": [folder_id]})
    if init.status_code >= 300:
        print("upload init failed:", init.status_code, init.text[:1000])
        sys.exit(1)
    loc = init.headers["Location"].replace(f"https://{DRIVE_HOST}/", f"{base}/")
    data = path.read_bytes()
    total = len(data)
    for start in range(0, total, CHUNK):
        end = min(start + CHUNK, total)
        put = s.put(loc, data=data[start:end],
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "video/mp4",
                             "Content-Range": f"bytes {start}-{end - 1}/{total}"})
        if put.status_code not in (200, 201, 308):
            print("upload failed:", put.status_code, put.text[:1000])
            sys.exit(1)
    print(f"  uploaded {name} ({total // 1024} KB)")


def push_to_drive(s, cfg, token, proxy, args, masters):
    base = f'{proxy}/{cfg["drive_account"]}/{DRIVE_HOST}'
    root_name = cfg.get("drive_root_name", "Ads")
    print(f"Uploading to Drive: {root_name}/{args.arg_key}/{args.ad_id}/")
    arg_folder = ensure_folder(s, base, token, args.arg_key, cfg["drive_root_id"])
    ad_folder = ensure_folder(s, base, token, args.ad_id, arg_folder)
    for p in masters.values():
        drive_upload(s, base, token, p, ad_folder)
    return api(s, base, token, "GET", f"drive/v3/files/{ad_folder}?fields=webViewLink")["webViewLink"]


# ---------------- Dropbox ----------------

def dbx(s, base, token, path, payload=None, data=None, arg=None):
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/octet-stream"
        headers["Dropbox-API-Arg"] = json.dumps(arg)
        r = s.post(f"{base}/2/{path}", headers=headers, data=data)
    else:
        headers["Content-Type"] = "application/json"
        r = s.post(f"{base}/2/{path}", headers=headers, json=payload)
    if r.status_code >= 300:
        print(f"Dropbox error {r.status_code} on {path}:", r.text[:1000])
        sys.exit(1)
    return r.json() if r.text else {}


def dropbox_upload(s, api_base, content_base, token, path, dest):
    """Chunked upload session (files/upload_session/*) so each body stays under the proxy cap."""
    data = path.read_bytes()
    total = len(data)
    first = data[:CHUNK]
    sess = dbx(s, content_base, token, "files/upload_session/start", data=first, arg={"close": False})["session_id"]
    offset = len(first)
    while offset < total:
        chunk = data[offset:offset + CHUNK]
        dbx(s, content_base, token, "files/upload_session/append_v2", data=chunk,
            arg={"cursor": {"session_id": sess, "offset": offset}, "close": False})
        offset += len(chunk)
    dbx(s, content_base, token, "files/upload_session/finish", data=b"",
        arg={"cursor": {"session_id": sess, "offset": offset},
             "commit": {"path": dest, "mode": "overwrite", "autorename": False, "mute": True}})
    print(f"  uploaded {path.name} ({total // 1024} KB)")


def push_to_dropbox(s, cfg, token, proxy, args, masters):
    api_base = f'{proxy}/{cfg["dropbox_account"]}/api.dropboxapi.com'
    content_base = f'{proxy}/{cfg["dropbox_account"]}/content.dropboxapi.com'
    folder = f'{cfg["dropbox_root"].rstrip("/")}/{args.arg_key}/{args.ad_id}'
    print(f"Uploading to Dropbox: {folder}/")
    for p in masters.values():
        dropbox_upload(s, api_base, content_base, token, p, f"{folder}/{p.name}")
    r = s.post(f"{api_base}/2/sharing/create_shared_link_with_settings",
               headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
               json={"path": folder})
    if r.status_code == 409 and "shared_link_already_exists" in r.text:
        r = s.post(f"{api_base}/2/sharing/list_shared_links",
                   headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                   json={"path": folder, "direct_only": True})
        links = r.json().get("links", [])
        return links[0]["url"] if links else folder
    if r.status_code >= 300:
        print("shared link failed (folder uploaded anyway):", r.status_code, r.text[:300])
        return folder
    return r.json()["url"]


# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ad-id", required=True)
    ap.add_argument("--arg", required=True, dest="arg_key",
                    help="argument key from ads/arguments.json, e.g. outcome-save_time")
    ap.add_argument("--hook", required=True, help="hook code, e.g. hcontra")
    ap.add_argument("--hook-title", required=True, help='on-screen hook, e.g. "Stop doing this / by hand"')
    ap.add_argument("--presenter", required=True)
    ap.add_argument("--len", type=float, required=True, dest="length")
    ap.add_argument("--cost", type=float, required=True, help="total production cost for this ad (split across the 2 rows)")
    ap.add_argument("--notes", default="")
    ap.add_argument("--config", default=CONFIG_PATH)
    args = ap.parse_args()

    if args.presenter not in PRESENTERS:
        print(f"Unknown presenter '{args.presenter}' (roster: {', '.join(PRESENTERS)}).")
        print("Exact spelling matters — a variant name splits the Axes slices. New presenter? Add it to ads/assets/presenters.md first.")
        sys.exit(1)

    if args.arg_key not in ARG_KEYS:
        print(f"Unknown argument key '{args.arg_key}'. Valid keys are in ads/arguments.json / the Arguments tab.")
        print("If this is a genuinely new argument, add it to arguments.json AND the sheet's Arguments tab first.")
        sys.exit(1)

    cfg = json.loads(Path(args.config).read_text())
    token = os.environ["PROXY_TOKEN"]
    proxy = os.environ["PROXY_BASE_URL"]
    sheets_base = f'{proxy}/{cfg["sheets_account"]}/{SHEETS_HOST}'
    ssid = cfg["spreadsheet_id"]
    s = requests.Session()

    masters = {m: OUT_DIR / f"{args.ad_id}-{suffix}-master.mp4"
               for m, suffix in zip(MUSIC_VALS, ["music", "nomusic"])}
    missing = [str(p) for p in masters.values() if not p.exists()]
    if missing:
        print("Missing master renders, aborting:\n  " + "\n  ".join(missing))
        sys.exit(1)

    col_a = api(s, sheets_base, token, "GET",
                f"v4/spreadsheets/{ssid}/values/Videos!A3:A").get("values", [])
    existing_ids = {r[0] for r in col_a if r}
    if args.ad_id in existing_ids:
        print(f"{args.ad_id} already in the tracker — aborting (edit the sheet directly to change it).")
        sys.exit(1)

    storage = cfg.get("storage", "drive")
    link = push_to_dropbox(s, cfg, token, proxy, args, masters) if storage == "dropbox" else push_to_drive(s, cfg, token, proxy, args, masters)

    def build_rows(first_row):
        out = []
        for i, music in enumerate(MUSIC_VALS):
            r = first_row + i
            tt_f, mt_f, comb_f = video_formulas(r)
            out.append([args.ad_id, family_formula(r), args.arg_key, args.hook, args.hook_title,
                        args.presenter, music, args.length, "Produced", "", round(args.cost / 2, 2), link]
                       + [0, 0, 0, 0, 0] + tt_f + [0, 0, 0, 0, 0] + mt_f + comb_f + [args.notes])
        return out

    # values:append is atomic server-side, so concurrent pushes from other
    # sessions can't overwrite each other (a fixed-range write at "next empty row" did).
    predicted = 3 + len(col_a)
    res = api(s, sheets_base, token, "POST",
              f"v4/spreadsheets/{ssid}/values/Videos!A3:AZ:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS",
              {"values": build_rows(predicted)})
    updated = res["updates"]["updatedRange"]
    actual = int(re.search(r"!A(\d+)", updated).group(1))
    if actual != predicted:
        api(s, sheets_base, token, "POST", f"v4/spreadsheets/{ssid}/values:batchUpdate", {
            "valueInputOption": "USER_ENTERED",
            "data": [{"range": f"Videos!A{actual}", "values": build_rows(actual)}]})
    print(f"Added 2 rows (music / no music) at Videos!{actual} — status Produced, metrics blank.")

    rebuild_views(s, sheets_base, token, ssid)
    print("Rollups/Axes rebuilt.")
    print("Sheet:", f'https://docs.google.com/spreadsheets/d/{ssid}/edit')
    print("Folder:", link)


if __name__ == "__main__":
    main()
