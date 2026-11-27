---
name: contract-terms
description: 'How to read a contract, order form or renewal notice for renewal terms, compute the notice-period deadline, set the auto-renew flag, record parse confidence, and keep the tracker row format. Use whenever a contract or renewal notice is added or updated.'
---

# Contract terms

## 1. What to read

Read the document itself: the PDF or DOCX attachment, the e-signature completion copy, or the Drive file. An email that says "your contract renews soon" is a pointer, not the terms. If an email links to a Drive file or a vendor portal page instead of attaching it, open the Drive file; for a portal that needs a sign-in, flag it for the user.

Scanned PDFs: if the text layer is empty or garbled, say so. Do not guess dates from a bad scan.

## 2. Fields to extract, with the clause they came from

| Field | Where it usually lives | Notes |
|---|---|---|
| Counterparty | parties block, signature page | Legal name, plus the name people use |
| Side | who pays whom | `vendor` (we pay) or `customer` (they pay us) |
| Value | fees, order form, pricing exhibit | Annualize multi-year totals; note currency |
| Effective / start date | first page, order form | |
| Initial term | term clause | e.g. 12 or 36 months |
| Renewal term | term or renewal clause | Often differs from the initial term (e.g. 3-year initial, 1-year renewals) |
| Renewal date | computed: start + initial term, or end of current renewal term | Recompute after each renewal |
| Auto-renew | renewal clause | `yes` if it renews unless someone gives notice ("evergreen", "automatically renew", "successive periods"); `no` if it simply expires; `unknown` if unclear |
| Notice period | renewal or termination clause | e.g. "at least 60 days prior to the end of the then-current term" |
| Notice method | notices clause | Written notice, specific address or email, certified mail, portal. An email to an account manager may not count. |
| Price change on renewal | fees clause | Uplift caps, CPI increases, "then-current list price" |
| Termination for convenience | termination clause | Can either side exit mid-term, and with what notice |
| Governing document | order of precedence clause | The latest signed order form or amendment usually controls term and price over the MSA |

Record the clause number or page next to each value.

## 3. Notice-period deadline

`notice_deadline = renewal_date - notice_period`

- "Days" means calendar days unless the clause says business days; then skip weekends (and say holidays were not checked).
- "Prior to the end of the term" means before the renewal date; count back from the last day of the term.
- If the deadline falls on a weekend, show the earlier business day as "act by" and the computed date beside it.
- Month-based periods ("three months prior") count back calendar months.
- If the contract does not auto-renew, there is no cancellation deadline, but there is still a decision date: the renewal date minus the configured lead time.
- Co-terminated order forms share the master's renewal date; check each one.

## 4. Parse status

Each tracker row carries `parse_status`:
- `parsed`: every key field found with a cited clause.
- `partial`: some found, list what is missing.
- `unparsed`: could not read the terms (scan, password, portal, missing attachment).

Never fill a missing date or notice period from a typical value. Partial and unparsed rows are alerted as data holes. For an unknown notice period on an auto-renewing contract, alert at renewal date minus 90 days and say the period is unknown.

## 5. Tracker row

`counterparty | side | value/yr | renewal date | auto-renew | notice period | notice deadline (act by) | notice method | price change | owner | status | parse_status | source link | last alert`

Status: `active`, `deciding`, `renewing`, `renegotiating`, `cancel_requested`, `notice_sent` (only when the user confirms), `renewed`, `ended`.

## 6. Alert order

Sort every alert batch: auto-renew = yes and value over the big-ticket threshold first, then other auto-renewing contracts, then big-ticket non-renewing, then the rest; within each group, the nearest notice deadline first. Data holes go in their own section at the top if any of them auto-renew.
