#!/usr/bin/env python3
"""Compress no-change waiting stretches in a video, with on-screen wait labels."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", "/workspace/bin/ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "/workspace/bin/ffprobe")


@dataclass
class Segment:
    start: float
    end: float

    @property
    def duration(self) -> float:
        return max(0.0, self.end - self.start)


@dataclass
class Piece:
    """One piece of the output timeline."""

    kind: str  # "play" | "wait"
    src_start: float
    src_end: float
    out_duration: float = 0.0
    label: str = ""
    original_wait: float = 0.0

    @property
    def src_duration(self) -> float:
        return max(0.0, self.src_end - self.src_start)

    def output_duration(self) -> float:
        if self.kind == "play":
            return self.src_duration
        return max(0.35, self.out_duration)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=False, text=True, capture_output=True)


def probe_duration(path: str) -> float:
    cp = run(
        [
            FFPROBE,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            path,
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {cp.stderr}")
    return float(json.loads(cp.stdout)["format"]["duration"])


def probe_has_audio(path: str) -> bool:
    cp = run(
        [
            FFPROBE,
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            path,
        ]
    )
    return bool(cp.stdout.strip())


def probe_size(path: str) -> tuple[int, int]:
    cp = run(
        [
            FFPROBE,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "json",
            path,
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(f"ffprobe size failed: {cp.stderr}")
    s = json.loads(cp.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def detect_freezes(path: str, noise: float, min_freeze: float) -> list[Segment]:
    cmd = [
        FFMPEG,
        "-hide_banner",
        "-i",
        path,
        "-vf",
        f"freezedetect=n={noise}:d={min_freeze}",
        "-f",
        "null",
        "-",
    ]
    cp = run(cmd)
    text = cp.stderr or ""

    starts: list[float] = []
    ends: list[float] = []
    start_re = re.compile(r"freeze_start:\s*([0-9.]+)")
    end_re = re.compile(r"freeze_end:\s*([0-9.]+)")
    for line in text.splitlines():
        m = start_re.search(line)
        if m:
            starts.append(float(m.group(1)))
            continue
        m = end_re.search(line)
        if m:
            ends.append(float(m.group(1)))

    freezes: list[Segment] = []
    i = j = 0
    unpaired: list[float] = []
    while i < len(starts):
        s = starts[i]
        while j < len(ends) and ends[j] <= s + 1e-6:
            j += 1
        if j < len(ends):
            freezes.append(Segment(s, ends[j]))
            j += 1
            i += 1
        else:
            unpaired.append(s)
            i += 1

    duration = probe_duration(path)
    for s in unpaired:
        freezes.append(Segment(s, duration))

    freezes.sort(key=lambda x: x.start)
    merged: list[Segment] = []
    for fr in freezes:
        if not merged or fr.start > merged[-1].end + 1e-3:
            merged.append(Segment(fr.start, fr.end))
        else:
            merged[-1].end = max(merged[-1].end, fr.end)
    return merged


def format_ts(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    if h:
        return f"{h:02d}:{m:02d}:{s:06.3f}"
    return f"{m:02d}:{s:06.3f}"


def format_wait_label(seconds: float) -> str:
    """Human label like 'waited 12s' or 'waited 1:10'."""
    sec = max(0, int(round(seconds)))
    if sec < 60:
        return f"waited {sec}s"
    m, s = divmod(sec, 60)
    if m < 60:
        return f"waited {m}:{s:02d}"
    h, m = divmod(m, 60)
    return f"waited {h}:{m:02d}:{s:02d}"


def wait_hold_duration(
    original: float, min_hold: float, max_hold: float, scale: float
) -> float:
    """Map a long real-world wait to a short on-screen hold."""
    if original <= 0:
        return min_hold
    hold = min_hold + scale * math.log2(1.0 + original)
    return max(min_hold, min(max_hold, hold))


def build_timeline(
    freezes: list[Segment],
    duration: float,
    *,
    label_threshold: float,
    keep_short_under: float,
    min_hold: float,
    max_hold: float,
    hold_scale: float,
    context_pad: float,
    label_freezes: set[int] | None = None,
    hard_cut_unlabeled: bool = False,
    cut_pad: float = 0.2,
    hard_cut_min: float | None = None,
    custom_label: str | None = None,
    skip_ranges: list[tuple[float, float]] | None = None,
) -> list[Piece]:
    """
    label_freezes: optional set of freeze indices (0-based) that should get a
    labeled wait hold. If None, every freeze >= label_threshold is labeled.
    hard_cut_unlabeled: when True, long freezes NOT in label_freezes are cut
    out entirely (with cut_pad kept at edges) instead of played in full.
    custom_label: if set, used for every labeled wait instead of format_wait_label.
    skip_ranges: absolute source ranges to drop entirely (after freeze handling).
    """
    pieces: list[Piece] = []
    cursor = 0.0

    def add_play(a: float, b: float) -> None:
        if b - a < 0.04:
            return
        if pieces and pieces[-1].kind == "play" and abs(pieces[-1].src_end - a) < 1e-3:
            pieces[-1].src_end = b
        else:
            pieces.append(Piece(kind="play", src_start=a, src_end=b))

    for idx, fr in enumerate(freezes):
        if fr.start > cursor:
            add_play(cursor, fr.start)

        wait_len = fr.duration
        should_label = wait_len >= label_threshold and (
            label_freezes is None or idx in label_freezes
        )

        if should_label:
            pad = min(context_pad, wait_len / 4.0)
            pre_end = fr.start + pad
            post_start = fr.end - pad
            mid_len = max(0.0, post_start - pre_end)

            add_play(fr.start, pre_end)

            if mid_len >= 0.2:
                hold = wait_hold_duration(mid_len, min_hold, max_hold, hold_scale)
                frame_t = (pre_end + post_start) / 2.0
                label = custom_label if custom_label else format_wait_label(wait_len)
                pieces.append(
                    Piece(
                        kind="wait",
                        src_start=frame_t,
                        src_end=frame_t,
                        out_duration=hold,
                        label=label,
                        original_wait=wait_len,
                    )
                )

            add_play(post_start, fr.end)
        elif hard_cut_unlabeled and wait_len >= (
            hard_cut_min if hard_cut_min is not None else label_threshold
        ):
            # Strip the freeze, keep a little edge context so the cut isn't harsh
            pad = min(cut_pad, wait_len / 5.0)
            add_play(fr.start, fr.start + pad)
            add_play(fr.end - pad, fr.end)
        elif wait_len >= keep_short_under:
            add_play(fr.start, fr.end)
        else:
            add_play(fr.start, min(fr.end, fr.start + 0.1))

        cursor = fr.end

    if cursor < duration:
        add_play(cursor, duration)

    pieces = [p for p in pieces if p.kind == "wait" or p.src_duration >= 0.04]
    if skip_ranges:
        pieces = apply_skip_ranges(pieces, skip_ranges)
    return pieces


def apply_skip_ranges(
    pieces: list[Piece], ranges: list[tuple[float, float]]
) -> list[Piece]:
    """Drop any source content overlapping skip ranges (play pieces only)."""
    if not ranges:
        return pieces
    out: list[Piece] = []
    for piece in pieces:
        if piece.kind == "wait":
            # drop wait if its source frame sits inside a skip range
            if any(a - 1e-6 <= piece.src_start < b + 1e-6 for a, b in ranges):
                continue
            out.append(piece)
            continue
        segs = [(piece.src_start, piece.src_end)]
        for a, b in ranges:
            nxt: list[tuple[float, float]] = []
            for s, e in segs:
                if e <= a + 1e-6 or s >= b - 1e-6:
                    nxt.append((s, e))
                    continue
                if s < a:
                    nxt.append((s, a))
                if e > b:
                    nxt.append((b, e))
            segs = nxt
        for s, e in segs:
            if e - s >= 0.04:
                if out and out[-1].kind == "play" and abs(out[-1].src_end - s) < 1e-3:
                    out[-1].src_end = e
                else:
                    out.append(Piece(kind="play", src_start=s, src_end=e))
    return out


def parse_ranges(spec: str) -> list[tuple[float, float]]:
    """Parse 'a-b,c-d' second ranges."""
    ranges: list[tuple[float, float]] = []
    if not spec.strip():
        return ranges
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" not in part:
            raise ValueError(f"Bad range (want start-end): {part}")
        a_s, b_s = part.split("-", 1)
        a, b = float(a_s), float(b_s)
        if b <= a:
            raise ValueError(f"Bad range order: {part}")
        ranges.append((a, b))
    return ranges


def ass_timestamp(seconds: float) -> str:
    """ASS time format H:MM:SS.cs (centiseconds)."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - h * 3600 - m * 60
    cs = int(round((s - int(s)) * 100))
    sec_i = int(s)
    if cs >= 100:
        sec_i += 1
        cs = 0
    return f"{h}:{m:02d}:{sec_i:02d}.{cs:02d}"


