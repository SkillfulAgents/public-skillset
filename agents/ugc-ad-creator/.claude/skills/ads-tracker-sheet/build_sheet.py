"""Build the ads tracker Google Sheet. See SKILL.md.

Default: empty tracker (rows are added later via push_ad.py).
--dummy: seed a few fake rows + metrics so the user can preview the layout.
"""
import argparse
import json
import os
import random

import requests

from arguments_data import FAMILIES, ARGUMENTS
from common import (SHEETS_HOST, STATUSES, PRESENTERS, MUSIC_VALS, MAX_ROWS, V_HDR, N_COLS,
                    GREY, DARK, BLUE, PURPLE, LIGHT,
                    api, banner, bold_row, numfmt, grad3, grad2, hex_color,
                    family_formula, video_formulas, rebuild_views)

VID_ID, CFG_ID, ARG_ID = 0, 3, 4


def dummy_metrics(rng, published):
    if not published:
        return [0, 0, 0, 0, 0]
    spend = round(rng.uniform(8, 70), 2)
    impr = int(spend * rng.uniform(600, 1500))
    v3s = int(impr * rng.uniform(0.18, 0.45))
    clicks = int(impr * rng.uniform(0.004, 0.02))
    signups = max(0, int(clicks * rng.uniform(0.02, 0.09)))
    return [spend, impr, v3s, clicks, signups]


DUMMY_ADS = [
    ("demo-hpain-f1-" + PRESENTERS[0], ARGUMENTS[0][0] if ARGUMENTS else "outcome-demo", "hpain", "Stop doing this / by hand", PRESENTERS[0], 13, 1.10, "Published"),
    ("demo-hclaim-f1-" + PRESENTERS[0], ARGUMENTS[0][0] if ARGUMENTS else "outcome-demo", "hclaim", "This replaced / my whole workflow", PRESENTERS[0], 13, 0.60, "Published"),
    ("demo-hpov-quick-" + PRESENTERS[-1], ARGUMENTS[-1][0] if ARGUMENTS else "outcome-demo", "hpov", "POV: it's 9am / and it's done", PRESENTERS[-1], 8, 0.70, "Produced"),
]


def dummy_video_rows():
    ADS = DUMMY_ADS
    rng = random.Random(42)
    rows = []
    for (ad_id, arg, hook, title, presenter, length, cost, status) in ADS:
        for music in MUSIC_VALS:
            r = len(rows) + 3
            published = status == "Published"
            pub_date = f"2026-08-{rng.randint(24, 30)}" if published else ""
            tt_f, mt_f, comb_f = video_formulas(r)
            row = [ad_id, family_formula(r), arg, hook, title, presenter, music, length,
                   status, pub_date, round(cost / 2, 2), "https://drive.google.com/ (dummy)"]
            row += dummy_metrics(rng, published) + tt_f
            row += dummy_metrics(rng, published and rng.random() < 0.7) + mt_f
            row += comb_f + [""]
            rows.append(row)
    return rows


