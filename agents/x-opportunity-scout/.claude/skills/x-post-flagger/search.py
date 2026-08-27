# /// script
# dependencies = ["requests"]
# ///
"""Search X for posts matching the opportunity query bank in queries.json.

Two providers, same output shape:
  --provider builtin     (default) Gamut's built-in X API. Works out of the box,
                         no keys needed. Billed per object returned:
                         $0.005/post + $0.010/distinct author.
  --provider twitterapi  twitterapi.io advanced search (BYOK, cheaper reads:
                         ~$0.15/1k tweets). Needs TWITTERAPI_IO_KEY in .env.

Usage:
  uv run --env-file /workspace/.env search.py --since-hours 24 --out /tmp/candidates.json
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

TWITTERAPI_URL = "https://api.twitterapi.io/twitter/tweet/advanced_search"

CRYPTO_NOISE = [
    "crypto", "token", "airdrop", "web3", "solana", "defi", "nft", "presale",
    "$", "onchain", "on-chain", "memecoin", "staking", "pump", "tokenomics",
    "eth", "btc", "blockchain", "dex ", "swap",
]

LAUNCH_MARKERS = (
    "we're launching", "we are launching", "just launched", "just shipped",
    "today we're launching", "today we launched", "introducing ",
    "now available", "now live", "we're shipping", "we just shipped",
)


def load_queries(path):
    with open(path) as f:
        bank = json.load(f)
    return bank["queries"], bank["common_exclusions"]


def crypto_score(text):
    t = (text or "").lower()
    return sum(1 for k in CRYPTO_NOISE if k in t)


def is_launch_announcement(text):
    t = (text or "").lower()
    return any(k in t for k in LAUNCH_MARKERS)


# ---------------- built-in provider (Gamut X proxy, official v2 shape) ----------------

def builtin_base():
    base = os.environ.get("ANTHROPIC_BASE_URL")
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if not base or not token:
        sys.exit("built-in X API env not available (ANTHROPIC_BASE_URL / ANTHROPIC_AUTH_TOKEN)")
    return f"{base}/v1/x", {"Authorization": f"Bearer {token}"}


def run_query_builtin(q, since_dt, max_pages, page_size):
    url, headers = builtin_base()
    params = {
        "query": q,
        "max_results": page_size,
        "start_time": since_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "tweet.fields": "created_at,public_metrics,referenced_tweets,lang",
        "expansions": "author_id,referenced_tweets.id",
        "user.fields": "username,name,description,public_metrics",
    }
    tweets, users, ref_tweets = [], {}, {}
    next_token = None
    for _ in range(max_pages):
        if next_token:
            params["next_token"] = next_token
        r = requests.get(f"{url}/2/tweets/search/recent", params=params, headers=headers, timeout=30)
        if r.status_code == 429:
            reset = int(r.headers.get("x-rate-limit-reset", "0"))
            wait = max(0, reset - int(time.time()))
            if wait > 120:
                print(f"rate limited, reset in {wait}s — skipping rest of query", file=sys.stderr)
                break
            time.sleep(wait + 1)
            r = requests.get(f"{url}/2/tweets/search/recent", params=params, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        tweets.extend(data.get("data") or [])
        inc = data.get("includes") or {}
        for u in inc.get("users") or []:
            users[u["id"]] = u
        for rt in inc.get("tweets") or []:
            ref_tweets[rt["id"]] = rt
        next_token = (data.get("meta") or {}).get("next_token")
        if not next_token:
            break
        time.sleep(0.3)
    return tweets, users, ref_tweets


def normalize_builtin(t, users, ref_tweets, now):
    author = users.get(t.get("author_id"), {})
    metrics = t.get("public_metrics") or {}
    a_metrics = author.get("public_metrics") or {}
    created = datetime.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc) \
        if "." in t["created_at"] else \
        datetime.strptime(t["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    quoted_id, quoted_text = None, ""
    for ref in t.get("referenced_tweets") or []:
        if ref.get("type") == "quoted":
            quoted_id = ref.get("id")
            quoted_text = (ref_tweets.get(quoted_id) or {}).get("text", "")
    username = author.get("username")
    return {
        "id": t["id"],
        "url": f"https://x.com/{username}/status/{t['id']}" if username else f"https://x.com/i/status/{t['id']}",
        "text": t.get("text"),
        "created_at": created.isoformat(),
        "age_hours": round((now - created).total_seconds() / 3600, 1),
        "likes": metrics.get("like_count", 0),
        "replies": metrics.get("reply_count", 0),
        "views": metrics.get("impression_count", 0),
        "author": username,
        "author_name": author.get("name"),
        "author_followers": a_metrics.get("followers_count", 0),
        "author_bio": author.get("description", ""),
        "is_quote": quoted_id is not None,
        "quoted_id": quoted_id,
        "quoted_author": None,
        "quoted_text": (quoted_text[:400] or None),
        "quotes_launch": is_launch_announcement(quoted_text),
    }


# ---------------- twitterapi.io provider (BYOK) ----------------

def run_query_twitterapi(key, q, since_dt, max_pages):
    query = f"{q} since:{since_dt.strftime('%Y-%m-%d_%H:%M:%S_UTC')}"
    tweets, cursor = [], ""
    for _ in range(max_pages):
        r = requests.get(
            TWITTERAPI_URL,
            params={"query": query, "queryType": "Latest", "cursor": cursor},
            headers={"X-API-Key": key},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        tweets.extend(data.get("tweets") or [])
        if not data.get("has_next_page") or not data.get("next_cursor"):
            break
        cursor = data["next_cursor"]
        time.sleep(0.3)
    return tweets


def normalize_twitterapi(t, now):
    author = t.get("author") or {}
    created = datetime.strptime(t["createdAt"], "%a %b %d %H:%M:%S %z %Y")
    quoted = t.get("quoted_tweet") or {}
    quoted = quoted if isinstance(quoted, dict) else {}
    quoted_author = quoted.get("author") or {}
    quoted_text = quoted.get("text") or ""
    return {
        "id": t.get("id"),
        "url": t.get("url"),
        "text": t.get("text"),
        "created_at": created.isoformat(),
        "age_hours": round((now - created).total_seconds() / 3600, 1),
        "likes": t.get("likeCount", 0),
        "replies": t.get("replyCount", 0),
        "views": t.get("viewCount", 0),
        "author": author.get("userName"),
        "author_name": author.get("name"),
        "author_followers": author.get("followers", 0),
        "author_bio": author.get("description", ""),
        "is_quote": bool(t.get("isQuote")),
        "quoted_id": quoted.get("id"),
        "quoted_author": quoted_author.get("userName"),
        "quoted_text": (quoted_text[:400] or None),
        "quotes_launch": is_launch_announcement(quoted_text),
        "_is_reply": bool(t.get("isReply")),
        "_is_retweet": bool(t.get("isRetweet")),
    }


# ---------------- main ----------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["builtin", "twitterapi"], default="builtin")
    ap.add_argument("--since-hours", type=float, default=24)
    ap.add_argument("--max-pages", type=int, default=1)
    ap.add_argument("--page-size", type=int, default=25, help="builtin only: posts per page (10-100)")
    ap.add_argument("--min-followers", type=int, default=150)
    ap.add_argument("--no-crypto-filter", action="store_true",
                    help="disable the crypto-noise filter (use if the product IS crypto/web3)")
    ap.add_argument("--out", default="-")
    ap.add_argument("--queries", default=os.path.join(os.path.dirname(__file__), "queries.json"))
    args = ap.parse_args()

    queries, exclusions = load_queries(args.queries)
    excl = exclusions[args.provider] if isinstance(exclusions, dict) else exclusions
    since_dt = datetime.now(timezone.utc) - timedelta(hours=args.since_hours)
    now = datetime.now(timezone.utc)

    key = None
    if args.provider == "twitterapi":
        key = os.environ.get("TWITTERAPI_IO_KEY")
        if not key:
            sys.exit("TWITTERAPI_IO_KEY not set — add it to /workspace/.env or use --provider builtin")

    seen, out, billed_posts = {}, [], 0
    for spec in queries:
        q = f"{spec['q']} {excl}".strip()
        try:
            if args.provider == "builtin":
                raw, users, ref_tweets = run_query_builtin(q, since_dt, args.max_pages, args.page_size)
                billed_posts += len(raw)
                recs = [normalize_builtin(t, users, ref_tweets, now) for t in raw]
            else:
                raw = run_query_twitterapi(key, q, since_dt, args.max_pages)
                recs = [normalize_twitterapi(t, now) for t in raw]
        except Exception as e:
            print(f"query failed [{spec['category']}]: {e}", file=sys.stderr)
            continue

        for rec in recs:
            tid = rec.get("id")
            if not tid:
                continue
            if tid in seen:
                seen[tid]["categories"].append(spec["category"])
                continue
            if rec.pop("_is_reply", False) or rec.pop("_is_retweet", False):
                continue
            created = datetime.fromisoformat(rec["created_at"])
            if created < since_dt:
                continue
            if rec["author_followers"] < args.min_followers:
                continue
            if not args.no_crypto_filter:
                noise = crypto_score(rec["text"]) + crypto_score(rec["author_bio"])
                if noise >= 3:
                    continue
                rec["crypto_noise"] = noise
            rec["categories"] = [spec["category"]]
            seen[tid] = rec
            out.append(rec)
        print(f"[{spec['category']}] {spec['q'][:60]}... -> {len(raw)} tweets", file=sys.stderr)

    out.sort(key=lambda r: r["created_at"], reverse=True)
    payload = json.dumps(out, indent=1)
    if args.out == "-":
        print(payload)
    else:
        with open(args.out, "w") as f:
            f.write(payload)
        print(f"{len(out)} unique candidates -> {args.out}", file=sys.stderr)
    if args.provider == "builtin" and billed_posts:
        print(f"builtin billing: ~{billed_posts} posts returned (~${billed_posts * 0.005:.2f} + authors)", file=sys.stderr)


if __name__ == "__main__":
    main()
