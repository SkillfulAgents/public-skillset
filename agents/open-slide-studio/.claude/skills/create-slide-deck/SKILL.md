---
name: Create Slide Deck
description: Create, draft, or generate a new presentation in the shared OpenSlide studio at /workspace/artifacts/open-slide-studio. Use for requests such as “make a deck,” “create slides,” “draft a presentation,” or “new deck.”
metadata:
  version: "1.0.0"
---

# Create Slide Deck

Create every new deck in `/workspace/artifacts/open-slide-studio` with OpenSlide.

## Workflow

1. Read `/workspace/artifacts/open-slide-studio/.agents/skills/create-slide/SKILL.md`.
2. Read `/workspace/artifacts/open-slide-studio/.agents/skills/slide-authoring/SKILL.md` and any referenced primitive guides needed by the deck.
3. Follow the bundled skill’s theme and scoping workflow. Ask only for choices not already clear from the request.
4. Create `slides/<kebab-case-id>/index.tsx` and deck-local assets only under `slides/<id>/assets/`.
5. Immediately before writing a new deck, run `node -e "console.log(new Date().toISOString())"` and set that exact literal as `meta.createdAt`; this drives newest-first ordering.
6. Build from the studio root with `bun run --cwd /workspace/artifacts/open-slide-studio build` and fix errors.
7. The persistent preview uses OpenSlide HMR. Do not restart the dashboard after slide edits; saved files should appear automatically, with browser refresh as fallback.

## Result

Report the deck id, source path, and preview route `/s/<id>`. Keep all decks in the shared studio so the main library remains the canonical index.
