---
name: gmail-inbox-screener
description: 'Fetch recent Gmail messages through the connected-account proxy, flag likely marketing versus important mail, and mark messages as read. First pass for every Inbox Manager sort.'
---

# Gmail Inbox Screener

Screen Gmail inboxes for recent emails, categorize them as important vs marketing/unimportant, and take actions like marking as read or sending replies.

The marketing flag is a keyword and label heuristic. Treat it as a first pass and apply the user's rules from `config.json` on top (see `CLAUDE.md`).

## Running the scripts on Gamut

- Connect Gmail first with `mcp__user-input__request_connected_account` (`gmail`). The runtime then provides `PROXY_BASE_URL`, `PROXY_TOKEN`, and `CONNECTED_ACCOUNTS` as environment variables. No API key or `.env` entry is needed.
- The scripts need `requests` and have no inline dependency block, so run them with `--with requests` and the absolute path. Do not pass `--env-file .env`: this agent stores no secrets, and `uv` exits with an error when the file does not exist.
- Some proxy calls pause for the user's approval in the app the first time. A slow response is not a failure.

## Scripts

### screen_inbox.py - Screen and categorize emails

Fetch recent emails and categorize them as important vs marketing/unimportant.

```bash
uv run --with requests /workspace/.claude/skills/gmail-inbox-screener/screen_inbox.py --hours 12
```

**Arguments:**
- `--hours N` - Look back N hours (default: 12)
- `--mark-read` - Mark marketing emails as read. Use only if the user opted in to marking noise as read.

Screens every connected Gmail account, up to 100 messages per account per run. Only unread messages appear in the output.

**Output:** JSON with `marketing_emails` and `important_emails` arrays, each containing email metadata (`id`, `thread_id`, `labels`, `from`, `subject`, `date`, `snippet`) and a Gmail link.

### gmail_actions.py - Take actions on emails

Mark emails as read or send replies.

**Mark as read:**
```bash
uv run --with requests /workspace/.claude/skills/gmail-inbox-screener/gmail_actions.py --action mark-read --email-id <message_id> --account <email>
```

**Send a reply (sends immediately):**
```bash
uv run --with requests /workspace/.claude/skills/gmail-inbox-screener/gmail_actions.py --action reply --email-id <message_id> --account <email> --reply-body "Your reply text"
```

The `reply` action sends the email at once; it does not create a draft. Inbox Manager never sends by default. Use it only when the user approves one exact reply in the conversation and asks you to send it. For pre-drafted replies, create a Gmail draft through the proxy instead (`POST .../gmail/v1/users/me/drafts`, described in `CLAUDE.md`).

**Arguments:**
- `--action` - Either `mark-read` or `reply`
- `--email-id` - Gmail message ID
- `--account` - Gmail account email address (the `name` in `CONNECTED_ACCOUNTS`)
- `--reply-body` - Reply text (required for reply action)

**Output:** JSON with success status and action details.

## Features

- Fetches emails from the last N hours
- Categorizes emails as important vs marketing/unimportant based on sender, subject, and labels
- Mark individual or bulk emails as read
- Send threaded replies that appear in the original conversation (approval required)
- Returns structured JSON output for easy processing

Labeling, archiving, and drafts are not in these scripts; make those calls through the proxy as described in `CLAUDE.md` under "Gmail operations".

## Requirements

- A connected Gmail account (`gmail`)
- `PROXY_BASE_URL`, `PROXY_TOKEN`, and `CONNECTED_ACCOUNTS`, all set by the runtime once Gmail is connected
