import React from 'react';
import { renderToString } from 'react-dom/server';
import fs from 'fs';

const B = './src';
const { KpiRow, Targets } = await import(`${B}/sections/Kpis.jsx`);
const Trend = (await import(`${B}/sections/Trend.jsx`)).default;
const Content = (await import(`${B}/sections/Content.jsx`)).default;
const QueriesPages = (await import(`${B}/sections/QueriesPages.jsx`)).default;
const Links = (await import(`${B}/sections/Links.jsx`)).default;
const Outreach = (await import(`${B}/sections/Outreach.jsx`)).default;
const Program = (await import(`${B}/sections/Program.jsx`)).default;
const Backlog = (await import(`${B}/sections/Backlog.jsx`)).default;
const { SnapshotHistory, WeeklyHistory } = await import(`${B}/sections/History.jsx`);
const { OrganicVsPaid, OrganicFootprint } = await import(`${B}/sections/Ahrefs.jsx`);
const Header = (await import(`${B}/sections/Header.jsx`)).default;

const d = JSON.parse(fs.readFileSync('/workspace/seo/dashboard/data.json', 'utf8'));

const empty = {
  ...d,
  kpis: [],
  targets: [],
  articles: [],
  velocity: [],
  activity: [],
  kpi_history: [],
  kpi_history_state: [],
  gsc: { ...d.gsc, daily: [], daily_nonbrand: [], queries: [], pages: [], page_queries: {} },
  refdomains: { all: [], new_30d: [], lost: [], clean_count: 0, suspect_count: 0, dr_buckets: {} },
  outreach: { config: {}, funnel: {}, by_status: {}, active: [], followups_due: [], won: [], send_timeline: [] },
  backlog: { content: [], links: [], content_counts: {}, link_counts: {} },
  ahrefs: { metrics: {}, history: [], organic_keywords: [], top_pages: [], backlinks: {} },
};

const cases = [
  ['Header', <Header data={d} loading={false} refreshing={false} onRefresh={() => {}} lastLoaded={new Date().toISOString()} />],
  ['KpiRow', <KpiRow kpis={d.kpis} ranges={d.gsc.ranges} />],
  ['SnapshotHistory', <SnapshotHistory kpiHistory={d.kpi_history} />],
  ['SnapshotHistory(3pt)', <SnapshotHistory kpiHistory={[{date:'2026-08-01',dr:31,refdomains:150,org_keywords:3},{date:'2026-08-03',dr:32,refdomains:160,org_keywords:3},{date:'2026-08-06',dr:32,refdomains:169,org_keywords:4}]} />],
  ['WeeklyHistory', <WeeklyHistory rows={d.kpi_history_state} />],
  ['Trend', <Trend gsc={d.gsc} />],
  ['Targets', <Targets targets={d.targets} />],
  ['Content', <Content articles={d.articles} />],
  ['OrganicVsPaid', <OrganicVsPaid ahrefs={d.ahrefs} />],
  ['OrganicFootprint', <OrganicFootprint ahrefs={d.ahrefs} />],
  ['QueriesPages', <QueriesPages gsc={d.gsc} />],
  ['Links', <Links refdomains={d.refdomains} ahrefs={d.ahrefs} />],
  ['Outreach', <Outreach outreach={d.outreach} />],
  ['Program', <Program velocity={d.velocity} activity={d.activity} />],
  ['Backlog', <Backlog backlog={d.backlog} />],
  // empty-data cases
  ['EMPTY KpiRow', <KpiRow kpis={empty.kpis} ranges={undefined} />],
  ['EMPTY Trend', <Trend gsc={empty.gsc} />],
  ['EMPTY Content', <Content articles={[]} />],
  ['EMPTY QueriesPages', <QueriesPages gsc={empty.gsc} />],
  ['EMPTY Links', <Links refdomains={empty.refdomains} ahrefs={empty.ahrefs} />],
  ['EMPTY Outreach', <Outreach outreach={empty.outreach} />],
  ['EMPTY Program', <Program velocity={[]} activity={[]} />],
  ['EMPTY Backlog', <Backlog backlog={empty.backlog} />],
  ['NULL everything', <><KpiRow kpis={undefined} /><Trend gsc={undefined} /><Content articles={undefined} /><Links refdomains={undefined} ahrefs={undefined} /><Outreach outreach={undefined} /><Program /><Backlog /><OrganicVsPaid /><OrganicFootprint /><SnapshotHistory /><WeeklyHistory /></>],
];

let fail = 0;
for (const [name, el] of cases) {
  try {
    const html = renderToString(el);
    console.log(`OK   ${name.padEnd(24)} ${String(html.length).padStart(7)} bytes`);
    if (/NaN|undefined|Infinity/.test(html)) {
      const m = html.match(/.{0,60}(NaN|undefined|Infinity).{0,60}/);
      console.log(`  !! suspicious token: ${m[0]}`);
    }
  } catch (e) {
    fail++;
    console.log(`FAIL ${name}: ${e.message}`);
  }
}
console.log(fail ? `\n${fail} FAILURES` : '\nall render');
