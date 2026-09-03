---
name: Skip Static Video
description: Compress no-change waiting stretches in screen recordings, replacing long freezes with short labeled "waited Xs" holds so pacing stays realistic.
metadata:
  version: 2.0.0
---

# Skip Static Video

Detect frozen / no-pixel-change stretches in a video and compress them into short on-screen waits with labels like **waited 12s** / **waited 1:10**, instead of hard-cutting (which feels too fast).

## Usage

```bash
uv run /workspace/.claude/skills/skip-static-video/skip_static.py \
  --input /path/to/video.mov \
  --output /workspace/output/edited.mp4
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--input` | required | Source video path |
| `--output` | required | Output video path |
| `--min-freeze` | `0.8` | Minimum freeze duration for detection |
| `--noise` | `0.001` | freezedetect noise tolerance |
| `--label-threshold` | `1.5` | Freezes ≥ this become labeled waits |
| `--min-hold` | `1.2` | Min seconds to show a labeled wait |
| `--max-hold` | `2.8` | Max seconds to show a labeled wait |
| `--hold-scale` | `0.35` | How hold length grows with real wait |
| `--context-pad` | `0.35` | Real freeze kept before/after the label |
| `--crf` | `20` | x264 quality |
| `--preview` | off | Print timeline only, don't encode |
| `--hard-cut` | off | Old behavior: delete freezes, no labels |

## Behavior

1. Detect freezes with ffmpeg `freezedetect`
2. Short freezes (< threshold): keep as natural pauses
3. Long freezes: keep a bit of real freeze for context, replace the middle with a still frame + **"waited Xm Ys"** badge, hold 1.2–2.8s depending on how long the real wait was
4. Concatenate and encode H.264 MP4
