# OpenSlide Studio Agent

> Create, edit, preview, and present polished slide decks in a native Gamut-managed OpenSlide dashboard.

## What it does

This template provides a slide-focused agent and a fully wired OpenSlide dashboard. The dashboard artifact is the OpenSlide project itself, so Gamut installs the real dependencies with Bun before starting it. The library supports deck search, native editing and presentation views, deep routes, and live updates through Vite HMR.

The stock **Getting Started** deck is included so the studio is useful immediately after import.

## What you'll need

- **Accounts:** None.
- **API keys:** None.
- **Other:** A Gamut environment with dashboard artifacts enabled and package-registry access for the first automatic Bun install.

## Getting started

1. Import this template zip into Gamut.
2. Open the **OpenSlide Studio** dashboard.
3. Gamut discovers `artifacts/open-slide-studio/package.json`, installs the locked dependencies with Bun, and launches OpenSlide.
4. Browse the stock Getting Started deck or ask the agent: `Create a slide deck about …`
5. Saved deck edits update in the open dashboard through native HMR; no restart is needed.

No onboarding session is required because this template has no user-specific settings, accounts, databases, or secrets.

## What's inside

- `CLAUDE.md` — the slide agent's durable role, native dashboard contract, commands, and skill map.
- `artifacts/open-slide-studio/` — the complete OpenSlide application and dashboard artifact.
- `artifacts/open-slide-studio/package.json` — real dependencies, scripts, and `gamut.upstreamPath: mounted`.
- `artifacts/open-slide-studio/bun.lock` — dependency lockfile used by Gamut's automatic installer.
- `artifacts/open-slide-studio/open-slide.config.ts` — reads `DASHBOARD_BASE_PATH` and `DASHBOARD_PORT`.
- `artifacts/open-slide-studio/slides/getting-started/` — OpenSlide's stock sample deck and assets.
- `.claude/skills/create-slide-deck/` — creates and validates decks in the shared library.
- `.claude/skills/edit-slide-deck/` — revises decks while preserving metadata and live preview behavior.
- `.claude/skills/create-slide/`, `slide-authoring/`, `create-theme/`, `apply-comments/`, and `current-slide/` — OpenSlide's supplied authoring skills.

## Dependency model

The template intentionally contains no `node_modules` and no manual install script. Gamut runs `bun install` in the dashboard artifact directory, then runs:

```text
open-slide dev --host 0.0.0.0 --no-skills-check
```

This avoids npm's `chmod` failure on Windows-backed 9p/drvfs workspaces and keeps dependency lifecycle under Gamut's dashboard manager.

## Validation

```bash
bun install --cwd /workspace/artifacts/open-slide-studio --frozen-lockfile
bun run --cwd /workspace/artifacts/open-slide-studio build
```

The dashboard uses Gamut's mounted-path mode, so OpenSlide's HTTP routes and HMR WebSocket remain under the agent artifact path without custom routing shims.
