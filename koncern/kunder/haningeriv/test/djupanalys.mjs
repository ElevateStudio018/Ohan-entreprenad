// Kör Elevate Studios "Djupanalys" lokalt: samma serverkod (elevate-studio-pre/worker/crawl.js + sitecheck.js) och
// samma poängsättning som assets/js/sitetest-deep.js. Googles test (PSI = Lighthouse, mobil) körs med lokal Lighthouse
// i stället för PageSpeed-API:t, med samma kategorier.
//
//   node djupanalys.mjs <sajtens adress> <utfil.json> [domän för mejlkontroll]
import fs from 'node:fs';
// Sökväg till en klon av ElevateStudio018/elevate-studio-pre (Elevate Studios sajt med Djupanalys)
const ELEVATE = process.env.ELEVATE || '/home/user/elevate-studio-pre';
const { crawl } = await import(ELEVATE + '/worker/crawl.js');
const { siteCheck } = await import(ELEVATE + '/worker/sitecheck.js');
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

const [, , SITE, UT, MAILDOMAIN] = process.argv;
const base = new URL(SITE).origin + '/';
const API = 'https://elevatestudio.nu';
const env = {};
const post = async (op, body) => {
  const req = new Request(`${API}/api/crawl?op=${op}&url=${encodeURIComponent(base)}`, { method: 'POST', headers: { 'content-type': 'application/json', 'accept-encoding': 'gzip, br' }, body: JSON.stringify(body || {}) });
  return (await crawl(req, env)).json();
};
const chunks = (a, n) => { const c = []; for (let i = 0; i < a.length; i += n) c.push(a.slice(i, i + n)); return c; };
const log = (...a) => console.error('·', ...a);

// ---------- körningen (samma steg som run() i sitetest-deep.js) ----------
const R = { base };
const list = await post('list'); R.urls = process.env.URLS ? process.env.URLS.split(',') : (list.urls || []); log(R.urls.length, 'sidor i sajtkartan');
R.headers = await post('headers');
R.pages = [];
for (const c of chunks(R.urls, 12)) R.pages.push(...((await post('pages', { urls: c })).pages || []));
R.ok = R.pages.filter((p) => p.ok);
const internal = new Set(), external = new Set(), images = new Set();
R.ok.forEach((p) => { p.links.internal.forEach((h) => internal.add(h)); p.links.external.forEach((h) => external.add(h)); p.links.images.forEach((h) => images.add(h)); });
R.internal = [...internal]; R.external = [...external]; R.images = [...images];
R.linkStatus = {}; R.extStatus = {}; R.imgStatus = {};
for (const c of chunks(R.internal, 40)) ((await post('links', { urls: c })).links || []).forEach((l) => { R.linkStatus[l.url] = l; });
for (const c of chunks(R.external, 40)) ((await post('links', { urls: c })).links || []).forEach((l) => { R.extStatus[l.url] = l; });
for (const c of chunks(R.images, 40)) ((await post('images', { urls: c })).images || []).forEach((l) => { R.imgStatus[l.url] = l; });
log(R.internal.length, 'interna,', R.external.length, 'externa länkar,', R.images.length, 'bilder');
const sc = await (await siteCheck(new Request(`${API}/api/sitecheck?url=${encodeURIComponent(base)}`), env)).json();
R.files = sc.files || null; R.mail = sc.mail || null; R.cert = sc.cert || null;
if (MAILDOMAIN) { // den lokala testadressen har ingen DNS: mejl och certifikat läses från den riktiga domänen
  const m = await (await siteCheck(new Request(`${API}/api/sitecheck?url=${encodeURIComponent('https://' + MAILDOMAIN + '/')}`), env)).json();
  R.mail = m.mail; R.cert = m.cert;
}

