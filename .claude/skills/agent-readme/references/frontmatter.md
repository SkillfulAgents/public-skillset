# README frontmatter reference

Everything here is enforced by `generate_index.py` (shape), by
`tests/test_generate_index.py` (non-empty for every agent), and by
`tests/test_superagent_slugs.py` in CI (slugs, against the live
`SkillfulAgents/SuperAgent` registries).

The five keys, in this order, in every agent README:

```yaml
---
category: <string>
icon: <lucide-kebab-name>
tags: [<4-7 display strings>]
works_with: [<{type, slug} objects, or []>]
developer: {name, url}
---
```

Keys that must **not** appear in README frontmatter:

| Key | Why |
|---|---|
| `name`, `description`, `createdAt`, `version` | Owned by `CLAUDE.md`; it wins the shallow merge, so a README copy is dead weight that silently rots. |
| `path`, `details` | Generated. Setting them is meaningless and misleading. |
| anything else | The light-import suite asserts the key set is exactly the five above. |

---

## `category`

One primary marketplace category. Required and non-empty.

**Reuse an existing value verbatim.** Introducing a near-duplicate splits the
storefront's category filter. In use today:

| Category | Count | Use for |
|---|---|---|
| `Marketing` | 36 | content, SEO, social, campaigns, brand |
| `Productivity` | 32 | personal workflow, notes, briefings, scheduling |
| `Personal` | 29 | household, health, travel, hobbies, family |
| `Sales` | 27 | prospecting, CRM, outbound, deal support |
| `Ops` | 27 | internal operations, finance, admin, logistics |
| `Customer Success` | 11 | support queues, tickets, retention |
| `Agent Creation` | 1 | agents that build other agents |
| `Design & Creative` | 1 | decks, visuals, design systems |
| `Email & Communication` | 1 | inbox and messaging management |
| `Health & Fitness` | 1 | nutrition, training, wellbeing |
| `Human Resources` | 1 | hiring, recruiting, people ops |
| `Operations` | 1 | legacy long form of `Ops` |

Known wart: `Ops` and `Operations` both exist. Use `Ops` — it has 27 entries to
`Operations`' 1. Do not "fix" the existing outlier as a side effect of adding
an agent.

Light imports normalize the upstream Bot Directory category, including
`Success` → `Customer Success`. That mapping is asserted by
`tests/test_botdirectory_templates.py`; take the value from
`sources/botdirectory/catalog.json` rather than choosing one yourself.

## `icon`

The lowercase kebab-case name of an icon from the
[Lucide catalog](https://lucide.dev/icons/) — the catalog name (`calendar-check`),
never the React export (`CalendarCheck`). Validated against
`[a-z0-9]+(?:-[a-z0-9]+)*`.

The generator does not pin a Lucide release, so a typo passes validation and
fails silently at render time. **Confirm the name exists on lucide.dev before
using it.**

Prefer an icon already in use — it keeps the grid visually coherent:

`list-checks` (20) · `badge-dollar-sign` (19) · `megaphone` (14) · `sparkles` (14)
· `workflow` (13) · `life-buoy` (11) · `pen-line` (9) · `mail` (6) ·
`presentation` (5) · `code-2` (5) · `messages-square` (5) · `video` (5) ·
`search` (5) · `plane` (5) · `mic` (5) · `calculator` (4) · `user-search` (4) ·
`calendar-check` (4) · `house` (4) · `book-open` (3) · `shield-check` (2) ·
`apple` · `inbox` · `search-check` · `shopping-cart` · `target` · `wand-sparkles`

Rough mapping: generic productivity → `list-checks`; sales/revenue →
`badge-dollar-sign`; marketing → `megaphone`; multi-step automation →
`workflow`; support → `life-buoy`; writing → `pen-line`; email → `mail` or
`inbox`; research → `search` or `user-search`.

## `tags`

**4–7** display strings, unique, non-empty, presentation-ready. The 4–7 bound is
asserted for light imports and holds across every existing agent.

These are labels, not identifiers. Keep human spacing, capitalization,
acronyms, and product names: `Email Management`, `SEO`, `Inbox Zero`,
`Google Calendar`, `OpenSlide`. Never `email-management` or `email_management`.
Consumers normalize for search; the index keeps the pretty form.

The light-import convention is a predictable four-to-seven: the category, the
agent's display name, each connected service by product name, then
`Workflow Automation` as filler when fewer than four would result. Full
templates use five or six genuine topic tags and skip the name echo.

Do not duplicate a tag, and do not pad past seven.

## `works_with`

The connectors the agent actually requests or consumes at runtime. Each item is
an object with **exactly** `type` and `slug` — no extra keys, no display names,
no duplicates.

```yaml
works_with:
  - type: api_account
    slug: googlecalendar
  - type: mcp
    slug: linear
```

- `type: api_account` — SuperAgent's canonical account `Provider.slug`, which is
  also the runtime `toolkitSlug`. Not a display name, not a per-user account ID,
  not a `composioSlug` or `nangoSlug`.
- `type: mcp` — the canonical `CommonMcpServer.slug`. Not a per-user MCP UUID.

`type` is required because some slugs exist in both registries. Slugs are
lowercase and case-sensitive, matched exactly.

**Do not list** — these are not connectors, and CI treats fabricated slugs for
them as errors:

- browser sessions (a logged-in Amazon or LinkedIn tab)
- built-in chat integrations (iMessage, the in-app chat)
- built-in web search
- public APIs and anything reached with only a raw API key (Ahrefs via key,
  a weather feed, an RSS URL)
- local tools and files

Those still belong in the body's `Connect first` / `What you'll need` section
with the honest phrasing from `references/body-structure.md` — they just get no
registry slug.

Slugs verified in this repo today (safe to reuse):

`api_account`: `airtable` `discord` `figma` `github` `gmail` `googlecalendar`
`googledocs` `googledrive` `googleslides` `googlesheets` `intercom` `linear`
`linkedin` `microsoft_teams` `notion` `outlook` `quickbooks` `salesforce`
`slack` `stripe` `xero` `youtube` `zendesk` `zoom`

`mcp`: `ahrefs` `dataforseo` `datadog` `granola` `posthog` `webflow`

For anything outside that list, check the registry before committing:

```bash
uv run tests/test_superagent_slugs.py --superagent-root .superagent-main
```

CI runs that check against both the recorded commit and current `main`, and
also flags labels that now have an exact registry match but no connector
entry — so a service you left out as "external" may come back as a suggestion.

## `developer`

Credit for whoever wrote the prompt or agent. `name` is required and non-empty;
`url` is optional but must be an absolute `http(s)` URL with a host when present.
No other keys are allowed.

```yaml
developer:
  name: SkillfulAgents
  url: https://github.com/SkillfulAgents
```

First-party agents use `SkillfulAgents` / `https://github.com/SkillfulAgents`.
Imported prompts credit the original author, matching the recorded creator in
`sources/botdirectory/catalog.json` exactly — usually an X handle:

```yaml
developer:
  name: "@elie2222"
  url: "https://x.com/elie2222"
```

Never replace an imported author with `SkillfulAgents`. The credit is a license
condition, and `tests/test_botdirectory_source.py` compares it against the
upstream checkout.
