---
name: maintain-brain
description: The brain's scheduled upkeep, plus the agent's own improvement. Retries pending contributions, picks up new or removed connected accounts, checks the brain's health (links, staleness, end dates, index, structure), learns from people's edits and moves, re-syncs sources when due, then reflects on recent sessions and improves its own skills. Sends one report, only if something changed or someone is needed. Use when the scheduled task fires, or for "run upkeep", "check the brain's health", "re-sync", or "reflect on recent sessions".
---

# Maintain the brain

**Read-only here?** If the brain location is marked `(read only)` in your system prompt, follow *When the brain is read-only here* in your system prompt and stop.

Follow the system prompt. This skill adds only what's specific to upkeep. It usually runs with nobody watching, so follow the system prompt's rules for unattended sessions.

**A newer template?** Check this first, so it happens even when upkeep stops early. Your template's source is in `.skillset-agent-metadata.json` at the top of your workspace, which the app owns: read it, don't edit it. The published version is the `version` in the frontmatter of `CLAUDE.md` in that folder. When it is newer than the `version` in your own instructions, and you haven't flagged that version before, say so under **Needs you** in your report: the new version is out, and saying "update from template" in a chat with you reviews it. Updating changes your own instructions, so it happens in a session with a person, through `update-from-template`, not here.

```
1 Claim      claim the brain (stop if a fresh claim is held)
2 Pending    retry contributions waiting on an answer
3 Accounts   new or removed connected accounts
4 Health     check the brain against its guarantees and defaults
5 Learn      people's edits and moves, structural signals
6 Re-sync    when due: refresh sources and public research
7 Release    update the index, release the claim
8 Reflect    learn from recent sessions, improve the skills
9 Summarize  write this run's summary to _brain/syncs/, every run
10 Report    one message, only if something changed or someone is needed
```

The order matters: new material lands before the health check, and the brain work finishes before reflection so reflection can learn from it. A quiet night should cost little. If nothing arrived, nothing changed, nothing is due and there's nothing to learn, write the short summary and go straight to the report.

## 1. Claim

Claim the brain as the system prompt describes. If a claim is less than 2 hours old, stop: another run is going, or the schedule fired twice.

## 2. Pending

Retry the pending asks in your memory whose blocker has since been answered, following the system prompt's contribution steps. An ask still pending a full cycle later goes in the report.

## 3. Accounts

Compare the connected accounts with the ones in your memory.

- **New account, known source.** Read what it can see over the source's normal depth. Merge on each item's id or link: a second account only adds what the others couldn't see. The sensitivity decisions apply to it like any other.
- **New kind of source.** Read it the way the `build-brain` skill describes, file what it adds into the existing structure, and add it to `_brain/sources.md`. New grey categories it brings wait for a person's decision. File everything else.
- **Account gone.** Keep the pages. Note it in `sources.md` and the report. If it was the source's only account, mark the source disconnected.
- **Write each new account into memory:** service, who connected it, their area. Mention it in the report in one line.
- **New workspace agents are never discovered here.** That usually needs an approval nobody is around to give. Read only the agents in scope, by name, and save discovery for a session someone is in.

## 4. Health

Check the brain against the system prompt's guarantees and the team's defaults (`_brain/team.md`). When a finding has exactly one sensible fix, apply it. Otherwise record it as a structural signal, or put it in the report.

| Finding | Action |
|---|---|
| Broken link | If the target moved, find it by name and fix the link. Otherwise remove the link and note it on the page. |
| Page past its review interval | Re-check it against its sources. Update it and its `last_checked`, or mark it stale if the source can't be reached. |
| Page past its `until` date, or its project, ticket or PR has ended | Archive it, giving the end as the reason. |
| Source a reader can't open (private notes, a moved file) | Replace it with the original link, finding moved files by name. If there's none, mark the page `inferred`. |
| Page missing its summary, sources, verified label or last-checked date | Fill them in from the page's sources. Where that's impossible, label the page honestly. |
| Frontmatter that doesn't parse as YAML | Quote its string values. Change no wording. |
| A page that changes over time but has no timeline | Add one, with a first entry from the page's sources. |
| Folder without a README (outside `_brain/`), or an index that doesn't match the brain | Write the README. Rebuild the index in step 7. |
| Empty folder | Remove it and log it. There's nothing to archive. |
| Top level too wide, or too deep | Propose a flatter shape in the report. |
| Folder past the split size | Split only if there's a natural subgroup of 3 or more. |
| Folder under the minimum size past its grace period | Merge its pages into the closest folder. |
| A brain page that differs from what you last wrote | Step 5. |

**On large brains,** don't re-read every file every night. Tell which files changed by size and modified time, then read only those. A full read of a large synced drive can take most of an hour.

When a check repeats nightly, script it and keep the script with this skill. Your own script is fine. What matters is that it reliably catches the problems in the table.

## 5. Learn

- **A person edited a page you wrote.** Accept the edit and log the acceptance. If it corrects a fact, fix every other place the same fact appears.
- **A person moved or renamed something you filed.** Find where it went, accept it, and update the index. Record the pattern. The second time the same pattern shows up, add it as a filing rule in `team.md`, which is a tightening you're allowed to make yourself. Never move it back.
- **Structural signals** you've noted: things that don't fit, folders that are too big or too small, failed lookups, misfiles. Act on each once its evidence meets the threshold in the defaults, within your authority. Otherwise put it in the report.
- **Reader questions.** Fold in any new ones from recent sessions. Note which ones the brain can't answer yet, and fill a gap now if a connected source has the answer.

