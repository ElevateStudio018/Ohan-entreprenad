"""Analyserar hemsidorna i kandidater.csv: skärmdumpar och uppmätta designvärden.

Kör:  python3 research/analysera.py research/kandidater.csv research/data

Resultat: data/resultat.json (en post per sajt) och data/shots/<slug>-desk.jpg / -mob.jpg.
"""
import asyncio
import csv
import json
import pathlib
import re
import sys
import unicodedata

from playwright.async_api import async_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
SHOTS = OUT / "shots"
SHOTS.mkdir(parents=True, exist_ok=True)

ACCEPT = ["Acceptera alla", "Godkänn alla", "Tillåt alla", "Acceptera alla cookies", "Godkänn alla cookies", "Jag godkänner",
          "Acceptera", "Godkänn", "Accept all", "Allow all", "Accept all cookies", "Accept", "OK", "Jag förstår", "Tillåt alla cookies"]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


# Runs in the page: measures what the eye sees above the fold and in the navigation.
MEASURE = r"""
() => {
  const cs = (el) => el ? getComputedStyle(el) : null;
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 2 && r.height > 2 && s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.05; };
  const first = (sel) => [...document.querySelectorAll(sel)].find(vis) || null;
  const fam = (el) => el ? cs(el).fontFamily.split(',')[0].replace(/["']/g, '').trim() : null;
  const out = {};
  out.title = document.title;
  const h1 = first('h1'), h2 = first('h2'), body = document.body;
  out.font_body = fam(first('main p') || first('p') || body);
  out.font_h1 = fam(h1); out.font_h2 = fam(h2);
  out.h1_size = h1 ? parseFloat(cs(h1).fontSize) : null;
  out.h1_weight = h1 ? cs(h1).fontWeight : null;
  out.h1_transform = h1 ? cs(h1).textTransform : null;
  out.h1_text = h1 ? h1.innerText.trim().slice(0, 140) : null;
  out.h1_letter = h1 ? cs(h1).letterSpacing : null;
  out.body_size = parseFloat(cs(first('main p') || first('p') || body).fontSize);
  out.fonts_loaded = [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family.replace(/["']/g, '')))].slice(0, 12);

  // Header
  const header = first('header') || first('[class*=header]') || first('nav');
  if (header) {
    const r = header.getBoundingClientRect(), s = cs(header);
    out.header_h = Math.round(r.height); out.header_pos = s.position; out.header_bg = s.backgroundColor;
    let p = header; let pos = s.position; while (p && pos === 'static') { p = p.parentElement; if (p) pos = cs(p).position; }
    out.header_sticky = ['fixed', 'sticky'].includes(pos);
  }
  const navLinks = [...document.querySelectorAll('header a, nav a')].filter(vis).filter(a => a.getBoundingClientRect().top < 160);
  out.nav_count = navLinks.length;
  out.nav_texts = [...new Set(navLinks.map(a => a.innerText.trim()).filter(t => t && t.length < 40))].slice(0, 25);
  out.nav_upper = navLinks.length ? cs(navLinks[0]).textTransform === 'uppercase' : null;
  out.has_burger_desktop = !!first('header button[aria-expanded], header [class*=burger], header [class*=hamburger], header [class*=menu-toggle], header [aria-label*=eny i], header [aria-label*=enu i]');
  out.has_search = !!first('header [type=search], header [aria-label*=ök i], header [aria-label*=Sök], header [class*=search], header [aria-label*=earch]');
  const allText = (document.body.innerText || '').toLowerCase();
  const navAll = [...document.querySelectorAll('header a, nav a, footer a')].map(a => (a.innerText || '').toLowerCase());
  const has = (re) => navAll.some(t => re.test(t));
  out.sig_investor = has(/investera|investor|aktie|finansiell|ir\b|rapport/);
  out.sig_hallbarhet = has(/hållbar|sustainab/);
  out.sig_karriar = has(/karriär|jobba|lediga|career|jobb/);
  out.sig_press = has(/press|nyheter|news|media/);
  out.sig_english = has(/^english$|^en$|in english/) || !!first('[hreflang=en], a[href*="/en/"], a[href*="/en-"]');

  // Buttons: the radius and colour of real call-to-actions
  const btns = [...document.querySelectorAll('a[class*=btn], a[class*=button], button, [role=button], a[class*=Button], a[class*=cta]')]
    .filter(vis).filter(b => { const r = b.getBoundingClientRect(); return r.height >= 28 && r.height <= 90 && r.width >= 50 && r.top < 5000; })
    .filter(b => { const s = cs(b); return s.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(s.borderTopWidth) > 0; });
  out.btn_count = btns.length;
  out.btn_samples = btns.slice(0, 8).map(b => { const s = cs(b), r = b.getBoundingClientRect();
    return { r: parseFloat(s.borderTopLeftRadius), h: Math.round(r.height), bg: s.backgroundColor, fg: s.color, border: s.borderTopWidth + ' ' + s.borderTopColor,
             upper: s.textTransform === 'uppercase', weight: s.fontWeight, text: (b.innerText || '').trim().slice(0, 30) }; });

  // Images: rounded or square
  const imgs = [...document.querySelectorAll('main img, img')].filter(vis).filter(i => { const r = i.getBoundingClientRect(); return r.width > 160 && r.height > 110; });
  out.img_count = imgs.length;
  out.img_radius = imgs.slice(0, 12).map(i => { let el = i, best = 0; for (let k = 0; k < 4 && el; k++) { const s = cs(el);
      const rr = parseFloat(s.borderTopLeftRadius) || 0; if (rr > best && (k === 0 || s.overflow !== 'visible')) best = rr; el = el.parentElement; } return best; });

  // Cards
  const cards = [...document.querySelectorAll('[class*=card], [class*=Card], [class*=teaser], [class*=tile]')].filter(vis).filter(c => { const r = c.getBoundingClientRect(); return r.width > 180 && r.height > 150; });
  out.card_count = cards.length;
  out.card_radius = cards.slice(0, 10).map(c => parseFloat(cs(c).borderTopLeftRadius) || 0);
  out.card_shadow = cards.slice(0, 10).filter(c => cs(c).boxShadow !== 'none').length;

  // Hero: the first big block
  const vh = innerHeight;
  const blocks = [...document.querySelectorAll('main > *, main section, body > div section, section, [class*=hero], [class*=Hero]')].filter(vis);
  const hero = blocks.find(b => { const r = b.getBoundingClientRect(); return r.top < 260 && r.height > 300; });
  if (hero) {
    const r = hero.getBoundingClientRect();
    out.hero_h_vh = +(r.height / vh).toFixed(2);
    out.hero_video = !!hero.querySelector('video') || !!first('video');
    const bgimg = [hero, ...hero.querySelectorAll('*')].slice(0, 60).some(e => cs(e).backgroundImage.includes('url('));
    out.hero_image = !!hero.querySelector('img, picture') || bgimg;
    const ht = hero.querySelector('h1, h2');
    out.hero_text_color = ht ? cs(ht).color : null;
    if (ht && hero.querySelector('img, picture, video')) {
      const a = ht.getBoundingClientRect(), m = (hero.querySelector('img, picture, video')).getBoundingClientRect();
      out.hero_overlay = a.left < m.right && a.right > m.left && a.top < m.bottom && a.bottom > m.top;
    } else out.hero_overlay = false;
  }
  // Max content width
  const wraps = [...document.querySelectorAll('main *')].slice(0, 400).filter(e => { const s = cs(e); return s.maxWidth.endsWith('px') && parseFloat(s.maxWidth) > 900; });
  out.max_width = wraps.length ? Math.max(...wraps.map(e => parseFloat(cs(e).maxWidth))) : null;

  // Colour census: backgrounds weighted by area, text colours by length, link colours
  const bg = {}, fg = {}, ac = {};
  const els = [...document.querySelectorAll('body *')].slice(0, 2500);
  for (const e of els) {
    const s = cs(e); const r = e.getBoundingClientRect();
    if (r.width < 2 || r.height < 2 || r.top > 4 * vh) continue;
    if (s.backgroundColor && s.backgroundColor !== 'rgba(0, 0, 0, 0)') { bg[s.backgroundColor] = (bg[s.backgroundColor] || 0) + Math.min(r.width * r.height, 1440 * 900); }
    if (e.childNodes.length && [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 2)) {
      fg[s.color] = (fg[s.color] || 0) + 1;
      if (e.tagName === 'A' || e.closest('button')) ac[s.color] = (ac[s.color] || 0) + 1;
    }
  }
  const top = (o, n) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([k, v]) => [k, Math.round(v)]);
  out.bg_colors = top(bg, 8); out.text_colors = top(fg, 6); out.link_colors = top(ac, 5);
  out.body_bg = cs(body).backgroundColor;
  const footer = first('footer');
  out.footer_bg = footer ? cs(footer).backgroundColor : null;
  out.page_h = document.documentElement.scrollHeight;
  out.sections = document.querySelectorAll('main section, main > div').length;
  out.has_video_any = !!first('video');
  out.anim = [...document.querySelectorAll('[data-aos], [class*=animate], [class*=reveal], [class*=fade]')].length;
  return out;
}
"""


