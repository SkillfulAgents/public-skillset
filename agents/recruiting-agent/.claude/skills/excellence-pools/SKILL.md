---
name: Excellence Pools (non-LinkedIn sourcing)
description: Non-LinkedIn search modes for finding exceptional people — arXiv paper-author search (scripted), competition/olympiad results, fellowships, elite athletics, OSS maintainers, YC alumni, creator portfolios, and Juicebox/Metaview/Paraform pre-filter recipes. Use whenever sourcing beyond LinkedIn, and always when LinkedIn is on hold.
metadata:
  version: "1.1.0"
---

# Excellence Pools — non-LinkedIn search modes

Per the recruiting philosophy: hunt for stamps of excellence wherever they live, including ones not visible on LinkedIn. Every mode below outputs candidates into the same per-role longlist (`longlist.py bulk`, source.kind = the mode name) and goes through the SAME disqualify → score → shortlist funnel. LinkedIn URL discovery happens at enrichment (web search "<name> linkedin"), NOT via LinkedIn search — so these modes work during a LinkedIn hold.

**LinkedIn is a HARD condition (the hiring lead, 2026-07-24 — resolve-then-DQ).** These modes surface people via GitHub, arXiv, personal sites, or competition results — great *discovery*, but a candidate CANNOT be shortlisted/advanced/contacted without a real `linkedin.com/in/` profile (LinkedIn is the primary outreach channel). So a GitHub URL, personal site, or `pending-enrich://` placeholder in `linkedin_url` is NOT sufficient: resolve the actual LinkedIn profile at enrichment (web search "<name> <company> linkedin", then browser to confirm identity) BEFORE shortlisting. If it genuinely can't be found, disqualify — do not shortlist. `longlist.py` enforces this: any lock-status transition (shortlisted+) with a non-LinkedIn `linkedin_url` is refused with `needs-linkedin`, and such rows carry `needs_linkedin: true` until resolved.

## Scripted modes

### M1 — Paper authors (arXiv) — best for: Head of Research, FE-ML flags
```bash
uv run --with requests /workspace/.claude/skills/excellence-pools/pools.py arxiv \
  --query 'all:"agent evaluation" AND cat:cs.AI' --max 200 --since 2024-01-01 \
  --by-author --min-papers 2 --top 40
```
Ranks authors by first-authorships + volume on a topic. Good topic queries for us: `"agent evaluation"`, `"tool use" AND agents`, `"multi-agent" planning`, `"LLM agents" reliability`. Then web-verify each author (affiliation, seniority) before longlisting. Note: pure-academic profiles need the "shipped to production" check from the Head-of-Research rubric.

### M2 — YC directory — best for: founding roles, GTM founder-alumni (recipe B5)
`yc-companies` skill. Founders/early engineers: `--batch-since 2022 --max-team 15`; wind-downs/exits (open to operator roles): `--status Acquired|Inactive`. Founder names + LinkedIn links live on each company's `yc_url` page (browser or web_fetch).

## Web-search modes (mcp web_search / web_fetch — no login, no LinkedIn)

### M3 — Competition results — best for: engineering roles
Public results pages: IMO (imo-official.org), IOI (stats.ioinformatics.org), ICPC world-finals standings (icpc.global), Putnam top-500 (MAA). Search pattern: pull medalist/finalist names for years ~2014–2022 (now 2–10 yrs into careers), then web-search "<name> software engineer" to find where they landed. High effort per hit but the hit rate on "history of crushing it" is unmatched.

### M4 — Fellowships & lists — all roles
Thiel Fellowship directory, Forbes 30u30 (eng + enterprise-tech lists), Kleiner/Sequoia scout-adjacent fellowships, Neo Scholars, Z Fellows. The team's own stamps (Thiel Fellow CEO) validate this pool.

### M5 — Elite athletics × technical degree — engineering + GTM (team-calibrated 2026-07-22)
NCAA champions / national-team athletes with CS/eng degrees (exemplar: founding eng = 4x NCAA champion gymnast, Stanford CS). Search: roster pages of top programs × major, "NCAA champion computer science", athlete-alumni "now at" searches. Rare profiles, extreme signal on discipline + clock speed.

### M6 — OSS maintainers — engineering roles
Top contributors/maintainers of widely-used repos in our space (agent frameworks, dev-tools, TS/React infra). GitHub profiles usually link personal sites/LinkedIn. Verify adoption (stars/downloads), not just activity. (GitHub API unauthenticated = 60 req/hr; fine for targeted pulls, request a token if scaling.)

### M7 — Creator portfolios — Growth (REQUIRED for that role) + GTM pattern B
X/YouTube/newsletter creators in the AI-tools niche with real engagement AND startup work history. Verify the portfolio directly (views, cadence, quality) — it's the role's hard requirement. Search: "built in public" + AI agents, YouTube channels reviewing AI tools, newsletter authors on Substack/beehiiv.

### M8 — MBB/MBA operator trails — GTM pattern A
Web-search MBB alumni now at startups ("ex-McKinsey" + "founding" site:linkedin.com/in via web results is fine — reading public results is not LinkedIn platform activity), HBS/GSB class notes, "left McKinsey to join" press. the hiring lead's own 2nd-degree network is the warmest version of this — needs LinkedIn, so only after hold lifts.

### M9 — VC-portfolio harvest — engineering roles first (HM idea, calibration call 2026-07-24)
Premise: employment at a top-tier-VC-backed company (Sequoia, a16z, Benchmark, Thrive, etc.) is a company-quality proxy — those portfolios skew toward stronger engineering cultures. Procedure: enumerate portfolio companies from the VC's public portfolio page / Crunchbase-type sources → filter to product/dev-tools/AI companies with credible eng bars → harvest their ICs (company People tab in LinkedIn windows, or web modes). A proxy, not proof — normal rubric scoring applies. Track yield per role like every mode.

## Browser pre-filter platforms (logins unverified — check before relying)
- **Juicebox (PeopleGPT)** — ~70% quality; prompt with the role's rubric essence; EVERYTHING gets re-scored by us.
- **Metaview** — interview-data pre-filter; same rule: input, never a verdict.
- **Paraform** — 10–20 inbound profiles/day on FE-FS (source=Paraform applications in Ashby); review, never auto-reject (the hiring lead: missing a great one is the expensive mistake).

## Norms
- **Every mode applies to every open role** (the hiring lead, 2026-07-22). The "best for" notes above are historical-yield hints for query design, NOT assignments — parameterize the mode with role-specific queries and let the role's rubric do the filtering. Track yield per (mode × role) in the role's calibration log; modes earn or lose time by data, never by upfront assumption.
- Every mode's output: `{name, source:{kind:"<mode>", query, date}, evidence...}` → longlist → normal funnel. No mode bypasses scoring.
- Enrichment order: web-verify identity/affiliation → **resolve real `linkedin.com/in/` profile via web search (HARD gate — no LinkedIn, no shortlist; DQ if unresolvable)** → (only when hold lifted) profile touch.
- Log per-mode yield in the role's calibration log — modes that keep producing sub-bar people get retired, same as company stamps.
