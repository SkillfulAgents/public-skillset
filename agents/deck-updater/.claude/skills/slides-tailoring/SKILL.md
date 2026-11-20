---
name: slides-tailoring
description: 'How to copy the master Google Slides deck, map its layouts, tailor the copy with batchUpdate, tag every change as said or inferred in speaker notes, and the default follow-up deck outline. Use on every deck build or refresh.'
---

# Slides tailoring

All calls go through the proxy with the user's `googledrive` and `googleslides` connected accounts:
`$PROXY_BASE_URL/<account_id>/www.googleapis.com/drive/v3/...` and `$PROXY_BASE_URL/<account_id>/slides.googleapis.com/v1/...`.

## 1. Copy, never edit the master

1. Find or create the account folder under the configured parent: `GET drive/v3/files?q=name='<Account>' and '<parentId>' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false`. Create with `POST drive/v3/files` (`mimeType: application/vnd.google-apps.folder`) if missing.
2. Copy: `POST drive/v3/files/<masterId>/copy` with `{"name": "<Account> – Follow-up – <YYYY-MM-DD>", "parents": ["<folderId>"]}`. For a later call with the same account, copy the latest tailored deck instead of the master.
3. Do not call `permissions.create` on the copy. Sharing is the user's decision.
4. Record the new file ID in `/workspace/state/deck-updater/decks.json` before editing, so a crash never leaves an orphan copy.

## 2. Map the copy

`GET v1/presentations/<copyId>` and build a map per slide: `objectId`, layout name, the text of each placeholder shape, and the speaker-notes shape ID (`slideProperties.notesPage.notesProperties.speakerNotesObjectId`). Identify slides by the library tags (below), not by position.

## 3. Slide library tags

Ask the user (onboarding) to tag standard slides in the master by putting one line at the top of each slide's speaker notes, for example:
`#library pain:manual-reporting usecase:finance-close industry:saas proof:case-study-acme-like cleared:yes`

- `pain:` / `usecase:` / `industry:` drive selection.
- `proof:` marks a proof-point slide; `cleared:yes` means names, logos and numbers on it are approved for external use. Never keep a `proof:` slide without `cleared:yes`.
- `fixed` marks slides that always stay (title, agenda, about us, CTA).
- `pricing` marks pricing slides (kept only if pricing was discussed).
- Untagged slides are kept only if the outline below needs them; otherwise deleted from the copy.

If the user has a separate proof-point doc or sheet instead, read it from Drive and use only its rows.

## 4. Default outline (8–12 slides)

1. Title: "<Their company> × <Our company>: follow-up from <date>".
2. What we heard: their goals and top two or three pains, in their own words.
3. Who's involved and what each cares about (only if more than one stakeholder spoke).
4–6. Pain → how we address it: one slide per top pain, from the matching library slide, text adjusted to their wording.
7. Proof: one or two cleared proof points matching their industry, size or use case.
8. Your questions answered: objections raised, with the library's standard answer.
9. Pricing: only if discussed, and only what was said or the configured list price.
10. Next steps / mutual plan: agreed steps, owners, dates ("date to confirm" if none was said).
11. Call to action: one ask, matching the agreed next step.

## 5. Edit with batchUpdate

`POST v1/presentations/<copyId>:batchUpdate` with `requests`, grouped in one call where possible:
- `replaceAllText` for template tokens (`{{account}}`, `{{date}}`, `{{next_step}}`), scoped with `pageObjectIds` when a token repeats.
- `deleteText` then `insertText` on a placeholder `objectId` to rewrite a body; keep text inside existing shapes so theme styling holds.
- `deleteObject` for slides that don't apply.
- `duplicateObject` to reuse a standard slide twice (for example two pain slides).
- `updateSlidesPosition` to put slides in outline order.
- `insertText` into the speaker-notes shape for source tags.

Never send `updateTextStyle`, `updateShapeProperties`, `updatePageProperties` or `createImage` unless the user asked for that specific change. Branding stays as the master has it. Keep bullets short: at most five per slide, about twelve words each.

## 6. Source tags in speaker notes

Under each tailored slide's notes, add one line per changed text block:
- `[SAID] "<short quote>" — <speaker>, <mm:ss>`
- `[INFERRED] <what was inferred and why>`
- `[NEEDS PROOF POINT]` or `[CHECK] <unclear passage>` where applicable.

Collect every `[INFERRED]`, `[NEEDS PROOF POINT]` and `[CHECK]` line into the review list sent to the user, with the slide number.

## 7. Before you hand it over

- Re-read the presentation and confirm no `{{token}}` remains and no other account's name appears anywhere (search all text for previous account names in `decks.json`).
- Confirm every number in the deck appears either in the call brief or in a `cleared:yes` library slide.
- Link format for the email: `https://docs.google.com/presentation/d/<copyId>/edit`.
