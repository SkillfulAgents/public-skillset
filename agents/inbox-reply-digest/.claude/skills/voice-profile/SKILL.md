---
name: voice-profile
description: 'Build and apply a short profile of how the user writes, learned from their own sent mail, so reply drafts sound like them. Use during onboarding, on the monthly refresh, and before writing any reply draft.'
---

# Voice profile

## Build or refresh

1. Pull the user's last 40 to 60 sent replies (Gmail `in:sent newer_than:60d`, Outlook Sent Items). Skip forwards, calendar replies, auto-replies, mail-merge or sequence sends, and messages that are mostly quoted text.
2. Strip quoted history and signatures before reading.
3. Note, separately for external and internal recipients when they differ:
   - typical length (median word count) and paragraph count;
   - greeting habits ("Hi Name," / "Name -" / none);
   - sign-off habits ("Thanks," / "Best," / initials / none);
   - formality, contractions, exclamation marks, emoji (yes or no);
   - how the user says yes, no, and "not yet" (short paraphrased patterns, not copied sentences with names);
   - whether they bullet, and whether they propose times or ask for them.
4. Write `/workspace/state/inbox-reply-digest/voice.md` with those notes in under 40 lines. No names, emails, prices or full message bodies.

## Apply when drafting

- Match length to the profile; when in doubt, go shorter.
- Use the user's greeting and sign-off for that audience. Do not add their email signature; the mail client does that.
- Answer the question asked first, then any next step.
- Facts come only from the thread or the user's own context. Anything missing becomes a marked blank: `[confirm date]`, `[attach deck]`.
- No filler openers ("I hope this finds you well") unless the profile shows the user writes them.
- Never promise a discount, deadline, deliverable or meeting the thread does not already support.
