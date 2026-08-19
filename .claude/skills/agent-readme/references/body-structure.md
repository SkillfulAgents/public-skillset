# README body structure

The body (frontmatter stripped) becomes `details` in `index.json` and is
rendered as the agent's detail page. Write it as marketplace copy: no "this
directory", no TODOs, no notes to future contributors.

Section headings come from a closed vocabulary. Adding a novel heading is how a
storefront layout breaks, so pick from the tables below.

---

## Light import (has `PROMPT.md`) — 160 agents

Fixed skeleton, fixed order, fixed sentence stems. Deviating breaks
`tests/test_botdirectory_templates.py`.

```markdown
# <Name>

<CLAUDE.md description, verbatim>

## What it does

- Act as the <Name>: <description with a lowercase first letter>
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **<Label>** — <suffix from the vocabulary below>

## Sample use cases

- <first clause of the description, as a sentence>
- <second clause of the description, as a sentence>

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- <first-run ask>
- <signature ask>
- <depth or cadence ask>

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [<handle>](<url>) on [Bot Directory](https://botdirectory.ai/bots/<slug>/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
```

Notes:

- The summary line under the H1 is the `CLAUDE.md` `description` **verbatim**,
  including its typographic punctuation. Do not paraphrase or re-wrap it.
- Bullets two and three of `What it does` are constant across all 160 agents.
- `Sample use cases` splits the description on its `;` or `,` clause boundary
  into two standalone sentences. One bullet is acceptable for a single-clause
  description; do not invent a third.
- The three `Getting started` steps and the three `Files` lines are constant.
- `Example prompts` is the one section of a light import that must be written
  fresh. Derive it from `PROMPT.md`, not from the description.
- `Connect first` and the `First run` section of `CLAUDE.md` must name the same
  labels, and every mapped connector must appear in both with its slug.

### `Connect first` suffix vocabulary

One bullet per label, always `- **<Label>** — <suffix>`. The suffix encodes the
transport, and only the first two rows also produce a `works_with` entry.

| Transport | Suffix | `works_with` |
|---|---|---|
| SuperAgent API account | ``SuperAgent API account `<slug>`.`` | `api_account` |
| SuperAgent MCP | ``SuperAgent MCP `<slug>`.`` | `mcp` |
| Browser session | `browser session; no registry slug.` | none |
| Local tool or file | `local tool or resource; no connection slug.` | none |
| Built-in capability | `built-in capability; no connection slug.` | none |
| Built-in iMessage | `built-in iMessage chat integration; no registry slug.` | none |
| External service, no connector | `external connection; no canonical registry slug.` | none |
| Raw API key / feed | `direct API, feed, or required credentials; no canonical registry slug.` | none |

The transport for a given label is recorded in
`sources/botdirectory/connect-first.json` — read it rather than guessing, and
if the label is new, add it there with a `reason` first.

---

## Full template (no `PROMPT.md`) — 8 agents

Real copy. The frontmatter and the heading vocabulary are still fixed; the prose
is yours.

```markdown
# <Name>

> <one-sentence hook, distinct from the description>

## What it does

<1–3 paragraphs, or a short bulleted feature list for complex agents.>

## What you'll need

- **<Service>** — <why, and whether it is required or optional>
- **API keys:** <none, or which ones>

## Getting started

1. Import the template into Gamut.
2. <what onboarding does>
3. <the first real task the user should ask for>

## Example prompts

- <first-run ask>
- <signature ask>
- <depth or cadence ask>

## What's inside

- `CLAUDE.md` — <one line>
- `.claude/skills/<name>/` — <one line each>
- `<dir>/` — <one line each>

## Notes

- <caveats, limits, reset instructions>
```

Heading vocabulary, by preference:

