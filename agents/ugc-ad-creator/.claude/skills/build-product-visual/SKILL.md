---
name: Build Product Visual
description: 'Produce the product half of a UGC ad — either from user-supplied assets (screenshots, product photos, screen recordings) or by building a self-contained HTML animation clip that the studio drives frame-by-frame (window.ANIM + window.seek contract). Use in produce-ad-video Stage 4, and in onboarding step 4 to set up the asset library.'
metadata:
  version: "1.0.0"
---

# Build Product Visual

Every ad shows the product for ~5–7s: a split-screen panel (bottom 960px of the frame, 1080×960) and a full-bleed punch-in (1080×1920). This skill produces those visuals in one of two modes. Decide the mode in onboarding step 4 and record it in `/workspace/ads/company.md`.

## Mode A — asset library (user supplies visuals)

1. Ask for screenshots (PNG/JPG, ideally ≥ 1080px wide, light UI is fine — captions flip dark automatically), product photos, and short screen recordings (MP4, ≥ 720p, the money moment within the first 5s).
2. Save them under `/workspace/ads/studio/public/assets/<slug>.<ext>` with descriptive slugs; keep an index in `/workspace/ads/studio/public/assets/INDEX.md` (file, what it shows, best moment / crop notes).
3. Reference them from props:
   - Screenshot: `{"kind":"still","src":"assets/dashboard.png","from":{"scale":1.05,"x":0,"y":-2},"to":{"scale":1.2,"x":-3,"y":2}}` — the Ken Burns drift keeps the shot alive; aim the drift at the UI element the VO mentions.
   - Recording: `{"kind":"video","src":"assets/demo.mp4","trimBefore":45,"playbackRate":1.3,"zoom":1.1,"focusY":0.4}` — `trimBefore` in frames; speed up slow UI.
4. Photos of physical products: `still` with a tighter drift (`scale 1.1 → 1.3`) and `background` matching the photo's edge color.

## Mode B — build an animation clip ad-hoc

When there are no assets (or the product is abstract), build a self-contained HTML clip. Clips live in `/workspace/ads/studio/public/animations/<slug>.html` and follow this contract so Remotion can render them deterministically:

```html
<!doctype html><html><head><meta charset="utf-8">
<style>html,body{margin:0;background:#fff;width:960px;height:540px;overflow:hidden;font-family:Inter,-apple-system,sans-serif}</style>
</head><body>
<div id="stage"></div>
<script>
  // 1) declare the clip
  window.ANIM = { duration: 8, fps: 30, params: {} };
  // optional URL params: ?title=...&items=a|b|c
  const q = new URLSearchParams(location.search);
  ANIM.params.title = q.get('title') || 'Reminder sent';
  // 2) build the DOM once
  // 3) seek(t) must be PURE: set every animated property from t (seconds), never accumulate
  window.seek = function (t) {
    const p = Math.min(1, Math.max(0, t / ANIM.duration));
    // e.g. a card sliding in with an ease-out
    const ease = 1 - Math.pow(1 - Math.min(1, t / 0.6), 3);
    document.getElementById('stage').style.transform = `translateY(${(1 - ease) * 80}px)`;
  };
  seek(0);
</script></body></html>
```

Rules:
- Design size 960×540 (16:9) by default; pass `designW/designH` in the spec if different. Full-bleed uses `fit:'width'` + `Punch` 1.5→1.75 to fill 9:16; split panel uses `fit:'cover'`.
- `seek(t)` sets state from `t` alone (no `requestAnimationFrame`, no CSS transitions, no timers) — Remotion calls it once per frame out of order.
- Use CSS/DOM or canvas; inline everything (no external scripts). Fonts: system stack or a `<link>` to Google Fonts (the loader waits for `document.fonts.ready`).
- Show ONE idea per clip: a notification arriving, a status flipping to done, a list filling in, a before/after wipe, a chat message being typed and sent, a chart climbing. Pick the moment that proves the VO's mechanism sentence.
- Brand it lightly: use the company's primary color (from `company.md` / website) on one accent element; white background by default so the caption dark-mode kicks in.
- Reference: `{"kind":"html","src":"animations/<slug>.html?title=Invoice%20paid","startFrom":0.5,"speed":1.2}`. `startFrom/speed` hit the money moment inside the scene window; don't seek past `ANIM.duration`.
- Test before compositing: `npx remotion still src/index.ts ClassicF1 /tmp/test.png --frame 90 --props='{"splitVisual":{"kind":"html","src":"animations/<slug>.html"},"s2At":1.5,"s3At":4,"s4At":6,"endAt":8}'` and look at the image.

## Reusable clip ideas (build once, parameterize with URL params)

- `notification.html` — phone lock-screen notification (`?title&body&app`)
- `chat-send.html` — message typed into a composer and sent (`?prompt`)
- `status-flip.html` — a row/badge flipping from "Overdue" to "Paid" (`?from&to`)
- `list-fill.html` — items appearing with checkmarks (`?items=a|b|c`)
- `before-after.html` — split wipe between two screenshots (`?before&after` as asset URLs)
- `counter.html` — big number counting up with a label (`?to&label`)

Keep an index of built clips in `/workspace/ads/studio/public/animations/INDEX.md` (file, params, duration, best moment) so `ideate-ads` can plan with them.
