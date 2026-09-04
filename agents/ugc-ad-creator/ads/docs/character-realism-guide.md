# Character Realism Guide — beating the uncanny valley for UGC presenters

Governs how presenter portraits and talking-head prompts are written. Pair with `/workspace/ads/assets/presenters.md`, `/workspace/ads/refs/persona-reference.md` and the `generate-talking-head` skill.

## 0. Why the reference persona reads human and polished portraits don't

Side-by-side of a flux-style "influencer" portrait vs. the reference persona (`refs/persona-reference.jpg`, gpt-image-2):

| Tell | Polished (DSLR-look models) | Reference persona (gpt-image-2) |
|---|---|---|
| Camera | Shallow bokeh, tack-sharp, centered subject | True arm's-length front camera: wide-angle edge stretch, off-center, slight tilt |
| Light | Single flattering key, symmetric catchlights, even fill (ring light) | Mixed practicals — cool LED strip + warm room bounce, uneven exposure |
| Skin | Smooth, glossy, uniform tone | Visible texture, slight redness, not retouched |
| Expression | Posed "model smile", perfectly framed | Caught mid-moment, half-smile, casual head tilt |
| Background | Curated / product-shot tidy | Lived-in room: posters, cables, clutter, mirrored hoodie logo |
| Sharpness | Over-detailed | Soft, mild compression / noise — like a real camera roll |

**Realism = a believable capture process, not a "photorealistic" token.** Every presenter prompt describes the phone, the messy light, the imperfect skin and the candid moment.

## 1. Principles (priority order)

1. **Prompt the camera, not a quality score.** "Unedited iPhone front-camera snapshot, arm's length, ~24mm equivalent, mild wide-angle distortion, deep focus, computational HDR, slight noise + JPEG compression." Never combine "selfie" with "85mm / f1.2 / bokeh / 8k" — that contradiction produces the ad-stock look.
2. **Skin is a non-uniform material.** Name 3–5 specifics: visible pores, peach fuzz, under-eye texture, slight T-zone oil, uneven redness, a healed blemish, faint lines, natural asymmetry (say "natural asymmetry", never "asymmetric face").
3. **Texture needs a light source.** Side window with falloff, overcast daylight, or mixed cool window + warm lamp. Avoid "beauty lighting", "ring light", "evenly lit".
4. **Candid beat, lived-in room.** "mid-sentence", "just glanced back from the laptop", "adjusting the phone"; add clutter evidence (charging cable, mug, laundry, sticky notes).
5. **Restraint tokens.** "no beauty filter, not airbrushed, not a studio portrait, not CGI." Negative-prompt fields are unreliable — state the positive alternative.

### Do / don't vocabulary

| Use | Avoid |
|---|---|
| unedited phone photo, camera-roll snapshot | masterpiece, best quality, 8k, ultra-detailed |
| natural skin texture, pores, peach fuzz, under-eye texture | flawless / perfect / porcelain skin |
| minor blemishes, uneven pigmentation, flyaway hairs | symmetrical perfect face |
| mixed practical light, imperfect exposure, slightly clipped window | beauty lighting, evenly illuminated, ring light |
| slight motion blur, sensor noise, mild JPEG compression | tack-sharp, hyperclarity, HDR glossy |
| candid, mid-sentence, unposed, slightly awkward crop | glamorous, posed model, cinematic |
| lived-in bedroom / kitchen / desk / car | luxury minimalist studio |

## 2. Portrait model options (platform proxy, 9:16)

| Model | $/img | Notes |
|---|---|---|
| `openai/gpt-image-2` | 0.128 | **Default.** Best prose adherence; produced the reference persona. Supports `input_images` for preservation-style edits ("keep pores + light, change only wardrobe"). Repeated edits gradually smooth skin — compare to source. |
| `xai/grok-imagine-image-2` | 0.04 | Same family as the video model → good identity lock into I2V. `quality=medium`, `resolution=2k`. Regression-test with a fixed prompt. |
| `black-forest-labs/flux-1.1-pro-ultra` (`raw=true`) | 0.06 | Strongest formal anti-polish switch; cheap fallback; needs the full imperfection vocabulary. |
| `google/nano-banana-pro` | 0.30 | Often most natural phone-style skin/light; use as an *editor* to fix a near-miss ("restore under-eye texture, replace flat frontal light with side window"). |
| `bytedance/seedream-5-pro` | 0.09 | Strong skin / multi-reference identity; check hands + face drift. |

Recommended for a new archetype: gpt-image-2 + grok-imagine-image-2 on the *same* prompt (~$0.17), pick by eye. Always confirm the model is on the platform list (`/opt/gamut/docs/media-generation.md`).

## 3. House portrait prompt v2

