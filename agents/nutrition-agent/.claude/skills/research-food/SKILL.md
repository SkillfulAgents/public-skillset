---
name: Research Food
description: Research the nutritional content of a specific dish at a specific restaurant — typically before ordering on DoorDash, UberEats, Grubhub, or directly from the restaurant. Use whenever the user names a dish + restaurant ("what's in the X at Y", "I'm about to order the Z from W", "look up nutrition for...") and wants macros before they commit. Finds official nutrition info when published; otherwise builds a defensible estimate from the menu description, listed ingredients, and dish photos. Outputs calories + protein + fat + carbs ready to hand to log-meal.
---

# Research Food

Researches a single dish at a single restaurant and returns a macro estimate (calories, protein, fat, carbs) plus a short rationale.

## How to use

1. **Confirm the inputs** — you need a dish name AND a restaurant name. If either is missing, ask one short question. If the user gave a location hint (city, neighborhood, "the one near me"), keep it for disambiguation.

2. **Check the cheatsheet first.** Grep `/workspace/nutrition/cheatsheet.md` for the dish, restaurant, or aliases. If there's a hit, report from there — skip the web research entirely. Note "from cheatsheet (last verified: <date>)" as the source.

3. **Find the canonical source.** Try in this order, stop as soon as you have what you need:
   - **WebSearch** for `"<restaurant> <dish> nutrition"` and `"<restaurant> nutrition facts"`. Chains (Chipotle, Sweetgreen, Panera, Cava, Shake Shack, Chick-fil-A, etc.) almost always publish official numbers — use those verbatim and you're done.
   - **WebSearch** for the restaurant's DoorDash / UberEats / Grubhub listing for that dish. Get the URL.
   - If WebSearch surfaces the menu description directly in snippets, you may not need the browser. Otherwise open the browser.

4. **Open the menu page** (only if needed):
   - `browser_open(<url>)` — DoorDash/UberEats item pages show description, ingredients/modifiers, and a photo.
   - Delegate to the `web-browser` agent with a prompt like: "Extract the full item description, any listed ingredients/modifiers, portion/size info, price, and describe the dish photo (what's visible — proteins, sauces, sides, approximate portion). Return as plain text." Close the browser when done with `browser_close()`.

5. **Estimate macros.**
   - If official nutrition was found → use it directly, cite the source.
   - Otherwise, decompose the dish into components (protein, carb base, fats/oils, sauces, toppings, sides). Estimate each from standard reference portions, then sum. Visible portion size from the photo matters — a "bowl" at Cava is ~600–800 kcal, a burrito at Chipotle is ~900–1300 kcal, etc. Be honest about uncertainty: sauces, oils, and cheese are the usual silent calorie bombs.
   - Round to sensible numbers (calories to nearest 10, macros to nearest 1g).

6. **Save to cheatsheet.** Write the result to `/workspace/nutrition/cheatsheet.md` so the work isn't repeated next time. Follow the format used by existing entries — `## <Dish> — <Restaurant>` heading, `aliases:`, `macros:`, `add-ons:` (if any modifiers were priced/listed), `ingredients:` or `recipe:`, `notes:`, `last_verified:` today's date. Append to the end of the file. If an entry for this dish + restaurant already exists, **update it in place** (bump `last_verified`, adjust macros if they differ materially) instead of duplicating.
   - Skip this step ONLY if the dish was a true one-off the user is unlikely to repeat (rare).

7. **Report back** in this shape:
   ```
   <Dish> @ <Restaurant>
   ~<kcal> kcal · <P>g protein · <F>g fat · <C>g carbs
   Source: <official | estimated from DoorDash listing + photo | etc.>
   Notes: <1–2 lines on key assumptions — portion size, sauces included, modifiers>
   ```
   Briefly mention you've saved it to the cheatsheet (one short line).

8. **Offer to log it.** End with "Want me to log this?" — if yes, hand the numbers + a short description to the `log-meal` skill.

## Notes
- Prefer official chain nutrition pages over third-party aggregators (MyFitnessPal user entries, Nutritionix crowd data) — they're often wrong by 30%+.
- If the dish has size variants (regular vs large, 6" vs 12"), confirm which one before estimating.
- If the user adds modifiers ("extra guac", "no rice", "double protein"), adjust the estimate and call out the delta.
- Don't auto-log. The user explicitly opts in.
- Don't burn time browsing if WebSearch already produced the answer.
