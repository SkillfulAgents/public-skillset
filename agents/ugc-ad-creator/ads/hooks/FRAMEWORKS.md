# Script Frameworks

Structure every script with one spine below, then skin it with a flow. Prefer 10–15s over 8s (sub-9s reach penalty); 13–14s totals leave retake headroom (grok duration is an integer ≤15s).

Budget: ~2.2 words/s. Clip A (7s) ≈ 15 words. Clip B (7s) ≈ 15 words. Whole ad ≤ ~33 spoken words.

## Spines (with 8–15s timing maps)

| Spine | Beats | 13s map | Best for |
|---|---|---|---|
| **5-part DR** | Hook → Problem → Mechanism → Proof → CTA | 0–1 hook · 1–4 problem · 4–8 mechanism · 8–11 proof · 11–13 CTA | Anchor ads, hpain/hclaim |
| **PAS** | Problem → Agitate → Solve | 0–3 problem · 3–6 agitate · 6–13 solve+CTA | hpain, hwarning |
| **BAB** | Before → After → Bridge | 0–4 before · 4–8 after · 8–13 bridge (how) + CTA | hbefore, hpov |
| **Testimonial arc** | Skepticism → Try → Moment → Result → CTA | 0–2 skeptic · 2–5 try · 5–9 moment · 9–13 result+CTA | hconfession, hstory |
| **Curiosity loop** | Open loop → Tease → Reveal → CTA | 0–1 open · 1–6 tease (visual) · 6–11 reveal · 11–13 CTA | hcuriosity, hsecret |
| **Tutorial** | Promise → Step 1 → Step 2 → Step 3 → CTA | 0–2 promise · 2–10 steps (StepPop overlays) · 10–13 CTA | htut |
| **Reply** | Comment → Direct answer → Show → CTA | 0–1 card · 1–5 answer · 5–10 show · 10–13 CTA | hreply |
| **Quick hit** | Hook → One mechanism → CTA | 0–1.5 hook · 1.5–6 mechanism · 6–8 CTA | hgenz, 8–10s |

## Flows (shot structures → studio compositions)

| Code | Flow | Shape | Comp |
|---|---|---|---|
| F1 | Classic | full TH + hook title → split (TH top / product panel slides up) → full-bleed product punch-in → TH + lockup + CTA | `ClassicF1` |
| F2 | Demo-first | full-bleed product with hook title (VO over) → TH reveal → split → TH CTA | ClassicF1 with scene props reordered (new comp when needed) |
| F3 | Rant | TH throughout, one quick product insert, titles carry the visuals | QuickHit with short S2/S3 |
| F4 | Skit | TH acts the pain (beat) → hard cut "then I found this" → product → CTA | ClassicF1, comment-card or hook title |
| F5 | Fail-then-fix | "other tool fails" visual → TH → product → CTA | new comp variant |
| Q | Quick hit | one head clip, 8–11s, fast cuts | `QuickHit` |

Native format skins: hreply → CommentCard on frame 1; htut → StepPop pills over light UI; hdemo → F2.

## Retention rules

- **s0–1**: face already talking + title lands by 0.3s + first words are the promise.
- **s2–4**: first visual change (split panel) — never let the same shot run > 4s.
- **s5–7 re-hook**: a second visual mode (full-bleed punch-in) + the mechanism sentence. Most drop-off is here; give the eye something new AND finish a thought.
- **Loop closure**: the last spoken line should answer the title. If the title says "Stop chasing invoices", the closer says what happens instead.
- Muted playthrough must still work — captions carry the argument.

## CTA craft

- ≤ 6 words spoken; imperative verb; brand spoken as "<brand> dot <tld>" (speech models garble ".com" less than URLs with paths).
- CTA card copy is brand-level (`studio/brand.json`), two lines: action + URL.
- Music ducks out at the CTA so the closer lands dry.
- Don't park a qualification before the CTA — that's A-clip material.

## Shared-B economics

Clip B (payoff + CTA) can be shared across hook variants of the same argument when it opens with a connective ("So…", "And when…") so any A+B reads as one thought. Halves head cost per variant. QC voice match across A and B (see generate-talking-head).