Keep the frame contract (chest-up, face in upper third, looking into lens) — it makes the split-screen/caption layout work. Everything else is capture-process language:

```
Unedited vertical iPhone front-camera snapshot, arm's-length framing, slightly off-center with a small tilt,
mild wide-angle edge distortion, deep phone-camera focus, computational HDR, faint sensor noise and JPEG compression.
<PERSON: age, build, hair, wardrobe with creases>, chest-up, face in the upper third, looking into the lens,
caught mid-sentence with a relaxed natural expression, lips slightly parted, natural facial asymmetry.
Skin: visible pores, peach fuzz, under-eye texture, slight T-zone shine, a little uneven redness, a couple of small blemishes, flyaway hairs.
Light: <one motivated imperfect source, e.g. cool window light from camera-left mixed with a warm desk lamp>, slightly imperfect auto white balance, soft shadow falloff.
Setting: <lived-in room with 2–3 pieces of clutter evidence>, slightly out of focus.
Ordinary camera-roll photo, not a studio portrait, not airbrushed, no beauty filter, not CGI.
```

### Archetype starters (adapt to the company's ICP)

| Slug idea | Person | Light / setting |
|---|---|---|
| `dorm-genz` (the reference) | man early 20s, curly hair, oversized grey hoodie | dorm room, LED strip + warm bounce, posters, closet clutter |
| `kitchen-founder` | woman early 30s, hair up messy, hoodie, leaning on counter mid-explanation | overcast window + warm ceiling spill; mug, open grocery bag |
| `car-ops` | man late 30s in a parked car, phone below eye level, slight stubble | broken windshield sunlight, blown highlight in side window |
| `night-desk-dev` | man mid 20s, glasses, wrinkled tee, glanced back from laptop | monitor spill on one cheek, single desk lamp, noisy shadows |
| `study-expert` | woman ~50, gray flyaways, reading glasses pushed up | window camera-left + warm lamp behind; stacked papers |
| `post-run` | man ~35 just after a run, flushed, uneven sweat | overcast park, motion softness |
| `bathroom-mirror` | woman late 20s, bare skin, damp hair | harsh overhead + side daylight, slight green WB cast |
| `shop-floor` | woman 40s, apron, hair tied back, retail/back-office clutter | fluorescent overhead + daylight door |

## 4. Talking-head (grok-imagine-video-1.5) prompt rules

- **I2V locks the still.** Describe only what *changes* (motion, speech, sound). Re-describing face/wardrobe causes identity drift.
- **Timeline order matters** (sequential generation): first beat first, CTA beat last.
- **One camera instruction**: "Camera locked, static, no zoom."
- **Small motion beats realism**: "holds eye contact, irregular natural blinks, small nod on the first line, one brief hand gesture, then still, gentle breathing." Big influencer gestures push toward rubber mouth / eye drift. Energy comes from **voice direction**, not body.
- **Voice direction block**: "Tone: casual, medium energy, dry, not announcer." Add "Sound: close phone mic, quiet room tone, no music" — otherwise it may add BGM or narration.
- **Clean-frame as positive**: "Clean picture only: no subtitles, captions, lower-thirds, watermarks." Negatives are ignored; still QC every take.
- **Duration**: 5–8s is markedly more stable than 12–15s; ~2.2 words/s ceiling.
- **Don't pass `aspect_ratio` on I2V** — it stretches. Shoot the still in 9:16 and let AR inherit.
- Expression in the still: neutral / slightly parted lips, not a broad grin (teeth smear).

House video prompt v2 is the default template inside `generate-talking-head/talking_head.py`.

### Voice consistency (open gap)

The voice is synthesized fresh per generation — the image locks the face, not the voice. Generate 2 candidates for shared clips and pick the closest voice match (rms / f0 / spectral centroid via `qc_heads.py`). `xai/grok-imagine-r2v` with preset `voice_id`s is a candidate fix worth an A/B when consistent voices matter.

## 5. Uncanny-tells QC checklist (per take)

Retake if any is conspicuous:

- [ ] Lips drift on P/B/M/F/V; mouth stretches like rubber; teeth uniform/gummy/flicker
- [ ] Pupils drift or gaze lands past the lens; catchlights disagree between eyes
- [ ] Blinks absent, or mechanically periodic
- [ ] Torso frozen while only the mouth moves; or canned nod/sway loop
- [ ] Skin tone, pores, freckles or face shape change across frames (compare frame 0 vs last)
- [ ] Halos at hairline / jaw / collar / hoodie edge
- [ ] Fingers warp when hands enter frame
- [ ] Face and room light direction/color disagree
- [ ] Skin looks smoother in motion than in the still
- [ ] Voice has no breaths / contractions / emphasis; reads as written copy
- [ ] Baked captions, jargon garble, hot audio (standard checks)
