---
name: board-prep-memo
description: 'The fixed 7-section board meeting prep memo: section rules, the 3-period QoQ table, the health rubric, how to anchor questions to numbers, and the Drive file name. Use for every Board Meeting Prep run.'
---

# Board prep memo

Every memo has the same seven sections in the same order, so the user can scan any company's memo in the same two minutes. Keep the whole memo to about two pages.

## Before writing

1. List every source you parsed: file name or link, page or slide count, and whether it parsed cleanly. Anything that failed goes in the "Didn't parse" list at the end. Never fill a number you couldn't read.
2. Pull the company's portfolio brief and the last board meeting's notes. Write down what was promised last time.
3. Find the plan or budget numbers if the deck has them. Variance to plan matters more than variance to last quarter.

## The seven sections

**1. TL;DR.** Three to five bullets: the single most important thing, the health call, the biggest risk, and a separate line **"Board is asked to approve:"** listing every vote or consent item in the materials (or "nothing flagged").

**2. Health: Green / Yellow / Red.** One call with two or three sentences of reasons. Defaults the user can change during onboarding:
- Red: runway under 6 months with no financing in motion, revenue more than 30% below plan, or loss of a top customer or key executive without a plan.
- Yellow: runway 6 to 12 months, revenue 10 to 30% below plan, burn up while growth is flat, or a priority from last meeting that disappeared.
- Green: on or above plan with at least 12 months of runway.
If you compute runway (cash divided by net monthly burn), say so.

**3. Financial review.** A table with the last three periods the deck reports, then a short read of what moved and why.

| Metric | Q-2 | Q-1 | Current | QoQ change | vs. plan |
|---|---|---|---|---|---|
| Revenue or ARR (say which) | | | | | |
| Gross margin | | | | | |
| Net burn | | | | | |
| Cash | | | | | |
| Runway (months) | | | | | |
| Headcount | | | | | |

Use the company's own period labels (fiscal quarters stay fiscal). If a period is missing from the materials, write "not provided", not a blank and not an estimate. Add rows for the two or three metrics this company actually runs on (for example net revenue retention, CAC payback, GMV, pipeline coverage).

**4. Wins and losses.** Bullets, each with the number or slide that supports it.

**5. Upcoming priorities.** What management says the next quarter is about, and how that compares with what they said last time.

**6. Four sharp questions.** Exactly four. Each is tied to a specific number and its slide or page: "Slide 14: pipeline grew 40% QoQ but closed-won was flat. Did stage definitions change?" Good sources of questions: a variance to plan, a metric whose definition shifted, a promise from last meeting that vanished, a cohort or segment the deck averages away, and a hiring plan that doesn't match burn.

**7. Investor takeaways.** What this means for the user as an investor: follow-on or pro-rata considerations, help the company needs from the board, and anything to watch before the next meeting.

End with **Didn't parse**: each source that failed, and why.

## Saving

- File name: `YYYY-MM-DD Company Board Prep`, using the meeting date if known, otherwise today.
- Folder: the board-prep folder saved in context. Create the folder if it doesn't exist.
- Create as a Google Doc (Docs API through the `googledocs` connected account) so the user can comment on it.
