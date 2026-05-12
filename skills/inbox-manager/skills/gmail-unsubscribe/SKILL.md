# Gmail Unsubscribe

Unsubscribe from marketing emails by extracting unsubscribe links from email bodies and returning them for browser automation.

## Usage

```bash
uv run --env-file .env find_unsubscribe.py --email-id <message_id> --account <account_email>
```

## Features

- Fetches full email body from Gmail API
- Extracts unsubscribe links from:
  - List-Unsubscribe headers
  - HTML body links containing "unsubscribe"
  - Plain text URLs containing "unsubscribe"
- Returns the best unsubscribe link for browser automation

## Requirements

- `PROXY_BASE_URL` and `PROXY_TOKEN` environment variables
- `CONNECTED_ACCOUNTS` environment variable with Gmail account metadata

## Output

Returns JSON with:
- `unsubscribe_url`: The extracted unsubscribe URL
- `subject`: Email subject for confirmation
- `from`: Sender email
