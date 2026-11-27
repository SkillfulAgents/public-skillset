---
name: x-incremental-pull
description: 'How to pull only new X bookmarks and likes through the user''s twitter connected account, read threads and quoted posts cheaply, stop at already-seen items, and estimate the cost. Use on every X Bookmark Sweep run and when giving the onboarding cost estimate.'
---

# Incremental X pull

Read `/opt/gamut/docs/x.md` first. It is the allowlist of paths and the source of current prices; if a price below differs from the doc, the doc wins.

## Base

```
$PROXY_BASE_URL/<account_id>/api.x.com
Authorization: Bearer $PROXY_TOKEN
```

`<account_id>` is the `twitter` entry in `CONNECTED_ACCOUNTS`. The user's X user ID is stored in `config.json` (`x_user_id`). Look it up with `GET /2/users/me` only if it is missing.

## Fields to request

`tweet.fields=created_at,conversation_id,author_id,note_tweet,entities,referenced_tweets`

Add `expansions=author_id&user.fields=username` only if the run needs handles for links and attribution. Each distinct author adds a billed user object, so cache handles in `/workspace/state/x-bookmark-sweep/authors.json` and skip the expansion when every author ID in the page is already cached. Links of the form `https://x.com/i/status/<id>` work without a handle.

## Bookmarks

`GET /2/users/<x_user_id>/bookmarks?max_results=<page>&tweet.fields=...`

- Returned newest first. No since filter exists.
- First page size: the config `page_size` (default 20).
- Walk the page in order. Stop at the first post ID already in `seen.json` under `bookmarks`, and also stop after the config `max_pages` (default 3) or `max_items_per_run` (default 60).
- If the first page has no seen IDs and the cap is hit, record "possible backlog" in the run log and mention it in the recap instead of continuing.

## Likes

`GET /2/users/<x_user_id>/liked_tweets?max_results=<page>&tweet.fields=...`

- Ordered by when the user liked them, newest first, but the like time itself is not returned.
- Same stop rule against `seen.json` under `likes`.
- Skip entirely if likes are disabled in config.

## Threads

For a saved post with `conversation_id` different from its own ID, or a post that looks like the start of a thread:
- If `created_at` is within the last 7 days: `GET /2/tweets/search/recent?query=conversation_id:<cid> from:<author_id>&max_results=<n>` with a small `n` (default 25), then order by `created_at`.
- If older: recent search cannot reach it. Use what you have and mark the entry "thread not fully retrieved".
- For the thread's first post when the user saved a later one: `GET /2/tweets/<conversation_id>`.

## Quoted posts

If `referenced_tweets` has `type: quoted` and the saved post depends on it, `GET /2/tweets?ids=<id1>,<id2>` in one batched call.

## Errors

- `429`: read `x-rate-limit-reset`, wait until then, retry once, then stop and record.
- `402`: stop the run, tell the user the workspace needs a top-up for platform services.
- `403` with `account_reauth_dismissed`: stop and ask the user to reconnect X.
- `404`: the path is not on the allowlist. Do not try alternates.

## Cost estimate

Per run, approximately:

```
posts   = new_bookmarks + new_likes + (thread_posts_fetched) + (quoted_posts_fetched) + (overlap: seen items returned on the stop page)
users   = new distinct authors not in the cache (only when the expansion is used)
cost    = posts x price_per_post + users x price_per_user
weekly  = cost x runs_per_week
```

Use the prices in `/opt/gamut/docs/x.md` (at the time of writing $0.005 per post, $0.010 per user). Worked example, clearly labeled as an estimate: 10 new bookmarks and 15 new likes per run, 3 threads of about 6 posts, 2 quoted posts, 5 already-seen posts on the stop page, 15 new authors:

```
posts = 10 + 15 + 18 + 2 + 5 = 50  ->  50 x 0.005 = 0.25
users = 15                         ->  15 x 0.010 = 0.15
per run about 0.40; three runs a week about 1.20; about 5 per month
```

The first run is the expensive one if it backfills. Offer the user a choice: start from today (cheapest), the last 50 items, or a bigger backfill, and quote each one before pulling.
