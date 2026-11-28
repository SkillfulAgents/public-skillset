---
name: read-usage-page
description: Read the Gamut Platform org usage page in the browser and save its spend for the dashboard's five ranges (week to date, month to date, last 7, 14 and 30 days). Needs a person present to sign in. Use during setup after the admin signs in, from refresh-review, or for "read the usage page".
---

# Read the usage page

Writes `review/exports/usage-page/rolling/<range>/<read date>.json` through `scripts/usage_page.py save`, the only writer.
Then `cost.py` turns each reading into its view's cost file.

| Page range | Dashboard view |
|---|---|
| `wtd` | `wtd` |
| `mtd` | `mtd` |
| `7d` | `last7` |
| `14d` | `last14` |
| `30d` | `last30` |

## Steps

1. Open the org usage page. Its address is under *Cost source* in `review/workspace.md`, captured at setup. Add the range and the review's timezone (`timezone` in `cards.json`):
   `<address>?total_range=<range>&llm_range=<range>&service_range=<range>&tz=<timezone>`
   No address recorded? Ask the admin for the org's usage page link. Never guess it.
2. **Signed out** (the page redirects to `/auth/login`)?
   - With a person present: sign in with `mcp__user-input__request_login`. The account must be an owner or admin of the org. The person types any code the sign-in asks for.
   - With nobody present: stop. Say the usage page needs an owner or admin to sign in, in a session they're in.
3. For each of the five ranges, in turn:
   1. Load the page for that range.
   2. `python3 scripts/usage_page.py js --kind <range> > /tmp/page.js`, Read it, and run its exact text with one `browser_eval`. Never click "Show N more", and never print raw page data: the script drops every agent outside scope inside the page. It throws if the page data changed shape or a card failed to load. That's a failed read: say which range failed and why.
   3. Write the returned JSON to `/tmp/usage-reading.json`, then `python3 scripts/usage_page.py save < /tmp/usage-reading.json`, and delete the temp file.
   4. `python3 scripts/cost.py --period <view>`.
4. Close the browser.

`save` refuses a reading whose ranges don't all match, or whose timezone isn't the review's.

Where the data sits: the page is Next.js. The data is in the `self.__next_f.push([1, "..."])` script tags. Joined, they hold one `"agents":[...]` array (the AI card: `key`, `label`, `agent_id` = the short id, `total_cost_usd`, `total_tokens`, `request_count`. One row without `agent_id` is AI spend tied to no agent), plus `totalLlmSpendUsd`, `totalServiceSpendUsd` and the flags `agentsOk`, `totalLlmOk`, `totalServicesOk`.
