# Presenter Roster

One entry per presenter character. **Same portrait file = same character across all ads** (consistency comes from reusing the exact image with grok-imagine-video-1.5). Presenter slugs are the tracker's `presenter` axis — spelling matters. `ads-tracker-sheet` reads slugs from the first column of the table below.

Start from the library: `presenter-library/LIBRARY.md` + `contact-sheet.jpg` hold 14 ready-made archetypes — copy one to `<slug>-portrait.jpg` and add a row (free). New custom presenter: follow `/workspace/ads/docs/character-realism-guide.md` §3 prompt, generate with `generate-talking-head/portrait.py` (gpt-image-2 default, $0.128; 9:16), eyeball it against `/workspace/ads/refs/persona-reference.jpg`, then add a row here. Include the voice/tone direction and any custom talking-head prompt notes so every ad uses the same voice direction for that character.

| Slug | Portrait | Character | Setting / light | Voice direction (tone, accent, energy) |
|---|---|---|---|---|
<!-- agent-onboarding step 3 fills this table, e.g.
| maya | maya-portrait.jpg | Woman early 30s, hair up messy, grey hoodie, leaning on kitchen counter | Kitchen, overcast window + warm ceiling spill, mug + grocery bag | Warm, dry, medium energy, American |
| theo | theo-portrait.jpg | Man early 20s, curly hair, oversized hoodie | Dorm room, LED strip + warm bounce, posters | Fast, casual, meme-adjacent, American |
-->

## Scratched attempts

<!-- Record archetypes the user rejected so they aren't regenerated without new direction. -->

## Notes

- Portrait frame contract: chest-up, face in upper third, looking into the lens, 9:16.
- Expression in the still: neutral / slightly parted lips — broad grins smear teeth in motion.
- Voice drifts between takes (image locks face, not voice). Generate 2 candidates for shared B clips, pick the closest match with `qc_heads.py`.
