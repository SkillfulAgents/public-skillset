# Remotion Audio Notes (extract)

> Source: `/workspace/vox-pipeline/research/remotion-notes.md` — the parts describing how audio is rendered and how the sound catalog is consumed at assembly time. Relevant if your agent also assembles video in Remotion; the sound-design skill itself only *plans*.

## Audio components

- `<Audio>` and `<Video>` from **`@remotion/media`** — the currently recommended components (preferred over core `<Audio>`/`<OffthreadVideo>`). Props: `trimBefore`/`trimAfter` (frames), `volume` (number or `(f) => ...` for fades), `playbackRate`, `loop`. Core `<OffthreadVideo>` from `remotion` still works and is the classic render-safe video component; `@remotion/media` is its successor.
- `staticFile("foo.png")` — references files in `public/`; combine: `<Img src={staticFile("chart.png")} />`, `<Audio src={staticFile("vo.mp3")} />`.
- `getAudioDurationInSeconds()` etc. from `@remotion/media-utils` (or `mediabunny` for metadata) — for sizing comps to voiceover length.

## How the main composition renders audio (Main.tsx)

`Main` (props = whole script.json) renders: beats as hard-cut `<Sequence premountFor={30}>` (timings via `beatWindow`) → global `FilmGrain` + `Vignette` (above scenes, below captions) → `Captions` from `vo.words` file → `<Audio>` VO (full volume) → music bed (`music.file` at `gain_db`, −6dB step over 12f at the `turn` beat, 12f fade-out ending at the `kicker` beat start = kicker nearly dry) → SFX from `beats[].sfx` (`at`: `"start"` | `"end"` | seconds offset) resolved via `public/sounds/catalog.json` (entry `gain_db` → linear volume; falls back to `sounds/<name>.wav`; silent if missing). `calculateMainMetadata` = max(vo.duration_s, last beat end) × fps.

- Missing anything (asset file, chart data, words.json, sounds) → labeled `Placeholder` box or silent skip. Never crashes on partial data.

## Sound library (consumption side)

`/workspace/vox-pipeline/sounds/catalog.json` — `{sounds: {name: {file, gain_db, description}}, music: {...}}`; files relative to sounds/. Assembly copies the whole `sounds/` dir into `public/sounds/`. Catalog maps the house family (whoosh-short/deep, marker-swipe, paper-slap, paper-slide, pop-soft, tick-count, chart-ticks, thud-soft, turn-impact, riser-subtle, typewriter, page-turn, crackle-vinyl, map-whoosh, whip-whoosh, kicker-note, …) with §8.3 dB offsets; real mp3s from the sound-design stage win over the synthesized placeholder wavs.

## Known limitations (audio-relevant)

- SFX `gain_db` maps to linear volume directly — real -14 LUFS mixing/ducking of VO vs music is approximated (music duck is a fixed step at the turn, not sidechained).
- `Main` always hard-cuts between beats; `blurPush`/`paperSlide` are exported but not driven by a script field (use custom scenes for the Turn's "biggest transition").
