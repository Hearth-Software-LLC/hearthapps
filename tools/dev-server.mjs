// Local preview server for hearthapps.com — no dependencies.
// Serves this folder the way Vercel does (vercel.json "cleanUrls"):
//   /privacy -> privacy/index.html, /about -> about.html, unknown paths -> 404.html.
//
//   npm run dev              http://localhost:3000
//   PORT=8080 npm run dev    another port
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = fileURLToPath(new URL('..', import.meta.url));
const PORT = Number(process.env.PORT) || 3000;
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8', '.json': 'application/json', '.webmanifest': 'application/manifest+json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.txt': 'text/plain; charset=utf-8', '.xml': 'application/xml; charset=utf-8', '.woff2': 'font/woff2',
};

async function isFile(p) { try { return (await stat(p)).isFile(); } catch { return false; } }

async function resolve(urlPath) {
  const clean = normalize(decodeURIComponent(urlPath)).replace(/^(\.\.[/\\])+/, '');
  const base = join(ROOT, clean);
  if (!base.startsWith(ROOT) || base.includes(`${sep}tools${sep}`) || base.includes(`${sep}_to_delete${sep}`)) return null;
  for (const candidate of [base, base + '.html', join(base, 'index.html')]) {
    if (await isFile(candidate)) return candidate;
  }
  return null;
}

createServer(async (req, res) => {
  const { pathname } = new URL(req.url, 'http://localhost');
  // Clean URLs: /privacy/index.html or /privacy.html redirect to /privacy, as on Vercel.
  if (/\/index\.html$|\.html$/.test(pathname) && pathname !== '/404.html') {
    const target = pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '') || '/';
    res.writeHead(308, { Location: target }); res.end(); return;
  }
  let file = await resolve(pathname);
  let status = 200;
  if (!file) { file = join(ROOT, '404.html'); status = 404; }
  const body = await readFile(file);
  res.writeHead(status, { 'Content-Type': TYPES[extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  res.end(body);
  console.log(`${status} ${req.method} ${pathname}`);
}).listen(PORT, () => {
  console.log(`\n  Hearth is running at http://localhost:${PORT}\n`);
});
