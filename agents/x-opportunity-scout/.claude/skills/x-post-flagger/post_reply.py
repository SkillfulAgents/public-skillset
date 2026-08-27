# /// script
# dependencies = ["requests", "requests-oauthlib"]
# ///
"""Post a reply to X via the official API (OAuth 1.0a user context, BYOK).

Optional: requires the user's own X developer app keys in /workspace/.env
(X_API_KEY / X_API_SECRET / X_ACCESS_TOKEN / X_ACCESS_TOKEN_SECRET).

X POLICY LIMITATION (since 2026-02-23): the API only allows replies to posts
whose author mentioned/quoted the authenticated account — cold replies to
discovered posts return 403 and must be posted manually or via the user's
logged-in browser session. Do not retry the API for cold replies.

SAFETY RULE: Only run this when the user has EXPLICITLY approved posting this
exact reply in this conversation. Never call from automated/scheduled runs.

Usage:
  uv run --env-file /workspace/.env post_reply.py --reply-to <tweet_id> --text "reply text"
  uv run --env-file /workspace/.env post_reply.py --verify   # check credentials, posts nothing
"""
import argparse
import json
import os
import sys

import requests
from requests_oauthlib import OAuth1

def auth():
    return OAuth1(
        os.environ["X_API_KEY"],
        os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"],
        os.environ["X_ACCESS_TOKEN_SECRET"],
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reply-to", help="tweet ID to reply to")
    ap.add_argument("--text", help="reply text (<=280 chars)")
    ap.add_argument("--verify", action="store_true", help="verify credentials only")
    args = ap.parse_args()

    if args.verify:
        r = requests.get("https://api.x.com/2/users/me", auth=auth(), timeout=30)
        print(r.status_code, r.text[:500])
        sys.exit(0 if r.ok else 1)

    if not args.reply_to or not args.text:
        sys.exit("need --reply-to and --text (or --verify)")
    if len(args.text) > 280:
        sys.exit(f"text is {len(args.text)} chars (max 280)")

    r = requests.post(
        "https://api.x.com/2/tweets",
        auth=auth(),
        json={"text": args.text, "reply": {"in_reply_to_tweet_id": args.reply_to}},
        timeout=30,
    )
    print(r.status_code, r.text[:800])
    if r.ok:
        tid = r.json()["data"]["id"]
        print(f"posted: https://x.com/i/status/{tid}")
    sys.exit(0 if r.ok else 1)

if __name__ == "__main__":
    main()
