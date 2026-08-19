---
category: "Marketing"
icon: megaphone
tags:
  - "Marketing"
  - "Ad Pacing Digest"
  - "Apple Search Ads"
  - "Slack"
  - "Monitoring"
works_with:
  - type: api_account
    slug: slack
developer:
  name: "@ericzakariasson"
  url: "https://x.com/ericzakariasson"
---

# Ad Pacing Digest

Compare Apple Search Ads spend with plan in Slack; recommend bid changes and apply only approved edits.

## What it does

- Act as the Ad Pacing Digest: compare Apple Search Ads spend with plan in Slack; recommend bid changes and apply only approved edits.
- Uses the original setup prompt as the workflow brief and starts with a supervised run.
- Captures the user's preferences, boundaries, approvals, and cadence when applicable.

## Connect first

- **Apple Search Ads** — direct API, feed, or required credentials; no canonical registry slug.
- **Slack** — SuperAgent API account `slack`.

## Sample use cases

- Compare Apple Search Ads spend with plan in Slack.
- Recommend bid changes and apply only approved edits.

## Getting started

1. Import this directory as an agent template.
2. Start a conversation and complete the guided connections and setup questions.
3. Review the supervised first result before saving or scheduling the workflow.

## Example prompts

- Post today's Apple Search Ads spend against plan
- What is over-delivering and what should I cut right now?
- Apply the bid change I just approved and confirm what moved

## Files

- `CLAUDE.md` — lightweight operating instructions and first-run connection guidance.
- `PROMPT.md` — the original Bot Directory prompt, preserved verbatim.
- `README.md` — marketplace metadata, examples, connection mapping, and credits.

## Credits

Original prompt credited to [@ericzakariasson](https://x.com/ericzakariasson) on [Bot Directory](https://botdirectory.ai/bots/ad-pacing-digest/). Imported from the MIT-licensed Bot Directory catalog; see the [attribution and license](../../sources/botdirectory/NOTICE.md).
