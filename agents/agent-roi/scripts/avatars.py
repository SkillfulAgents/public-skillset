#!/usr/bin/env python3
"""Agent avatars and member stacks for the dashboard, cut from two screenshots of the Gamut app.

  js    print scripts/avatars_overlay.js with the in-scope agent ids filled in (stdlib only).
  crop  recover the images from a white and a black screenshot of the overlay, and write them with the manifest.
        Needs Pillow and numpy: uv run --with pillow --with numpy python3 scripts/avatars.py crop ...

Screenshots are of the viewport at 2 device pixels per CSS pixel. The overlay grid starts at 20px, 20px:
  avatars  7 columns of 120×120 cells, each avatar scaled 3× and centred. Cut: the centred 100×100 square, to 96×96.
  members  4 columns of 280×80 cells, each stack scaled 2.5× from the left, centred vertically. Cut: the left 160×50,
           trimmed to what shows, 40px tall. A cut with almost nothing in it is no stack.
On white and black, a pixel of colour c and opacity a shows as W = a·c + (1−a)·255 and B = a·c, so
a = 1 − mean(W − B)/255 and c = B/a.
Writes artifacts/agent-roi/public/avatars/<id>.png, members/<id>.png and avatars.json = {id: {avatar, members}}.
These are snapshots of the app on the day they were taken.
"""
import argparse, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.environ.get("REVIEW_DIR", os.path.join(os.getcwd(), "review"))
OUT = os.path.join(os.path.dirname(HERE), "artifacts", "agent-roi", "public")
S, PAD = 2, 20
GRID = {"avatars": (7, 120, 120), "members": (4, 280, 80)}


def in_scope_ids():
    return sorted(a["agent_id"] for a in json.load(open(os.path.join(REVIEW, "coverage.json")))["agents"] if a.get("in_scope"))


def overlay_js(kind, ids):
    js = open(os.path.join(HERE, "avatars_overlay.js")).read()
    return js.replace("__IDS__", json.dumps(ids)).replace("__KIND__", json.dumps(kind))


def cell_box(kind, i):
    """CSS px box to cut for the i-th agent in grid order."""
    cols, w, h = GRID[kind]
    x, y = PAD + i % cols * w, PAD + i // cols * h
    if kind == "avatars":
        return x + w / 2 - 50, y + h / 2 - 50, x + w / 2 + 50, y + h / 2 + 50
    return x, y + (h - 50) / 2, x + 160, y + (h + 50) / 2


def unmatte(white, black):
    """RGBA float array from the same pixels shot on white and on black (H×W×3 arrays, 0-255)."""
    import numpy as np
    w, b = white.astype(float), black.astype(float)
    a = np.clip(1 - (w - b).mean(axis=-1) / 255, 0, 1)
    rgb = np.clip(b / np.maximum(a, 1e-6)[..., None], 0, 255)
    return np.dstack([rgb, a * 255])


def crop(kind, white_path, black_path, order):
    import numpy as np
    from PIL import Image
    white, black = (np.asarray(Image.open(p).convert("RGB")) for p in (white_path, black_path))
    os.makedirs(os.path.join(OUT, kind), exist_ok=True)
    manifest_path = os.path.join(OUT, "avatars.json")
    manifest = json.load(open(manifest_path)) if os.path.exists(manifest_path) else {}
    for i, slug in enumerate(order):
        x0, y0, x1, y1 = (round(v * S) for v in cell_box(kind, i))
        rgba = unmatte(white[y0:y1, x0:x1], black[y0:y1, x0:x1])
        entry = manifest.setdefault(slug, {"avatar": None, "members": None})
        if kind == "avatars":
            img = Image.fromarray(rgba.astype("uint8"), "RGBA").resize((96, 96), Image.LANCZOS)
        else:
            alpha = rgba[..., 3] / 255
            if alpha.max() < 0.2:
                entry["members"] = None
                continue
            ys, xs = np.nonzero(alpha > 0.05)
            img = Image.fromarray(rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1].astype("uint8"), "RGBA")
            img = img.resize((max(1, round(img.width * 40 / img.height)), 40), Image.LANCZOS)
        img.save(os.path.join(OUT, kind, f"{slug}.png"))
        entry["avatar" if kind == "avatars" else "members"] = f"{kind}/{slug}.png"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=1, sort_keys=True)
    print(f"{len(order)} {kind} written, manifest {manifest_path}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=("js", "crop"))
    p.add_argument("--kind", choices=tuple(GRID), required=True)
    p.add_argument("--ids", help="js: comma-separated agent ids, default every in-scope agent")
    p.add_argument("--white", help="crop: screenshot on white")
    p.add_argument("--black", help="crop: screenshot on black")
    p.add_argument("--order", help="crop: JSON file with the ids the overlay returned, in grid order")
    args = p.parse_args(argv)
    if args.cmd == "js":
        print(overlay_js(args.kind, args.ids.split(",") if args.ids else in_scope_ids()))
    else:
        if not (args.white and args.black and args.order):
            raise SystemExit("crop needs --white, --black and --order")
        crop(args.kind, args.white, args.black, json.load(open(args.order)))


if __name__ == "__main__":
    main()
