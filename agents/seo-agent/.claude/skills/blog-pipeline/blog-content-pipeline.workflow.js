export const meta = {
  name: 'blog-content-pipeline',
  description: 'Research, draft, fact-check, and humanize an SEO blog post from a target keyword',
  whenToUse: 'After keyword selection (Ahrefs). Pass {primary, secondary[], company, intent?, angleNotes?}. Returns final humanized markdown + meta + cta + media_brief + links.',
  phases: [
    { title: 'Research', detail: '4 parallel angles: definition, setup/how-to, use-cases, SEO/SERP gaps' },
    { title: 'Draft', detail: 'synthesize keyword-optimized article from verified research' },
    { title: 'Fact-check', detail: 'verify every claim against primary sources, add/repair links' },
    { title: 'Humanize', detail: 'strip AI tells, vary rhythm, natural developer voice' },
  ],
}

const KW = typeof args === 'string' ? JSON.parse(args) : args
if (!KW || !KW.primary) throw new Error('args must include {primary, secondary[]}')
if (!KW.company) throw new Error('args must include company — one line: "<domain> — <what the product is>" (see seo/config.json "company")')
const secondary = KW.secondary || []
const company = KW.company
const intent = KW.intent || 'informational'
const topic = KW.primary

const RESEARCH_SCHEMA = {
  type: 'object',
  required: ['angle', 'summary', 'facts', 'sources'],
  properties: {
    angle: { type: 'string' },
    summary: { type: 'string' },
    facts: {
      type: 'array',
      items: {
        type: 'object',
        required: ['claim', 'detail', 'sources'],
        properties: {
          claim: { type: 'string' },
          detail: { type: 'string' },
          sources: { type: 'array', items: { type: 'string' } },
        },
      },
    },
    questions_people_ask: { type: 'array', items: { type: 'string' } },
    sources: { type: 'array', items: { type: 'string' } },
  },
}

const ANGLES = [
  {
    key: 'definition',
    prompt: `Research the core definition and technical facts for the topic "${topic}", grounded in OFFICIAL / primary sources (vendor docs, official GitHub repos, official blog posts). Explain exactly what it is, who makes it, what problem it solves, key components/terminology, and any version/edition distinctions. Capture exact names, URLs, and any official quotes. Use web search + fetch primary pages. Return precise, citable facts only; flag anything you cannot verify against a primary source.`,
  },
  {
    key: 'setup',
    prompt: `Research HOW to actually use/set up "${topic}", grounded in official docs + official repo READMEs. Capture concrete steps, exact install/run commands, config snippets (verbatim), supported platforms/clients, options/flags, and security or best-practice notes. Prefer copy-pasteable commands and code. Use web search + fetch. Flag anything unverifiable or version-specific.`,
  },
  {
    key: 'usecases',
    prompt: `Research real-world use cases, the "why it matters", and the broader direction around "${topic}". Cover concrete examples, who uses it and for what, benefits, risks/limitations/guardrails, and any notable stats or quotes from primary or reputable press sources. Use web search + fetch. Return citable facts with sources; clearly separate confirmed vs speculative.`,
  },
  {
    key: 'seo',
    prompt: `Do SERP + content-gap research for the keyword "${topic}" (and these secondaries: ${secondary.join(', ') || 'n/a'}). Identify who ranks on page 1, what subtopics those pages cover, the "People Also Ask" questions, and the CONTENT GAPS a new article can win on. Also note how ${company} could add a credible, NON-salesy angle. Use web search. Return a recommended H2/H3 outline plus the PAA questions captured as facts.`,
  },
]

phase('Research')
const research = (await parallel(
  ANGLES.map((a) => () =>
    agent(a.prompt, { label: `research:${a.key}`, phase: 'Research', schema: RESEARCH_SCHEMA })
  )
)).filter(Boolean)
log(`Research: ${research.length}/4 angles, ${research.reduce((n, r) => n + (r.facts?.length || 0), 0)} facts`)

const DRAFT_SCHEMA = {
  type: 'object',
  required: ['title', 'slug', 'metaTitle', 'metaDescription', 'excerpt', 'body_markdown', 'media_brief'],
  properties: {
    title: { type: 'string' },
    slug: { type: 'string' },
    metaTitle: { type: 'string', description: '<= 60 chars' },
    metaDescription: { type: 'string', description: '<= 160 chars' },
    excerpt: { type: 'string', description: '<= 200 chars' },
    body_markdown: { type: 'string', description: 'full article markdown: ## h2 / ### h3, lists, fenced code blocks with language tags, inline markdown links to real sources' },
    cta: {
      type: 'object',
      properties: {
        heading: { type: 'string' },
        text: { type: 'string' },
        buttonLabel: { type: 'string' },
        url: { type: 'string' },
      },
    },
    media_brief: {
      type: 'array',
      items: {
        type: 'object',
        required: ['placement', 'description', 'search_terms', 'alt'],
        properties: {
          placement: { type: 'string', description: 'hero / after-section-N' },
          description: { type: 'string' },
          search_terms: { type: 'array', items: { type: 'string' } },
          alt: { type: 'string' },
        },
      },
    },
  },
}

