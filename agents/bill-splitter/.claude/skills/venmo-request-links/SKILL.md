---
name: venmo-request-links
description: 'How to build prefilled Venmo request (charge) links for each person''s share, how to encode them, and how to check the format still works before relying on it.'
---

# Venmo request links

Venmo has no public API for personal payments, and you must never hold Venmo credentials. Instead you build a link. When the user taps it on their phone, the Venmo app opens with the request already filled in, and the user reviews it and taps Request. Nothing moves until the user taps.

## Formats

Venmo does not formally document these formats, and they have changed before. These are the community-documented forms as of 2026:

| Form | Example | Notes |
|---|---|---|
| App deep link | `venmo://paycharge?txn=charge&recipients=alex-r&amount=42.17&note=Electric-Aug-2026` | Opens the Venmo app directly. Works only on a phone with Venmo installed; most email clients show it as plain text, so put it behind a button or link text. |
| Web link | `https://venmo.com/?txn=charge&recipients=alex-r&amount=42.17&note=Electric-Aug-2026` | Clickable everywhere. On a phone it hands off to the app. On a desktop it may only open the Venmo website, which cannot start the transaction. |
| Web link, user in path | `https://venmo.com/alex-r?txn=charge&amount=42.17&note=Electric-Aug-2026` | Same behavior. |

Parameters:
- `txn=charge` means a request; `txn=pay` would send money. **Always use `charge`. Never build a `pay` link.**
- `recipients`: a Venmo username without the `@`, a phone number or an email address. Use one recipient per link so each person gets their own amount.
- `amount`: a plain decimal with 2 places, no `$` and no thousands separator (`1250.00`, not `$1,250`).
- `note`: URL-encoded with `%20` for spaces, not `+`. Keep it short and with no account numbers: `<Bill>-<Mon>-<YYYY>`, for example `Electric-Aug-2026`. Use the service month, not the month the email arrived, unless the user prefers otherwise.
- `audience=private` is optional and keeps the request off the public feed. Include it unless the user says otherwise.

In each summary, include both the app deep link (labelled "Open in Venmo app") and the web link (labelled "Web link") for every person, because neither works in every client.

## Build them

```python
from urllib.parse import quote

def venmo_links(recipient: str, amount_cents: int, note: str) -> dict:
    amount = f"{amount_cents // 100}.{amount_cents % 100:02d}"
    q = (f"txn=charge&audience=private&recipients={quote(recipient, safe='')}"
         f"&amount={amount}&note={quote(note, safe='')}")
    return {"app": f"venmo://paycharge?{q}", "web": f"https://venmo.com/?{q}"}
```

Work in cents end to end (see the splitting rules in `AGENTS.md`) so the shares add up exactly to the bill.

## Verify on first run, and whenever in doubt

1. Before the first real summary, search the web (`mcp__web__web_search`) for current reports on Venmo payment links and deep links. If anything suggests the format changed or stopped working, tell the user, and switch to a fallback until it's resolved.
2. Ask the user to tap one test link on their phone (a $0.01 request to themselves or a test recipient that they cancel in the app) and confirm the request screen opened with the right person, amount and note.
3. Record the verified format and date in `/workspace/state/bill-splitter/venmo-format.json`. Re-verify if the user reports a link that didn't work, or every 6 months.

## Fallbacks

- If the links stop working: list each person's Venmo handle, amount and note as copy-ready text.
- Splitwise: if the user prefers it, create the expense in Splitwise through the `splitwise` connected account instead. Splitwise records who owes what; it doesn't move money.
