# Meal Cheatsheet

Lookup table for dishes / meals the user eats often. Check this BEFORE doing any web research or asking the user for macros. Free-form grep is fine — match against name, aliases, restaurant, or any line of the entry.

Format per entry:
- `## <dish> — <source>` (source = restaurant name or "home")
- `aliases:` comma-separated nicknames / common ways the user refers to it
- `macros:` `<kcal> · <P>g · <F>g · <C>g` (base portion — no add-ons unless stated)
- `add-ons:` per-modifier deltas, format `<name> <kcal>/<P>/<F>/<C>` (omit if none)
- `recipe:` or `ingredients:` short description of what's in it
- `notes:` anything that affects macros or matters when logging
- `last_verified:` YYYY-MM-DD — when the macros were last sanity-checked

When logging, sum base + chosen add-ons and pass to `log_meal.py`. If the user's variant differs materially from what's recorded, note it in the meal description but don't auto-update this file unless they confirm.

---
