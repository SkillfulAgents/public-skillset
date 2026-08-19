---
category: "Marketing"
icon: megaphone
tags:
  - "Marketing"
  - "Episode Launch Crew"
  - "Castos"
  - "Google Drive"
  - "YouTube"
  - "Slack"
  - "Workflow Automation"
works_with:
  - type: api_account
    slug: googledrive
  - type: api_account
    slug: youtube
  - type: api_account
    slug: slack
developer:
  name: "@elie2222"
  url: "https://x.com/elie2222"
---

# Episode Launch Crew

Turn approved final audio into a complete Castos episode draft; publish only after approval and verify podcast and YouTube links.

## What it does

- Act as the Episode Launch Crew: turn approved final audio into a complete Castos episode draft; publish only after approval and verify podcast and YouTube links.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Castos** — direct API, feed, or required credentials; no canonical registry slug.
- **Google Drive** — SuperAgent API account `googledrive`.
- **YouTube** — SuperAgent API account `youtube`.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Turn approved final audio into a complete Castos episode draft.
- Publish only after approval and verify podcast and YouTube links.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Prepare a Castos draft from the final audio in Drive
- Show me the title, description, and chapters first
- Publish the approved episode and verify both links

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@elie2222](https://x.com/elie2222) on [Bot Directory](https://botdirectory.ai/bots/episode-launch-crew/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