def arguments_rows():
    hdr = ["Key", "Family", "Argument", "One-liner", "# Vids", "Spend", "Signups", "CPA"]
    rows = [hdr]
    for i, (key, name, desc) in enumerate(ARGUMENTS):
        r = i + 2
        rows.append([key, FAMILIES[key.split("-", 1)[0]], name, desc,
                     f'=COUNTIF(Videos!$C:$C,$A{r})',
                     f'=SUMIF(Videos!$C:$C,$A{r},Videos!$AE:$AE)',
                     f'=SUMIF(Videos!$C:$C,$A{r},Videos!$AF:$AF)',
                     f'=IFERROR(F{r}/G{r},"")'])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True, help='e.g. "<Company> Ads Tracker"')
    ap.add_argument("--dummy", action="store_true")
    ap.add_argument("--account", default=None, help="googlesheets account id (overrides CONNECTED_ACCOUNTS)")
    args = ap.parse_args()

    acct = args.account or json.loads(os.environ["CONNECTED_ACCOUNTS"])["googlesheets"][0]["id"]
    base = f'{os.environ["PROXY_BASE_URL"]}/{acct}/{SHEETS_HOST}'
    token = os.environ["PROXY_TOKEN"]
    s = requests.Session()

    created = api(s, base, token, "POST", "v4/spreadsheets", {
        "properties": {"title": args.title},
        "sheets": [
            {"properties": {"sheetId": VID_ID, "title": "Videos",
                            "gridProperties": {"rowCount": MAX_ROWS + 10, "columnCount": 40,
                                               "frozenRowCount": 2, "frozenColumnCount": 1}}},
            {"properties": {"sheetId": ARG_ID, "title": "Arguments",
                            "gridProperties": {"frozenRowCount": 1}}},
            {"properties": {"sheetId": CFG_ID, "title": "Config"}},
        ]})
    ssid = created["spreadsheetId"]
    url = created["spreadsheetUrl"]

    vrows = dummy_video_rows() if args.dummy else []
    arows = arguments_rows()

    cfg_rows = [["Statuses", "Presenters", "Music"]]
    for i in range(max(len(STATUSES), len(PRESENTERS), len(MUSIC_VALS))):
        cfg_rows.append([STATUSES[i] if i < len(STATUSES) else "",
                         PRESENTERS[i] if i < len(PRESENTERS) else "",
                         MUSIC_VALS[i] if i < len(MUSIC_VALS) else ""])

    api(s, base, token, "POST", f"v4/spreadsheets/{ssid}/values:batchUpdate", {
        "valueInputOption": "USER_ENTERED",
        "data": [{"range": "Videos!A2", "values": [V_HDR] + vrows},
                 {"range": "Arguments!A1", "values": arows},
                 {"range": "Config!A1", "values": cfg_rows}]})

    money, cnt, pct = '"$"#,##0.00', "#,##0", "0.00%"
    reqs = []
    reqs += banner(VID_ID, 0, 0, 12, "VIDEO", GREY)
    reqs += banner(VID_ID, 0, 12, 21, "TIKTOK", DARK)
    reqs += banner(VID_ID, 0, 21, 30, "META", BLUE)
    reqs += banner(VID_ID, 0, 30, 33, "COMBINED", PURPLE)
    reqs += banner(VID_ID, 0, 33, 34, "NOTES", GREY)
    reqs.append(bold_row(VID_ID, 1, N_COLS, LIGHT))
    reqs += numfmt(VID_ID, [10, 12, 19, 20, 21, 28, 29, 30, 32], 2, MAX_ROWS, money, "CURRENCY")
    reqs += numfmt(VID_ID, [13, 14, 15, 16, 22, 23, 24, 25, 31], 2, MAX_ROWS, cnt, "NUMBER")
    reqs += numfmt(VID_ID, [17, 18, 26, 27], 2, MAX_ROWS, pct, "PERCENT")
    reqs += grad3(VID_ID, [20, 29, 32], 2, MAX_ROWS)
    reqs += grad2(VID_ID, [17, 26], 2, MAX_ROWS)
    reqs.append({"addConditionalFormatRule": {"rule": {
        "ranges": [{"sheetId": VID_ID, "startRowIndex": 2, "endRowIndex": MAX_ROWS,
                    "startColumnIndex": 0, "endColumnIndex": N_COLS}],
        "booleanRule": {"condition": {"type": "CUSTOM_FORMULA",
                                      "values": [{"userEnteredValue": '=AND($A3<>"",$AE3<20)'}]},
                        "format": {"textFormat": {"foregroundColor": hex_color("b0b0b0")}}}}, "index": 0}})
    # dropdowns: Argument from the Arguments tab; Status/Presenter/Music inline
    reqs.append({"setDataValidation": {"range": {"sheetId": VID_ID, "startRowIndex": 2, "endRowIndex": MAX_ROWS,
                                                 "startColumnIndex": 2, "endColumnIndex": 3},
                                       "rule": {"condition": {"type": "ONE_OF_RANGE",
                                                              "values": [{"userEnteredValue": "=Arguments!$A$2:$A$200"}]},
                                                "showCustomUi": True, "strict": False}}})
    for col, vals in [(8, STATUSES), (5, PRESENTERS), (6, MUSIC_VALS)]:
        reqs.append({"setDataValidation": {"range": {"sheetId": VID_ID, "startRowIndex": 2, "endRowIndex": MAX_ROWS,
                                                     "startColumnIndex": col, "endColumnIndex": col + 1},
                                           "rule": {"condition": {"type": "ONE_OF_LIST",
                                                                  "values": [{"userEnteredValue": v} for v in vals]},
                                                    "showCustomUi": True, "strict": False}}})
    for sc, ec, px in [(0, 1, 230), (2, 3, 210), (4, 5, 250), (33, 34, 300), (12, 33, 92)]:
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": VID_ID, "dimension": "COLUMNS",
                                                             "startIndex": sc, "endIndex": ec},
                                                   "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    # Arguments tab formatting: header, widths, coverage gradient, money formats
    n_args = len(arows)
    reqs.append(bold_row(ARG_ID, 0, 8, LIGHT))
    reqs += numfmt(ARG_ID, [5, 7], 1, n_args + 1, money, "CURRENCY")
    reqs += grad2(ARG_ID, [4], 1, n_args + 1)
    reqs += grad3(ARG_ID, [7], 1, n_args + 1)
    for sc, ec, px in [(0, 1, 230), (2, 3, 200), (3, 4, 460)]:
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": ARG_ID, "dimension": "COLUMNS",
                                                             "startIndex": sc, "endIndex": ec},
                                                   "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    api(s, base, token, "POST", f"v4/spreadsheets/{ssid}:batchUpdate", {"requests": reqs})

    rebuild_views(s, base, token, ssid)
    print("OK", ssid, url)


if __name__ == "__main__":
    main()
