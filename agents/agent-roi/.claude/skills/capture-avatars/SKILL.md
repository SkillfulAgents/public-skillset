---
name: capture-avatars
description: Capture each in-scope agent's avatar and member stack from the Gamut app, so the dashboard shows them instead of initials. Uses two screenshots per kind and scripts/avatars.py. Run once in setup, then from refresh-review for new agents only, or for "update the avatars".
---

# Capture avatars

The images are snapshots of the app on the day you took them. Without them the dashboard shows initials, so a failed capture never blocks anything.
Writes `artifacts/agent-roi/public/avatars/<id>.png`, `members/<id>.png` and `avatars.json`, through `scripts/avatars.py` only.

1. **Open your own agent page in the Gamut app** (`<app address>/agents/<your slug>`, slug from `$SUPERAGENT_AGENT_SLUG`), not the home page: the home page also loads every agent's dashboard and can hang the browser, while your agent page shows the same agent sidebar with no dashboards (Settings pages don't show the sidebar). The app address is the workspace's own, under *Gamut app* in `review/workspace.md`. Not recorded? Find it yourself, never ask: the usage page's "Open Cloud Agents" link goes to it (`https://<app host>/auth/platform/start…`, so the app is `https://<app host>/`), and in a cloud workspace it is also the host the Gamut app links to sessions on. Record it. Only if neither works, ask the admin once. Wait until the agent list has loaded: the app is heavy, so wait for `[data-testid^="agent-item-"]` with `browser_wait` (up to 60 s) before any `browser_eval`. If it still won't load, close the browser, open it once more and retry; after that, keep initials and say so.
2. Set the viewport to at least 1200×900 CSS pixels at 2 device pixels per CSS pixel.
3. **Avatars.**
   1. `python3 scripts/avatars.py js --kind avatars > /tmp/avatars.js`. For new agents only, add `--ids <id>,<id>`. Read it and run its exact text with one `browser_eval`. It returns the agent ids it placed, in grid order: write them to `/tmp/avatars-order.json`.
   2. Screenshot the viewport to `/tmp/avatars-white.png`.
   3. Run `document.getElementById('wr-capture').style.background = '#000'` with `browser_eval`, and screenshot to `/tmp/avatars-black.png`.
   4. `uv run --with pillow --with numpy python3 scripts/avatars.py crop --kind avatars --white /tmp/avatars-white.png --black /tmp/avatars-black.png --order /tmp/avatars-order.json`
4. **Member stacks.** The same four steps with `--kind members` and `/tmp/members-*` files.
5. Remove the overlay (`document.getElementById('wr-capture').remove()`), close the browser, and delete the `/tmp` files.
6. Reload the dashboard and look at it. Each row should show a round avatar and, where the app shows one, a small stack of member faces. A blank, boxed or shifted image means the cut missed: say so, and leave that agent's initials.

How it finds them: each agent's row in the app's list is the `li` around `[data-testid="agent-item-<short id>"]` (the short id is the last segment of the agent id). The avatar is `button[class*="group/avatar"] span.relative.block` in that `li`. The member stack is the smallest element holding all the `li`'s `img` tags.
An agent missing from the list, or with nothing found, is left out of the grid and keeps its initials.
When more agents are in scope than fit on screen (about 42 avatars or 40 stacks), capture them in batches with `--ids`.
