# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Generate a presenter portrait (9:16) through the platform media proxy.

Default model is openai/gpt-image-2 (quality=high) — the most photoreal option
tested for UGC presenters. Alternatives via --model:
  xai/grok-imagine-image-2            $0.04   (same family as the video model)
  black-forest-labs/flux-1.1-pro-ultra $0.06  (pass --raw for the anti-polish mode)

Usage:
  uv run --env-file /workspace/.env portrait.py --prompt "..." --out ads/assets/<slug>-portrait.jpg
  uv run --env-file /workspace/.env portrait.py --prompt "..." --model xai/grok-imagine-image-2 --out ...
  uv run --env-file /workspace/.env portrait.py --prompt "..." --ref ads/refs/persona-reference.jpg --out ...
      (--ref passes a style/realism reference image to gpt-image-2's input_images)
"""
import argparse
import base64
import mimetypes
import os
import sys
import time

import requests

BASE = os.environ["ANTHROPIC_BASE_URL"].rstrip("/") + "/v1/replicate"
HDRS = {"Authorization": f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}"}

COST = {
    "openai/gpt-image-2": 0.128,
    "xai/grok-imagine-image-2": 0.04,
    "black-forest-labs/flux-1.1-pro-ultra": 0.06,
    "black-forest-labs/flux-1.1-pro": 0.04,
}


def data_uri(path):
    if path.startswith("http"):
        return path
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode()}"


def build_input(model, args):
    if model == "openai/gpt-image-2":
        inp = {"prompt": args.prompt, "aspect_ratio": "9:16", "quality": args.quality, "output_format": "jpeg", "moderation": "low"}
        if args.ref:
            inp["input_images"] = [data_uri(r) for r in args.ref]
        return inp
    if model == "xai/grok-imagine-image-2":
        return {"prompt": args.prompt, "aspect_ratio": "9:16", "quality": "medium", "resolution": "2k"}
    if model.startswith("black-forest-labs/flux-1.1-pro"):
        inp = {"prompt": args.prompt, "aspect_ratio": "9:16", "output_format": "jpg", "safety_tolerance": 2}
        if args.raw and model.endswith("ultra"):
            inp["raw"] = True
        return inp
    return {"prompt": args.prompt, "aspect_ratio": "9:16"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--model", default="openai/gpt-image-2")
    ap.add_argument("--quality", default="high", help="gpt-image-2 only: low|medium|high|auto")
    ap.add_argument("--ref", action="append", help="reference image(s) for gpt-image-2 input_images")
    ap.add_argument("--raw", action="store_true", help="flux-1.1-pro-ultra raw mode")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    r = requests.post(f"{BASE}/models/{args.model}/predictions", headers=HDRS,
                      json={"input": build_input(args.model, args)}, timeout=120)
    if r.status_code == 403:
        sys.exit(f"{args.model} is not on the platform model list — run the list call from /opt/gamut/docs/media-generation.md")
    r.raise_for_status()
    pred = r.json()
    pid = pred["id"]
    print(f"prediction {pid} started ({args.model}, ~${COST.get(args.model, 0):.3f})")

    while pred["status"] in ("starting", "processing"):
        time.sleep(4)
        pred = requests.get(f"{BASE}/predictions/{pid}", headers=HDRS, timeout=30).json()
        print(" ", pred["status"])

    if pred["status"] != "succeeded":
        sys.exit(f"FAILED: {pred.get('error')}")

    url = pred["output"] if isinstance(pred["output"], str) else pred["output"][0]
    data = requests.get(url, timeout=120).content
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    open(args.out, "wb").write(data)
    print(f"saved {args.out} ({len(data)/1e6:.1f} MB)")


if __name__ == "__main__":
    main()