def escape_ass_text(text: str) -> str:
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def write_ass(
    path: str,
    pieces: list[Piece],
    width: int,
    height: int,
) -> None:
    """Write ASS subtitles for wait labels on the OUTPUT timeline."""
    fontsize = max(36, min(96, int(width * 0.036)))
    # MarginV from bottom ~18% of height
    margin_v = int(height * 0.16)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Wait,DejaVu Sans,{fontsize},&H00FFFFFF,&H000000FF,&HAA000000,&H80000000,-1,0,0,0,100,100,0,0,3,0,0,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events: list[str] = []
    t = 0.0
    for piece in pieces:
        d = piece.output_duration()
        if piece.kind == "wait" and piece.label:
            # slight inset so label doesn't flash on the very first/last frame
            start = t + 0.08
            end = t + d - 0.08
            if end > start:
                text = escape_ass_text(piece.label)
                # BorderStyle=3 = opaque box; add a bit of padding via \bord
                events.append(
                    f"Dialogue: 0,{ass_timestamp(start)},{ass_timestamp(end)},"
                    f"Wait,,0,0,0,,{{\\bord16\\shad0}}{text}"
                )
        t += d

    Path(path).write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def build_filter_complex(
    pieces: list[Piece], has_audio: bool, ass_path: str, fps: int = 30
) -> str:
    filters: list[str] = []
    v_labels: list[str] = []
    a_labels: list[str] = []

    # Escape ass path for ffmpeg filtergraph
    ass_esc = (
        ass_path.replace("\\", "/")
        .replace(":", r"\:")
        .replace("'", r"\'")
    )

    for i, piece in enumerate(pieces):
        v = f"v{i}"
        if piece.kind == "play":
            # Normalize fps so concat is happy across pieces
            filters.append(
                f"[0:v]trim=start={piece.src_start:.6f}:end={piece.src_end:.6f},"
                f"setpts=PTS-STARTPTS,fps={fps}[{v}]"
            )
            if has_audio:
                a = f"a{i}"
                filters.append(
                    f"[0:a]atrim=start={piece.src_start:.6f}:end={piece.src_end:.6f},"
                    f"asetpts=PTS-STARTPTS[{a}]"
                )
                a_labels.append(f"[{a}]")
        else:
            hold = piece.output_duration()
            # loop one frame: loop count = total_frames - 1
            nframes = max(2, int(round(hold * fps)))
            loops = nframes - 1
            frame_start = max(0.0, piece.src_start)
            # grab a slightly wider window so VFR sources still yield a frame
            frame_end = frame_start + 0.08
            filters.append(
                f"[0:v]trim=start={frame_start:.6f}:end={frame_end:.6f},"
                f"setpts=PTS-STARTPTS,fps={fps},"
                f"loop=loop={loops}:size=1:start=0,"
                f"setpts=N/{fps}/TB,"
                f"trim=duration={hold:.6f},setpts=PTS-STARTPTS[{v}]"
            )
            if has_audio:
                a = f"a{i}"
                filters.append(
                    f"anullsrc=channel_layout=stereo:sample_rate=48000,"
                    f"atrim=duration={hold:.6f},asetpts=PTS-STARTPTS[{a}]"
                )
                a_labels.append(f"[{a}]")
        v_labels.append(f"[{v}]")

    n = len(pieces)
    if has_audio:
        filters.append(
            "".join(v_labels + a_labels) + f"concat=n={n}:v=1:a=1[cv][outa]"
        )
        filters.append(f"[cv]ass='{ass_esc}'[outv]")
    else:
        filters.append("".join(v_labels) + f"concat=n={n}:v=1:a=0[cv]")
        filters.append(f"[cv]ass='{ass_esc}'[outv]")
    return ";".join(filters)


