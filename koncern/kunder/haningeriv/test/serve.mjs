// Statisk server som beter sig som Cloudflare Pages / Netlify: _headers, _redirects (301), gzip, 404.html med status 404.
import https from 'node:https'; import fs from 'node:fs'; import path from 'node:path'; import zlib from 'node:zlib';
const [, , ROOT, PORT = 8443] = process.argv;
const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json', '.xml': 'application/xml', '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.woff2': 'font/woff2', '.ico': 'image/x-icon' };
const rules = []; let cur = null;
for (const line of (fs.existsSync(path.join(ROOT, '_headers')) ? fs.readFileSync(path.join(ROOT, '_headers'), 'utf8') : '').split('\n')) {
  if (!line.trim()) continue;
  if (!/^\s/.test(line)) { cur = { pat: new RegExp('^' + line.trim().replace(/[.+^${}()|[\]\\]/g, '\\$&').replace(/\*/g, '.*') + '$'), h: [] }; rules.push(cur); }
  else { const i = line.indexOf(':'); cur.h.push([line.slice(0, i).trim(), line.slice(i + 1).trim()]); }
}
const redirects = Object.fromEntries((fs.existsSync(path.join(ROOT, '_redirects')) ? fs.readFileSync(path.join(ROOT, '_redirects'), 'utf8') : '').split('\n').filter(Boolean).map((l) => l.split(/\s+/)));
const headersFor = (p) => { const o = {}; rules.forEach((r) => { if (r.pat.test(p)) r.h.forEach(([k, v]) => { o[k] = v; }); }); return o; };
https.createServer({ key: fs.readFileSync(new URL('key.pem', import.meta.url)), cert: fs.readFileSync(new URL('cert.pem', import.meta.url)) }, (req, res) => {
  const u = new URL(req.url, 'https://x'); let p = decodeURIComponent(u.pathname);
  if (redirects[p]) { res.writeHead(301, { location: redirects[p] }); return res.end(); }
  if (p.endsWith('/')) p += 'index.html';
  let file = path.resolve(ROOT, '.' + p), status = 200;
  if (!file.startsWith(path.resolve(ROOT)) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) { file = path.resolve(ROOT, '404.html'); status = 404; }
  const ext = path.extname(file); let body = fs.readFileSync(file);
  const h = { 'content-type': TYPES[ext] || 'application/octet-stream', ...headersFor(p), ...(status === 404 ? headersFor('/404.html') : {}) };
  if (/text|json|xml|svg|javascript/.test(h['content-type']) && /gzip/.test(req.headers['accept-encoding'] || '')) { body = zlib.gzipSync(body); h['content-encoding'] = 'gzip'; h.vary = 'Accept-Encoding'; }
  h['content-length'] = body.length;
  res.writeHead(status, h); res.end(req.method === 'HEAD' ? undefined : body);
}).listen(PORT, '127.0.0.1', () => console.log('https://127.0.0.1:' + PORT));
