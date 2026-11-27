---
name: spend-rollup
description: 'How to detect recurring software charges, normalize vendor names, classify cadence, grade usage evidence, estimate savings and compute notice deadlines. Use in every subscription review.'
---

# Spend rollup procedure

## 1. Normalize vendor names

- Uppercase, strip processor prefixes (`PADDLE.NET*`, `FS *`, `SQ *`, `PAYPAL *`, `STRIPE*`), trailing reference numbers, city and state, and domain suffixes.
- Map known aliases (e.g. `GOOGLE*GSUITE` and `GOOGLE*WORKSPACE` to Google Workspace) and keep every raw descriptor seen in the inventory record.
- Prefer Ramp or Brex merchant names when present; they're already cleaned.
- If still ambiguous, list as "unidentified recurring charge" with the raw descriptor.

## 2. Classify cadence (13-month window)

| Pattern | Cadence |
|---|---|
| Charge every 28-33 days, amount within 10% | monthly |
| One charge 350-380 days after a similar one, or one large charge with no monthly pattern | annual (project next renewal = last charge + 12 months) |
| Every ~90 days | quarterly |
| Recurring but amount varies more than 25% | usage-based (not waste; report spikes only) |
| First charge in the last 45 days | new (check for trial conversion) |

## 3. Grade usage evidence

| Grade | Meaning | Example |
|---|---|---|
| A | Admin data | 12 paid seats, 4 active in 30 days (from admin API or export) |
| B | Direct activity | Login or activity emails, calendar events using the tool |
| C | Soft signal | Mentions in Slack or email in the last 30 days |
| none | No signal reachable | Say "no usage signal found", not "unused" |

"Probably cancel" requires grade A showing zero or near-zero use, or a confirmed duplicate. Everything else is "worth a closer look".

## 4. Estimate savings

- Monthly plan: annualized saving = monthly cost x 12; realizable next billing date.
- Annual plan: saving = annual cost (cancel) or (paid seats - active seats - buffer) x per-seat price (trim); realizable at renewal.
- Seat buffer: keep the configured headroom (default 10% or 2 seats, whichever is larger) for hiring.
- Never add estimates across groups into one headline number.

## 5. Notice deadline

- Notice deadline = renewal date - notice period (days).
- Notice period source priority: contract or order form > vendor terms email > user > unknown.
- Unknown: alert at renewal - 90 days and state the period is unknown.
- Alert when today >= notice deadline - lead time (default 21 days).

## 6. Digest item format

`<Vendor> | $<annualized>/yr | <cadence>, renews <date or unknown> | Flag: <reason> | Evidence: <grade, detail, date> | Next step: <action> | Unsure: <what to verify>`
