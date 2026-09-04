"""Shared structure/formatting logic for the ads tracker sheet.

Videos columns (0-indexed):
 A0 AdID  B1 Family(formula)  C2 Argument  D3 Hook  E4 HookTitle  F5 Presenter  G6 Music
 H7 Len  I8 Status  J9 Published  K10 ProdCost  L11 DriveLink
 TikTok:  M12 Spend N13 Impr O14 3sViews P15 Clicks Q16 Signups R17 HookRate S18 CTR T19 CPC U20 CPA
 Meta:    V21 Spend W22 Impr X23 3sViews Y24 Clicks Z25 Signups AA26 HookRate AB27 CTR AC28 CPC AD29 CPA
 Combined: AE30 Spend AF31 Signups AG32 CPA   AH33 Notes
"""
import os
import sys

from arguments_data import FAMILIES, ARG_NAMES, family_of

SHEETS_HOST = "sheets.googleapis.com"
DRIVE_HOST = "www.googleapis.com"

STATUSES = ["Draft", "Produced", "Published", "Paused", "Killed", "Scaling"]
MUSIC_VALS = ["music", "no music"]

PRESENTERS_PATH = os.environ.get("ADS_PRESENTERS_PATH", "/workspace/ads/assets/presenters.md")


def load_presenters():
    """Presenter slugs = first column of the roster table in presenters.md."""
    slugs = []
    try:
        for line in open(PRESENTERS_PATH):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and line.startswith("|") and cells[0] not in ("Slug", "") and not set(cells[0]) <= set("-: "):
                slugs.append(cells[0])
    except FileNotFoundError:
        pass
    return slugs or ["presenter"]


PRESENTERS = load_presenters()
MAX_ROWS = 1003  # formatting/validation pre-applied through this row on Videos

V_HDR = ["Ad ID", "Family", "Argument", "Hook", "Hook Title", "Presenter", "Music", "Len (s)",
         "Status", "Published", "Prod Cost", "Drive Link",
         "Spend", "Impressions", "3s Views", "Clicks", "Signups", "Hook Rate", "CTR", "CPC", "CPA",
         "Spend", "Impressions", "3s Views", "Clicks", "Signups", "Hook Rate", "CTR", "CPC", "CPA",
         "Spend", "Signups", "CPA", "Notes"]
N_COLS = len(V_HDR)  # 34

ROLL_HDR = ["", "# Vids",
            "Spend", "Impressions", "Clicks", "Signups", "Hook Rate", "CTR", "CPA",
            "Spend", "Impressions", "Clicks", "Signups", "Hook Rate", "CTR", "CPA",
            "Spend", "Signups", "CPA"]


def api(session, base, token, method, path, payload=None):
    r = session.request(method, f"{base}/{path}",
                        headers={"Authorization": f"Bearer {token}"}, json=payload)
    if r.status_code >= 300:
        print(f"API error {r.status_code} on {method} {path}:", r.text[:2000])
        sys.exit(1)
    return r.json()


def family_formula(r):
    return f'=IF($C{r}="","",REGEXEXTRACT($C{r},"^[^-]+"))'


def video_formulas(r):
    """Rate/combined formula cells for Videos row r (1-indexed). Returns (tt, meta, combined)."""
    tt = [f'=IF(N{r}=0,"",O{r}/N{r})', f'=IF(N{r}=0,"",P{r}/N{r})',
          f'=IF(P{r}=0,"",M{r}/P{r})', f'=IF(Q{r}=0,"",M{r}/Q{r})']
    mt = [f'=IF(W{r}=0,"",X{r}/W{r})', f'=IF(W{r}=0,"",Y{r}/W{r})',
          f'=IF(Y{r}=0,"",V{r}/Y{r})', f'=IF(Z{r}=0,"",V{r}/Z{r})']
    comb = [f'=M{r}+V{r}', f'=Q{r}+Z{r}', f'=IF(AF{r}=0,"",AE{r}/AF{r})']
    return tt, mt, comb