def encode(
    input_path: str,
    output_path: str,
    pieces: list[Piece],
    has_audio: bool,
    width: int,
    height: int,
    crf: int,
) -> None:
    with tempfile.TemporaryDirectory(prefix="skipstatic_") as td:
        ass_path = str(Path(td) / "waits.ass")
        write_ass(ass_path, pieces, width, height)

        fc = build_filter_complex(pieces, has_audio, ass_path)
        cmd = [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-i",
            input_path,
            "-filter_complex",
            fc,
            "-map",
            "[outv]",
        ]
        if has_audio:
            cmd += ["-map", "[outa]", "-c:a", "aac", "-b:a", "160k"]
        else:
            cmd += ["-an"]

        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            str(crf),
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            output_path,
        ]

        print("Encoding…", flush=True)
        cp = run(cmd)
        if cp.returncode != 0:
            err = cp.stderr or ""
            sys.stderr.write(err[-5000:])
            raise RuntimeError(f"ffmpeg encode failed (code {cp.returncode})")


def estimate_out_duration(pieces: list[Piece]) -> float:
    return sum(p.output_duration() for p in pieces)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--min-freeze", type=float, default=0.8)
    p.add_argument("--noise", type=float, default=0.001)
    p.add_argument(
        "--label-threshold",
        type=float,
        default=1.5,
        help="Freezes >= this many seconds become labeled waits",
    )
    p.add_argument(
        "--keep-short-under",
        type=float,
        default=0.0,
        help="Drop freezes shorter than this (seconds)",
    )
    p.add_argument("--min-hold", type=float, default=1.2)
    p.add_argument("--max-hold", type=float, default=2.8)
    p.add_argument("--hold-scale", type=float, default=0.35)
    p.add_argument("--context-pad", type=float, default=0.35)
    p.add_argument("--cut-pad", type=float, default=0.2,
                   help="Edge seconds kept when hard-cutting unlabeled freezes")
    p.add_argument("--crf", type=int, default=20)
    p.add_argument("--preview", action="store_true")
    p.add_argument(
        "--hard-cut",
        action="store_true",
        help="Delete all freezes entirely (no labels)",
    )
    p.add_argument(
        "--label-only",
        type=str,
        default="",
        help="Comma-separated 1-based freeze numbers to label "
        "(e.g. '7'). Others are hard-cut if long.",
    )
    p.add_argument(
        "--label-longest",
        type=int,
        default=0,
        metavar="N",
        help="Label only the N longest freeze(s); hard-cut the rest",
    )
    p.add_argument(
        "--label-text",
        type=str,
        default="",
        help="Custom text for labeled waits (e.g. 'wait for about a min')",
    )
    p.add_argument(
        "--hard-cut-min",
        type=float,
        default=-1.0,
        help="Only hard-cut unlabeled freezes >= this many seconds "
        "(-1 = same as --label-threshold). Shorter freezes are kept.",
    )
    p.add_argument(
        "--end-at",
        type=float,
        default=0.0,
        help="Trim source after this timestamp (seconds). 0 = full duration",
    )
    p.add_argument(
        "--skip",
        type=str,
        default="",
        help="Comma-separated source ranges to drop, e.g. '126.7-148.8,183-999'",
    )
    args = p.parse_args()

    for binary in (FFMPEG, FFPROBE):
        if not Path(binary).exists():
            print(f"Missing binary: {binary}", file=sys.stderr)
            return 1
    if not Path(args.input).exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    full_duration = probe_duration(args.input)
    has_audio = probe_has_audio(args.input)
    width, height = probe_size(args.input)
    duration = full_duration
    if args.end_at and 0 < args.end_at < full_duration:
        duration = args.end_at
        print(f"Trimming source end at {duration:.3f}s (of {full_duration:.3f}s)")
    try:
        skip_ranges = parse_ranges(args.skip)
    except ValueError as e:
        print(f"Bad --skip: {e}", file=sys.stderr)
        return 2
    custom_label = args.label_text.strip() or None
    print(f"Input: {args.input}")
    print(f"Duration: {duration:.3f}s | {width}x{height} | audio={has_audio}")
    if skip_ranges:
        print("Skip ranges: " + ", ".join(f"{a:.2f}-{b:.2f}" for a, b in skip_ranges))
    if custom_label:
        print(f"Custom wait label: {custom_label!r}")
    print(
        f"Detecting freezes (noise={args.noise}, min={args.min_freeze}s)…",
        flush=True,
    )

    freezes = detect_freezes(args.input, noise=args.noise, min_freeze=args.min_freeze)
    # Clamp / drop freezes past the trimmed end
    clamped: list[Segment] = []
    for fr in freezes:
        if fr.start >= duration - 1e-3:
            continue
        clamped.append(Segment(fr.start, min(fr.end, duration)))
    freezes = clamped
    total_freeze = sum(f.duration for f in freezes)
    print(f"Found {len(freezes)} freeze segment(s), {total_freeze:.2f}s total:")
    for i, fr in enumerate(freezes, 1):
        print(
            f"  freeze {i}: {format_ts(fr.start)} → {format_ts(fr.end)} "
            f"({fr.duration:.2f}s)"
        )

    label_freezes: set[int] | None = None
    hard_cut_unlabeled = False

    if args.label_only:
        # 1-based freeze numbers from CLI → 0-based indices
        label_freezes = set()
        for part in args.label_only.split(","):
            part = part.strip()
            if not part:
                continue
            n = int(part)
            if n < 1 or n > len(freezes):
                print(f"Bad --label-only value: {n}", file=sys.stderr)
                return 2
            label_freezes.add(n - 1)
        hard_cut_unlabeled = True
    elif args.label_longest > 0 and freezes:
        ranked = sorted(
            range(len(freezes)), key=lambda i: freezes[i].duration, reverse=True
        )
        label_freezes = set(ranked[: args.label_longest])
        hard_cut_unlabeled = True
        print(
            "Labeling freeze(s): "
            + ", ".join(
                f"#{i+1} ({freezes[i].duration:.1f}s)" for i in sorted(label_freezes)
            )
        )

    hc_min = None if args.hard_cut_min < 0 else args.hard_cut_min
    common_kw = dict(
        label_threshold=args.label_threshold,
        keep_short_under=args.keep_short_under,
        min_hold=args.min_hold,
        max_hold=args.max_hold,
        hold_scale=args.hold_scale,
        context_pad=args.context_pad,
        cut_pad=args.cut_pad,
        hard_cut_min=hc_min,
        custom_label=custom_label,
        skip_ranges=skip_ranges,
    )
    if args.hard_cut:
        pieces = build_timeline(
            freezes,
            duration,
            label_freezes=set(),  # label none
            hard_cut_unlabeled=True,
            **common_kw,
        )
    else:
        pieces = build_timeline(
            freezes,
            duration,
            label_freezes=label_freezes,
            hard_cut_unlabeled=hard_cut_unlabeled,
            **common_kw,
        )

    out_est = estimate_out_duration(pieces)
    print(f"\nTimeline ({len(pieces)} pieces, ~{out_est:.1f}s output):")
    t = 0.0
    for piece in pieces:
        if piece.kind == "play":
            d = piece.src_duration
            print(
                f"  [{format_ts(t)}] play  src {format_ts(piece.src_start)}"
                f"→{format_ts(piece.src_end)} ({d:.2f}s)"
            )
            t += d
        else:
            d = piece.out_duration
            print(
                f"  [{format_ts(t)}] WAIT  \"{piece.label}\" "
                f"(was {piece.original_wait:.1f}s → show {d:.2f}s)"
            )
            t += d

    if args.preview:
        print("\nPreview only — no output written.")
        return 0

    if not pieces:
        print("Nothing to write.", file=sys.stderr)
        return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    encode(
        args.input,
        str(out),
        pieces,
        has_audio=has_audio,
        width=width,
        height=height,
        crf=args.crf,
    )
    out_dur = probe_duration(str(out))
    size_mb = out.stat().st_size / (1024 * 1024)
    print(f"\nWrote {out} ({out_dur:.2f}s, {size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
