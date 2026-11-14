import lighthouse from 'lighthouse'; import * as chromeLauncher from 'chrome-launcher';
const chrome = await chromeLauncher.launch({ chromePath: '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome', chromeFlags: ['--headless=new', '--no-sandbox', '--ignore-certificate-errors'] });
for (const u of process.argv.slice(2)) {
  const r = await lighthouse(u, { port: chrome.port, output: 'json', logLevel: 'error', onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'] });
  const lr = r.lhr; console.log('\n####', u, Object.values(lr.categories).map((c) => c.id + ' ' + Math.round(c.score * 100)).join(' | '));
  ['first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift','speed-index'].forEach(k=>console.log('  ', k, lr.audits[k].displayValue, lr.audits[k].score));
  for (const c of Object.values(lr.categories)) for (const ref of c.auditRefs) { const a = lr.audits[ref.id];
    if (!a || a.score === null || a.score >= 0.9 || ['manual','notApplicable','informative'].includes(a.scoreDisplayMode)) continue;
    console.log(' -', c.id, ref.id, a.displayValue || '');
    const items = (a.details && (a.details.items || [])) || [];
    items.slice(0, 6).forEach((it) => console.log('     ', JSON.stringify(it).slice(0, 260)));
  }
}
await chrome.kill();
