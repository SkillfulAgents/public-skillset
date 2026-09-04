"""Generate a music bed via Eleven Music (direct API, falls back to the platform's built-in media proxy with google/lyria-3 — no ElevenLabs/Replicate key needed).

Usage:
  uv run --env-file /workspace/.env --with requests music_gen.py \
      --prompt "minimal curious documentary underscore, soft marimba pulse, 95 BPM, instrumental, sparse midrange" \
      --ms 45000 --out bed.mp3
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", required=True)
    p.add_argument("--ms", type=int, default=30000)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    if os.environ.get("ELEVEN_LABS_API_KEY"):
        r = requests.post(
            "https://api.elevenlabs.io/v1/music",
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": os.environ["ELEVEN_LABS_API_KEY"]},
            json={"prompt": args.prompt, "music_length_ms": args.ms},
            timeout=600,
        )
        if r.ok and r.headers.get("content-type", "").startswith("audio"):
            out.write_bytes(r.content)
            print(out)
            return
        print(f"Eleven Music direct failed ({r.status_code}: {r.text[:200]}), falling back...", file=sys.stderr)
    else:
        print("no ELEVEN_LABS_API_KEY, using platform proxy (google/lyria-3, $0.04/clip)...", file=sys.stderr)

    # platform's built-in media proxy fallback: google/lyria-3 (30s instrumental clips)
    import time

    base = os.environ["ANTHROPIC_BASE_URL"].rstrip("/") + "/v1/replicate"
    hdrs = {"Authorization": f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}"}
    r = requests.post(
        f"{base}/models/google/lyria-3/predictions",
        headers=hdrs,
        json={"input": {"prompt": args.prompt + ", instrumental"}},
        timeout=60,
    )
    r.raise_for_status()
    pred = r.json()
    while pred["status"] in ("starting", "processing"):
        time.sleep(5)
        pred = requests.get(f"{base}/predictions/{pred['id']}", headers=hdrs, timeout=30).json()
    if pred["status"] != "succeeded":
        sys.exit(f"lyria-3 FAILED: {pred.get('error')}")
    url = pred["output"] if isinstance(pred["output"], str) else pred["output"][0]
    out.write_bytes(requests.get(url, timeout=120).content)
    print(out)


if __name__ == "__main__":
    main()