phase('Draft')
const draft = await agent(
  `You are an expert technical content writer for ${company}. Write a comprehensive, genuinely useful blog post.

PRIMARY KEYWORD: "${topic}" (use naturally in title, first 100 words, one H2, meta, slug).
SECONDARY KEYWORDS to weave in naturally (no stuffing): ${secondary.join(', ') || 'none'}.
SEARCH INTENT: ${intent}.
${KW.angleNotes ? 'EDITOR NOTES: ' + KW.angleNotes : ''}

Use ONLY the verified research below. Do not invent commands, names, URLs, or stats. Where research flagged something unverifiable, omit it or phrase cautiously.

RESEARCH:
${JSON.stringify(research, null, 2)}

REQUIREMENTS:
- 1500-2000 words. Intro answers the core question in the first paragraph.
- Clear H2/H3 structure; include a step-by-step / how-to section with real commands in fenced code blocks (tag the language).
- Include a short FAQ section using the "People Also Ask" questions.
- ONE natural, non-salesy tie-in to ${company} near the end, plus a CTA.
- Markdown only for body_markdown. Use real source URLs as inline markdown links.
- metaTitle <=60, metaDescription <=160, excerpt <=200 chars. slug = kebab-case containing the primary keyword.
Return the structured object.`,
  { phase: 'Draft', schema: DRAFT_SCHEMA }
)

const FACTCHECK_SCHEMA = {
  type: 'object',
  required: ['revised_markdown', 'links', 'claims_checked'],
  properties: {
    claims_checked: {
      type: 'array',
      items: {
        type: 'object',
        required: ['claim', 'verdict'],
        properties: {
          claim: { type: 'string' },
          verdict: { type: 'string', enum: ['supported', 'wrong', 'unverifiable'] },
          correction: { type: 'string' },
          source: { type: 'string' },
        },
      },
    },
    links: {
      type: 'array',
      items: {
        type: 'object',
        required: ['anchor_text', 'url'],
        properties: { anchor_text: { type: 'string' }, url: { type: 'string' } },
      },
    },
    revised_markdown: { type: 'string' },
  },
}

phase('Fact-check')
const fc = await agent(
  `You are a rigorous technical fact-checker. Verify every factual/technical claim in this draft about "${topic}" against PRIMARY sources via web search + fetch (official docs, official repos, official blog). Verify commands, version numbers, names, URLs, stats, and quotes.

For each claim: mark supported / wrong / unverifiable. FIX wrong claims and REMOVE or soften unverifiable ones directly in the markdown. Ensure inline markdown links point to correct, current URLs (verify they resolve). Add authoritative links where claims lack a citation. Preserve structure, code blocks, and the ${company} CTA.

DRAFT MARKDOWN:
${draft.body_markdown}

Return claims_checked, the links you ensured/added, and the corrected revised_markdown (full article).`,
  { phase: 'Fact-check', schema: FACTCHECK_SCHEMA }
)
log(`Fact-check: ${fc.claims_checked.length} claims, ${fc.claims_checked.filter(c => c.verdict !== 'supported').length} corrected/softened`)

const HUMANIZE_SCHEMA = {
  type: 'object',
  required: ['final_markdown'],
  properties: {
    final_markdown: { type: 'string' },
    ai_tells_removed: { type: 'array', items: { type: 'string' } },
  },
}

phase('Humanize')
const hum = await agent(
  `Rewrite the PROSE of this article so it reads like an experienced human developer wrote it and scores LOW on AI detectors. Keep ALL facts, numbers, names, links, and code blocks exactly intact (do not touch anything inside \`\`\` fences; keep markdown link targets identical). Keep headings and order.

Remove AI tells:
- NO em dashes (—). Use commas, periods, or parentheses.
- Kill slop words: delve, dive in, seamless, robust, leverage (verb), unlock/unleash, game-changer, "in today's", "it's worth noting", "in the realm of", elevate, tapestry, "testament to", "in conclusion".
- Avoid "It's not just X, it's Y" and "Whether you're X or Y" and appositive openers ("X, a Y that Z,").
- Don't open with "<Topic> is <definition>". Vary sentence length aggressively (mix 3-6 word sentences with longer ones; allow fragments). Use contractions. Vary paragraph openers. Active voice. Add light, concrete developer voice without inventing facts.

Keep length within ~10%.

ARTICLE MARKDOWN:
${fc.revised_markdown}

Return final_markdown and a short list of ai_tells_removed.`,
  { phase: 'Humanize', schema: HUMANIZE_SCHEMA }
)

return {
  meta: { title: draft.title, slug: draft.slug, metaTitle: draft.metaTitle, metaDescription: draft.metaDescription, excerpt: draft.excerpt },
  cta: draft.cta,
  media_brief: draft.media_brief,
  links: fc.links,
  claims_checked: fc.claims_checked,
  final_markdown: hum.final_markdown,
  ai_tells_removed: hum.ai_tells_removed,
}
