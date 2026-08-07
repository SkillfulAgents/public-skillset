---
name: role-{{slug}}
description: "{{title}} @ {{company}} ({{ats_or_record}} {{job_id}}) — {{one_line_archetype}}; {{geo_policy}}. Outreach {{HELD|ACTIVE}}."
metadata:
  type: project
---

# Role: {{title}} ({{company}})

**Job:** `{{job_id}}`. **{{geo_policy}}.** {{seniority_band}}. **Outreach {{HELD|ACTIVE}}.**

## Role essence (posting)
{{2-4 line distillation of the JD: what this hire owns, why now, what shape of person}}

**Screening prompt (the evaluation instrument — keep in sync with calibration log):** `/workspace/pipeline/screening/{{slug}}.md`

## Scoring rubric (0–100 = 4 criteria × 25)
- **1. Academic Excellence (0–25):** {{role-adapted sub-bullets — selective programs, honors, olympiads/competitions; never reject on school alone}}
- **2. Company Quality (0–25):** {{tier-A companies for THIS role; judge what they did there, not the logo}}
- **3. Career Trajectory (0–25):** {{velocity signals: promotions, scope growth, shipped work with their name on it, speed picking things up}}
- **4. Role Fit (0–25):** {{the 4-6 things that make someone great at THIS role}}
- **Disqualifiers:** tenure <1yr pattern, job-hopping, {{role-specific DQs}}, geo.
- Bands: 85+ shortlist no hesitation · 70–84 shortlist if skeptic-review holds · 50–69 longlist · <50 out.

## Constraints (for answering candidates — NEVER in outreach)
Comp: {{band or TBD}}. Equity: {{philosophy or TBD}}. Visa: {{yes/no}}. Start: {{constraint or flexible}}.

## Pools
Seed companies: {{list}} (graph file: `/workspace/pipeline/companies-{{slug}}.md`). LinkedIn recipes: {{which}}. Non-LinkedIn excellence pools worth running: {{which modes}}. Longlist: `longlist-{{slug}}.jsonl`.

## Outreach angle
Templates: `/workspace/pipeline/outreach/{{slug}}.md`. Angle: {{why a great person says yes to this role, 1-2 lines}}.

## Interview process & panel
{{process + who takes the first call, or TBD — ask}}

## Calibration log
- {{date}} — File created at onboarding from posting. No sourcing yet.
