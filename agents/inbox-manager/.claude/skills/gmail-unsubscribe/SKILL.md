---
name: gmail-unsubscribe
description: 'Find the unsubscribe link for a Gmail marketing message (List-Unsubscribe header first, then body links) so an approved unsubscribe can be completed in the browser.'
---

# Gmail Unsubscribe

Unsubscribe from marketing emails by extracting unsubscribe links from email bodies and returning them for browser automation.

Only use this for senders the user has approved one by one. Never for banks, utilities, schools, government senders, paid services, or transactional mail.

## Usage

```bash
uv run --with requests /workspace/.claude/skills/gmail-unsubscribe/find_unsubscribe.py --email-id <message_id> --account <account_email>
```

The script needs `requests` and has no inline dependency block, hence `--with requests`. Do not pass `--env-file .env`: this agent stores no secrets, and `uv` exits with an error when the file does not exist. `PROXY_BASE_URL`, `PROXY_TOKEN`, and `CONNECTED_ACCOUNTS` are set by the runtime once Gmail is connected.

## Features

- Fetches full email body from Gmail API
- Extracts unsubscribe links from:
  - List-Unsubscribe headers (HTTP links only; `mailto:` entries are ignored)
  - HTML body links containing "unsubscribe"
  - Plain text URLs containing "unsubscribe"
- Returns the best unsubscribe link for browser automation

## Completing the unsubscribe on Gamut

1. Prefer `list_unsubscribe_header` when present; otherwise use `unsubscribe_url`.
2. Open it with `mcp__browser__browser_open`, then delegate the clicks to the `web-browser` subagent with a narrow brief: confirm the unsubscribe for this address, take no other action.
3. If a CAPTCHA appears, use `mcp__user-input__request_browser_input`. If the page asks the user to sign in or enter anything beyond confirming their email address, stop and report it to the user instead.
4. Record the sender, date, and result in `/workspace/state/inbox-manager/unsubscribes.json`. If the sender's mail keeps arriving after a week, suggest a skip-list rule.

If no link is found (`unsubscribe_url` is null), suggest a skip-list rule instead.

## Requirements

- A connected Gmail account (`gmail`)
- `PROXY_BASE_URL`, `PROXY_TOKEN`, and `CONNECTED_ACCOUNTS`, all set by the runtime once Gmail is connected

## Output

Returns JSON with:
- `unsubscribe_url`: The extracted unsubscribe URL
- `list_unsubscribe_header`: The HTTP link from the `List-Unsubscribe` header, if any
- `all_unsubscribe_links`: Every candidate link found in the body
- `subject`: Email subject for confirmation
- `from`: Sender email