## 6. Re-sync (when due)

Re-sync on the cadence in `team.md`, weekly by default.

- **For each connected source:** read what changed since its last sync, once per account, and merge on item id or link.
  - New projects, channels, important pages, repos and people go in as summaries with links.
  - When a fact has changed, rewrite the page's summary, add a dated timeline entry with the source, and update `last_checked`. Follow the guarantee that a person's edit always wins.
  - Things gone from the source get marked on their pages. Archive them only once they're clearly gone for good.
  - Update the source's last-sync date in `sources.md`.
- **Re-read the public sources:** a launch, a pricing change or new people go in as dated snapshots.
- **When a source fails** (calls hang or keep erroring, or a call held for review times out or is denied), skip it for this cycle. Keep its last-sync date, note it, and report it. If it fails twice in a row, ask in the report for someone to reconnect it.
- **For a large re-sync,** have helpers read and draft in parallel, each into its own paths. Check every draft before applying it: no existing timeline line dropped, no new entry without a source, no sensitive figures added. Then apply the changes one at a time.

## 7. Release

Bring every folder README's page list and `INDEX.md` into line with the brain. Update the people-facing map in `README.md` if the top level changed. Release the claim.

## 8. Reflect

Run this when the sessions since the last reflection include real work: requests, corrections, a build or a re-sync. With nothing new, just record that you checked.

1. **Read the sessions since the last reflection,** including your own past runs of this skill. Look for:
   - **corrections:** a person or agent fixing you, or a human moving or editing what you filed;
   - **friction:** questions you asked that the rules didn't require, steps that failed or had to be retried, work you repeated;
   - **misses:** lookups that failed, reader questions the brain couldn't answer, things you should have caught;
   - **what worked:** approaches people accepted without pushback. Keep those, so you don't drift away from them.
2. **Change things based on what you found.** Every change cites the session it came from.
   - Update your memory: lessons, preferences, facts about your environment.
   - Improve your skills, `build-brain` and this one: fix a step that failed, add a trap you hit, remove a step that never helps. When a skill keeps doing the same work by hand, give it a script.
   - Tighten a team rule in `team.md` when the evidence is clear (a filing rule, for example). Never loosen one: put loosening in the report.
   - Never change the system prompt, the sensitivity decisions or routing. Propose those in the report.
3. **Keep a short record** in memory for each run of each job (build, request, upkeep): what happened, how long it took, what went wrong. Judge each run by what happened afterwards (corrections, rework, questions that came back), not by how the run felt. Look across runs for patterns before changing a skill.
4. **Fold what you changed into the report,** under Applied, so anyone can revert any of it.

A failed reflection never undoes the brain work above.

## 9. Summarize

Write one summary for the run to `_brain/syncs/<YYYY-MM-DD HHMM>.md` in the brain, in the team's timezone. If that file already exists, add the next unused number before `.md`, ` (2)`, ` (3)`, rather than overwrite it. Write it every run that has a brain, quiet runs included: it tells "nothing new" apart from "didn't run", and it carries open items forward. The app's Team Brain page reads these files, so keep this shape exactly:

```markdown
---
type: team-brain-sync
at: 2026-10-23T00:00:00-07:00
session: 526c9fe1-1f4e-47da-920a-3896e5e3c12c
sources: [slack, notion]
added: 3
updated: 9
---
## Highlights
### Acme's renewal moves to Q1
Two or three sentences, linking the pages: [Acme](../../customers/acme.md).

## Changes
- One line per page added, updated or archived, linking it.

## Needs you
### Blocked
- Reconnect Slack. #sales and #eng weren't read this run.
### To decide
- Is Acme's renewal Q1 or Q2? Two threads disagree. Filed as Q1 on [Acme](../../customers/acme.md).
```

- **`type`:** always `team-brain-sync`. The page reads only files with it, so other files in the folder are ignored.
- **`at`:** when you write the summary, in ISO 8601 with the timezone offset. The page shows it as when the brain last synced.
- **`session`:** the value of `GAMUT_SESSION_ID`. If it isn't set, leave the line out. Never write a placeholder.
- **`sources`:** the apps this run found something new in, by their key in `CONNECTED_ACCOUNTS`. `[]` when none.
- **`added`, `updated`:** how many pages this run added and updated.
- **Links** follow the brain's rule: relative Markdown links from the summary's folder, so `../../` is the brain's top. Link a source by its web address.
- **Highlights:** at most 3. A highlight is something a teammate would want to be told without asking. Everything else is one line under Changes.
- **Needs you:** only what a person needs to act on, every line with what to do. The run never waits on these: it does everything else and records them here.
  - **Blocked:** what kept this run from covering part of the brain (a missing or expired account, a call held for review that timed out or was denied, a source that kept failing). Name what wasn't covered.
  - **To decide:** a call that is a person's, not yours (facts that disagree, a sensitive item, a structure change). Say what you filed meanwhile.
  - Re-check the previous summary's lines and carry over the ones still open: the page shows only the latest summary's.
- Leave out a section with nothing in it. A quiet run is the header alone, with zeros.

## 10. Report

If the team chose a reporting channel, send one message there for the whole run, in the system prompt's format: the brain changes and skill changes under **Applied**, decisions under **Needs you**, and new accounts and failing sources one line each. If nothing changed and nobody is needed, send nothing.
