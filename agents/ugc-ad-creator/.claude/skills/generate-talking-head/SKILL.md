---
name: Generate Talking Head
description: 'Generate hyper-real UGC presenter portraits (openai/gpt-image-2 by default) and lip-synced talking-head video clips with speech audio (xai/grok-imagine-video-1.5) through the platform media proxy. Use for creating personas (onboarding step 3) and for any ad shot that needs a person speaking to camera.'
metadata:
  version: "2.0.0"
---

# Generate Talking Head

Two-step pipeline producing consistent-character talking-head clips for vertical ads. Read `/workspace/ads/docs/character-realism-guide.md` before writing any prompt — realism comes from describing a believable capture process (phone camera, messy light, imperfect skin, candid moment), not from "photorealistic" tokens.

## Cost (confirm with user before generating!)
- Portrait: `openai/gpt-image-2` $0.128/image (default, quality=high) · `xai/grok-imagine-image-2` $0.04 · `flux-1.1-pro-ultra` raw $0.06
- Video: `xai/grok-imagine-video-1.5` $0.08/second (image-to-video, integer 1–15s, includes lip-synced speech audio)
- Model slugs must be on the platform list (`/opt/gamut/docs/media-generation.md`); a 403 means re-check the list.

## Step 1 — Persona portrait (once per character, reuse the file forever)

Check `/workspace/ads/assets/presenter-library/LIBRARY.md` first — 14 archetypes already exist; adopting one is free (copy to `ads/assets/<slug>-portrait.jpg`). `generate_library.py` regenerates/extends the library (add an entry, run; skips existing slugs). For a custom persona:

```bash
uv run --env-file /workspace/.env /workspace/.claude/skills/generate-talking-head/portrait.py \
  --prompt "<house portrait prompt v2 with the person + room filled in>" \
  --ref /workspace/ads/refs/persona-reference.jpg \
  --out /workspace/ads/assets/<slug>-portrait.jpg
```

- Prompt = `character-realism-guide.md` §3 template. Keep the frame contract (chest-up, face upper third, looking into lens, 9:16). Neutral / slightly parted lips — no broad grin.
- `--ref` passes the Gen Z reference persona as a *style* reference (camera feel, light, skin). Add "Match the photographic style and realism of the reference exactly, but a completely different person and room" to the prompt. Never reuse the reference face itself.
- Generate 2 candidates per archetype (gpt-image-2 + grok-imagine-image-2 on the same prompt ≈ $0.17), show both to the user, keep the winner.
- QC the still against the reference: wide-angle stretch? mixed practical light? visible pores/redness? clutter? If it looks like a stock photo, rewrite the prompt — don't just retry.
- Add the presenter to `/workspace/ads/assets/presenters.md` (slug, portrait file, character, setting, voice direction). Record rejected archetypes there too.

## Step 2 — Talking clips

```bash
uv run --env-file /workspace/.env /workspace/.claude/skills/generate-talking-head/talking_head.py \
  --image /workspace/ads/assets/<slug>-portrait.jpg \
  --line "Stop chasing invoices by hand. My <Brand> agent sends the reminders and just gets us paid." \
  --pronoun she --tone "warm, dry" --accent "American" --room "kitchen" \
  --duration 7 --out /workspace/ads/assets/heads/<ad-id>-A.mp4
```

Parameters:
- `--image`: the presenter's portrait (local path or https URL). Same image = same face across all clips.
- `--line`: the dialogue (sentence case). Wrapped in the house video prompt v2 (motion-only description, voice direction, clean-frame instruction). `--pronoun/--tone/--accent/--room` fill the template from `presenters.md`. `--prompt` overrides the whole template.
- `--duration`: integer 1–15. Budget ~2.2 words/s (7s ≈ 15 words). 5–8s clips are markedly more stable than 12–15s.
- No `aspect_ratio` is sent on purpose — I2V inherits the still's 9:16; passing it stretches.

Generation takes 1–4 min; the script polls and downloads the mp4.

## QC — every take, no exceptions
```bash
uv run --env-file /workspace/.env --with faster-whisper --with librosa --with soundfile --with numpy \
  /workspace/.claude/skills/generate-talking-head/qc_heads.py <clips...> [--sheet-dir DIR]
```
Per clip: 1 fps contact sheet (eyeball for baked text + the uncanny checklist in `character-realism-guide.md` §5), whisper transcript + last-word end, voice metrics (rms dB, median f0, spectral centroid).

Known quirks:
- **Baked-in captions**: the model sometimes renders its own (misspelled) subtitles. The prompt asks for a clean frame but it still slips through — check frames, retake if present. CAPS in dialogue makes it worse.
- **Jargon garbling**: technical terms can come out mangled. Use plain words; spell out the URL ("<brand> dot com"). ALWAYS transcribe and compare to script.
- **Hot audio**: VO comes out near full scale — downstream mixes MUST be mastered (loudnorm -14 LUFS, produce-ad-video Stage 7).
- **Voice drift between takes**: voice is synthesized fresh per generation (image gives face consistency, NOT voice consistency). When clips are spliced (A + shared B), QC voice MATCH across them: rms within ~2 dB, similar f0/centroid. Generate 2 candidates for shared clips and pick the closest match.
- **Big gestures = rubber mouth**: keep body motion small in the prompt; energy comes from the voice direction.
