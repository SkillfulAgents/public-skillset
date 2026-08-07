# Why the motion is shaped this way

Every default in `config/outbound.example.yaml` is a decision. This documents the reasoning so you can disagree with it deliberately rather than by accident.

## Volume

**25 emails per mailbox per day, on a primary domain.**

The binding constraint on cold outbound is not how many prospects you can find. It is domain reputation. A primary domain that also carries your real business mail has no margin for a spam-folder reputation, and the recovery is measured in months.

Volume past roughly 25 a day per mailbox is a different setup, not a bigger number: a dedicated sending domain, separate from the one your invoices go out on, warmed by a provider that does it properly. If someone asks to raise the cap without that, the honest answer is that the config value is not what is stopping them.

**New mailboxes ramp 10 to 25 over about four weeks.** Opening a cold mailbox at full volume is the fastest route to the spam folder.

**Per-campaign rates stack.** Most sending platforms enforce a rate per campaign and have no concept of an organization-wide ceiling. Three campaigns at 25 a day pointed at the same mailbox is 75 a day, and nothing in the vendor UI will tell you. `caps.audit_planned_rates()` sums intended volume across campaigns and rebalances before anything sends. This is the single most common way a well-configured program quietly torches a domain.

## Cadence

**Six steps, three emails, over two weeks.**

Three emails is where the marginal reply rate stops justifying the marginal annoyance. Beyond that you are mostly generating unsubscribes and spam complaints, and complaints are the metric that actually kills a domain.

Mixing channels helps more than adding emails does. A connection request that gets accepted before the second email raises reply rates more than a fourth email would.

**A reply stops everything, including an ambiguous reply.** Automated classification of "is this positive" is wrong often enough that the cost of being wrong (following up on someone who said no, or who said yes) exceeds the labor saved. A human reads it.

## Targeting

**Tiers with an intake mix, not a single filter.**

A single ICP filter produces a list that is uniform and therefore unfalsifiable: if it does not convert, you cannot tell which assumption was wrong. Tiers with a target mix let you see which segment is actually working after a few hundred sends.

**Buyer tiers A/B/C, leading with B.** At small companies the champion often replies faster than the decision maker: they own the workflow, feel the pain daily, and have a quieter inbox. Include the decision maker for awareness, do not blast both on the same day.

**Hard disqualifiers are named rules, not judgment.** "Too small" is a number. "No ops function" is a check. Rules that live in someone's head get applied inconsistently and cannot be audited later.

## The three exclusion concepts

Operators conflate these constantly. They are different questions with different failure modes.

| | Question | If it fails |
|---|---|---|
| **ICP** | Are they a fit? | You waste a send |
| **Suppression** | Have they already engaged? | You embarrass yourself with a customer |
| **Do not touch** | Is there a reason we must never contact them, unrelated to fit? | You create a real problem |

Suppression is fail-closed: an unreachable source halts the run. The asymmetry is the argument. A delayed batch costs a day. Cold-emailing your biggest customer's CEO costs considerably more, and you will not find out from a metric.

The do-not-touch gate runs before everything else, including the linter. There is no reason to lint copy for someone who must never receive it.

## Copy

**Enforced mechanically, not requested politely.**

An instruction not to use em dashes is a suggestion a model will occasionally ignore, and the failure is invisible until a prospect notices the email reads like it was generated. `lib/linter.py` refuses the send instead: em and en dashes, word and subject ceilings, tracking artifacts, retired brand names, unfilled placeholders, banned phrases, and one CTA.

The linter cannot enforce voice, which is why onboarding insists on real past emails. This is the question operators most want to skip and the one that most determines whether the copy works. Mechanics make a message inoffensive. Samples make it sound like a person.

**One CTA.** Two asks is a decision, and a decision is friction. Prefer a self-serve link over a meeting request for anything a prospect can try alone.

## Measurement

**No open tracking.** The pixel hurts deliverability for exactly the low-volume senders this template targets, and the number has been unreliable since Apple Mail Privacy Protection began pre-fetching images. A metric that is both harmful to collect and wrong is not a tradeoff.

**No rate without its denominator.** An 18% reply rate off 11 sends is noise presented as signal, and it is how teams talk themselves into scaling a variant that was never better. Below the configured floor you get the count.

**Positive reply rate is first class, and meetings booked and held are separate.** Total reply rate rewards messages that provoke, which is a real and common way to optimize a campaign into uselessness. Booked-versus-held is where a program that looks healthy on a dashboard turns out not to be.

**Meetings come from the calendar, not from replies.** The most common way a meeting gets booked is a prospect clicking the link and never writing back, which the mailbox cannot see. A meeting recorded as a flag on a reply therefore undercounts the outcome the entire motion exists to produce, and undercounts it worst for the campaigns that are working. `meetings.py` reads the sender's calendar and matches attendee addresses against known prospects exactly, on email only. Name matching would raise recall and destroy the metric's credibility, which is a bad trade for the one number a program gets judged on.

What the calendar proves is narrow, and it is worth being pedantic about: an event that ended and was not cancelled was **scheduled and not cancelled**. It does not prove anyone attended. "Held" means exactly that here, and no-shows have to be marked by a human, because a system that silently reports scheduled meetings as attended is how a pipeline review goes wrong.

**A/B tests carry an honest confidence state.** Directional, Trending, or Significant, plus how many more sends significance would take. Most outbound A/B tests never reach significance and get called anyway.

## Vendors

**Seven capability slots, vendors as interchangeable modules.**

Vendor churn in this category is high, and the motion outlives any of them. The parts worth keeping are the ICP logic, the identity matching, the cap governor, the suppression chain, the linter, and the reporting definitions. None of those should need to change when you switch enrichment providers.

The cost is one indirection. The benefit is that a vendor swap is a config line rather than a rewrite, and that the whole motion is exercisable against `dryrun` with no network calls and no risk.

## Identity matching

`lib/identity.py` is small and worth more than its size suggests. The LinkedIn slug is ground truth; enrichment results that disagree with it are rejected rather than merged; seed values are never overwritten.

The specific bug this prevents: you look up a person, the provider returns a coworker with the same first name at the same company, and the record silently becomes a different human with a valid-looking email. Nothing downstream catches it. The message goes to the wrong person with the right company name in it.
