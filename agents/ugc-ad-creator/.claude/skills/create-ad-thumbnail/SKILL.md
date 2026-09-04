---
name: Create Ad Thumbnail
description: 'Create a reusable 1080x1920 JPG thumbnail from a produced ad, selecting a strong split-screen frame and adding a concise black-or-white seam headline banner. Use after an ad ships when the user wants a cover image / feed still.'
metadata:
  version: "1.1.0"
---

# Create Ad Thumbnail

One thumbnail per produced video. It must communicate the ad's promise even when the video is paused in a feed.

## Frame selection

1. Use a mastered video as the source.
2. Inspect frames around the split-screen reveal, not only the first frame. Make a contact sheet when timing is unknown:
   ```bash
   ffmpeg -i /workspace/ads/studio/out/<ad-id>-nomusic-master.mp4 \
     -vf "fps=2,scale=270:-1,tile=4x3:padding=4:margin=4" -frames:v 1 /tmp/<ad-id>-samples.jpg
   ```
3. Prefer a stable frame after the transition has finished. Avoid wipes, motion blur, frozen UI, and frames where the caption is a mid-sentence fragment.
4. Keep both halves legible: presenter with a natural, inviting expression (an open hand or gesture is a plus); product half showing recognizable UI or a meaningful state.
5. Choose the timestamp manually after inspection. Default seam is `y=960`; adjust `--seam-y` for other splits.

## Banner treatment

- Banner sits over the split seam, centered. Short standalone promise, 3–8 words (`Invoices that chase themselves`, `How I set up an AI coworker`). Never a random caption fragment; it must make sense without audio.
- `--style auto|black|white` — auto picks a high-contrast treatment at random; force one for consistency across a batch.

## Usage

```bash
python /workspace/.claude/skills/create-ad-thumbnail/scripts/create_thumbnail.py \
  --video /workspace/ads/studio/out/<ad-id>-nomusic-master.mp4 \
  --time 4.4 \
  --headline "Invoices that chase themselves" \
  --output /workspace/ads/studio/out/thumbnails/<ad-id>-thumbnail.jpg
```

Optional: `--seam-y 960` `--banner-height 120` `--margin-x 70` `--font-size 54`. Requires FFmpeg; writes a native 1080×1920 JPG. Does not alter the source video or the ledger.
