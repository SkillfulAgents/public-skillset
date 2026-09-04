# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///
"""Animate a presenter portrait into a lip-synced talking-head clip
(xai/grok-imagine-video-1.5, image-to-video, $0.08/s, integer 1-15s).

The house prompt (v2) describes only what CHANGES — motion, speech, sound —
because I2V locks the still; re-describing the face causes identity drift.

Usage:
  uv run --env-file /workspace/.env talking_head.py \
      --image ads/assets/<slug>-portrait.jpg --line "..." --duration 7 \
      [--pronoun he|she|they] [--tone "casual, fast, dry"] [--accent "American"] \
      [--room "dorm room with LED strips"] --out ads/assets/heads/<ad-id>-A.mp4
  Use --prompt to override the template entirely (presenters.md may carry a custom prompt).
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

HOUSE_PROMPT = (
    "Raw unedited selfie phone footage. Same person, same room, same light as the photo. "
    "{S} holds eye contact with the lens, blinks irregularly, small nod as {s} starts, one brief hand gesture, "
    "then settles; gentle breathing, tiny head sway. Camera locked, static handheld framing, no zoom, no pan. "
    "{S} says: \"{line}\" "
    "Tone: {tone}, {accent}, medium energy, talking to a friend, not an announcer. "
    "Sound: close phone mic, quiet {room} room tone, no music. "
    "Clean picture only: no subtitles, no captions, no on-screen text, no watermarks."
)

PRONOUNS = {"he": ("He", "he"), "she": ("She", "she"), "they": ("They", "they")}


def image_to_url(path: str) -> str:
    if path.startswith("http"):
        return path
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    data = base64.b64encode(open(path, "rb").read()).decode()
    return f"data:{mime};base64,{data}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--line")
    ap.add_argument("--prompt")
    ap.add_argument("--pronoun", default="they", choices=list(PRONOUNS))
    ap.add_argument("--tone", default="casual, relaxed")
    ap.add_argument("--accent", default="natural accent")
    ap.add_argument("--room", default="")
    ap.add_argument("--duration", type=int, default=7)
    ap.add_argument("--resolution", default="720p")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not args.prompt and not args.line:
        sys.exit("need --line or --prompt")
    if not 1 <= args.duration <= 15:
        sys.exit("duration must be an integer 1-15")
    if args.line and any(c.isupper() for w in args.line.split() for c in w[1:]) and any(w.isupper() and len(w) > 1 for w in args.line.split()):
        print("WARNING: ALL-CAPS words in dialogue tend to trigger baked-in on-screen text. Prefer sentence case.", file=sys.stderr)

    S, s = PRONOUNS[args.pronoun]
    prompt = args.prompt or HOUSE_PROMPT.format(S=S, s=s, line=args.line, tone=args.tone, accent=args.accent, room=args.room).replace("  ", " ")

    # No aspect_ratio on I2V — it stretches. Shoot the still in 9:16 and let it inherit.
    r = requests.post(
        f"{BASE}/models/xai/grok-imagine-video-1.5/predictions",
        headers=HDRS,
        json={"input": {"image": image_to_url(args.image), "prompt": prompt,
                        "duration": args.duration, "resolution": args.resolution}},
        timeout=60,
    )
    r.raise_for_status()
    pred = r.json()
    pid = pred["id"]
    print(f"prediction {pid} started (${0.08 * args.duration:.2f})")

    while pred["status"] in ("starting", "processing"):
        time.sleep(8)
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
