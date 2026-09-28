#!/usr/bin/env node
// `open-slide dev` with two additions it has no config hook for: a Vite cache
// outside node_modules, and small slide SVGs inlined into the importing module.
import { fork } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Mirrors @open-slide/core's dev supervisor so the in-app "restart server" works.
const SUPERVISED_ENV = 'OPEN_SLIDE_DEV_SUPERVISED';
const RESTART_EXIT_CODE = 52;
const SVG_INLINE_LIMIT_BYTES = 16 * 1024;
const SVG_IMPORT = /^import\s+([A-Za-z_$][\w$]*)\s+from\s+(["'])([^"'\n]+\.svg)\2;?[ \t]*$/gm;
const SCRIPT_ID = /\.[cm]?[jt]sx?$/;

// Vite module ids are realpaths; compare against the same form.
const userCwd = fs.realpathSync(process.cwd());

if (process.env[SUPERVISED_ENV] === '1') {
  await startServer();
} else {
  supervise();
}

function supervise() {
  let child;
  let shuttingDown = false;
  const spawnChild = () => {
    child = fork(fileURLToPath(import.meta.url), process.argv.slice(2), {
      cwd: userCwd,
      stdio: 'inherit',
      env: { ...process.env, [SUPERVISED_ENV]: '1' },
    });
    child.on('exit', (code, signal) => {
      if (shuttingDown) process.exit(0);
      if (code === RESTART_EXIT_CODE) return spawnChild();
      process.exit(signal ? 1 : (code ?? 0));
    });
  };
  for (const signal of ['SIGINT', 'SIGTERM']) {
    process.on(signal, () => {
      shuttingDown = true;
      child?.kill(signal);
    });
  }
  spawnChild();
}

async function startServer() {
  const { createServer, mergeConfig } = await import('vite');
  const { createViteConfig } = await import('@open-slide/core/vite');
  const base = await createViteConfig({ userCwd });
  const server = await createServer(
    mergeConfig(base, {
      cacheDir: persistentCacheDir(),
      server: { host: '0.0.0.0' },
      plugins: [inlineSmallSvgImports()],
    }),
  );
  await server.listen();
  server.printUrls();
}

// node_modules may live on a disk that is wiped on restart; keep the optimized
// deps (and their browser hash) next to the project so browser caches stay valid.
function persistentCacheDir() {
  const dir = path.join(userCwd, '.vite-cache');
  const probe = path.join(dir, `.probe-${process.pid}`);
  try {
    fs.mkdirSync(path.join(probe, 'a'), { recursive: true });
    fs.writeFileSync(path.join(probe, 'a', 'f'), '');
    fs.renameSync(path.join(probe, 'a'), path.join(probe, 'b'));
    fs.rmSync(probe, { recursive: true, force: true });
    return dir;
  } catch (error) {
    console.warn(`[gamut-dev] ${dir} can't hold the Vite cache (${error.message}); using the default`);
    fs.rmSync(probe, { recursive: true, force: true });
    return undefined;
  }
}

// Each `import x from './a.svg'` costs a module request plus an image request.
// Runs after open-slide's loc tagging and keeps line counts, so inspector
// locations are unaffected.
function inlineSmallSvgImports() {
  return {
    name: 'gamut:inline-small-svg-imports',
    apply: 'serve',
    async transform(code, id) {
      if (!SCRIPT_ID.test(stripQuery(id)) || !isProjectFile(id) || !code.includes('.svg')) return null;
      const replacements = [];
      for (const match of code.matchAll(SVG_IMPORT)) {
        const [statement, name, , specifier] = match;
        const resolved = await this.resolve(specifier, id);
        if (!resolved || resolved.id.includes('?')) continue;
        const file = resolved.id;
        if (!isProjectFile(file) || !file.endsWith('.svg')) continue;
        let svg;
        try {
          svg = fs.readFileSync(file);
        } catch (error) {
          this.warn(`skipping ${file}: ${error.message}`);
          continue;
        }
        if (svg.length > SVG_INLINE_LIMIT_BYTES) continue;
        this.addWatchFile(file);
        const uri = `data:image/svg+xml;base64,${svg.toString('base64')}`;
        replacements.push([statement, `const ${name} = ${JSON.stringify(uri)};`]);
      }
      if (replacements.length === 0) return null;
      let out = code;
      for (const [from, to] of replacements) out = out.replace(from, () => to);
      return { code: out, map: null };
    },
  };
}

function stripQuery(id) {
  return id.split('?')[0];
}

function isProjectFile(file) {
  const rel = path.relative(userCwd, stripQuery(file));
  return !rel.startsWith('..') && !path.isAbsolute(rel) && !rel.split(path.sep).includes('node_modules');
}
