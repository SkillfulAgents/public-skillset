---
name: agent-readme
description: Write or fix the README.md for an agent template in agents/<slug>/, so its marketplace metadata and long-form copy match every other template in this repo. Use whenever a new agent directory is added, an agent's README is missing, or an existing README's frontmatter, sections, or connector list needs to be brought back in line before regenerating index.json.
---

# Agent README generator

`agents/<slug>/README.md` is not documentation — it is the marketplace record.
`generate_index.py` lifts its frontmatter into `index.json` as the agent's
`category`, `icon`, `tags`, `works_with`, and `developer`, and lifts its entire
Markdown body (frontmatter stripped) into `details`. The storefront renders
those fields directly, so drift in one README shows up as a broken card.

Produce a README that is byte-for-byte conventional: same field set, same field
order, same section names, same sentence shapes as the 168 templates already in
`agents/`.

## Step 1 — Read the agent first

Never write the README from the user's description alone. Read, in order:

1. `agents/<slug>/CLAUDE.md` — frontmatter gives you `name` and `description`
   (which the README must echo, not restate); the body gives you the real
   capabilities, the first-run connections, and the operating rules.
2. `agents/<slug>/PROMPT.md` if present — its presence means this is a
   **light import** (see Step 2). The prompt text is the source of truth for
   what the agent actually does and what it must connect to.
3. Everything else in the directory — `.claude/skills/*/SKILL.md`, `artifacts/`,
   state directories, `.env.example`. Each one becomes a line in
   `## What's inside`, and `.env.example` tells you which API keys to list.

If `CLAUDE.md` is missing `name`, `description`, `createdAt`, or `version`, stop
and fix that first — `tests/test_generate_index.py` requires all four to be
non-empty for every agent, and the README cannot supply them (`CLAUDE.md` wins
the merge on every shared key).

## Step 2 — Pick the flavor

Two body shapes exist. Pick by the presence of `PROMPT.md`; do not invent a third.

| | **Light import** | **Full template** |
|---|---|---|
| Marker | `PROMPT.md` present | no `PROMPT.md` |
| Count today | 160 | 8 |
| Body | fixed, formulaic, ~40 lines | hand-written marketing copy |
| Template | `templates/README.light.md` | `templates/README.full.md` |

A light import is a third-party prompt wrapped in a thin operating layer. Its
README is generated from a formula and must not be embellished — the section
set, the sentence stems, and the `Credits` line are all asserted by
`tests/test_botdirectory_templates.py`.

A full template is a first-party agent with skills, state, and artifacts. Its
README is real copy, but the frontmatter and the section vocabulary are still
fixed.

## Step 3 — Write the frontmatter

Exactly these five keys, in this order, in every agent README:

```yaml
---
category: Productivity
icon: calendar-check
tags:
  - Planning
  - Automation
  - Gmail
  - Workflow Automation
works_with:
  - type: api_account
    slug: gmail
  - type: mcp
    slug: linear
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
---
```

- **Never** put `name`, `description`, `createdAt`, or `version` here — they
  belong to `CLAUDE.md`, which wins the shallow merge anyway.
- **Never** set `path` or `details`; the generator owns both.
- `works_with: []` when the agent needs no registry connector. The key still
  appears — do not omit it.
- Quote strings only where YAML requires it. Match the quoting style already
  used in the sibling files you are editing alongside.

Field rules, the allowed `category` and `icon` vocabularies, and the strict
`works_with` slug rules are in **`references/frontmatter.md`**. Read it before
choosing a category, an icon, or any slug. Getting a slug wrong fails CI
against the live SuperAgent registry; inventing one is never acceptable.

## Step 4 — Write the body

The body is `details` — it must read as standalone marketplace copy, not as a
note to a repo contributor.

Both flavors open the same way:

```markdown
# <Name>
```

The H1 must match `CLAUDE.md`'s `name` exactly. Four legacy READMEs drift from
this; do not add a fifth.

The line under the H1 differs by flavor:

- **Light import** — repeat `CLAUDE.md`'s `description` verbatim, as a plain
  paragraph. This is deliberate redundancy: the card shows the description, the
  detail page shows the body, and they must agree.
- **Full template** — a `>` blockquote hook of one sentence that sells the
  agent and is *different* from the description.

Both flavors also carry a `## Example prompts` section of exactly three lines.
The detail page renders them as clickable starter chips prefixed with the
agent's mention (`@Agent Pill  Screen my inbox`), falling back to a generic
"Help me get started / What can you do? / Walk me through your first run" trio
when a template does not supply its own. Replacing that fallback is the whole
point — write three concrete asks, in the order first-run → signature →
depth-or-cadence, naming only services the README actually declares.

Section-by-section rules, the fixed sentence stems for light imports, the
`Connect first` suffix vocabulary, and the full `Example prompts` spec are in
**`references/body-structure.md`**.

End the file with a single trailing newline.

## Step 5 — Validate, regenerate, verify

Run the checker on the agent you just wrote:

```bash
uv run .claude/skills/agent-readme/scripts/check_agent_readme.py agents/<slug>
```

It reports `error:` lines (must be fixed) and `warning:` lines (justify or fix).
Then regenerate the index and run the repo's own suites:

```bash
uv run generate_index.py
```

```bash
uv run tests/test_generate_index.py
```

For a light import, also run:

```bash
uv run tests/test_botdirectory_templates.py
```

`--all` sweeps every agent. It is currently red for three legacy full
templates (`outbound-campaign-agent`, `recruiting-agent`, `seo-agent`) whose
section names predate this vocabulary, and `outbound-campaign-agent`
additionally carries `version` in its README frontmatter instead of
`CLAUDE.md`. Those are known and pre-existing — do not copy their shape, and do
not silence the checker to hide them.

`index.json` is generated — never hand-edit it, and always commit the
regenerated file alongside the new README.

## Step 6 — Root README

The root `README.md` lists each full template under `## Agent Templates` with an
H3 heading and a one-paragraph summary, and states the light-import count in the
"Bot Directory light templates" paragraph. Update whichever applies:

- new full template → add an H3 section, alphabetically among its siblings
- new light import → bump the count in that paragraph

## Checklist

- [ ] Read `CLAUDE.md`, `PROMPT.md`, and every skill/artifact directory
- [ ] Flavor chosen from `PROMPT.md` presence
- [ ] Frontmatter has exactly `category`, `icon`, `tags`, `works_with`, `developer`, in order
- [ ] `icon` is a real lowercase kebab-case Lucide name
- [ ] 4–7 unique, presentation-ready `tags`
- [ ] Every `works_with` slug verified against the registry; every listed connector is one the agent actually calls
- [ ] `developer` credits the original author, with an absolute http(s) `url`
- [ ] H1 matches `CLAUDE.md` `name`
- [ ] Summary line matches the flavor (verbatim description / blockquote hook)
- [ ] Section names drawn from the approved vocabulary, in the approved order
- [ ] `Example prompts` has exactly three concrete, agent-specific chips — none of the generic fallbacks
- [ ] `Credits` present and correct for any third-party prompt
- [ ] Checker clean, `index.json` regenerated, tests pass
- [ ] Root `README.md` updated
