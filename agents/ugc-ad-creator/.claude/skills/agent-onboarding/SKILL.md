---
name: agent-onboarding
description: 'First-run setup for UGC Ad Creator. Learns the company from its website, writes the company/ICP brief and positioning arguments, picks hyper-real UGC personas from a 14-archetype library or generates custom ones, sets up the product-visual mode, produces and iterates the first ad with the user, and optionally wires up cloud storage + a tracking sheet. Runs automatically on import; re-run anytime to reconfigure or add personas.'
---

# Onboard UGC Ad Creator

You are setting this agent up for a new company. Work through the six steps **in order** — each has an output file and an exit gate. Be conversational and fast: one focused question at a time, sensible defaults everywhere, and **confirm cost before any generation** (portraits, talking heads, music). Save state after every step so a dropped session can resume.

Files you will write:
- `/workspace/ads/company.md` — company, product, ICP, positioning arguments, voice/CTA
- `/workspace/ads/arguments.json` — machine copy of the positioning arguments
- `/workspace/ads/studio/brand.json` — CTA card text + logo files
- `/workspace/ads/assets/presenters.md` + `/workspace/ads/assets/<slug>-portrait.jpg` — the persona roster (picked from `presenter-library/` or generated)
- `/workspace/ads/studio/public/assets/` (+ INDEX.md) or `/workspace/ads/studio/public/animations/` — product visuals
- `/workspace/ads/campaigns/<slug>/IDEAS.md`, `/workspace/ads/ADS.md` — the first ad
- `/workspace/ads/tracker.json` — storage + sheet IDs (optional step 6)
- `/workspace/CLAUDE.md` `## Your context` — company one-liner, chosen visual mode, presenter default, tracker status

## Step 1 — Introduce what you do

In 3–4 sentences, your own words:

> I make UGC-style video ads for you with AI — short vertical TikTok/Reels spots with a realistic presenter talking to camera, your product on screen, word-pop captions and proper sound design. Because every ad costs a couple of dollars and minutes instead of a shoot, we can run rapid messaging and positioning experiments (which hook, which angle, which presenter actually converts) and then scale the winners into big custom campaigns. Setup takes ~20 minutes: I'll learn your company from your website, pick presenter personas with you (there's a ready-made library, or I'll make custom ones), sort out product visuals, make your first ad together, and optionally set up a tracking sheet.

Then go straight to step 2.

## Step 2 — Learn the company → `company.md` + `arguments.json`

Ask: **"What's your website? I'll read it and tell you what I understood."**

- Fetch the homepage and 1–3 obvious subpages (/pricing, /about, /customers, /product). Extract: company name, what the product does (concrete capabilities, physical verbs), who it's for, pricing/trial, proof points actually stated on the site, brand colors/logo, competitors named or implied.
- Present your read in a tight summary: *company · product · who buys · the pain · the mechanism · proof points I found*. Ask: "What did I get wrong or miss? Who is the buyer, specifically (role + company type)? What's the moment they feel the pain?" Iterate until confirmed.
- Ask what claims you may use (numbers, customer names) — only approved facts go in scripts. Ask how the brand should be spoken ("<brand> dot com") and what the CTA card should say (default: "Try for free / www.<domain>").
- Derive 4–8 **positioning arguments** — testable viewer promises, grouped into families (outcome / feature / audience / usecase). Show them as a table and confirm.

Write `company.md` (fill every section of the template), `arguments.json` (replace the example entries), and `studio/brand.json` (`companyName`, `ctaText`). If the site has an SVG/PNG logo, download a white and a dark variant to `studio/public/brand/` and set `logoWhite` / `logoDark`; otherwise leave them `null` (the outro then shows only the CTA card).

**Exit gate:** user confirms the brief and the arguments table.

## Step 3 — Create the personas → portraits + `presenters.md`

Explain in one sentence: presenters are AI-generated people who become recurring characters; what works is hyper-real, phone-shot, imperfect — not polished.

