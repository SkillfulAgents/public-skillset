---
name: collections-playbook
description: 'Aging buckets, the living aging log format, the tone ladder for collection drafts, the cleared-payment test, skip rules and the one-chase-per-cycle ledger. Use on every collections run before drafting anything.'
---

# Collections playbook

## 1. Bucket every open invoice

Compute days overdue from the invoice **due date** (not the invoice date), in the user's timezone, on the day of the run.

| Bucket | Rule | Draft? |
|---|---|---|
| Current | not yet due | No, unless the user opted into a courtesy reminder a few days before the due date |
| 1-30 | 1 to 30 days past due | Yes, after the configured grace days (default 3) |
| 31-60 | 31 to 60 days past due | Yes |
| 60+ | 61 days or more | Yes, and it goes in the worst-offenders summary |

If the vertical config also tracks 61-90 and 90+, keep those as sub-buckets of 60+ in the log. The tone step below does not change after 60+; what changes past 90 is that the item belongs to a human.

## 2. Living aging log

One row per open invoice, kept in the configured place (a Google Sheet tab, or `/workspace/state/<agent-slug>/aging-log.json` if the user has no sheet). Update rows in place; never rebuild the log from scratch and lose history.

Columns: account, billing contact, invoice number, invoice date, due date, amount, balance due, currency, days overdue, bucket, status, last contact (date and channel), last draft (date and tone step), promise date, notes, source record link.

Status is one of: `open`, `payment_claimed` (they say it's paid, nothing has cleared), `promised` (dated promise to pay), `payment_plan`, `disputed`, `paid_cleared`, `do_not_contact`, `written_off` (only if the user recorded it), `human` (escalated, agent stops drafting).

## 3. Cleared-payment test

Mark `paid_cleared` only when you can see the money:
- the invoice shows a zero balance in QuickBooks or Xero with a payment or deposit applied to it, or
- a Stripe charge or invoice payment shows `succeeded`/`paid` and has not been refunded or disputed.

Not payment: "check's in the mail", "we paid it yesterday", remittance advice, an AP portal saying "approved" or "scheduled", a Stripe payment still `processing`, a bank transfer the user has not seen. Log these as `payment_claimed` with the date and the exact wording, pause drafting for the configured verification window (default 5 business days; ACH and checks take time), then verify. If it still has not cleared, the next draft politely says you have not received it yet.

Partial payment: update the balance and chase only the remainder; name the payment you received.
Unapplied payment or credit on the account: do not chase; flag it to the user as "may already be paid, needs matching".

## 4. Skip rules (check every one before drafting)

Skip and note why when the account:
- is `paid_cleared`, `do_not_contact`, `written_off` or `human`;
- is on a payment plan with installments current (a missed installment is flagged to the user, never chased automatically);
- has a promise date that has not passed (one catch-up note after it slips);
- is `disputed` (wrong amount, unhappy with the work, missing PO): stop and route to the user;
- is in its verification window after a payment claim;
- already got a draft this cycle (see section 6).

## 5. Tone ladder

Every draft names the **invoice number, amount and due date**, copied from the system of record, plus the payment link if the system provides one. Never invent a link, amount or date. Several overdue invoices for one account go in **one** email, listed oldest first with a total.

| Step | When | Tone |
|---|---|---|
| 1 | 1-30 days | Friendly nudge. Assume an oversight. Offer to resend the invoice. |
| 2 | 31-60 days | Direct. State it is now over 30 days past due and ask for a payment date. |
| 3 | 60+ days | Firm. Ask for payment or a call by a specific date the user approves. Still courteous. |

Never write late fees, interest, legal, lien, credit-reporting or collections-agency language unless the user wrote that exact language into the draft themselves. Match the user's voice samples. Short beats long.

## 6. One chase per account per cycle

A cycle is the configured chase interval (default 7 days). Keep a ledger at `/workspace/state/<agent-slug>/chase-ledger.json`:

```json
{ "entries": [ { "account": "", "invoices": [""], "cycle_start": "YYYY-MM-DD", "tone_step": 1, "draft_id": "", "drafted_at": "", "sent_seen_at": null } ] }
```

Before drafting, if the account has an entry with `cycle_start` inside the current cycle, skip it. Check the user's Sent folder for each draft on later runs; record `sent_seen_at` so "last contact" reflects what was really sent, not what was drafted. A draft the user deleted is not a contact.

## 7. Worst-offenders summary

Top five accounts by balance in the oldest bucket (60+ first, then 31-60), each with total owed, oldest due date, last contact and a recommended next step (call, pause new work, hand to the owner). Add bucket totals, what changed since last run (newly paid, newly overdue, promises due this week, claims awaiting clearance) and the number of drafts waiting. If nothing is overdue and nothing changed, send nothing.
