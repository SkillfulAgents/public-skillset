// Read-only. Every number comes from scripts/review_math.py. Edits happen in chat with the agent.
import { existsSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import { agentsCsv, outcomesCsv, reportPdf, fileName } from './export.js';

const port = process.env.DASHBOARD_PORT || 3000;
const root = process.env.WORKSPACE_DIR || join(import.meta.dir, '..', '..');
const review = join(root, 'review');
const page = readFileSync(join(import.meta.dir, 'public', 'index.html'), 'utf8');

function run(script, args) {
  const p = Bun.spawnSync(['python3', join(root, 'scripts', script), ...args], { cwd: root, env: { ...process.env, REVIEW_DIR: review } });
  if (p.exitCode !== 0) throw new Error(p.stderr.toString().trim() || `${script} failed`);
  return JSON.parse(p.stdout.toString());
}

// The usage page's own ranges. Months are only storage underneath.
const VIEWS = ['wtd', 'mtd', 'last7', 'last14', 'last30'];
const peopleArg = url => url.searchParams.get('people') === 'yes' ? ['--people-in-cost', 'yes'] : [];

const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

Bun.serve({
  port,
  fetch(req) {
    const url = new URL(req.url);
    if (req.method !== 'GET') return new Response('Read-only', { status: 405 });
    if (url.pathname === '/') return new Response(page, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
    const stat = url.pathname.match(/^\/(fonts|avatars|members)\/([A-Za-z0-9._-]+\.(woff2|png))$/) || (url.pathname === '/avatars.json' && [null, '', 'avatars.json', 'json']);
    if (stat) {
      const file = join(import.meta.dir, 'public', stat[1] ? `${stat[1]}/${stat[2]}` : 'avatars.json');
      if (!existsSync(file)) return new Response('Not found', { status: 404 });
      const type = { woff2: 'font/woff2', png: 'image/png', json: 'application/json' }[stat[3]];
      return new Response(Bun.file(file), { headers: { 'Content-Type': type, 'Cache-Control': 'max-age=3600' } });
    }
    try {
      if (url.pathname === '/api/periods') return json(VIEWS);
      if (url.pathname === '/api/review') {
        const period = url.searchParams.get('period') || 'last30';
        if (!VIEWS.includes(period)) return json({ error: 'Bad period' }, 400);
        return json(run('review_math.py', ['--period', period, ...peopleArg(url)]));
      }
      if (url.pathname === '/api/export') {
        const period = url.searchParams.get('period') || 'last30', format = url.searchParams.get('format');
        if (!VIEWS.includes(period)) return json({ error: 'Bad period' }, 400);
        const view = run('review_math.py', ['--period', period, ...peopleArg(url)]);
        const send = (body, type, ext) => new Response(body, { headers: { 'Content-Type': type, 'Content-Disposition': `attachment; filename="${fileName(view, ext)}"`, 'Cache-Control': 'no-store' } });
        if (format === 'pdf') return reportPdf(view).then(b => send(b, 'application/pdf', 'pdf'));
        if (format === 'agents') return send(agentsCsv(view), 'text/csv; charset=utf-8', 'agents.csv');
        if (format === 'outcomes') return send(outcomesCsv(view), 'text/csv; charset=utf-8', 'outcomes.csv');
        return json({ error: 'Bad format' }, 400);
      }
    } catch (e) {
      return json({ error: String(e.message || e) }, 500);
    }
    return new Response('Not found', { status: 404 });
  },
});
console.log(`Agent ROI on :${port}`);
