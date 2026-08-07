---
name: Edit Slide Deck
description: Edit, revise, restyle, reorder, or apply inspector comments to an existing deck in the shared OpenSlide studio at /workspace/artifacts/open-slide-studio. Use for requests involving slide changes, “this slide,” selected elements, or @slide-comment markers.
metadata:
  version: "1.0.0"
---

# Edit Slide Deck

Edit existing decks in `/workspace/artifacts/open-slide-studio` without restarting the preview app.

## Workflow

1. If the user says “this slide,” “this page,” or refers to the selected element, read `/workspace/artifacts/open-slide-studio/.agents/skills/current-slide/SKILL.md` and resolve `node_modules/.open-slide/current.json` first.
2. If applying visual inspector comments, read `/workspace/artifacts/open-slide-studio/.agents/skills/apply-comments/SKILL.md`.
3. For every source edit, read `/workspace/artifacts/open-slide-studio/.agents/skills/slide-authoring/SKILL.md` plus any relevant primitive references.
4. Touch only the requested deck under `slides/<id>/`; preserve `meta.createdAt` and unrelated pages unless the request requires changing them.
5. For targeted edits, locate page declarations with `grep -n ": Page = " slides/<id>/index.tsx` and read only the needed range.
6. Build with `bun run --cwd /workspace/artifacts/open-slide-studio build` and fix errors.
7. Rely on OpenSlide HMR for the running preview. Do not restart the dashboard after edits; use browser refresh only if HMR does not update.

## Result

Summarize changed pages and the preview route `/s/<id>`. If inspector markers were processed, report counts applied and skipped.
