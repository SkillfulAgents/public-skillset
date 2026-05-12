# Gmail Inbox Screener

Screen Gmail inboxes for recent emails, categorize them as important vs marketing/unimportant, and take actions like marking as read or sending replies.

## Scripts

### screen_inbox.py - Screen and categorize emails

Fetch recent emails and categorize them as important vs marketing/unimportant.

```bash
uv run --env-file .env screen_inbox.py --hours 12 --mark-read
```

**Arguments:**
- `--hours N` - Look back N hours (default: 12)
- `--mark-read` - Mark marketing emails as read

**Output:** JSON with `marketing_emails` and `important_emails` arrays, each containing email metadata and links.

### gmail_actions.py - Take actions on emails

Mark emails as read or send replies.

**Mark as read:**
```bash
uv run --env-file .env gmail_actions.py --action mark-read --email-id <message_id> --account <email>
```

**Send a reply:**
```bash
uv run --env-file .env gmail_actions.py --action reply --email-id <message_id> --account <email> --reply-body "Your reply text"
```

**Arguments:**
- `--action` - Either `mark-read` or `reply`
- `--email-id` - Gmail message ID
- `--account` - Gmail account email address
- `--reply-body` - Reply text (required for reply action)

**Output:** JSON with success status and action details.

## Features

- Fetches emails from the last N hours
- Categorizes emails as important vs marketing/unimportant based on sender, subject, and labels
- Mark individual or bulk emails as read
- Send threaded replies that appear in the original conversation
- Returns structured JSON output for easy processing

## Requirements

- `PROXY_BASE_URL` and `PROXY_TOKEN` environment variables
- `CONNECTED_ACCOUNTS` environment variable with Gmail account metadata