// Googles test på upp till 12 viktiga sidor (samma urval som verktyget)
const pick = []; const add = (u) => { if (u && !pick.includes(u) && pick.length < 12) pick.push(u); };
add(R.base); R.ok.forEach((p) => { if (/\/(kontakt|priser|tjanster)/.test(p.url)) add(p.url); }); R.ok.forEach((p) => add(p.url));
R.psiPages = pick; R.psi = {};
const starta = () => chromeLauncher.launch({ chromePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', chromeFlags: ['--headless=new', '--no-sandbox', '--ignore-certificate-errors'] });
for (const u of pick) {
  const chrome = await starta();
  const r = await lighthouse(u, { port: chrome.port, output: 'json', logLevel: 'error', locale: 'sv', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] }, { extends: 'lighthouse:default', settings: { formFactor: 'mobile' } }).catch((e) => ({ error: e.message }));
  R.psi[u] = r && r.lhr ? r.lhr : { error: (r && r.error) || 'none' };
  await chrome.kill();
  log('Lighthouse', u.replace(base, '/'), R.psi[u].categories ? Object.values(R.psi[u].categories).map((c) => Math.round(c.score * 100)).join(' / ') : R.psi[u].error);
}

// ---------- poängen (kopierat från collect() och show() i sitetest-deep.js) ----------
const esc = (s) => String(s == null ? '' : s);
const path = (u) => esc(String(u).replace(/^https?:\/\/[^/]+/, '') || '/');
const kb = (b) => Math.round(b / 1024) + ' KB';
const PSI_CATS = ['performance', 'accessibility', 'best-practices', 'seo'];
const HEADERS_WANTED = { 'content-security-policy': 'Säkerhetspolicy (CSP)', 'strict-transport-security': 'HSTS', 'x-content-type-options': 'X-Content-Type-Options', 'x-frame-options': 'X-Frame-Options', 'referrer-policy': 'Referrer-Policy', 'permissions-policy': 'Permissions-Policy' };
const SEVERE = { 'seo|title-missing': 1, 'seo|h1-missing': 1, 'seo|noindex': 1, 'seo|robots-block': 1, 'practice|mixed': 1, 'security|spf': 1, 'security|dmarc': 1, 'security|cert': 1, 'links|broken-int': 1, 'links|broken-ext': 1, 'links|img-broken': 1, 'practice|hdr-content-security-policy': 1 };
function collect(R) {
  const F = {};
  const add = (cat, id, label, where, extra) => { const k = cat + '|' + id; if (!F[k]) F[k] = { cat, id, label, where: [], google: !!extra }; F[k].where.push(where); };
  const ok = R.ok, pageBad = { seo: {}, access: {}, practice: {}, perf: {} }, extBroken = {}, extSeen = {};
  ok.forEach((p) => {
    const a = p.a, d = p.d, u = p.url, lab = path(u);
    const t = (cat, id, label) => { pageBad[cat][u] = (pageBad[cat][u] || 0) + (SEVERE[cat + '|' + id] ? 30 : 8); add(cat, id, label, lab); };
    if (!a.titleLen) t('seo', 'title-missing', 'Sidan saknar titel');
    if (a.titleLen > 60) t('seo', 'title-long', 'Titeln är för lång (över 60 tecken)');
    if (a.titleLen && a.titleLen < 25) t('seo', 'title-short', 'Titeln är för kort (under 25 tecken)');
    if (!a.descLen) t('seo', 'desc-missing', 'Saknar metabeskrivning');
    if (a.descLen > 160) t('seo', 'desc-long', 'Beskrivningen är för lång (över 160 tecken)');
    if (a.descLen && a.descLen < 70) t('seo', 'desc-short', 'Beskrivningen är för kort (under 70 tecken)');
    if (a.h1 === 0) t('seo', 'h1-missing', 'Saknar rubrik h1');
    if (a.h1 > 1) t('seo', 'h1-multi', 'Har flera rubriker h1');
    if (d.headingSkips) t('seo', 'heading-skip', 'Rubriknivåerna hoppar');
    if (d.emptyHeadings) t('seo', 'heading-empty', 'Tomma rubriker');
    if (!a.canonical) t('seo', 'canonical', 'Saknar canonical-länk');
    if (!d.ogComplete) t('seo', 'og', 'Saknar fullständig Open Graph');
    if (a.noindex) t('seo', 'noindex', 'Markerad noindex, Google visar inte sidan');
    if (a.ldBad) t('seo', 'ld-bad', 'Strukturerad data (JSON-LD) är trasig');
    if (d.genericLinks) t('seo', 'generic', 'Länktext som "läs mer" eller "klicka här"');
    if (d.words < 150) t('seo', 'thin', 'Tunn text, under 150 ord (' + d.words + ' ord)');
    if (d.metaRefresh) t('practice', 'refresh', 'Använder meta refresh');
    if (!a.lang) t('access', 'lang', 'Språket är inte angivet');
    if (!a.viewport) t('access', 'viewport', 'Saknar viewport');
    if (a.noAlt) t('access', 'alt', 'Bilder saknar alt-text (' + a.noAlt + ' st)');
    if (d.emptyLinks) t('access', 'link-empty', 'Länkar utan text eller etikett');
    if (d.emptyButtons) t('access', 'button-empty', 'Knappar utan text eller etikett');
    if (d.unlabeledInputs) t('access', 'input-label', 'Fält utan etikett');
    if (!d.doctype) t('practice', 'doctype', 'Saknar doctype');
    if (!d.charset) t('practice', 'charset', 'Saknar charset');
    if (a.mixed) t('practice', 'mixed', 'Laddar innehåll över http');
    if (d.blankTarget) t('practice', 'blank', 'Ny flik utan rel="noopener" (' + d.blankTarget + ' st)');
    if (d.deprecated) t('practice', 'deprecated', 'Föråldrade HTML-taggar');
    if (d.blockingScripts) t('perf', 'blocking', 'Skript i sidhuvudet blockerar visningen (' + d.blockingScripts + ' st)');
    if (d.imgNoSize) t('perf', 'img-size', 'Bilder utan width och height (' + d.imgNoSize + ' st)');
    if (d.bytes > 150 * 1024) t('perf', 'heavy', 'Stor HTML-fil (' + kb(d.bytes) + ')');
    if (d.inlineStyles > 200) t('perf', 'inline-styles', 'Många inline-stilar (' + d.inlineStyles + ')');
    if (d.inlineScripts > 5) t('perf', 'inline-scripts', 'Många inline-skript (' + d.inlineScripts + ')');
  });
  const titles = {}, texts = {};
  ok.forEach((p) => { if (p.a.title) (titles[p.a.title] = titles[p.a.title] || []).push(p.url); if (p.d.words >= 30) (texts[p.d.textHash] = texts[p.d.textHash] || []).push(p.url); });
  Object.keys(titles).forEach((t) => { if (titles[t].length > 1) titles[t].forEach((u) => add('seo', 'dup-title', 'Samma titel på flera sidor', path(u))); });
  Object.keys(texts).forEach((h) => { if (texts[h].length > 1) texts[h].forEach((u) => add('seo', 'dup-text', 'Samma innehåll på flera sidor', path(u))); });
  ok.forEach((p) => {
    p.links.internal.forEach((h) => { const s = R.linkStatus[h] || {}; if (!s.status || s.status >= 400) add('links', 'broken-int', 'Trasig intern länk', path(p.url) + ' → ' + path(h) + ' (' + (s.status || 'inget svar') + ')'); else if (s.redirected) add('links', 'redir', 'Intern länk som omdirigeras', path(p.url) + ' → ' + path(h)); });
    p.links.external.forEach((h) => { const s = R.extStatus[h] || {}; if (s.status === 429 || s.status === 403 || s.status === 999) { extSeen[h] = extSeen[h] || { status: s.status, pages: [] }; extSeen[h].pages.push(p.url); } else if (!s.status || s.status >= 400) { extBroken[h] = extBroken[h] || { status: s.status, pages: [] }; extBroken[h].pages.push(p.url); } });
  });
  Object.keys(extBroken).forEach((h) => add('links', 'broken-ext', 'Trasig extern länk', h + ' (' + (extBroken[h].status || 'inget svar') + ')'));
  Object.keys(extSeen).forEach((h) => add('links', 'ext-unknown', 'Extern länk som inte går att kontrollera automatiskt', h + ' svarar ' + extSeen[h].status));
  const imgTotal = Object.keys(R.imgStatus).length;
  Object.keys(R.imgStatus).forEach((src) => { const im = R.imgStatus[src], where = path(src); if (!im.status || im.status >= 400) add('links', 'img-broken', 'Trasig bild', where); if (im.bytes > 300 * 1024) add('perf', 'img-big', 'Stor bild över 300 KB (' + kb(im.bytes) + ')', where); else if (im.bytes > 120 * 1024 && /jpeg|png/.test(im.type)) add('perf', 'img-format', 'Bild över 120 KB i jpg eller png (' + kb(im.bytes) + ')', where); });
  const files = R.files || {};
  if (files.sitemap && !files.sitemap.found) add('seo', 'sitemap', 'Sajtkartan hittades inte', 'sajten');
  if (files.robots && !files.robots.found) add('seo', 'robots', 'robots.txt hittades inte', 'sajten');
  if (files.robots && files.robots.blocksAll) add('seo', 'robots-block', 'robots.txt blockerar hela sajten', 'sajten');
  if (files.notFound && !files.notFound.ok) add('seo', 'soft404', 'En okänd adress svarar ' + (files.notFound.status || 'inget') + ' i stället för 404', 'sajten');
  const hd = (R.headers && R.headers.home) || {};
  Object.keys(HEADERS_WANTED).forEach((h) => { if (R.headers && !hd[h]) add('practice', 'hdr-' + h, HEADERS_WANTED[h] + ' saknas', 'startsidan'); });
  if (R.headers && hd['content-encoding'] === null) add('perf', 'no-gzip', 'Sidan komprimeras inte', 'startsidan');
  const css = (R.headers && R.headers.css) || {};
  if (R.headers && !css['cache-control']) add('perf', 'no-cache-css', 'Stilfilen saknar cache-inställning', 'stilfilen');
  const m = R.mail;
  if (m) {
    if (!m.spf.found) add('security', 'spf', 'SPF saknas', 'domänen');
    if (!m.dkim.found) add('security', 'dkim', 'DKIM hittades inte', 'domänen');
    if (!m.dmarc.found) add('security', 'dmarc', 'DMARC saknas', 'domänen'); else if (m.dmarc.policy === 'none') add('security', 'dmarc-none', 'DMARC står på none', 'domänen');
    if (!m.mx.found) add('security', 'mx', 'Inga MX-poster', 'domänen');
  }
  if (R.cert && R.cert.checked && R.cert.daysLeft < 30) add('security', 'cert', 'Certifikatet går ut om ' + R.cert.daysLeft + ' dagar', 'domänen');
  const psiOk = R.psiPages.filter((u) => R.psi[u] && !R.psi[u].error);
  const hits = {};
  psiOk.forEach((u) => { const lr = R.psi[u]; PSI_CATS.forEach((c) => { const cat = lr.categories[c]; if (!cat) return; cat.auditRefs.forEach((ref) => { const a = lr.audits[ref.id]; if (!a || a.score === null || a.score >= 0.9 || ['manual', 'notApplicable', 'informative'].includes(a.scoreDisplayMode)) return; const k = c + '|' + ref.id; hits[k] = hits[k] || { cat: c, id: ref.id, title: a.title, pages: [], value: a.displayValue || '' }; hits[k].pages.push(path(u)); }); }); });
  const gcat = (c) => (c === 'performance' ? 'perf' : c === 'accessibility' ? 'access' : c === 'best-practices' ? 'practice' : 'seo');
  return { F, pageBad, psiOk, hits, gcat, imgTotal };
}
const C = collect(R), F = C.F, total = R.ok.length || 1;
const pctPages = (cat) => { let lost = 0; Object.keys(C.pageBad[cat]).forEach((u) => { lost += Math.min(100, C.pageBad[cat][u]); }); return Math.max(0, Math.round(100 - lost / total)); };
const linksTotal = R.internal.length + R.external.length;
const linksBad = Object.keys(F).filter((k) => k.indexOf('links|broken') === 0).reduce((n, k) => n + F[k].where.length, 0);
let sec = 0; ['spf', 'dkim', 'dmarc', 'dmarc-none', 'mx', 'cert'].forEach((id) => { if (F['security|' + id]) sec++; });
const secPct = Math.max(0, Math.round((6 - sec) / 6 * 100));
const gAvg = {};
if (C.psiOk.length) PSI_CATS.forEach((c) => { const s = C.psiOk.map((u) => R.psi[u].categories[c].score); gAvg[c] = Math.round(s.reduce((a, b) => a + b, 0) / s.length * 100); });
const G2 = { seo: 'seo', access: 'accessibility', practice: 'best-practices', perf: 'performance' };
const blend = (cat) => { const ours = pctPages(cat), g = gAvg[G2[cat]]; const v = g == null ? ours : Math.round((ours + g) / 2); const open = Object.keys(F).some((k) => F[k].cat === cat) || Object.keys(C.hits).some((k) => C.gcat(C.hits[k].cat) === cat); return open ? Math.min(v, 99) : v; };
const linksPct = linksTotal ? Math.round((linksTotal - linksBad) / linksTotal * 100) : 100;
const scores = { SEO: blend('seo'), 'Tillgänglighet': blend('access'), 'Bästa praxis': blend('practice'), Prestanda: blend('perf'), 'Säkerhet och mejl': secPct, 'Länkar': linksPct };
const findings = [...Object.values(F).map((f) => ({ kategori: f.cat, id: f.id, fel: f.label, antal: f.where.length, var: f.where.slice(0, 8) })),
  ...Object.values(C.hits).map((h) => ({ kategori: C.gcat(h.cat), id: 'google:' + h.id, fel: 'Googles test: ' + h.title, antal: h.pages.length, var: h.pages.slice(0, 8), varde: h.value }))];
const ut = { sajt: base, datum: new Date().toISOString(), sidor: R.ok.length, sidorISajtkarta: R.urls.length, lankar: { interna: R.internal.length, externa: R.external.length }, bilder: C.imgTotal,
  betyg: scores, google: gAvg, googlePerSida: Object.fromEntries(C.psiOk.map((u) => [path(u), Object.fromEntries(PSI_CATS.map((c) => [c, Math.round(R.psi[u].categories[c].score * 100)]))])),
  mejl: R.mail, fel: findings, sidinfo: R.ok.map((p) => ({ url: path(p.url), titel: p.a.title, titelLangd: p.a.titleLen, beskrivning: p.a.desc, beskrLangd: p.a.descLen, h1: p.a.h1, ord: p.d.words, canonical: p.a.canonical, noindex: p.a.noindex, ld: p.a.ld, ldTypes: p.d.ldTypes })) };
fs.writeFileSync(UT, JSON.stringify(ut, null, 1));
console.log(JSON.stringify(scores), '| Google:', JSON.stringify(gAvg));
findings.forEach((f) => console.log(' -', f.kategori, '|', f.fel, '|', f.antal, f.varde ? '| ' + f.varde : ''));
