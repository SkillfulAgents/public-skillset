---
name: Ideate Ads
description: 'Turn a positioning argument, feature, or use case (+ context) into a batch of production-ready UGC ad concepts for rapid experimentation — a test matrix across hooks, presenters, and flows, with full scripts, visual pairings, and cost estimates. Use at the START of any ad request ("make a video about X", "let''s test Y") before produce-ad-video. Also use to spin new variants off an existing ad''s results.'
metadata:
  version: "2.0.0"
---

# Ideate Ads — from argument to experiment batch

Input: a positioning argument / feature / use case + whatever context the user gives (audience, angle, references).
Output: `/workspace/ads/campaigns/<slug>/IDEAS.md` — a concept matrix + full scripts, ready to feed `produce-ad-video` one ad-id at a time.

## Process

1. **Gather context**: read `/workspace/ads/company.md` (product, ICP, approved proof points, voice), `/workspace/ads/arguments.json` (which argument key this batch targets — the tracker's Arguments tab shows which have zero ads), `/workspace/ads/ADS.md` (what's been tried, standing learnings), `/workspace/ads/assets/presenters.md` (roster), and the visual inventory (`/workspace/ads/studio/public/assets/` user-supplied screenshots/videos, `/workspace/ads/studio/public/animations/` built clips). If the core promise is unclear ("what does the viewer get?"), ask ONE clarifying question, not five.
2. **Angle expansion**: write the argument as 3–5 distinct *viewer promises* (e.g. "invoice chasing" → "never write a reminder email again", "get paid two weeks sooner", "your books close themselves"). Each promise is a testable positioning, not a phrasing tweak. If a promise is a genuinely new argument, add it to `arguments.json` (and the sheet's Arguments tab if the tracker exists).
3. **Build the matrix**: pick test cells across the axes below. **Default starter batch = ONE anchor ad** when the user is new (onboarding step 5 — produce one, iterate, then widen); otherwise 3–4 variants that differ on ONE axis at a time from the anchor. Go wider only if asked.
4. **Script every selected cell** (production-ready, per `produce-ad-video` Stage 1 and `/workspace/ads/docs/vo-house-rules.md`): hook title (≤2 lines, sentence case), VO clip A (~7s) + clip B (~7s) or a single ~8–10s clip for Quick hits, emphasis words, visuals per scene (which asset / which clip, startFrom/speed or Ken Burns), overlay plan, CTA. Respect: ~2.2 words/s, integer durations, one connective per clip, brand named once as the doer, no jargon the speech model garbles, "<brand> dot <tld>".
5. **Cost the batch**: heads $0.08/s (≈$1.12/ad for 2×7s, ≈$0.56 if clip B is shared, ≈$0.64 for an 8s quick hit), portraits $0.128 per NEW presenter, retake allowance ~30%. Call out reuse savings explicitly.
6. **Write IDEAS.md** (template below), show the user the matrix + scripts, get their pick(s), then run `produce-ad-video` per approved ad-id.

## Experiment axes

**Hooks** — codes and templates in `/workspace/ads/hooks/HOOKS.md` (20 codes). Starter set for a new company: hpain, hclaim, hcuriosity, hnumber, hpov, hcontra.

**Presenters** — roster in `presenters.md`. Vary demographics / setting / energy to test who converts. New presenter = new portrait + roster row.

**Flows** — `/workspace/ads/hooks/FRAMEWORKS.md` (F1 Classic, F2 Demo-first, F3 Rant, F4 Skit, F5 Fail-then-fix, Q Quick hit). `ClassicF1` and `QuickHit` exist as comps; others are comp variations built at production time.

**Spines** — 5-part DR, PAS, BAB, testimonial arc, curiosity loop, tutorial, reply, quick hit (FRAMEWORKS.md).

**Other testable axes**: CTA phrasing, music (hype / house / none — already dual-rendered), length (8s vs 13s), visual mode (screenshot vs animation vs screen recording), emphasis density.

## Naming & tracking

- ad-id: `<campaign-slug>-<hook>-<flow>-<presenter>` e.g. `invoices-hpain-f1-maya`; variants suffix `-v2`.
- Every produced variant gets its own `ADS.md` entry linking back to the campaign's IDEAS.md.
- After results come in, record which cell won in IDEAS.md AND ADS.md — the next batch iterates on the winner's axis.

## IDEAS.md template

```markdown
# Campaign: <argument / use case> (<date>)
Argument key: <family-argument>
Context: <user's context, audience, goal>
Promises: 1) … 2) … 3) …
Visuals available: <asset or clip — why it fits, params>

## Test matrix
| ad-id | hook | flow | presenter | promise | status |
|---|---|---|---|---|---|

## Scripts
### <ad-id>
- Hook title: "…" / "…"
- VO A (7s, ~15w): "…" | VO B (7s, ~15w): "…" (shared with: <ad-ids>)
- Emphasis: word, word | Visuals: split = <spec>, full = <spec> | Overlays: <plan> | CTA: "…"

## Batch cost: $X.XX  (savings: shared B-clips across <ids>)
## Results & next iteration
- <date>: <which cells ran, verdicts, winner axis, next batch idea>
```
