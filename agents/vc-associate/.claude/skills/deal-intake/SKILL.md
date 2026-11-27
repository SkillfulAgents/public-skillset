---
name: deal-intake
description: 'Classifying inbound deal mail, the opportunity-type allowlist, sender allowlist and domain blocklist, the sensitivity threshold, the priority rubric, and thread-level dedup. Use for every Deal Flow to Pipeline run.'
---

# Deal intake

## 1. Gate

Run these in order. Stop at the first decisive one.

1. **Domain blocklist** (from config): drop. Typical entries are vendor, recruiter and event-sponsorship domains the user named.
2. **LP and fund-admin mail**: not deal flow. Leave it to triage.
3. **Sender allowlist** (trusted introducers, co-investors, accelerators, scouts): always passes the gate.
4. **Opportunity-type allowlist** (from config, for example "primary seed", "Series A", "co-invest allocation", "secondary"): the message must plausibly be one of these.
5. **Sensitivity threshold** (`low` / `medium` / `high`, default `medium`): how sure you must be that this is a real opportunity before logging. Below the threshold, add it to the "Needs review" list in the digest instead of the tracker.

Signals that a message is deal flow: a deck or data-room link or attachment, an intro with a founder on the thread, round language ("raising", "allocation", "lead", "closing"), a company website.

## 2. Dedup

- Key 1: Gmail thread ID (or Outlook conversation ID). Already in `/workspace/state/deal-ledger.json` means update, never insert.
- Key 2: company domain (from the website or founder email, ignoring free-mail domains like gmail.com). A match means append the new source to the existing row.
- Key 3: normalized company name, only to flag a possible duplicate for the user, never to merge automatically.

## 3. Priority rubric

Always **High**, regardless of score: a term sheet, or a co-invest allocation with a deadline.

Otherwise score 0 to 10 and record the reasons in "Priority reason":
- Thesis fit, 0 to 4: stage, sector, geography and check size each match what's in context (1 point each).
- Source, 0 to 3: allowlisted introducer or co-investor 3, other warm intro 2, accelerator or scout 1, cold 0.
- Round signal, 0 to 2: a named lead or a near-term close date stated in the mail or deck.
- Second independent intro to the same company, 0 to 1.

High is 7 or more, Medium 4 to 6, Low 3 or less. The user can change the cut-offs. The score reflects stated information only. Say "thin info" when most fields were not stated rather than scoring it as weak.

## 4. Opening decks and data rooms

- Attachments: read PDF, PPTX and XLSX directly.
- Google Drive and Docs links: through the `googledrive` connected account; if access is denied, record "no access".
- DocSend: try the passcode if it is in the email. If the page asks for an email address, a verification code, or acceptance of terms or an NDA, stop and record "not opened: gated".
- Never accept terms, NDAs or e-signatures to get access.

## 5. Write

Fill the tracker columns from `crm-access`. Mark fields taken from the deck with "(deck)". Update `deal-ledger.json` with thread ID, company domain, row reference and timestamp.
