---
name: ship-filter-and-formats
description: 'Decides which shipped changes are customer-facing, groups them into stories, and gives the per-platform and per-format rules for drafts and verification links. Use on every campaign run before drafting.'
---

# Ship filter and formats

## 1. Keep or drop

Drop by default:
- Conventional-commit prefixes `refactor:`, `chore:`, `ci:`, `test:`, `build:`, `style:`, `docs:` (internal docs), `perf:` with no user-visible effect stated.
- Dependency bumps, including automated dependency PRs (from GitHub dependency updates or Renovate), lockfile-only changes, and version-bump PRs.
- Labels such as `internal`, `infra`, `tech-debt`, `no-changelog`, `skip-release-notes`, or any label onboarding listed.
- Reverts, and anything reverted later in the same window.
- Draft PRs, PRs closed without merging, and PRs merged to a branch other than the default branch.
- Linear issues that are not in a completed state, or that are marked duplicate or canceled.

Keep:
- `feat:` changes, labels such as `feature`, `enhancement`, `customer-facing`, or a release note that names the change.
- `fix:` changes that customers reported or that affect a common workflow (changelog material; a social post only if many customers asked).
- Performance work only when the source states the customer-visible effect.
- Anything listed under a "Highlights" or "New" heading in a release note.

Hold and ask: anything behind a feature flag, in beta, in staged rollout, plan-limited, or a security fix.

When unsure, list it under "Left out" in the review message with a one-line reason, so the approver can pull it back in.

## 2. Group into stories

- One story = one thing a customer can now do, or one problem that is gone.
- Merge PRs that share a linked issue, a Linear project, a feature label, or a release-note heading.
- A release with one big feature and many fixes is usually one feature story plus one "also fixed" changelog note.
- Rank stories by customer reach: new capability > widely used improvement > niche fix.

## 3. Formats

Give two formats per story from the set onboarding chose:
- **Social post**: one per enabled account; the benefit in the first line.
- **Changelog note**: title in plain words, then 1 to 3 sentences: what changed, who it helps, how to use it. Past tense, no marketing adjectives.
- **Blog blurb**: 80 to 150 words: the problem, what is new, a short how-to, where to learn more.

Platform rules for social posts:
- **X**: at most 280 characters (a URL counts as 23). Links in the main post can reduce reach; offer a version with the link in a follow-up reply. Hashtags only if the voice samples use them, at most one or two.
- **LinkedIn**: 600 to 1,300 characters works well; a strong first two lines before the "see more" cut; short paragraphs; links are fine but keep one.
- **Bluesky**: at most 300 characters; plain and conversational.
- **Mastodon**: 500 characters by default (the instance may differ); hashtags help discovery, two or three in CamelCase.
- **Threads**: at most 500 characters.

## 4. Verification links

- Every story in the review message lists its sources: PR URLs, Linear issue URLs, release URL, changelog anchor.
- Public copy may link only to public pages: the public changelog, docs, a public release page, a public repo.
- For a private repo, never quote PR titles, branch names, issue IDs, codenames, or customer names in public copy.

## 5. Review message shape

```
Release campaign: <release or week>  (campaign <id>)
1. <story title>  [sources: PR #123, LIN-456]
   Social (X): <draft or link to draft>
   Changelog: <draft or link>
   Flags: <beta / plan-limited / none>
   Proposed: X Tue 10:00, LinkedIn Tue 11:00
2. ...
Left out: <item> (internal refactor), <item> (dependency bump)
Reply "approve 1, 2", edit inline, or "cut 2".
```
