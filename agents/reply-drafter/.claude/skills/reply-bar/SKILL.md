---
name: reply-bar
description: 'The bar a post on X must clear to make the morning reply shortlist, how to rank candidates, the voice rules for drafts, reply vs. quote post, and the cost-controlled query plan. Use on every Reply Drafter run.'
---

# Reply bar

Read `/opt/gamut/docs/x.md` first. It is the allowlist of paths and the source of current prices; if a number here differs, the doc wins.

## Query plan (cheapest, highest-value first)

Base: the `twitter` connected account (`$PROXY_BASE_URL/<account_id>/api.x.com`) if connected, otherwise built-in reads (`$PLATFORM_BASE_URL/v1/x`). Fields on every post call: `tweet.fields=created_at,author_id,conversation_id,in_reply_to_user_id,referenced_tweets,public_metrics,lang`. Add `expansions=author_id&user.fields=username,name` only when an author is not in `users.json`.

| Order | Call | Limits |
|---|---|---|
| 1 | `GET /2/users/{me}/mentions?since_id=<mentions>` | `max_results` 20 |
| 2 | `GET /2/users/{me}/tweets?since_id=<own>` | `max_results` 10; only to find what the user already replied to |
| 3 | `GET /2/tweets/search/recent?query=(from:a OR from:b …) -is:retweet&since_id=<watch>` | `max_results` 30; split into two queries if the query passes ~500 characters |
| 4 | per topic: `GET /2/tweets/search/recent?query=<topic> -is:retweet -is:reply lang:<lang> <exclusions>&since_id=<topic>` | `max_results` 10 each |

- First run with no `since_id`: use `start_time` = 24 hours ago instead.
- Recent search covers 7 days only. There is no archive search.
- Keep a running cost total (posts returned × per-post price, users × per-user price). Stop before a call would push the run past `budget_usd_per_run`, and note it in the footer.
- Store the newest ID from each call as the next `since_id`, even if nothing was shortlisted.

## Disqualify first

Drop a candidate if any is true:
- Already in `shortlisted.json`, or the user already replied in that conversation (from call 2).
- Engagement bait: "reply with…", "drop your link", "tag someone", giveaways, follow-for-follow, reach polls, "agree?" one-liners.
- Rage-bait, dunks, pile-ons, or a reply that would mainly argue with a stranger.
- Politics or other hot-button topics, unless `politics_opt_in` is true.
- Older than 48 hours (24 for topic posts), unless it is an unanswered direct question to the user.
- From automated, spam, or obviously promotional accounts; or a thank-you tag that needs no answer.
- A crowded thread (roughly 100+ replies) where a reply would be buried. Consider a quote post instead, or skip.
- Text the user could not reply to credibly given what you know about them.

## Qualify: the four reasons

A survivor must match at least one. Write the matched reason as the one-line "why".
1. **Mention needing a response**: a real person asked or told the user something directly.
2. **Question the user can answer well**: squarely in their stated expertise.
3. **Conversation to join**: an active thread among people the user respects, on their topics, where the user has a distinct angle.
4. **Relationship to build**: a watch-list person posted something personal or substantive where a thoughtful reply moves the relationship forward.

## Rank

Mentions with a direct question → watch-list relationship posts → answerable questions → conversations. Within a tier: fresher first, then fewer existing replies. Keep the top N (default 5, minimum 0). Never pad to reach 3.

## Draft rules

- Lead with substance: an answer, a specific experience, a number the user has stated publicly, a resource, or a sharp question. No openers like "Great post!", "Love this", "100%".
- Match `voice.md`: typical length, casing, punctuation, emoji and hashtag habits (none unless the user uses them), how they disagree.
- Under 280 characters unless the user writes long posts. One idea per draft.
- Missing fact → bracketed gap (`[link to your write-up]`) and mention it in the why line. Never invent.
- No links unless needed; they cost the user more to post via the API and get less reach.

**Reply or quote post.** Reply when the poster is the audience (mentions, relationships, questions). Quote post when the user's take is useful to their own followers, the thread is crowded, or the user is adding a counterpoint they want on their own timeline.

## Message format

```
Your X shortlist, Fri Nov 20 (3)

1. @handle (Name), 5h. Mention needing a response
   "excerpt…" https://x.com/handle/status/123
   Reply: draft text

2. ...

Checked 12 mentions, 7 watch-list accounts, 2 topics. ~$0.38.
```
