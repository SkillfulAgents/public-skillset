---
category: Marketing
icon: clapperboard
tags:
  - Video Ads
  - UGC
  - TikTok
  - Instagram Reels
  - Creative Testing
  - AI Video
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: googlesheets
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---

# UGC Ad Creator

> Test twenty ad angles for the price of one coffee, then scale the ones that convert into a campaign of custom variants.

## What it does

UGC Ad Creator turns a message you want to test into a finished 8–15s vertical ad: a hyper-real AI presenter talking to camera (a recurring character from a 14-archetype library or one made for you), your product on screen (your screenshots and recordings, or small animations it builds), word-aligned pop captions, UGC sound design and a mastered mix — delivered as no-music and music variants.

Onboarding reads your website to write the company brief, ICP and positioning arguments, lets you pick presenters from the library, sets up product visuals, and produces your first ad with you. From then on every ad is an experiment: filed under one argument, one hook code, one presenter and one flow, logged in a ledger, and iterated from the time-coded comments you leave on the video. Winners become batches of variants at roughly $1–2 of generation cost each.

Optionally it uploads final masters to Google Drive or Dropbox and maintains a Google Sheets tracker (Family → Argument → Video, with hook / presenter / music slices) — but only when you explicitly say "push".

## What you'll need

- **Google Drive + Google Sheets:** Optional, for the masters folder and the performance tracker. Dropbox can replace Drive for storage (connected during onboarding; that path is less exercised than Drive).
- **API keys:** None. Portraits, talking heads and audio run on the platform's built-in media generation (gpt-image-2, grok-imagine-video-1.5, stable-audio / lyria). Optional `ELEVEN_LABS_API_KEY` for ElevenLabs sound generation.
- **Other:** A public website the agent can read. Node 18+ and FFmpeg (standard in the container). Generation costs are quoted and confirmed before every run.

## Getting started

1. Import the template into Gamut; `agent-onboarding` starts automatically.
2. Give it your website — confirm the brief, ICP and 4–8 positioning arguments it derives.
3. Pick presenters from the contact sheet of 14 archetypes, or describe your own.
4. Upload product screenshots / recordings, or let it build animations as it goes.
5. Choose the first angle, pick one of its hook scripts, and iterate the resulting video with timeline comments.
6. Optionally connect Drive/Dropbox and Sheets for the tracker.

## Example prompts

- Read our website and draft the positioning arguments we should test
- Make four hook variants of the invoice-chasing ad with a new presenter
- Push the two winning ads to the tracker and plan next week's batch

## What's inside

- `CLAUDE.md` — operating instructions: workflow, locked house style, cost and push rules.
- `.claude/skills/agent-onboarding/` — six-step first-run setup.
- `.claude/skills/ideate-ads/` — argument → hooks × flows × presenters matrix with production-ready scripts.
- `.claude/skills/produce-ad-video/` — end-to-end production pipeline and the whisper caption aligner.
- `.claude/skills/generate-talking-head/` — gpt-image-2 portraits, grok-imagine talking heads, QC, library generator.
- `.claude/skills/build-product-visual/` — asset-library mode or self-contained HTML animation clips.
- `.claude/skills/sound-design/` — UGC SFX/music planning, generation fallbacks, -14 LUFS mastering.
- `.claude/skills/create-ad-thumbnail/` — 1080×1920 cover stills.
- `.claude/skills/ads-tracker-sheet/` — Google Sheets tracker build/push with Drive or Dropbox upload.
- `ads/studio/` — Remotion project (ClassicF1 and QuickHit flows, captions, overlays, sound, `brand.json`, sample clip).
- `ads/sounds/` — UGC sound library with measured sync offsets.
- `ads/assets/presenter-library/` — 14 ready-made presenter portraits, contact sheet and voice directions.
- `ads/hooks/` — hook database and script frameworks. `ads/docs/` — character realism guide, VO house rules, audio references.
- `ads/refs/` — the benchmark persona portrait and prompt. `ads/company.md`, `ads/arguments.json`, `ads/ADS.md`, `ads/tracker.json.example` — templates onboarding fills.
- `.env.example` — the one optional key.

## Notes

The agent spends money on generation (≈ $0.13 per portrait, $0.08 per second of talking head) and always quotes the cost first. It never pushes to the tracker or uploads masters without an explicit instruction. AI presenters are meant for paid social creative and must not be framed as real customer testimonials; the hook database carries the guardrails.
