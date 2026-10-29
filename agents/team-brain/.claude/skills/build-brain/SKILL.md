---
name: build-brain
description: Build the team's brain with the user, from almost nothing to a brain the team trusts, in a loop of research, questions, connected sources and writing, with the brain growing in place so the user can watch, redirect, leave and return. Also use it to revisit the brain later, to add a new area or source, go deeper, or refine its shape. Use for "set up our brain", "let's add context about X", "connect our Notion and pull it in", or any first session after setup.
---

# Build the brain

**Read-only here?** If the brain location is marked `(read only)` in your system prompt, follow *When the brain is read-only here* in your system prompt and stop.

Follow the system prompt. This skill adds only what's specific to building.

The brain grows in place from the first pass, so the user sees it take shape, can steer it, and loses nothing if they leave. The session is a loop, not a script. At every step, take whichever step would teach the most, never just the one next in order.

## Arriving

Read your memory and the brain first. One of three things is true:

- **New brain.** Nothing in your memory, and the brain is empty apart from what setup created. Start with *Opening*.
- **Unfinished build.** Your memory has a build in progress. Open with a short status: what's in the brain, what you were chasing, and what you need from the user. Then carry on. Never restart, and never re-ask anything already answered.
- **Revisit.** The brain was built and is in maintenance. Ask what the user wants to add or change, then run the loop for just that: a new area, a new source, more depth, or a different shape. Use the existing structure, and propose changes to it only when the new material requires them.

## Opening

Research before you ask anything. The setup block names who set you up: their email and name usually lead to the organization and their place in it, and each checks the other. Come back with what you found, how sure you are, and your best guess at what the brain should cover. Write that into the brain as an `inferred` overview first, so they see it start while they read. If nothing usable turns up, ask for the team's name and website, then research from that.

Show value before asking for effort. Keep what you say about a person to their work role and team.

Ask for a value you're missing when you first need it. Record the team's choices in the team record.

**If a wiki or docs space already exists,** it's the richest source you have. Read it before anything else. Keep what works, because people already know their way around it. Decide from what you find whether it becomes the brain or feeds it, and ask only if that's unclear.

Tell the user early that they can leave any time and pick up where they left off.

## Reader questions

Early on, draft 10 to 20 questions this team's readers will ask, specific to this team rather than generic. Seed them from what a newcomer needs:
- what is this team, and who does what;
- what are we building, and why;
- how do we work;
- what have we decided;
- where is X.

Keep them in your memory with how well each is answered. They're your working goal, not something to show, and they grow as you learn. When readers ask real questions later, those beat your guesses.

## The loop

```
understand → choose the step that teaches the most → gather → write it into the brain → show the user → repeat
```

### Choosing the next step

Weigh each possible step by how much it's likely to teach, not by how cheap it is. A step is worth more when it:
- answers an important open reader question;
- is likely to turn up something nobody asked about, like a founder's talk, an old wiki, a customer story or a public changelog; or
- opens better questions.

How to pace it:
- **Go broad first,** so the overall picture forms quickly.
- **Then go deep** where the team's own signals point: what's pinned, most linked, recently active, or what the user keeps coming back to.
- **Follow rich leads past "answered".** That's where the context nobody thought to give you usually is.
- **Drop leads that keep coming up empty.**
- **Stop digging an area** when new reads stop changing the brain.

### Ways to gather

- **Public research.** Website, docs, blog, repos, talks, press, public profiles. Costs the user nothing. Usually the first move, and worth repeating whenever a new name, product or event comes up.
- **Connected sources.** Ask the user to connect one when you can say what it would add for *this* team. Ask for several together when you can. Use account connections, never raw tokens. A declined source is fine: note it and don't ask again unless the user brings it up.
- **Workspace agents in scope.** Read only those in scope, and only their work.
- **The user.** For what only a person knows: priorities, why decisions were made, who knows what, what's unwritten, what matters and what doesn't.
- **Other people.** Only when the user asks you to involve them, and only in the way they ask. Until then, every question goes through the user.

### Reading a source

Read structure and summaries first, then go deep where the signals point. Starting points by kind of source:

| Source | Read first | Usually gives you |
|---|---|---|
| Website | home, about, product, pricing, blog, careers, docs | what the team says about itself, product summary, dated snapshots of pricing and positioning |
| Docs / wiki | page tree, top-level and most-linked pages, recently edited pages | a map of what's written down, glossary terms, decisions |
| Chat | channel list, purposes, pins, member counts, then recent threads in the main channels, read for decisions | channel guide, decision records, roles, how the team works |
| Issue tracker | teams, projects, cycles, labels, recently finished work | what's being built and its status, roadmap shape, team structure |
| Code host | repos by recent activity, READMEs of the most active ones, architecture docs | system map, tech stack, repo guide (links only) |
| File storage | folder tree, recently changed files, brand and template folders | an asset guide; copies of the canonical brand files |
| Calendar | recurring events: names, cadence and attendee counts only | the team's operating rhythm |
| Email / CRM | only as the sensitivity decisions allow | customer and partner overview |

A team's tools point at each other: chat links repos, READMEs link organizations, docs link drives. Follow those links, and when two candidates fit, prefer the official, most active one.

Things that have gone wrong before:
- A rate-limited API can answer "success" with nothing in it. An empty result isn't proof that nothing's there, so confirm another way.
- When crawling the storage the brain itself lives in, exclude the brain's folder, or you'll index yourself.
- A crawl through one person's account sees their private material too. The sensitivity decisions still apply.

When a crawl will need redoing later (weekly re-syncs, a second person's account), write yourself a small script for it and keep it with this skill.

### Writing as you go

- **Write into the brain from the first pass.** During a build you may create, rename and move folders, the top level included, as the content requires. Log every structural change.
- **Shape follows the content and the reader questions.** If a structure helps you start, these work for many teams:
  - company: about, product, customers, market, decisions, projects, brand
  - research group: about, projects, papers, datasets, decisions, people
  - community: about, events, members, programs, decisions, resources

  Adapt them freely or ignore them. The user's way of thinking wins ("we think in customers, not markets"). Restructure as soon as you hear it, while it's cheap.
- **Pages most teams need early:** an overview, a people page (roles, who to ask about what), a glossary, how the team works, and a decision record for each decision you find.
- **No empty or placeholder folders.** A folder appears when its first page does.
- **Parallel writers need separate paths.** When several helpers draft at once, give each its own set of paths before they start, decision records included. A helper that needs a path it doesn't own hands back a note instead of writing there.
- **Keep the team record current as you go:** `_brain/team.md` with the profile, sensitivity decisions as they're made, and routing; `_brain/sources.md`; and the changelog.

### Showing the user

- Report progress as the system prompt describes.
- Once the first source lands, offer two or three questions the brain can now answer, so the user can try it.

### Saving progress

After every meaningful step, update your memory: the reader questions and how well each is answered, open leads, pending asks, declined sources, user preferences, and where you are. The session can end at any moment. The brain plus your memory must be enough to carry on without asking the user anything twice.

## Knowing when it's done

The build ends when the user says so, or when your judgement says the brain is ready for maintenance. Ready means:
- the reader questions that matter are mostly answered in the brain, with sources, a few steps from the entry points;
- the sources worth connecting have been read, or the user declined them;
- what's still open can only be settled by time or the team, not by more work now; and
- **the newcomer test passes.** Starting from `README.md` and `INDEX.md` only, answer "what is this team, who does what, what's being built, where do I find X?" for at least five varied X's. Aim for 80% or more found on the first path. Fix whatever was slow.

When you judge it ready, say so, show the final structure and what's still open, and let the user confirm or keep going.

## Handing off

1. Check the brain against the system prompt's guarantees: the index matches, links resolve, every page has its sources and labels, and nothing sensitive went in without a decision.
2. Move the unresolved leads and questions to your memory, marked for maintenance. Make sure `_brain/sources.md` lists every source with how deeply it was read and when.
3. Make sure maintenance will have everything it depends on, written down rather than only in this conversation: which accounts map to which sources, and the in-scope list.
4. Mark the build done in your memory, even if the session drifted into other topics. A build left half-closed will re-ask settled questions next time.
5. Write the first sync summary, the way the `maintain-brain` skill's Summarize step describes, with what the build added.
6. Ask the user whether to announce the brain to the team, and through which channel. If they say yes, keep it to a few lines: what's in the brain, how to contribute (message you), and that nothing is ever deleted, only archived. Also offer to send upkeep reports to a channel. It's optional: the sync summaries carry them either way.

## Adding a source later

When a source is connected after the build, read it the way this skill describes and file what it adds into the existing structure through the normal contribution process. No new structure proposal is needed unless it would change the top level.