def sumline(name, crits):
    # ranges start at row 3: COUNTIFS/SUMIFS match case-insensitively, so a whole-column
    # range would count the header row (e.g. "Music" header matches criterion "music")
    cr = "".join(f',Videos!${c}$3:${c},"{v}"' for c, v in crits)
    def S(col):
        return f'SUMIFS(Videos!${col}$3:${col}{cr})'
    first_c, first_v = crits[0]
    rest = "".join(f',Videos!${c}$3:${c},"{v}"' for c, v in crits[1:])
    count = f'=COUNTIFS(Videos!${first_c}$3:${first_c},"{first_v}"{rest})'
    return [name, count,
            f'={S("M")}', f'={S("N")}', f'={S("P")}', f'={S("Q")}',
            f'=IFERROR({S("O")}/{S("N")},"")', f'=IFERROR({S("P")}/{S("N")},"")',
            f'=IFERROR({S("M")}/{S("Q")},"")',
            f'={S("V")}', f'={S("W")}', f'={S("Y")}', f'={S("Z")}',
            f'=IFERROR({S("X")}/{S("W")},"")', f'=IFERROR({S("Y")}/{S("W")},"")',
            f'=IFERROR({S("V")}/{S("Z")},"")',
            f'={S("M")}+{S("V")}', f'={S("Q")}+{S("Z")}',
            f'=IFERROR(({S("M")}+{S("V")})/({S("Q")}+{S("Z")}),"")']


def hex_color(h):
    return {"red": int(h[0:2], 16) / 255, "green": int(h[2:4], 16) / 255, "blue": int(h[4:6], 16) / 255}


GREY, DARK, BLUE, PURPLE, LIGHT = "5f6368", "111111", "1877f2", "7c3aed", "f1f3f4"
G_GREEN, G_YELLOW, G_RED, WHITE = "57bb8a", "ffd666", "e67c73", "ffffff"


def banner(sheet, sr, sc, ec, text_cell, bg, fg="ffffff"):
    merge_start = max(sc, 1)  # frozenColumnCount 1 — merges can't span the frozen boundary
    reqs = []
    if ec - merge_start > 1:
        reqs.append({"mergeCells": {"range": {"sheetId": sheet, "startRowIndex": sr, "endRowIndex": sr + 1,
                                              "startColumnIndex": merge_start, "endColumnIndex": ec},
                                    "mergeType": "MERGE_ALL"}})
    if text_cell:
        col = merge_start if sc >= 1 else 0
        reqs.append({"updateCells": {"range": {"sheetId": sheet, "startRowIndex": sr, "endRowIndex": sr + 1,
                                               "startColumnIndex": col, "endColumnIndex": col + 1},
                                     "rows": [{"values": [{"userEnteredValue": {"stringValue": text_cell}}]}],
                                     "fields": "userEnteredValue"}})
    return reqs + [
        {"repeatCell": {"range": {"sheetId": sheet, "startRowIndex": sr, "endRowIndex": sr + 1,
                                  "startColumnIndex": sc, "endColumnIndex": ec},
                        "cell": {"userEnteredFormat": {
                            "backgroundColor": hex_color(bg),
                            "horizontalAlignment": "CENTER",
                            "textFormat": {"bold": True, "foregroundColor": hex_color(fg), "fontSize": 11}}},
                        "fields": "userEnteredFormat(backgroundColor,horizontalAlignment,textFormat)"}},
    ]


def numfmt(sheet, cols, sr, er, pattern, ftype):
    return [{"repeatCell": {"range": {"sheetId": sheet, "startRowIndex": sr, "endRowIndex": er,
                                      "startColumnIndex": c, "endColumnIndex": c + 1},
                            "cell": {"userEnteredFormat": {"numberFormat": {"type": ftype, "pattern": pattern}}},
                            "fields": "userEnteredFormat.numberFormat"}} for c in cols]


def grad3(sheet, cols, sr, er):
    return [{"addConditionalFormatRule": {"rule": {
        "ranges": [{"sheetId": sheet, "startRowIndex": sr, "endRowIndex": er,
                    "startColumnIndex": c, "endColumnIndex": c + 1}],
        "gradientRule": {"minpoint": {"color": hex_color(G_GREEN), "type": "MIN"},
                         "midpoint": {"color": hex_color(G_YELLOW), "type": "PERCENT", "value": "50"},
                         "maxpoint": {"color": hex_color(G_RED), "type": "MAX"}}}, "index": 0}} for c in cols]


