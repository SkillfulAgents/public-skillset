import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const port = process.env.DASHBOARD_PORT || 3000;
const distDir = path.join(__dirname, 'dist');

const WORKSPACE = '/workspace';
const COLLECTOR = '.claude/skills/seo-dashboard/collect.py';
const DATA_PATH = '/workspace/seo/dashboard/data.json';

const mimeTypes = {
  '.html': 'text/html',
  '.js': 'application/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
};

// --- collector -------------------------------------------------------------

let inFlight = null; // de-dupe concurrent plain /api/data collector runs

async function runCollector(extraArgs = []) {
  const args = [
    'uv', 'run', '--env-file', '.env',
    '--with', 'google-auth,requests',
    COLLECTOR,
    ...extraArgs,
  ];
  const proc = Bun.spawn(args, {
    cwd: WORKSPACE,
    stdout: 'pipe',
    stderr: 'pipe',
    env: { ...process.env },
  });
  const [code, stdout, stderr] = await Promise.all([
    proc.exited,
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
  ]);
  return { code, stdout, stderr };
}

function tail(s, n = 500) {
  if (!s) return '';
  const t = s.trim();
  return t.length > n ? '…' + t.slice(-n) : t;
}

async function collectAndServe(extraArgs = []) {
  const started = Date.now();
  let result;
  try {
    if (extraArgs.length === 0 && inFlight) {
      result = await inFlight;
    } else {
      const p = runCollector(extraArgs);
      if (extraArgs.length === 0) inFlight = p;
      try {
        result = await p;
      } finally {
        if (inFlight === p) inFlight = null;
      }
    }
  } catch (err) {
    result = { code: -1, stdout: '', stderr: String((err && err.message) || err) };
  }
  const took = Date.now() - started;

  // Always fall back to the last good data.json on disk.
  let payload;
  try {
    payload = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
  } catch (err) {
    return Response.json(
      {
        fatal: true,
        error:
          `Collector exited ${result.code} and no cached data.json could be read: ${String(err)}`,
        collector_stderr: tail(result.stderr),
      },
      { status: 503 },
    );
  }

  if (result.code !== 0) {
    payload.stale = true;
    payload.error =
      `Collector exited ${result.code} — showing the last good snapshot on disk. ` +
      (tail(result.stderr) || 'No stderr output.');
  } else {
    payload.stale = false;
    payload.error = null;
  }
  payload.server_collect_ms = took;
  payload.served_at = new Date().toISOString();

  return new Response(JSON.stringify(payload), {
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

// --- static ----------------------------------------------------------------

function serveStatic(pathname) {
  let filePath = path.join(distDir, pathname === '/' ? 'index.html' : pathname);

  try {
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) filePath = path.join(filePath, 'index.html');
  } catch {
    if (pathname.startsWith('/api')) return new Response('Not Found', { status: 404 });
    filePath = path.join(distDir, 'index.html');
  }

  try {
    const content = fs.readFileSync(filePath);
    const ext = path.extname(filePath);
    return new Response(content, {
      headers: { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' },
    });
  } catch {
    return new Response('Not Found', { status: 404 });
  }
}

Bun.serve({
  port,
  idleTimeout: 240,
  async fetch(req) {
    const url = new URL(req.url);
    // Tolerate being mounted under a proxy subpath.
    const p = url.pathname.replace(/^.*(\/api\/)/, '$1');

    if (p === '/api/data' && req.method === 'GET') return collectAndServe([]);
    if (p === '/api/refresh' && req.method === 'POST') {
      return collectAndServe(['--refresh-ahrefs', '--refresh-gsc']);
    }
    if (p.startsWith('/api/')) return new Response('Not Found', { status: 404 });

    return serveStatic(url.pathname);
  },
});

console.log(`Dashboard server running on http://localhost:${port}`);
