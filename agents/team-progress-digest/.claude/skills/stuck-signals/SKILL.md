---
name: stuck-signals
description: 'Queries for pulling recent PR and issue activity from GitHub, Linear, and Jira, and the rules for flagging an item as stuck or waiting on a decision. Use on every Team Progress Digest run.'
---

# Stuck signals

All thresholds are in business days and can be overridden in config (`stuck_thresholds`).

## Stuck rules

| Signal | Default threshold |
|---|---|
| PR open with a review requested and no review | 2 days |
| PR with changes requested and no new commits since | 3 days |
| PR with failing required checks | 1 day |
| PR with merge conflicts | 2 days |
| Draft PR with no commits | 5 days |
| Issue in a started state with no update, comment, or linked PR activity | 5 days |
| Issue in a review state | 3 days |
| Issue marked blocked, or with an open blocking relation | immediately |
| Issue past its due date and not completed | immediately |
| Issue moved back and forth between states 3+ times this week | immediately |

## Waiting-on-a-decision rules

Flag as **Needs you** when any of these hold:
- a label or status matching config `decision_labels` (defaults: "needs decision", "needs-decision", "blocked: decision", "question");
- a comment mentions the user and asks a question, and the user hasn't replied since;
- the user is a requested reviewer on an open PR;
- the blocking item or blocker named in a comment is owned by the user.

## Exclusions

Skip items whose assignee is out of office (config `ooo` or a shared OOO calendar), items in an "icebox" or backlog state, and archived repos. Automated authors (names ending in `[bot]`, plus config `automation_authors`) are collapsed into one line.

## Queries

Use the high-water mark `since` (ISO 8601) from `runs.json`.

**GitHub** (REST via the proxy, `api.github.com`):
- Merged: `GET /search/issues?q=is:pr+is:merged+merged:>=<since>+org:<org>` (or `repo:<owner>/<name>` per repo).
- Opened: `GET /search/issues?q=is:pr+created:>=<since>+org:<org>`.
- Open queue: `GET /search/issues?q=is:pr+is:open+org:<org>+draft:false`.
- Review state: `GET /repos/{owner}/{repo}/pulls/{number}/reviews` and `requested_reviewers` on the PR object.
- Checks: `GET /repos/{owner}/{repo}/commits/{sha}/check-runs`.
- Mergeability: `mergeable` and `mergeable_state` on `GET /repos/{owner}/{repo}/pulls/{number}` (may be null on first read; read again later in the run).
Search returns at most 1,000 results per query; narrow the date range if `total_count` is higher.

**Linear** (GraphQL at `api.linear.app/graphql`):
```graphql
query($since: DateTimeOrDuration!, $teams: [String!]) {
  issues(first: 100, filter: {updatedAt: {gte: $since}, team: {key: {in: $teams}}}) {
    nodes {
      identifier title url priority dueDate updatedAt startedAt completedAt
      state { name type }
      assignee { name email }
      project { name }
      labels { nodes { name } }
      relations { nodes { type relatedIssue { identifier state { type } } } }
      inverseRelations { nodes { type issue { identifier state { type } } } }
      attachments { nodes { url } }
    }
    pageInfo { hasNextPage endCursor }
  }
}
```
State `type` values: `triage`, `backlog`, `unstarted`, `started`, `completed`, `canceled`. A relation of type `blocks` in `inverseRelations` whose blocking issue is not completed means this issue is blocked. Page with `after: endCursor`.

**Jira** (`POST /rest/api/3/search/jql` on the site's API host):
- Completed: `project in (<keys>) AND statusCategory = Done AND statusCategoryChangedDate >= "<since date>"`
- Active: `project in (<keys>) AND statusCategory = "In Progress"`
- Flagged: `project in (<keys>) AND Flagged is not EMPTY`
- Overdue: `project in (<keys>) AND duedate < now() AND statusCategory != Done`
Request `fields=summary,status,assignee,duedate,updated,labels,issuelinks` and page with `nextPageToken`.

## Linking PRs to issues

Match in this order: Linear attachments or the GitHub URL in the issue; issue key in the branch name (`eng-123-...`, `OPS-45-...`); issue key or `Closes #n` / `Fixes #n` in the PR title or body. Present a matched pair once, under the issue's project.