def grad2(sheet, cols, sr, er):
    return [{"addConditionalFormatRule": {"rule": {
        "ranges": [{"sheetId": sheet, "startRowIndex": sr, "endRowIndex": er,
                    "startColumnIndex": c, "endColumnIndex": c + 1}],
        "gradientRule": {"minpoint": {"color": hex_color(WHITE), "type": "MIN"},
                         "maxpoint": {"color": hex_color(G_GREEN), "type": "MAX"}}}, "index": 0}} for c in cols]


def bold_row(sheet, i, ncols, bg):
    return {"repeatCell": {"range": {"sheetId": sheet, "startRowIndex": i, "endRowIndex": i + 1,
                                     "startColumnIndex": 0, "endColumnIndex": ncols},
                           "cell": {"userEnteredFormat": {"backgroundColor": hex_color(bg),
                                                          "textFormat": {"bold": True}}},
                           "fields": "userEnteredFormat(backgroundColor,textFormat)"}}


def derive_meta(videos_rows):
    """From Videos!A3:G rows -> ordered [{ad_id, family, arg, hook, title, presenter, musics}]."""
    ads, order = {}, []
    for row in videos_rows:
        if len(row) < 7 or not row[0]:
            continue
        ad_id, family, arg, hook, title, presenter, music = row[:7]
        if ad_id not in ads:
            ads[ad_id] = {"ad_id": ad_id, "family": family, "arg": arg, "hook": hook,
                          "title": title, "presenter": presenter, "musics": []}
            order.append(ad_id)
        if music not in ads[ad_id]["musics"]:
            ads[ad_id]["musics"].append(music)
    return [ads[a] for a in order]


def rollup_rows(meta):
    """Family -> Argument -> video leaves."""
    rows, fam_idx, arg_idx, dims = [], [], [], []
    families = []
    for a in meta:
        if a["family"] not in families:
            families.append(a["family"])
    for fam in families:
        fi = len(rows)
        fam_idx.append(fi)
        rows.append(sumline(FAMILIES.get(fam, fam).upper(), [("B", fam)]))
        args = []
        for a in meta:
            if a["family"] == fam and a["arg"] not in args:
                args.append(a["arg"])
        for arg in args:
            ai = len(rows)
            arg_idx.append(ai)
            label = f'    {arg}' + (f' — {ARG_NAMES[arg]}' if arg in ARG_NAMES else "")
            rows.append(sumline(label, [("C", arg)]))
            for a in [a for a in meta if a["arg"] == arg]:
                for music in a["musics"]:
                    rows.append(sumline(f'        {a["ad_id"]} · {a["hook"]} · {music}',
                                        [("A", a["ad_id"]), ("G", music)]))
            dims.append((ai + 1, len(rows)))
        dims.append((fi + 1, len(rows)))
    return rows, fam_idx, arg_idx, dims


def axes_rows(meta):
    rows, sec_idx = [], []
    def section(label, entries):
        sec_idx.append(len(rows))
        rows.append([label] + ROLL_HDR[1:])
        for name, crits in entries:
            rows.append(sumline(name, crits))
        rows.append([""] * 19)
    def uniq(key):
        seen = []
        for a in meta:
            if a[key] not in seen:
                seen.append(a[key])
        return seen
    families = uniq("family") or list(FAMILIES)
    section("BY FAMILY", [(FAMILIES.get(f, f), [("B", f)]) for f in families])
    section("BY PRESENTER", [(p, [("F", p)]) for p in (uniq("presenter") or PRESENTERS)])
    section("MUSIC VS NO MUSIC", [(m, [("G", m)]) for m in MUSIC_VALS])
    section("BY HOOK TYPE", [(h, [("D", h)]) for h in (uniq("hook") or ["hclaim"])])
    return rows, sec_idx


