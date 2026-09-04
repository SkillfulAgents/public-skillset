---
name: Produce Ad Video
description: 'END-TO-END workflow for producing a UGC-style TikTok/Reels ad (8-15s, 1080x1920) — script, talking-head generation, word-aligned captions, Remotion compositing, sound design, mastering, QC, ledger, delivery. This is the master skill; invoke it for any new ad, variant, or re-render. It calls generate-talking-head, build-product-visual and sound-design as sub-stages.'
metadata:
  version: "3.0.0"
---

# Produce Ad Video — the content machine

Every ad goes through ALL stages below, in order. Do not skip QC gates or the ledger.

## Layout

- `/workspace/ads/company.md` — product, ICP, approved claims, voice. `/workspace/ads/ADS.md` — **the ledger**: read FIRST, update LAST.
- `/workspace/ads/studio` — Remotion project, 1080x1920@30fps:
  - `brand.json` — company-level CTA text + logo files (written by onboarding). `src/theme.ts` — locked overlay style; iterate style HERE, never per ad.
  - `src/lib.tsx` — W/H/FPS, `Punch` (punch-zoom wrapper), `Placeholder`, `staticSrc` (keeps `?params` on HTML clips)
  - `src/TalkingHead.tsx` — cover-cropped OffthreadVideo (heads are 720x1280; don't zoom past ~1.3)
  - `src/Visual.tsx` — `VisualSpec` = `{kind:'html'|'still'|'video', src, …}`; `HtmlClip.tsx` (window.ANIM/seek clips), `MediaClip.tsx` (StillClip with Ken Burns drift, VideoClip)
  - `src/Captions.tsx` — word-pop captions (`Word = {text,start,end,emphasis}`), scene-aware dark text via `lightRanges`
  - `src/Overlays.tsx` — HookTitle, CtaPill, BrandLockup, SlideUpPanel, CommentCard, StepPop, ImageBadges
  - `src/Sound.tsx` — SfxTrack (catalog-resolved, sync_s-compensated) + MusicBed (fade-in, duck, hard-out)
  - `src/ClassicF1.tsx`, `src/QuickHit.tsx` — flow comps; `src/Root.tsx` — registry (props per ad via `--props`)
  - `public/heads/` — talking-head mp4s · `public/assets/` — user screenshots/recordings · `public/animations/` — built HTML clips · `public/sounds/` — synced sound library · `public/brand/` — logo files
- `/workspace/ads/assets/` — presenter portraits + raw generated heads. `/workspace/ads/sounds/` — the sound library master copy.
- First run only: `cd /workspace/ads/studio && npm install --include=dev` (the container sets NODE_ENV=production, which would skip TypeScript/@types otherwise).

## Stage 0 — Brief
If the ad hasn't been scripted, run `ideate-ads` first; produce from an approved ad-id in `/workspace/ads/campaigns/<slug>/IDEAS.md`. Otherwise read `ADS.md`, pick argument key, hook code, flow, presenter (from `presenters.md`), and the 1–2 product visuals. For a VARIANT, start from the existing entry and change one axis. Reuse a shared B-clip (CTA half) across same-argument variants to halve head cost.

## Stage 1 — Script
Two talking-head clips (~7s each) for F1–F5, or one 8–10s clip for Quick hits. Integer durations, ~2.2 words/s. Rules (`/workspace/ads/docs/vo-house-rules.md`):
- Clip A: hook line + setup. Clip B: payoff + CTA ("…at <brand> dot <tld>"), opening with a connective if shared.
- Finite verbs, one connective per clip, brand named once as the doer, one physical mechanism, CTA ≤ 6 words.
- One emphasized word per sentence (drives caption emphasis flags + SFX pops).
- Sentence case in dialogue (CAPS trigger baked-in text). Avoid jargon the speech model garbles; transcribe and compare.

## Stage 2 — Talking heads (`generate-talking-head`)
**CONFIRM COST with the user first** ($0.08/s ≈ $1.12 for 2×7s + retake allowance). Use the presenter's portrait and voice direction from `presenters.md`. QC EVERY take before compositing:
1. frames (`ffmpeg -vf "fps=1,scale=240:-1,tile=8x2"` → view) — no baked-in text, framing OK, uncanny checklist in `character-realism-guide.md` §5
2. transcribe (`qc_heads.py`) — wording matches script; voice metrics match sibling clips
3. retake with adjusted phrasing if either fails
Copy passing takes to `studio/public/heads/<ad-id>-A.mp4` / `-B.mp4`.

## Stage 3 — Captions (word-aligned, never guessed)
```bash
cd /workspace/ads/studio
uv run /workspace/.claude/skills/produce-ad-video/captions_from_transcript.py \
  --clip public/heads/<ad-id>-A.mp4:0.0 --clip public/heads/<ad-id>-B.mp4:<B-start-sec> \
  --emphasis <comma,separated,words> --out props-<ad-id>.json
```
`:offset` = where the clip's audio starts on the composition timeline. Scene times (`s2At`, `s3At`, …) come from these word timings — cut on sentence boundaries, never mid-word.

## Stage 4 — Visuals (`build-product-visual`)
Pick per scene: a user asset (`{kind:'still'}` screenshot with Ken Burns, `{kind:'video'}` screen recording) or a built HTML clip (`{kind:'html'}`). No asset library → build a clip ad-hoc with the skill. Light-background visuals flip captions dark automatically via `isLight`.

## Stage 5 — Composition
Use `ClassicF1` or `QuickHit` with per-ad props (`props-<ad-id>-nomusic.json`): `hookLines`, heads, `captions`, `splitVisual`, `fullVisual`, scene times, `endAt`. New flow shape → copy a comp to `src/<Flow>.tsx`, register in `Root.tsx`. House structure: 2–4s per scene, NEVER static, `Punch` on every scene, audio continuity (one head video spans multiple visual scenes — never cut audio mid-clip).

## Stage 6 — Sound design (`sound-design` — MANDATORY)
UGC palette only (`ugc-*`). Timestamp-anchor every hit (caption word starts, exact cut seconds, spring lands + ~2 frames). ALWAYS produce both props files: `props-<ad-id>-nomusic.json` and `props-<ad-id>-music.json` (bed `ugc-bed-hype` / `ugc-bed-house`, `outAt` = CTA land).

## Stage 7 — Render + master (both variants)
```bash
cd /workspace/ads/studio
npx remotion render src/index.ts <CompId> out/<ad-id>-nomusic.mp4 --props=props-<ad-id>-nomusic.json
npx remotion render src/index.ts <CompId> out/<ad-id>-music.mp4 --props=props-<ad-id>-music.json
for v in nomusic music; do ffmpeg -y -i out/<ad-id>-$v.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k out/<ad-id>-$v-master.mp4; done
```
Never deliver an unmastered render. If a render hangs > 10 min, kill it and retry (timeout guard).

## Stage 8 — QC gates (all must pass)
- Frames from the EXACT props being shipped (`ffmpeg -vf fps=2,scale=270:-1,tile=…` → view; eyeball frame 0 of every master): hook readable in 1s, captions synced, no dead/static stretches, visuals show their money-shot, overlays land, no error pages / missing assets.
- Audio: ebur128 I ≈ -14 LUFS, volumedetect max ≤ -4 dB; SFX transients present at event times; music variant lifts VO-gap mean ~4–6 dB vs nomusic; dry after CTA.
- Muted playthrough: story works with sound off.

## Stage 9 — Ship
Deliver BOTH `-master` files via `deliver_file`. Tell the user (first time especially) that in the file tray they can click on the video timeline to leave time-coded comments — those comments come back to you and are the fastest way to iterate. Update `ADS.md` (script, clips, props, renders, cost, feedback, learnings). Optionally `create-ad-thumbnail`. **Do NOT push to the tracker** unless the user explicitly says to (`ads-tracker-sheet`).
