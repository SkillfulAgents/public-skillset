# API Reference — Sound Effects & Music (extract)

> Source: `/workspace/vox-pipeline/research/api-reference.md` §2, §3, §9 + cost lines (verified live 2026-07-17). The full reference also covers TTS/VO, image, and video APIs.

## 2. Sound Effects — ElevenLabs

`POST https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_128`
```bash
curl -X POST "https://api.elevenlabs.io/v1/sound-generation" \
  -H "xi-api-key: $ELEVEN_LABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"text": "quick whoosh transition", "duration_seconds": 1.0,
       "prompt_influence": 0.3, "model_id": "eleven_text_to_sound_v2"}' --output whoosh.mp3
```
- Returns raw audio bytes (`audio/mpeg`), not JSON.
- `duration_seconds`: 0.5–30 (API schema; omit → model guesses length). `loop: true` for seamless loops (v2 model only). Default model `eleven_text_to_sound_v2`.
- Cost: **40 credits/second** when duration specified (docs, capabilities page). WAV 48kHz available for non-looping.
- Fallback: none needed at ElevenLabs; on Replicate `stability-ai/stable-audio-2.5` can do SFX+ambience.
- verified: **yes** — live call HTTP 200, 1s MP3 saved to `samples/sfx_whoosh.mp3`.

## 3. Music — Eleven Music

`POST https://api.elevenlabs.io/v1/music?output_format=auto` (paid plans; commercial-use cleared)
```bash
curl -X POST "https://api.elevenlabs.io/v1/music" \
  -H "xi-api-key: $ELEVEN_LABS_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "warm curious documentary underscore, soft synth pulse, 90 BPM, instrumental", "music_length_ms": 30000}' --output track.mp3
```
- Returns raw audio (MP3 44.1/48kHz or WAV). Length 3s–5min. Instead of `prompt` you can send a structured `composition_plan` (`positive_global_styles`, `negative_global_styles`, `sections[]` with `section_name`, `duration_ms` 3000–120000, `lines[]` lyrics, per-section styles) — ideal for beat-timed underscore. Detailed variant: `POST /v1/music/detailed` returns metadata + song id.
- **FALLBACK (dollar-priced, same model):** Replicate `elevenlabs/music` — verified live; inputs: `prompt*`, `music_length_ms` (default 10000), `force_instrumental` (default true), `output_format` (`mp3_standard`…`wav_cd_quality`).
- Alt fallback: `google/lyria-2` (48kHz stereo instrumental; `prompt`, `negative_prompt`, `seed`) or `minimax/music-2.5` (full songs w/ vocals, up to 4–5 min).
- verified: **endpoint yes (docs + OpenAPI schema); no audio generated (cost)**. Replicate mirror slug verified live via API (HTTP 200).

## 9. Music generation — Replicate (fallback ranking)

1. `elevenlabs/music` (same engine as §3, dollar-priced per run)
2. `google/lyria-2` — 48kHz stereo instrumental, prompt+negative_prompt
3. `minimax/music-2.5` — full songs w/ vocals up to ~4min; `meta/musicgen` for cheap loops; `stability-ai/stable-audio-2.5` for music+SFX hybrids.

- verified: **yes** — all slugs 200 via live API.

## Cost (per asset, mid-2026)

- SFX: 40 credits/s specified duration (ElevenLabs credits)
- Music: Eleven Music is credit-priced on direct API; the Replicate mirror `elevenlabs/music` is dollar-priced per run
- (Full cheat-sheet in source doc also covers VO ~1 credit/char, images $0.006–0.21, video $0.35–1.2/clip)
