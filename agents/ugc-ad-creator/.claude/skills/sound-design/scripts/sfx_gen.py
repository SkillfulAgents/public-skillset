"""Generate a sound effect via ElevenLabs sound-generation, falling back to the
platform's built-in media proxy with stability-ai/stable-audio-2.5 ($0.20/run)
when no ELEVEN_LABS_API_KEY is set (elevenlabs/sound-effects is NOT on the proxy).

Usage:
  uv run --env-file /workspace/.env --with requests sfx_gen.py \
      --text "quick soft whoosh, papery, subtle" --out whoosh.mp3 [--seconds 0.6] [--loop]

Cost: ElevenLabs 40 credits/second when --seconds given (range 0.5-30s), or $0.20/run via proxy.
"""

import argparse
import os
from pathlib import Path

import requests


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--text", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, default=None)  # ElevenLabs range: 0.5-30
    p.add_argument("--loop", action="store_true")
    p.add_argument("--influence", type=float, default=0.3)
    args = p.parse_args()
    if args.seconds is not None:
        args.seconds = max(0.5, args.seconds)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if os.environ.get("ELEVEN_LABS_API_KEY"):
        body = {"text": args.text, "prompt_influence": args.influence, "model_id": "eleven_text_to_sound_v2"}
        if args.seconds:
            body["duration_seconds"] = args.seconds
        if args.loop:
            body["loop"] = True
        r = requests.post(
            "https://api.elevenlabs.io/v1/sound-generation",
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": os.environ["ELEVEN_LABS_API_KEY"]},
            json=body, timeout=120,
        )
        r.raise_for_status()
        out.write_bytes(r.content)
        print(out)
        return

    # Platform proxy fallback: stable-audio-2.5 text-to-audio
    import sys
    import time

    print("no ELEVEN_LABS_API_KEY, using platform proxy (stable-audio-2.5, $0.20/run)...", file=sys.stderr)
    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/") + "/v1/replicate"
    hdrs = {"Authorization": f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}"}
    inp = {"prompt": args.text}
    if args.seconds:
        inp["duration"] = max(1, round(args.seconds))
    r = requests.post(f"{base}/models/stability-ai/stable-audio-2.5/predictions", headers=hdrs, json={"input": inp}, timeout=60)
    r.raise_for_status()
    pred = r.json()
    while pred["status"] in ("starting", "processing"):
        time.sleep(4)
        pred = requests.get(f"{base}/predictions/{pred['id']}", headers=hdrs, timeout=30).json()
    if pred["status"] != "succeeded":
        sys.exit(f"stable-audio FAILED: {pred.get('error')}")
    url = pred["output"] if isinstance(pred["output"], str) else pred["output"][0]
    out.write_bytes(requests.get(url, timeout=120).content)
    print(out)


if __name__ == "__main__":
    main()
