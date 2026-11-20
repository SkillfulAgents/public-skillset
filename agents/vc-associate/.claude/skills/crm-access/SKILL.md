---
name: crm-access
description: 'How to read deal, portfolio and LP records from the CRM the user chose: Affinity through an API key or the browser, Attio or HubSpot through a connected account, or a Google Sheet fallback. Use before any CRM read or deal-tracker write.'
---

# CRM access

Check `config.json` for `crm.deals` and `crm.lps` (they can differ: many funds keep deals in Affinity and LPs in a separate sheet or tool). Always call `mcp__user-input__search_connection_options` for the service before requesting anything.

## Affinity

Affinity is not in the connector registry, so there is no connected account. Two routes:

1. **API key (preferred).** Ask with `mcp__user-input__request_secret`, `secretName: "AFFINITY_API_KEY"`, reason "Add AFFINITY_API_KEY so the agent can read your Affinity lists and relationship history?". The user creates the key in Affinity under Settings, then Manage Apps. API access requires a paid Affinity tier that includes it; if the user's plan doesn't, use the browser route.
   - Base URL `https://api.affinity.co/`. Send the key as a bearer token (`Authorization: Bearer $AFFINITY_API_KEY`); API v1 also accepts it as the basic-auth password with an empty username.
   - v1 covers people, organizations, lists and list entries, field values, notes and interactions. v2 (`/v2/...`) is faster for reading lists and saved views and writing list-entry fields. Check the current reference with web search before the first call; don't guess endpoint shapes.
   - Run scripts with `uv run --env-file /workspace/.env ...`. Never print the key.
   - Changes made through the API are attributed to the key owner, so writes look like the user. Only write to the deal list the user named, never to an LP list.
   - Respect rate limits: page through lists, cache list and field IDs in `/workspace/state/affinity-ids.json`.
2. **Browser.** `mcp__browser__browser_open` the Affinity web app, `mcp__user-input__request_login` for sign-in, `mcp__user-input__request_browser_input` for 2FA, then hand the page reads to the `web-browser` subagent. Read-only by default; this route is slow, so use it for LP briefs and the monthly digest, not for per-email deal logging.

Affinity's relationship data (last email, last meeting, strongest connection at a firm) is what LP Meeting Prep and LP Re-Engagement need most. Use those fields for "days since last contact" instead of recomputing from mail when available.

## Attio

Connected account `attio`. Read companies, people and list entries (deal pipeline list, LP list) through the proxy. Write only to the deal list.

## HubSpot

Connected account `hubspot`. Deals pipeline for deal flow; contacts and companies with a custom property or list for LPs. Notes and engagements give the last-interaction history. Writes are limited to deal records in the pipeline the user named.

## Google Sheet fallback

Connected account `googlesheets`. Deal tracker header row (create it if the sheet doesn't exist):

`Company | Website | One-liner | Sector | Stage | Round size | Stated terms | Location | Founders | Founder emails | Source type | Introducer | Deck link | Data room link | Opened? | Priority | Priority reason | Status | First seen | Last update | Thread ID | Notes`

An LP sheet, if used: `LP | Firm | Type | Fund or vehicle | Commitment status | Commitment amount | Contacts | Interests and handling notes | Last contact | Open follow-ups | Do not contact`.

## Rules for every CRM

- LP data is read-only.
- Record only what the source states. "Not recorded" beats a guess.
- If two records look like the same company or LP, flag it; don't merge.
