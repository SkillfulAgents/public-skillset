---
name: agent-onboarding
description: 'First-run setup for Release To Social Campaign: connects shipping sources, draft destination and Slack approvals, learns the voice, runs a drafts-only test on one past release, and sets the trigger or weekly sweep.'
---

# Release To Social Campaign onboarding

## 1. Welcome

Tell the user in three sentences: this agent watches what ships, keeps only customer-facing changes, drafts platform-specific posts and changelog notes, and sends them to an approver in Slack. Nothing is ever published without approval, and 72 hours after posts go live it reports how they did. Then show the plan:

1. Where shipping shows up (GitHub, Linear, a changelog).
2. Which releases count and what to leave out.
3. Which social accounts and formats.
4. Where drafts go (Postiz, Notion, or Google Docs).
5. Who approves, and where.
6. Your voice.
7. When it runs.
8. A drafts-only test on one past release.

Skip anything already answered in `## Your context` in `CLAUDE.md`.

## 2. Discover connections

Call `mcp__user-input__search_connection_options` for GitHub, Linear, Notion, Google Docs, Slack, X, LinkedIn, and Postiz. Note what is connected and the exact slugs. Call `mcp__chat__list_agent_integrations` to see whether the agent already has its own Slack app, email inbox, Telegram, or iMessage.

Mechanism rules:
- GitHub, Linear, Notion, Google Docs, X, LinkedIn: the user's connected account.
- Slack approvals: the agent's own Slack app (agent integration), not the user's Slack account.
- Postiz: no registry connector. Use a `POSTIZ_API_KEY` secret and its public API (plus the instance URL if self-hosted).

## 3. Ask, one question at a time

Use `AskUserQuestion` where the options are discrete.

1. **Sources.** Where does shipped work show up? (GitHub releases / GitHub merged PRs / Linear completed issues / A changelog page or file.) Which repositories or Linear teams? Is the repo public or private?
2. **What counts.** Which releases count (all, minor and major only, only ones tagged a certain way)? Any labels that always mean internal or always mean customer-facing?
3. **Accounts and platforms.** Which social accounts post these (X, LinkedIn company page, LinkedIn personal, Bluesky, Mastodon, Threads)?
4. **Formats.** Which two formats per story? (Social post + changelog note / Social post + blog blurb / Changelog note + blog blurb.)
5. **Draft destination.** (Postiz drafts / A Notion page per campaign / A Google Doc per campaign.)
6. **Approver.** Who approves, and where? (Their Slack DM from the agent / A review channel / The agent's email / In-app.) What counts as approval: a written "approve 1, 3" only, or also a checkmark reaction?
7. **Posting windows.** Preferred days and times per platform, and the timezone.
8. **Voice.** Ask for 3 to 5 past posts the user liked, and any words or claims to avoid. If Voice-Matched Drafts is installed, offer to pull its voice notes instead.
9. **Cadence.** On each release or merge (if GitHub offers a trigger), or a weekly sweep (default Monday 9:00)?
10. **Silence.** When nothing customer-facing shipped: say nothing, or send one line?
11. **Autonomy.** Confirm: "The agent drafts and proposes on its own. Nothing is published or scheduled without the approver's OK of the exact draft." Then ask whether, after approval, the agent may schedule approved drafts in Postiz, or should hand over copy-ready text only.
12. **Performance.** Which accounts can be read for the 72-hour summary (Postiz analytics, the user's X account, LinkedIn)?

## 4. Connect

- `mcp__user-input__request_connected_account` for `github`, and `linear`, `notion`, `googledocs`, `twitter`, `linkedin` as chosen. Reason text such as "Allow access to GitHub to read releases and merged pull requests for campaign drafts?"
- Postiz: `mcp__user-input__request_secret` with `POSTIZ_API_KEY` ("Add POSTIZ_API_KEY so the agent can save post drafts in Postiz?").
- Slack approvals: use the existing Slack integration, or set one up with `mcp__chat__list_available_integration_providers` and `mcp__chat__add_agent_integration` (or hand it over with `mcp__user-input__request_integration_setup`). Confirm with `list_agent_integrations`, then resolve the approver's user or channel with `mcp__chat__list_chat_users` / `list_chat_channels`.
- If X is used, read `/opt/gamut/docs/x.md` first.

## 5. Supervised dry run

Pick one recent past release (or last week's merges) with the user. Run routine 1 end to end as drafts only:
- show what was kept, grouped into stories, and what was left out and why;
- show the two formats per story and one variant per account;
- create the drafts in the chosen destination and send the review message to the user (not the approver) for this test.

Ask what was wrong: missed or wrongly included changes, tone, length, schedule. Update the filter labels and voice notes in `## Your context`, and redo once. Do not schedule anything to post. Add the test's source items to `/workspace/state/release-to-social-campaign/drafted.json` only if the user wants them treated as done.

## 6. Schedule and triggers

- If the user chose release or merge events: call `mcp__user-input__get_available_triggers` on the GitHub account, pick the release-published or PR-merged event if it exists, and set it up with `mcp__user-input__setup_trigger` for the chosen repositories. Never guess a trigger slug.
- Otherwise, or if no trigger exists: `mcp__user-input__schedule_task` with `scheduleType: "cron"`, default `0 9 * * 1` in the user's timezone.

Prompt template (self-contained):

> Run Release To Social Campaign routine 1 (ship-to-campaign drafts). Config: `/workspace/.claude/skills/agent-onboarding/config.json`. State: `/workspace/state/release-to-social-campaign/`. Follow `CLAUDE.md` and the `ship-filter-and-formats` skill. Collect what shipped since the high-water marks in `runs.json`, skip anything in `drafted.json`, draft to the configured destination, and send the review message with `send_chat_message` on integration `<id>` to `<approver>`. If nothing customer-facing shipped, follow the silence setting. Never publish, schedule, or post without explicit approval. If a source fails, say which one.

Confirm with `mcp__user-input__list_scheduled_tasks` and `mcp__user-input__list_triggers` and show the user the result. The 72-hour summaries are created later, per approved batch.

## 7. Save

Write the confirmed answers as short bullets under `## Your context` in `CLAUDE.md`. Write `.claude/skills/agent-onboarding/config.json`:

```json
{
  "timezone": "America/New_York",
  "sources": {
    "github": {"repos": ["org/repo"], "public": false, "events": ["release"], "default_branch": "main"},
    "linear": {"on": false, "teams": [], "done_states": ["Done"]},
    "changelog_url": ""
  },
  "release_rules": {"count": "minor_and_major", "internal_labels": ["internal", "no-changelog"], "customer_labels": ["feature"]},
  "accounts": [{"platform": "x", "handle": "@example"}, {"platform": "linkedin", "page": "Example Co"}],
  "formats": ["social_post", "changelog_note"],
  "draft_destination": {"type": "notion", "parent": ""},
  "postiz": {"on": false, "base_url": "", "schedule_after_approval": false},
  "approval": {"approver": "", "channel": "slack_dm", "integration_id": "", "destination": "", "reaction_counts": false},
  "posting_windows": {"x": ["Tue 10:00"], "linkedin": ["Tue 11:00"]},
  "voice": {"samples_file": "", "avoid": []},
  "cadence": {"mode": "trigger", "trigger_id": null, "cron": "0 9 * * 1"},
  "silence": "none",
  "performance_sources": ["postiz", "twitter"]
}
```

Finish with a short summary: what runs when, where drafts land, who approves, and that nothing is published without approval.