async def dismiss(page):
    for txt in ACCEPT:
        for frame in page.frames:
            try:
                b = frame.get_by_role("button", name=re.compile(rf"^\s*{re.escape(txt)}\s*$", re.I)).first
                if await b.count() and await b.is_visible(timeout=300):
                    await b.click(timeout=1500)
                    await page.wait_for_timeout(700)
                    return txt
            except Exception:
                pass
    for sel in ["#onetrust-accept-btn-handler", "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", "#CybotCookiebotDialogBodyButtonAccept",
                "button#accept-all", ".cc-allow", "[data-cookiefirst-action=accept]", "#coiPage-1 .coi-banner__accept", "button.coi-banner__accept"]:
        try:
            b = page.locator(sel).first
            if await b.count() and await b.is_visible(timeout=300):
                await b.click(timeout=1500)
                await page.wait_for_timeout(700)
                return sel
        except Exception:
            pass
    return None


async def one(browser, row, sem, results):
    async with sem:
        try:
            await asyncio.wait_for(one_inner(browser, row, results), timeout=150)
        except asyncio.TimeoutError:
            results.append(dict(row, slug=slug(row["namn"]), ok=False, error="tidsgräns 150 s"))
            print("ERR " + row["namn"], "tidsgräns", flush=True)
        save(results)


