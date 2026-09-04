#!/usr/bin/env python3
"""Export a video frame and add a high-contrast seam headline banner."""

import argparse
import random
import shlex
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--time", required=True, type=float)
    parser.add_argument("--headline", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--style", choices=("auto", "black", "white"), default="auto")
    parser.add_argument("--seam-y", type=int, default=960)
    parser.add_argument("--banner-height", type=int, default=120)
    parser.add_argument("--margin-x", type=int, default=70)
    parser.add_argument("--font-size", type=int, default=54)
    args = parser.parse_args()

    style = random.choice(("black", "white")) if args.style == "auto" else args.style
    if style == "black":
        box_color, text_color = "black@0.96", "white"
    else:
        box_color, text_color = "white@0.96", "black"

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    font = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    banner_y = args.seam_y - args.banner_height // 2
    banner_width = 1080 - 2 * args.margin_x
    escaped = args.headline.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    vf = (
        f"scale=1080:1920,"
        f"drawbox=x={args.margin_x}:y={banner_y}:w={banner_width}:h={args.banner_height}:"
        f"color={box_color}:t=fill,"
        f"drawtext=fontfile={font}:text='{escaped}':fontcolor={text_color}:"
        f"fontsize={args.font_size}:x=(w-text_w)/2:y={banner_y}+("
        f"{args.banner_height}-text_h)/2"
    )
    command = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", str(args.time), "-i", args.video, "-frames:v", "1",
        "-vf", vf, "-q:v", "2", str(output),
    ]
    subprocess.run(command, check=True)
    print(f"Created {output} ({style} banner)")


if __name__ == "__main__":
    main()
