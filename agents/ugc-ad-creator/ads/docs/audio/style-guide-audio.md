# Style Guide — Audio Rules (extract)

> Source: `/workspace/vox-pipeline/research/vox-style-guide.md` §8, §10, §11 (verbatim extract of the audio-relevant parts). The full style guide also covers visual design, motion, narrative and captions; only audio-relevant rules are reproduced here.

## 8. Audio Rules

### 8.1 Voiceover

- Delivery: conversational-curious. Directives for TTS/VO talent:
  medium-low intensity, "explaining to a friend at a kitchen table";
  upward energy on questions; slow to 85% speed + slight pitch-down on the
  Turn sentence; smile-tone on the kicker.
- Pace 155–175 wpm with real pauses: 0.4–0.6s after the hook, 0.5–0.8s
  before "But here's the thing," 0.3s before the kicker.
- Emphasis pattern: ONE stressed word per sentence, and that word is the one
  that gets the highlight/kinetic treatment on screen (audio and visual
  emphasis must point at the same word).
- Processing: high-pass 80Hz, de-ess, compression ≈ 3:1 ratio;
  VO peaks -6dBFS; overall mix loudness target -14 LUFS integrated
  (platform standard).

### 8.2 Music bed

- Style: minimal, rhythmic, instrumental — muted piano/mallets/plucks/soft
  synth pulse + low percussion. Must not contain lead melodies in the
  vocal frequency band (300Hz–3kHz busy = competes with VO — Vox rule).
  Think "curious ticking," not epic trailer, not lo-fi sleepy.
- Tempo 85–110 BPM. Cut scenes on the beat where possible.
- Music is an attention-structuring device (Fong method): the bed CHANGES at
  the Turn — either a track switch, a key/energy lift, or a stripped-back
  drop to sparse percussion. In 60s videos, also change/lift at the mid
  re-hook (track changes roughly every 20s in Vox longform; scale that to
  1 change per short, 2 max).
- End the music ON the resolution sentence (hard out or 12-frame fade), leave
  the kicker nearly dry (VO + room tone + one SFX) — an ending cue tells the
  brain "this is the takeaway."
- Duck music -12dB under VO (sidechain, 200ms attack / 600ms release);
  music alone (hook stings, transitions) at -20 to -16 LUFS momentary.

### 8.3 SFX punctuation (every visual event gets a sound)

| Event | SFX | Level vs VO | Timing |
|---|---|---|---|
| Text/headline entrance | Soft whoosh (airy, 200–400ms) | -14dB | Starts 2 frames before text lands |
| Highlight/underline sweep | Marker squeak (150–250ms) | -12dB | Exactly with sweep |
| Photo cutout pop | Paper slap / cardboard tap | -10dB | On the overshoot frame |
| Paper slide transition | Paper slide/shuffle | -12dB | With motion |
| Chart draw | Subtle rising tick-run or pencil scribble | -16dB | With draw duration |
| Count-up stat | Soft tick per ~4 frames, final thock | -14dB | Ends on final value |
| Map zoom | Low airy whoosh + soft "arrival" thump | -14dB | Thump on settle |
| Whip pan | Sharp whoosh (100–150ms) | -8dB | Across the 6 frames |
| The Turn | Record-scratch-adjacent but subtle: bass drop-out + single soft impact | -10dB | On "But here's the thing" |
| Kicker | One gentle low piano note or page-turn | -14dB | With final line |

Rules: max 1 SFX per 30 frames on average; SFX are dry and papery (no sci-fi,
no risers >1s, no booms); reuse the same 8–12 sound family across all videos
(sonic brand).

---

## Ship-gate checklist (audio items from §10 DO / DON'T)

DO:
- [ ] Music ducked -12dB under VO; ends on the resolution; kicker nearly dry.
- [ ] SFX on every entrance/sweep/pop from the house sound family.
- [ ] Mix -14 LUFS integrated; VO peaks -6dBFS.
- [ ] Muted playthrough test: full argument survives with sound off.

DON'T:
- [ ] No epic-trailer or vocal-heavy music; no SFX risers > 1s.

---

## Machine-readable audio tokens (from §11)

```json
{
  "audio": {
    "mixLUFS": -14, "voPeakDBFS": -6,
    "duckMusicDb": -12, "duckAttackMs": 200, "duckReleaseMs": 600,
    "musicBpm": [85, 110],
    "sfx": { "textWhooshDb": -14, "highlightDb": -12, "popDb": -10, "whipDb": -8 }
  }
}
```