async def one_inner(browser, row, results):
    if True:
        s = slug(row["namn"])
        rec = dict(row, slug=s)
        ctx = await browser.new_context(viewport={"width": 1440, "height": 900}, locale="sv-SE",
                                        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36")
        page = await ctx.new_page()
        page.on("dialog", lambda d: asyncio.ensure_future(d.dismiss()))
        try:
            resp = await page.goto(row["url"], wait_until="domcontentloaded", timeout=45000)
            rec["status"] = resp.status if resp else None
            try:
                await page.wait_for_load_state("networkidle", timeout=12000)
            except Exception:
                pass
            await page.wait_for_timeout(1500)
            rec["cookie"] = await dismiss(page)
            await page.wait_for_timeout(800)
            rec["final_url"] = page.url
            await page.screenshot(path=str(SHOTS / f"{s}-desk.jpg"), type="jpeg", quality=70)
            rec.update(await page.evaluate(MEASURE))
            # A taller look for the report: scroll through once so lazy images load, then a 3-screen capture
            for y in range(0, 2700, 450):
                await page.evaluate(f"window.scrollTo(0,{y})")
                await page.wait_for_timeout(180)
            await page.evaluate("window.scrollTo(0,0)")
            await page.wait_for_timeout(500)
            await page.screenshot(path=str(SHOTS / f"{s}-long.jpg"), type="jpeg", quality=55, clip={"x": 0, "y": 0, "width": 1440, "height": min(2700, rec.get("page_h") or 2700)})
            m = await ctx.new_page()
            await m.set_viewport_size({"width": 390, "height": 844})
            await m.goto(page.url, wait_until="domcontentloaded", timeout=45000)
            await m.wait_for_timeout(2500)
            await dismiss(m)
            await m.wait_for_timeout(500)
            await m.screenshot(path=str(SHOTS / f"{s}-mob.jpg"), type="jpeg", quality=65)
            rec["ok"] = True
        except Exception as e:
            rec["ok"] = False
            rec["error"] = str(e)[:200]
        finally:
            await ctx.close()
        results.append(rec)
        print(("OK  " if rec.get("ok") else "ERR ") + row["namn"], rec.get("error", "")[:80], flush=True)


def save(results):
    """Sparar efter varje sajt, så att en körning som avbryts inte tappar något."""
    path = OUT / "resultat.json"
    old = {r["slug"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    for r in results:
        old[r["slug"]] = r
    order = [slug(r["namn"]) for r in csv.DictReader(SRC.open(encoding="utf-8"))]
    merged = sorted(old.values(), key=lambda r: order.index(r["slug"]) if r["slug"] in order else 999)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    return merged


async def main():
    rows = list(csv.DictReader(SRC.open(encoding="utf-8")))
    only = set(sys.argv[3:])
    if only:
        rows = [r for r in rows if slug(r["namn"]) in only]
    results = []
    sem = asyncio.Semaphore(6)
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=CHROME)
        await asyncio.gather(*(one(browser, r, sem, results) for r in rows))
        try:
            await asyncio.wait_for(browser.close(), timeout=20)
        except Exception:
            pass
    merged = save(results)
    print("klart", sum(r.get("ok", False) for r in merged), "av", len(merged))


asyncio.run(main())
