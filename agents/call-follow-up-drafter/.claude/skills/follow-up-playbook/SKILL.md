---
name: follow-up-playbook
description: 'How to attribute a call to the right client, engagement and thread, the default client follow-up email structure, the welcome-email fill rules, and how to learn the user''s voice. Use on every call before drafting.'
---

# Follow-up playbook

## 1. Attribution check (do this before writing a word)

Score the evidence for client, engagement and thread separately.

| Evidence | Weight |
|---|---|
| Attendee email domain matches exactly one client in config | strong |
| Invite description or link names the engagement or project | strong |
| A thread in the last 30 days with these same external attendees | strong for thread |
| Company or project named in the first minutes of the transcript | medium |
| Meeting title only | weak, never enough alone |
| Personal email domain (gmail.com, outlook.com, icloud.com) | none, unless the address is a known contact in config or the CRM |

Draft only when client, engagement and thread each have at least one strong signal and nothing conflicts. Otherwise ask the user one short question with the options you found, and park the call in `pending-attribution.json`.

Always ask when:
- attendees come from two or more client domains;
- the client has more than one active engagement and nothing says which;
- two or more recent threads with these attendees cover different topics;
- the transcript names a different company than the invite.

Thread choice, in order: the thread holding the agenda or invite for this engagement; the latest human thread with these attendees about this engagement; otherwise a new message. Never reply on calendar, e-signature, invoice, or support-ticket notification threads.

Isolation check before saving: scan the draft for any client name, person, price or project that does not appear in this call's transcript, invite, or this client's config entry. If one appears, remove it and note it in the debrief.

## 2. Default follow-up structure

Use the user's own structure if they gave one. Otherwise:

```
Subject: Re: <thread subject>   (new thread: "<Client> / <topic>: next steps")

Hi <first names>,

<One line of thanks that mentions something specific from the call.>

Quick recap:
- <point the client would recognise>
- <decision, with the exact figure or date as said>

Next steps
On our side:
- <owner>: <deliverable> by <date as said>
On your side:
- <owner>: <deliverable> by <date as said>

<Restated asks, one per line, as polite direct questions.>

<Next meeting, if set: "Talk on Tuesday the 3rd at 10.">

<User's usual sign-off>
```

Rules:
- 120–220 words for a typical 30-minute call. Longer only for workshops or kickoffs.
- Numbers, prices, dates, quantities: exactly as spoken. Keep the client's words for dates; put any inferred calendar date only in the debrief.
- No promises, discounts, timelines or scope that were not said.
- No internal remarks, margin talk, or anything said off the record or after the client left.
- Owners are named people, not "we" or "the team", where the transcript says who.

## 3. Welcome or kickoff template

- Fill placeholders only from the transcript, the invite, and the client's config entry.
- Unfillable placeholders become `[[to confirm: <what>]]` and are listed in the debrief.
- Leave untouched any template section the call did not cover.
- Check every access or document request the user made on the call made it into the email.
- Never fill fees, rates or terms that were not said on this call or written in the template.

## 4. Learning the user's voice

On setup and every couple of weeks, read 10–20 recent sent emails to external recipients (not newsletters or one-liners) and note in `voice-notes.md`:
- greeting and sign-off they actually use;
- typical length and paragraph size;
- bullets or prose;
- formality markers (contractions, exclamation marks, first names);
- phrases they use often and phrases they never use.

When a sent follow-up differs from your draft, note what changed (shorter, removed a section, softer ask) and apply it next time. Store observations, not email bodies.

Banned filler unless the user writes this way: "I hope this email finds you well", "per our conversation", "just circling back", "please do not hesitate to reach out", "as discussed".
