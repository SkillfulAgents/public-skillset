"""Generate an Apple-Fitness-style status card PNG: two concentric rings (calories outer, protein inner)
plus the 4 macros listed on the right. Saved to /workspace/nutrition/output/status.png.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from db import connect, today_local, GOAL_PATH, ROOT


W, H = 900, 480
BG = (18, 18, 20)
FG = (240, 240, 240)
DIM = (140, 140, 145)
TRACK = (40, 40, 45)
CAL_COLOR = (255, 75, 95)      # red/pink (calories)
PROTEIN_COLOR = (120, 230, 130) # green (protein)
FAT_COLOR = (255, 200, 80)     # amber
CARB_COLOR = (90, 180, 255)    # blue

OUTPUT_DIR = ROOT / "output"


def load_goal() -> dict:
    if GOAL_PATH.exists():
        return json.loads(GOAL_PATH.read_text())
    return {"calories": 2200, "protein_g": 160, "fat_g": 70, "carbs_g": 220}


def fetch_totals(day: str) -> dict:
    with connect() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(calories),0) AS c,
                      COALESCE(SUM(protein_g),0) AS p,
                      COALESCE(SUM(fat_g),0) AS f,
                      COALESCE(SUM(carbs_g),0) AS cb
               FROM meals WHERE local_day = ?""",
            (day,),
        ).fetchone()
    return {"calories": row["c"], "protein_g": row["p"], "fat_g": row["f"], "carbs_g": row["cb"]}


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_ring(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, thickness: int,
              progress: float, color: tuple) -> None:
    """Draw an arc ring; progress = 0..(unbounded). Values >1 wrap (Apple-style overflow indicator)."""
    bbox = (cx - radius, cy - radius, cx + radius, cy + radius)
    # track
    draw.arc(bbox, 0, 360, fill=TRACK, width=thickness)
    if progress <= 0:
        return
    p = min(progress, 1.0)
    end = -90 + p * 360
    draw.arc(bbox, -90, end, fill=color, width=thickness)
    # overflow ring (lighter overlay) if >100%
    if progress > 1.0:
        overflow = min(progress - 1.0, 1.0)
        end2 = -90 + overflow * 360
        # Brighten color for overflow lap
        oc = tuple(min(255, c + 40) for c in color)
        draw.arc(bbox, -90, end2, fill=oc, width=thickness)


def macro_row(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, val: float, goal: float,
              unit: str, color: tuple, font_lbl, font_val, font_goal) -> int:
    # color swatch
    sw = 14
    draw.rectangle((x, y + 10, x + sw, y + 10 + sw), fill=color)
    # label
    draw.text((x + sw + 12, y), label, fill=FG, font=font_lbl)
    # value / goal
    val_str = f"{val:,.0f}{unit}"
    goal_str = f" / {goal:,.0f}{unit}"
    draw.text((x + sw + 12, y + 30), val_str, fill=FG, font=font_val)
    vw = draw.textlength(val_str, font=font_val)
    draw.text((x + sw + 12 + vw, y + 38), goal_str, fill=DIM, font=font_goal)
    return y + 72


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", default=None)
    p.add_argument("--out", default=None)
    args = p.parse_args()

    day = args.date or today_local().isoformat()
    goal = load_goal()
    totals = fetch_totals(day)

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Title
    f_title = get_font(28, bold=True)
    f_sub = get_font(16)
    draw.text((40, 28), "Nutrition", fill=FG, font=f_title)
    draw.text((40, 64), day, fill=DIM, font=f_sub)

    # Rings (left side)
    cx, cy = 230, 270
    outer_r = 130
    inner_r = 90
    thickness = 28

    cal_progress = totals["calories"] / goal["calories"] if goal["calories"] else 0
    prot_progress = totals["protein_g"] / goal["protein_g"] if goal["protein_g"] else 0

    draw_ring(draw, cx, cy, outer_r, thickness, cal_progress, CAL_COLOR)
    draw_ring(draw, cx, cy, inner_r, thickness, prot_progress, PROTEIN_COLOR)

    # Ring center labels (cal % and protein %)
    f_pct = get_font(22, bold=True)
    f_tiny = get_font(12)
    cal_pct = f"{cal_progress*100:.0f}%"
    pr_pct = f"{prot_progress*100:.0f}%"
    cw = draw.textlength(cal_pct, font=f_pct)
    pw = draw.textlength(pr_pct, font=f_pct)
    draw.text((cx - cw / 2, cy - 30), cal_pct, fill=CAL_COLOR, font=f_pct)
    draw.text((cx - pw / 2, cy + 4), pr_pct, fill=PROTEIN_COLOR, font=f_pct)
    lbl1 = "cal / prot"
    lw = draw.textlength(lbl1, font=f_tiny)
    draw.text((cx - lw / 2, cy + 36), lbl1, fill=DIM, font=f_tiny)

    # Macro list on right
    f_lbl = get_font(16)
    f_val = get_font(26, bold=True)
    f_goal = get_font(14)
    rx = 470
    ry = 110
    ry = macro_row(draw, rx, ry, "Calories", totals["calories"], goal["calories"], " kcal", CAL_COLOR, f_lbl, f_val, f_goal)
    ry = macro_row(draw, rx, ry, "Protein", totals["protein_g"], goal["protein_g"], "g", PROTEIN_COLOR, f_lbl, f_val, f_goal)
    ry = macro_row(draw, rx, ry, "Fat", totals["fat_g"], goal["fat_g"], "g", FAT_COLOR, f_lbl, f_val, f_goal)
    ry = macro_row(draw, rx, ry, "Carbs", totals["carbs_g"], goal["carbs_g"], "g", CARB_COLOR, f_lbl, f_val, f_goal)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out = Path(args.out) if args.out else OUTPUT_DIR / "status.png"
    img.save(out)
    print(str(out))


if __name__ == "__main__":
    main()