1. **Show the library first.** Deliver `/workspace/ads/assets/presenter-library/contact-sheet.jpg` and summarize the 14 archetypes from `presenter-library/LIBRARY.md` that best fit this ICP (name 3–5 with a one-line "reads as"). Ask: **"Would any of these work for your audience? Pick as many as you like — or tell me who you'd rather have and I'll make them."** Adopting a library portrait costs nothing.
2. **Adopt picks**: copy each chosen `presenter-library/<slug>.jpg` to `/workspace/ads/assets/<new-slug>-portrait.jpg` (let the user rename, e.g. a first name), and add the roster row (slug, portrait file, character, setting/light, voice direction from LIBRARY.md — adjust tone/accent to the company's market).
3. **Custom personas** (if asked, or to fill a gap): propose the archetype in one line (age/look, lived-in setting with motivated light, voice direction), using `/workspace/ads/docs/character-realism-guide.md` §3 for the prompt and `refs/persona-reference.md` as the quality bar. **Quote the cost** (gpt-image-2 $0.128 per portrait; ~$0.26 for two candidates) and get an OK. Generate with `generate-talking-head/portrait.py --ref /workspace/ads/refs/persona-reference.jpg`. Inspect against the reference yourself (wide-angle stretch? mixed practical light? pores/redness? clutter? neutral lips?) before showing it. Redo with a rewritten prompt, not a blind retry. Add keepers to the roster and to `presenter-library/` so the library grows; record rejects under "Scratched attempts".
4. Ask which presenter should be the default for the first ad.

**Exit gate:** at least one approved presenter in the roster, a default chosen.

## Step 4 — Product visuals → asset library or ad-hoc animations

Ask: **"Do you have visual assets I can use — product screenshots, product photos, screen recordings? Or should I build simple product animations as we go?"**

- **Assets:** request the files (screenshots ≥1080px wide, recordings ≥720p with the key moment in the first 5s), save them to `studio/public/assets/` with descriptive slugs, fill `assets/INDEX.md` with what each shows and its best moment. Mode = `assets`.
- **Animations:** explain you'll build small self-contained clips per ad (a notification arriving, a status flipping, a message sent…), in the brand color, using the `build-product-visual` skill. Show the sample `status-flip.html` as an example of the style. Mode = `animations`.
- Both is fine — record the choice (and the brand primary color) in `company.md`.

**Exit gate:** visual mode recorded; assets indexed if provided.

## Step 5 — The first ad → one video the user likes

Ask: **"What's the first message or angle you want to test?"** (offer 2–3 from the arguments table if they hesitate).

1. Run `ideate-ads` for that argument in **single-anchor mode**: 3–5 hook variants with full scripts (hook title + VO A + VO B, ~30 words total, per `docs/vo-house-rules.md`), one flow recommendation, one presenter recommendation, visual plan, cost per ad. Present the options and ask which ONE to produce as the trial run. Just one — you'll iterate on it before widening.
2. Run `produce-ad-video` end-to-end (confirm the talking-head cost first, ≈ $1.20 + retakes; sound library is already in place). QC everything. Deliver BOTH masters (no-music and music) with `deliver_file`.
3. **Teach the feedback loop** when you deliver: "Open the video in the tray on the right — you can click on the timeline to leave a comment at a specific moment (e.g. 'cut this faster', 'wrong word here', 'zoom on the button'). Those comments come straight to me, and time-coded notes are the fastest way for me to fix exactly the right thing." Also ask which of the two variants they prefer.
4. Iterate: apply comments (re-script a clip, re-time a cut, swap a visual, adjust sound), re-render, re-deliver. Record every change and its reason in `ADS.md`. Continue until the user says the video is good.
5. Ask whether to make a thumbnail (`create-ad-thumbnail`) — optional.

**Exit gate:** one video the user likes, post-iterations, logged in `ADS.md` with learnings.

## Step 6 — Tracking (optional) → `tracker.json`

Ask: **"Want me to put final masters in a Google Drive or Dropbox folder and set up a tracking sheet (ad × hook × presenter × spend/results)? It's how we'll learn which experiments win."**

If yes:
1. Storage — ask Drive or Dropbox. Request the connected account (`googledrive` or `dropbox`) with `request_connected_account`. Create the root folder "<Company> Ads" and store its ID/path.
2. Sheet — request the `googlesheets` connected account. Run `ads-tracker-sheet/build_sheet.py --title "<Company> Ads Tracker"` (Arguments tab seeds from `arguments.json`). Store `spreadsheet_id`.
3. Write `/workspace/ads/tracker.json` (see `tracker.json.example`), then push the approved first ad with `push_ad.py` — this one time with the user's OK, so they see the flow. Send them the sheet + folder links.
4. Explain the rule: from now on nothing is pushed unless they say "push it"; they own Status → Published and all metrics.

If no: note "tracker: not set up" in CLAUDE.md and move on.

## Wrap up

Append to `/workspace/CLAUDE.md` under `## Your context`: company one-liner + website, visual mode, presenter roster slugs (and the default), CTA phrasing, tracker status. Summarize what exists now (brief, N personas, visual mode, first ad, tracker) and how to continue: "give me the next angle to test", "make 4 hook variants of <ad-id>", "new persona: <archetype>", "push <ad-id>". Remind them they can re-run `agent-onboarding` anytime to add personas or reconfigure.
