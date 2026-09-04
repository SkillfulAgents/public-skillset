# Persona reference — the Gen Z performer

`persona-reference.jpg` (1152×2048, generated with `openai/gpt-image-2`, quality=high, 9:16) is the benchmark for what a UGC presenter should look like. It out-performed every polished "influencer" portrait in testing: it reads as a real camera-roll selfie, not an AI render. Every new persona is judged against it.

## What makes it work (copy these, not the person)

- **Capture process**: arm's-length front camera, mild wide-angle stretch on the shoulders, slightly off-center with a tilt, deep focus, faint noise/compression.
- **Light**: two motivated practicals — cool blue LED strip along the ceiling + warm room bounce — uneven exposure, no ring-light catchlights.
- **Skin**: visible texture and slight redness, no retouching, lips slightly parted, half-smile caught mid-moment.
- **Room**: lived-in dorm — posters, open closet, cables, a mirrored hoodie logo. Clutter = credibility.
- **Frame contract**: chest-up, face in the upper third, looking into the lens (needed for the split-screen and caption layout).

## Prompt reconstruction (use as the template; swap the person + room)

```
Unedited vertical iPhone front-camera selfie, arm's-length framing, slightly off-center with a small tilt,
mild wide-angle edge distortion, deep phone-camera focus, computational HDR, faint sensor noise and JPEG compression.
A young man in his early twenties with messy dark curly hair, wearing an oversized heather-grey hoodie with creases,
chest-up, face in the upper third, looking into the lens, relaxed half-smile caught mid-moment, lips slightly parted,
natural facial asymmetry. Skin: visible pores, slight redness on the cheeks, under-eye texture, a couple of small blemishes, flyaway hairs.
Light: cool blue LED strip along the ceiling edge mixed with warm room light, uneven exposure, slightly imperfect auto white balance.
Setting: lived-in dorm bedroom — sports posters on the wall, an open closet with hanging shirts, a desk chair, cables — slightly out of focus.
Ordinary camera-roll photo, not a studio portrait, not airbrushed, no beauty filter, not CGI.
```

## Using it as a style reference

`portrait.py --ref /workspace/ads/refs/persona-reference.jpg` passes the image to gpt-image-2's `input_images` alongside a new-person prompt: "Match the photographic style, lighting realism, skin texture and camera feel of the reference exactly, but a completely different person and room: <PERSON>, <ROOM>." Keep the reference for style only — never reuse his face as a company presenter (the personas must be unique to each company).

## Talking-head direction that suited this persona

Fast, casual, meme-adjacent energy in the VOICE ("Tone: fast, casual, dry, talking to a friend"), body motion kept small. 8s quick-hit ads were his best format.
