---
name: Sound Design
description: 'UGC sound design for produced ads — timestamp-anchored SFX on every visual event (title slams, panel slides, punch-ins, emphasis words, CTA) from the shared sound library, optional energetic music bed, dual no-music/music render, and -14 LUFS mastering. Mandatory stage of every ad production (after the composition exists), and the fix for any audio-balance note.'
metadata:
  version: "2.0.0"
---

# Sound Design (UGC palette)

The **library** lives at `/workspace/ads/sounds/` (`catalog.json` + `sfx/` + `music/`) — read `catalog.json` first, always prefer library sounds over generating new ones. A synced copy for Remotion lives at `/workspace/ads/studio/public/sounds/` (re-copy after growing the library). Reference docs: `/workspace/ads/docs/audio/`.

## Palette

**UGC ads (the default — use ONLY these):** `ugc-whoosh-punch` (title slams), `ugc-bass-hit` (cuts / drops / CTA), `ugc-riser` (peaks ON the cut), `ugc-swish` (panel slides), `ugc-pop` (emphasis words, badge runs), `ugc-click` (UI taps), `ugc-ding` (CTA chime), `ugc-zoom` (punch-ins). Music: `ugc-bed-hype` / `ugc-bed-house` — driving, 126–130 BPM, confident.

The library also contains a soft, papery *editorial* set (whooshes, paper, marker, ticks, `bed-curious/warm/tense`) inherited from an explainer pipeline. It reads as documentary, not UGC — don't use it on ads unless the user explicitly wants a calmer editorial feel.

## Timing is non-negotiable
"Close enough" reads as random. Anchor every `at` to a REAL timestamp:
- caption / emphasis words → whisper word starts (props.json captions)
- scene cuts → exact `s2At/s3At/s4At` values in the props
- spring entrances → appear time + ~2 frames for the overshoot land
Catalog entries carry `sync_s` (transient position inside the file, measured); `SfxTrack` subtracts it so the hit LANDS at `at`. When adding sounds, measure sync_s (first peak via a numpy onset scan) and store it — never assume 0.

## Aesthetic rules
- Music is OPTIONAL per ad but ALWAYS rendered as a second variant. ONE bed, ducked (calibrate `gainDb` — see below), fade in over the first shot, hard out (12-frame fade) at the CTA so the closer lands nearly dry.
- SFX punctuate ENTRANCES: one sound per event, not per frame. Max ~1 SFX per 1.5s; silence is a tool. (A fast stagger run like badges counts as ONE event — quiet pops per badge.)
- Word-pop captions do NOT each get a click — only the hook title and emphasis words.

## Event mapping

| Motion event | UGC sound |
|---|---|
| Hook title slam | `ugc-whoosh-punch` (+ `ugc-bass-hit` layered quiet, -14) |
| Emphasis caption word | `ugc-pop` |
| Panel slides up (split reveal) | `ugc-swish` |
| Build INTO a cut | `ugc-riser` (peaks ON the cut) |
| Full-bleed punch-in | `ugc-bass-hit` (+ riser before) |
| Cut back / punch zoom | `ugc-zoom` |
| UI element pop-in inside a visual | `ugc-click` |
| Badge stagger run | `ugc-pop` per badge, -12 |
| CTA card lands | `ugc-bass-hit` + `ugc-ding` |

## Steps (run for EVERY ad)
1. **SFX plan**: walk the comp's visual events and build the `sfx` prop: `[{sound, at, gainDb?}]` in composition seconds. Respect density.
2. **Music**: `music: null` in `props-<ad-id>-nomusic.json`; `music: {file: "music/ugc-bed-hype.mp3", gainDb: <calibrated>, outAt: <CTA land>}` in `props-<ad-id>-music.json`. Render both, deliver both.
3. **Missing sounds**: generate → save to `/workspace/ads/sounds/sfx/<id>.mp3`, add a catalog entry (dur_s + measured sync_s, use, pairs_with), re-copy to `studio/public/sounds/`. Prompt vocabulary: "punchy", "tight", "snappy", "energetic" (808 hits, risers, swishes; min `--seconds 0.5`). Never "epic cinematic boom".
   ```bash
   cd /workspace/.claude/skills/sound-design/scripts
   uv run --env-file /workspace/.env --with requests sfx_gen.py --text "tight punchy 808 bass hit, dry" --seconds 0.6 --out /workspace/ads/sounds/sfx/<id>.mp3
   uv run --env-file /workspace/.env --with requests music_gen.py --ms 30000 --prompt "driving confident house beat, 128 BPM, instrumental, sparse midrange" --out /workspace/ads/sounds/music/<id>.mp3
   ```
   Backends: ElevenLabs direct if `ELEVEN_LABS_API_KEY` is set; otherwise both scripts fall back to the platform media proxy automatically (SFX → `stability-ai/stable-audio-2.5` $0.20/run; music → `google/lyria-3` $0.04/clip). Confirm cost before music generation.
4. **Master the render (ALWAYS)** — VO is hot and SFX peak at 0 dBFS, so the raw mix clips:
   ```bash
   ffmpeg -y -i out/<ad>.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k out/<ad>-master.mp4
   ```
   Verify: ebur128 I ≈ -14 LUFS, volumedetect max ≤ -4 dB.
5. **Gain calibration**: `gain_db` values are relative to a bed mastered at VO level — the shipped beds are quiet (mean ≈ -24 dB), so `-12` on top buries them (a typical working value is `gainDb: -2` to `-4`). Calibrate empirically: render, `volumedetect` a VO-gap window — music should lift the gap mean by ~4–6 dB over the no-music render, max ≈ -10..-14 dBFS. The same check confirms SFX landed (gap max jumps from silence to ≈ -10 dB).
6. **Muted playthrough test**: the ad must still work with sound off.

## Notes
- This skill *plans* sounds and provides files; all mixing happens in Remotion (`src/Sound.tsx`).
- Regenerating a talking-head clip invalidates word-synced SFX timings — re-check the plan after any retake.