def view_format_reqs(roll_id, axes_id, n_roll_rows, n_axes_rows, fam_idx, arg_idx, dims, sec_idx):
    money, cnt, pct = '"$"#,##0.00', "#,##0", "0.00%"
    reqs = []
    for sid, label in [(roll_id, "FAMILY → ARGUMENT → VIDEO"), (axes_id, "CROSS-CUTTING AXES")]:
        reqs += banner(sid, 0, 0, 2, label, GREY)
        reqs += banner(sid, 0, 2, 9, "TIKTOK", DARK)
        reqs += banner(sid, 0, 9, 16, "META", BLUE)
        reqs += banner(sid, 0, 16, 19, "COMBINED", PURPLE)
        reqs.append(bold_row(sid, 1, 19, LIGHT))
    for sid, nr in [(roll_id, n_roll_rows + 2), (axes_id, n_axes_rows + 2)]:
        if nr <= 2:
            continue
        reqs += numfmt(sid, [2, 8, 9, 15, 16, 18], 2, nr, money, "CURRENCY")
        reqs += numfmt(sid, [3, 4, 5, 10, 11, 12, 17], 2, nr, cnt, "NUMBER")
        reqs += numfmt(sid, [6, 7, 13, 14], 2, nr, pct, "PERCENT")
    for i in fam_idx:
        reqs.append(bold_row(roll_id, 2 + i, 19, "ede9fe"))
    for i in arg_idx:
        reqs.append(bold_row(roll_id, 2 + i, 19, "f8f9fa"))
    for i in sec_idx:
        reqs.append(bold_row(axes_id, 1 + i, 19, "ede9fe"))
    for (a, b) in dims:
        reqs.append({"addDimensionGroup": {"range": {"sheetId": roll_id, "dimension": "ROWS",
                                                     "startIndex": 2 + a, "endIndex": 2 + b}}})
    if n_roll_rows:
        reqs += grad3(roll_id, [8, 15, 18], 2, n_roll_rows + 2)
        reqs += grad2(roll_id, [6, 13], 2, n_roll_rows + 2)
    reqs.append({"updateDimensionProperties": {"range": {"sheetId": roll_id, "dimension": "COLUMNS",
                                                         "startIndex": 0, "endIndex": 1},
                                               "properties": {"pixelSize": 380}, "fields": "pixelSize"}})
    reqs.append({"updateDimensionProperties": {"range": {"sheetId": axes_id, "dimension": "COLUMNS",
                                                         "startIndex": 0, "endIndex": 1},
                                               "properties": {"pixelSize": 220}, "fields": "pixelSize"}})
    return reqs


def rebuild_views(session, base, token, ssid):
    """Delete and regenerate the Rollups + Axes tabs from current Videos data."""
    doc = api(session, base, token, "GET", f"v4/spreadsheets/{ssid}?fields=sheets.properties")
    by_title = {sh["properties"]["title"]: sh["properties"]["sheetId"] for sh in doc["sheets"]}
    vals = api(session, base, token, "GET",
               f"v4/spreadsheets/{ssid}/values/Videos!A3:G?majorDimension=ROWS").get("values", [])
    meta = derive_meta(vals)
    rrows, fam_idx, arg_idx, dims = rollup_rows(meta)
    arows, sec_idx = axes_rows(meta)

    reqs = []
    for title in ["Rollups", "Axes"]:
        if title in by_title:
            reqs.append({"deleteSheet": {"sheetId": by_title[title]}})
    reqs.append({"addSheet": {"properties": {"title": "Rollups", "index": 1,
                                             "gridProperties": {"frozenRowCount": 2, "frozenColumnCount": 1}}}})
    reqs.append({"addSheet": {"properties": {"title": "Axes", "index": 2,
                                             "gridProperties": {"frozenColumnCount": 1}}}})
    reply = api(session, base, token, "POST", f"v4/spreadsheets/{ssid}:batchUpdate", {"requests": reqs})
    added = [r["addSheet"]["properties"]["sheetId"] for r in reply["replies"] if "addSheet" in r]
    roll_id, axes_id = added[0], added[1]

    api(session, base, token, "POST", f"v4/spreadsheets/{ssid}/values:batchUpdate", {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "Rollups!A2", "values": [["Family / Argument / Video"] + ROLL_HDR[1:]] + rrows},
            {"range": "Axes!A2", "values": arows},
        ]})
    api(session, base, token, "POST", f"v4/spreadsheets/{ssid}:batchUpdate",
        {"requests": view_format_reqs(roll_id, axes_id, len(rrows), len(arows), fam_idx, arg_idx, dims, sec_idx)})