| Heading | Use |
|---|---|
| `## What it does` | always — the capability description |
| `## What you'll need` | accounts, keys, time. Use `## What it needs` with a table only when requirements are genuinely tabular (see `seo-agent`) |
| `## Getting started` | always — numbered import-to-first-result steps |
| `## Example prompts` | always — the three starter chips (see below) |
| `## What's inside` | always — the file manifest. `## Layout` with a fenced tree is the accepted alternative for large agents |
| `## Notes` | optional — caveats, limits, timezone assumptions, reset steps |
| `## Privacy` | when the agent reads personal data or drives logged-in accounts |
| `## Credits` | whenever the work derives from a third party |

Guidance:

- The blockquote hook sells; the description states. `Inbox Manager`'s hook is
  "Turn a noisy Gmail inbox into a short, useful queue of messages that deserve
  your attention." — concrete outcome, no feature list.
- `What's inside` lists every top-level file and directory a user would notice,
  and one line per `.claude/skills/*` directory. This is the section that rots
  first; regenerate it from an actual directory listing.
- If onboarding is auto-launched on import, say so in `Getting started` and name
  the skill (`agent-onboarding`) so users can re-run it.
- State autonomy boundaries explicitly when the agent can spend money, send
  mail, publish, or merge. Every existing full template does.

---

## `## Example prompts` (both flavors)

The agent detail page renders these three lines as clickable starter chips,
prefixed with the agent's mention:

```
@Agent Pill  Help me get started
```

Until a template supplies its own, the page falls back to a generic trio —
"Help me get started", "What can you do?", "Walk me through your first run".
That fallback is what this section exists to replace. **Never ship it.**

```markdown
## Example prompts

- Screen my inbox and show me what needs a reply today
- Unsubscribe me from everything I haven't opened in three months
- Every weekday at 8am, screen the inbox and post the summary to Slack
```

### The three slots, in order

1. **First run** — the smallest useful ask right after setup. It should
   succeed on a fresh workspace and prove the agent works.
2. **Signature** — the capability the agent exists for. If a shopper reads one
   chip, this is the one that should sell the template.
3. **Depth or cadence** — a recurring schedule, a bulk pass, or a harder ask
   that shows range beyond the obvious.

### Format

- Exactly **three** `- ` bullets. Not two, not four.
- Plain text: no backticks, bold, links, or trailing period. Question marks are
  fine.
- **25–80 characters.** Shorter reads as a stub; longer wraps in the chip.
- No leading `@Name` — the page prepends the mention.
- Written as the user speaks to the agent: second person to it, first person
  about them ("my inbox", "our pipeline", "the deck I sent you").

### Content

- Concrete over generic. "Draft a reply to Priya's last email" beats "Help me
  with email". Every chip should name a real object, action, or output.
- Only reference services the README already declares in `works_with` or
  `Connect first`. A chip that names Slack for an agent with no Slack
  connection is a broken promise on the storefront.
- For a light import, read `PROMPT.md` and lift the actual instructions it
  gives. The description is a summary; the prompt is what the agent can do.
- No placeholders (`<your domain>`, `[COMPANY]`). Where a target is genuinely
  required, phrase it naturally: "audit my site", "for the Acme deal".
- Do not restate `Sample use cases`. That section describes the agent in third
  person; these are things a user types.

---

## Rules that apply to both flavors

- **H1 = `CLAUDE.md` `name`.** Four legacy READMEs drift (`OpenSlide Studio
  Agent`, `Outbound Agent Template`, `Recruiting Agent Template`,
  `SEO Agent — template`). Do not add a fifth.
- **No `##` heading before the summary line.** The H1 and its one-line summary
  come first, always.
- **No `#` H1 anywhere but the top.** Sections are `##`; sub-sections `###`.
- **Links must survive leaving the repo.** `details` renders outside a file
  tree, so prefer absolute URLs. The one sanctioned relative link is the Bot
  Directory `NOTICE.md` reference in `Credits`.
- **No secrets, no personal data, no local absolute paths.**
- **One trailing newline**, no trailing whitespace.
