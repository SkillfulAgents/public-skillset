# VO House Rules — writing lines a human can say

Synthesized from a four-model critique of ~40 produced UGC ad scripts. Goal: **make the VO read human out loud without losing the hook.**

## The diagnosis

Ad scripts drift into *caption grammar* instead of *mouth grammar*: the punch that works in on-screen titles gets pushed into the spoken line, where it becomes unperformable and the speech model delivers it flat. Six tics, in order of damage:

1. **Verbless fragment stacks.** "No keys, no setup." / "New email? On it. New order? Handled." A fragment has no verb to hang intonation on, so every word lands equally flat — the definition of robotic delivery.
2. **Metronomic parallel clauses.** Two same-length sentences, cloned syntax ("X lets you A. Y lets you B."). Isochronous phrasing is exactly what TTS prosody sounds like. Human speech is ragged: long clause, short kicker.
3. **Zero connective tissue.** No *so / because / when / then / which means*. Logic by juxtaposition performs as claim-claim-claim.
4. **Unresolved pronouns.** "This / Mine / It" carrying the product as the subject before the product is named.
5. **Deleted mechanism.** Compression cut the *how*. One physical "how" per ad is what makes it credible.
6. **Category labels as dialogue.** Positioning-deck nouns ("proactive AI", "agentic workforce", "end-to-end platform") nobody would say to the person next to them.

The winners in the corpus were already the most spoken-register lines: contractions, discourse openers ("Lemme show you…"), finite verbs, brand named as the doer, chronological logic. Punchy and human coexist.

## The rules

Budget: 7s A ≈ 15 words, 7–8s B ≈ 15–17 words, pair ≤ ~33 words / 15s.

1. **Finite Verb Rule.** Every sentence after the hook gets a subject and a conjugated verb. Fragments are legal ONLY as the first ~4 words of clip A ("Twelve warm leads, zero ad spend." stays).
2. **Say the Glue — exactly one connective per clip.** One of *so / when / because / now / then / which means*. Zero = robot; three = mush.
3. **Pay for context by cutting a boast, not adding a sentence.** Three claims → one becomes the mechanism clause, one dies (or moves to captions).
4. **Resolve the pronoun — name the brand once per ad as the doer.** "My <Brand> agent watches X…" not "Mine…". Max two "Mine"s per campaign, zero in an anchor.
5. **Break cloned syntax.** Long clause + short kicker instead of billboard parallelism.
6. **Mechanism lives in a subordinate clause, in physical verbs.** hears, rebuilds, pings, watches, clicks, sends. One "how" per ad; never a category label.
7. **Lists: two items + "and" + a verb** — unless it's an "even"-escalation ("LinkedIn, Amazon, even my bank").
8. **CAPS and staccato stay in the caption layer.** Title card and word-pop captions carry the punch; the mouth carries a complete sentence. (Production rule too: CAPS in dialogue triggers baked-in on-screen text in the video model.)
9. **B must resolve A.** Read A+B audio-only: one person finishing one thought. Open B with a connective when it's shared across variants. CTA ≤ 6 words.
10. **The coworker test.** Say the line to a person next to you without putting on a voice. If it fails, rewrite. Clone the anecdote shape: *"A better model dropped last night. My agents were using it by breakfast."*

## Before / after

| Before | After |
|---|---|
| "New email? On it. New order? Handled. No waiting, no asking. Build yours at <brand> dot com." | "So nothing sits there waiting for me to check it. Build yours at <brand> dot com." |
| "Their use case, their objections — fixed and sent in minutes." | "It hears their objections on the call and fixes the slides in minutes." |
| "Cloud-only AI can't touch your files. Mine runs on MY machine. Private, with my real browser." | "Cloud AI can't even see your files. Mine runs on my own machine, so everything stays private." |
| "It pings me, I reply, we win the customer. A virtual EMPLOYEE, quietly growing my business." | "When it finds one, it pings me, I reply, and we win them." |

## Do NOT sand these off

- First-second hooks and formats — "POV:", "Stop chasing leads.", "Twelve warm leads, zero ad spend." The robot lives in sentences 2–4, not sentence 1.
- Time-stamped anecdotes — "dropped last night… by breakfast", "2am, a ticket comes in". Clone this shape.
- Concrete objects and counts — one dropdown, twelve leads, fifty thousand. Specificity is not the robotic part; abstraction is.
- The Other-vs-Mine contrast frame — keep the frame, break the cloned syntax.
- Imperative CTAs — Build / Steal / Get yours at <brand> dot com. Vary the verb, keep the imperative.
- Contractions & swagger — "Lemme show you…", "You are not gonna believe…" (caps to captions).
- Stance markers ("apparently", "honestly", "no joke"): allowed, max one per ad, never in the hook.

## Speech-model safety

- Avoid jargon the model garbles (test any technical term with a transcription pass; substitute plain words: "webhook" → "alert").
- Spell out the URL: "<brand> dot com". Keep product/model names to ones you've tested.
- Sentence case only in the dialogue string.
