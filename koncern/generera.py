"""Bygger en koncernhemsida från ett innehåll (brief) och ett grafiskt paket.

Kör:  python3 koncern/generera.py <brief.json> <paket.json> <utmapp>

brief.json  – företagets innehåll (se koncern/exempel/*.json för formatet)
paket.json  – det grafiska paketet (se koncern/paket.py, som skapar unika paket)

Sajten blir statisk HTML/CSS/JS utan beroenden: index, verksamhet, projekt, hallbarhet, investerare, karriar, om-oss.
"""
import hashlib
import html
import json
import pathlib
import random
import shutil
import sys

ROT = pathlib.Path(__file__).resolve().parent
BANK = ROT / "bildbank"
E = html.escape

ELEVATE_CREDIT = '''<!-- elevate-credit -->
<style>.elevate-credit{max-width:1240px;margin:24px auto 0;padding:20px 16px 0;border-top:1px solid rgba(128,128,128,.25);display:flex;justify-content:center;box-sizing:border-box}.elevate-credit a{display:inline-flex;align-items:center;gap:10px;padding:8px 0;font:inherit;font-size:15px;line-height:1;color:inherit;opacity:.55;text-decoration:none;transition:opacity .2s}.elevate-credit a:hover,.elevate-credit a:focus-visible{opacity:1}.elevate-credit svg{width:20px;height:20px;flex:none;display:block}@media(min-width:1024px){.elevate-credit a{font-size:16px}}</style>
<div class="elevate-credit"><a href="https://elevatestudio.nu" target="_blank" rel="noopener"><svg viewBox="0 0 1884.3 1353.9" aria-hidden="true"><path d="M0.0 1353.9 L1218.7 0.0 L1218.7 329.1 L479.7 1136.4 L786.7 1132.4 L1215.5 687.4 L1884.3 1349.9 L1590.1 1349.9 L1218.6 994.7 L865.4 1349.9Z" fill="currentColor"/></svg>Byggd av Elevate Studio</a></div>
'''

PIL = '<svg class="pil" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h16M14 6l6 6-6 6"/></svg>'
SOK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/></svg>'

SIDOR = [("verksamhet", "Verksamhet"), ("projekt", "Projekt"), ("hallbarhet", "Hållbarhet"), ("investerare", "Investerare"),
         ("karriar", "Karriär"), ("om-oss", "Om oss")]


# --- Logga: ett enkelt märke som paketet styr (form), plus namnet i rubriktypsnittet --------------------------------
def marke(form, farg, ink):
    if form == "ring":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="14" fill="none" stroke="{farg}" stroke-width="7"/></svg>'
    if form == "kvadrat":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="3" y="3" width="34" height="34" fill="{farg}"/><path d="M11 29V11h7l11 18V11" fill="none" stroke="{ink}" stroke-width="3.2"/></svg>'
    if form == "tak":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M3 21 20 6l17 15v14H3z" fill="{farg}"/><path d="M15 35V24h10v11" fill="{ink}"/></svg>'
    if form == "bage":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M4 34V20a16 16 0 0 1 32 0v14h-8V20a8 8 0 0 0-16 0v14z" fill="{farg}"/></svg>'
    if form == "staplar":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="4" y="18" width="8" height="18" fill="{farg}"/><rect x="16" y="10" width="8" height="26" fill="{farg}"/><rect x="28" y="3" width="8" height="33" fill="{farg}"/></svg>'
    if form == "blad":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M6 34C6 16 18 5 36 5c0 18-11 29-29 29z" fill="{farg}"/><path d="M8 32 26 14" stroke="{ink}" stroke-width="2.5"/></svg>'
    if form == "romb":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 2 38 20 20 38 2 20z" fill="{farg}"/><path d="M20 12 28 20 20 28 12 20z" fill="{ink}"/></svg>'
    if form == "vag":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="10" fill="{farg}"/><path d="M8 26c6-10 10-10 12-6s6 4 12-6" fill="none" stroke="{ink}" stroke-width="3.5" stroke-linecap="round"/></svg>'
    if form == "punkt":
        return f'<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="20" r="17" fill="{farg}"/><circle cx="20" cy="20" r="6" fill="{ink}"/></svg>'
    return ""  # "ingen": bara ordbild


def logga(b, p, href):
    m = marke(p["logga"]["form"], p["logga"]["farg"], p["logga"]["ink"])
    namn = b["kortnamn"]
    return f'<a class="logga" href="{href}" aria-label="{E(b["namn"])}, till startsidan">{m}<span>{E(namn)}</span></a>'


# --- Bilder ---------------------------------------------------------------------------------------------------------
def bildbank():
    rader = []
    for line in (ROT / "bildbank.tsv").read_text(encoding="utf-8").splitlines():
        id_, tagg, alt = line.split("\t")
        rader.append(dict(id=id_, tagg=tagg, alt=alt))
    return rader


class Bilder:
    """Väljer bilder efter tagg utan att upprepa, med paketets frö så att två sajter får olika urval."""

    prefix = "img/"

    def __init__(self, fro, ut, tyngd, delad=None):
        self.rng = random.Random(fro)
        self.bank = bildbank()
        self.anvanda = set()
        self.ut = ut
        self.tyngd = tyngd
        self.delad = delad  # (mapp, url-prefix): bilderna läggs i en gemensam mapp som flera sajter delar
        if delad:
            Bilder.prefix = delad[1]
            delad[0].mkdir(parents=True, exist_ok=True)
        else:
            Bilder.prefix = "img/"
            (ut / "img").mkdir(parents=True, exist_ok=True)

    def ta(self, tagg=None):
        taggar = [tagg] if tagg else []
        taggar += self.tyngd + ["kontor", "bostad", "bygg", "stad", "tra", "infra", "people", "interior", "anlaggning"]
        for t in taggar:
            kandidater = [b for b in self.bank if b["tagg"] == t and b["id"] not in self.anvanda]
            if kandidater:
                b = self.rng.choice(kandidater)
                break
        else:
            self.anvanda.clear()
            b = self.rng.choice(self.bank)
        self.anvanda.add(b["id"])
        mal = self.delad[0] if self.delad else self.ut / "img"
        for suf in ("", "-s"):
            src = BANK / f'{b["id"]}{suf}.jpg'
            if src.exists() and not (mal / src.name).exists():
                shutil.copy(src, mal / src.name)
        return b

    @staticmethod
    def img(b, sizes="100vw", lazy=True, pos="50% 50%"):
        q = Bilder.prefix
        return (f'<img src="{q}{b["id"]}.jpg" srcset="{q}{b["id"]}-s.jpg 700w, {q}{b["id"]}.jpg 1600w" sizes="{sizes}" alt="{E(b["alt"])}" '
                f'{"loading=\"lazy\" " if lazy else "fetchpriority=\"high\" "}decoding="async" style="object-position:{pos}">')

    def foto(self, b, cls="", sizes="(min-width: 960px) 50vw, 100vw"):
        return f'<figure class="foto {cls}">{self.img(b, sizes)}<figcaption>Illustrationsbild</figcaption></figure>'


# --- Tokens ---------------------------------------------------------------------------------------------------------
def tokens_css(p):
    f, t, fo = p["farger"], p["typsnitt"], p["form"]
    v = {
        "--font-r": f'"{t["rubrik"]}", {t.get("rubrik_fallback", "system-ui, sans-serif")}',
        "--font-t": f'"{t["text"]}", {t.get("text_fallback", "system-ui, sans-serif")}',
        "--w-r": t["rubrik_vikt"], "--tr-r": t["spatiering"], "--tt-r": "uppercase" if t.get("versaler") else "none",
        "--skala-r": t.get("skala", 1), "--t-text": f'{t.get("textstorlek", 18)}px', "--w-siffra": t.get("siffra_vikt", t["rubrik_vikt"]),
        "--w-logo": t.get("logo_vikt", 700), "--tr-logo": t.get("logo_spatiering", "-0.01em"), "--tt-logo": "uppercase" if t.get("logo_versaler") else "none",
        "--tt-nav": "uppercase" if t.get("nav_versaler") else "none", "--tr-nav": ".08em" if t.get("nav_versaler") else "0",
        "--tt-btn": "uppercase" if t.get("knapp_versaler") else "none", "--tr-btn": ".08em" if t.get("knapp_versaler") else "0",
        "--c-p": f["primar"], "--c-p2": f.get("primar2", f["primar"]), "--c-p-ink": f["primar_ink"], "--c-p-text": f.get("primar_text", f["primar"]),
        "--c-a": f["accent"], "--c-a-on-dark": f.get("accent_mork", f["accent"]),
        "--c-bg": f["bg"], "--c-yta": f["yta"], "--c-ink": f["ink"], "--c-rubrik": f.get("rubrik", f["ink"]), "--c-mut": f["mut"], "--c-line": f["linje"],
        "--c-etikett": f.get("etikett", f["primar"]), "--c-siffra": f.get("siffra", f["primar"]),
        "--c-dark": f["mork"], "--c-dark-ink": f["mork_ink"], "--c-dark-mut": f.get("mork_mut", "rgba(255,255,255,.68)"),
        "--c-head": f.get("header", f["bg"]), "--c-head-ink": f.get("header_ink", f["ink"]),
        "--c-split": f.get("split", f["primar"]), "--c-split-ink": f.get("split_ink", f["primar_ink"]),
        "--c-fot": f["sidfot"], "--c-fot-ink": f["sidfot_ink"], "--c-fot-mut": f.get("sidfot_mut", "rgba(255,255,255,.62)"),
        "--c-fot-linje": f.get("sidfot_linje", "rgba(255,255,255,.16)"),
        "--r-btn": f'{fo["knapp"]}px', "--r-card": f'{fo["kort"]}px', "--r-img": f'{fo["bild"]}px', "--r-hero": f'{fo.get("hero", 0)}px',
        "--r-cta": f'{fo.get("cta", fo["kort"])}px', "--maxw": f'{p.get("maxbredd", 1320)}px', "--head-h": f'{p.get("header_hojd", 84)}px',
    }
    return ":root{" + ";".join(f"{k}:{val}" for k, val in v.items()) + "}\n"


def google_fonts(p):
    t = p["typsnitt"]
    fams = []
    for namn, vikter in ((t["rubrik"], t.get("rubrik_vikter", "400;500;600;700")), (t["text"], t.get("text_vikter", "400;500;600;700"))):
        if t.get("google", True) and namn not in [f[0] for f in fams]:
            fams.append((namn, vikter))
    if not fams:
        return ""
    q = "&".join(f"family={n.replace(' ', '+')}:wght@{w}" for n, w in fams)
    return (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">')


def ver(path):
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


# --- Sidbitar -------------------------------------------------------------------------------------------------------
class Sajt:
    def __init__(self, b, p, ut, delad=None):
        self.b, self.p, self.ut, self.delad = b, p, ut, delad

    def body_klass(self, har_hero):
        p = self.p
        attr = {"hero": p["hero"], "kort": p["kort"], "knapp": p["knappstil"], "header": p["header"], "meny": p["meny"],
                "rytm": p["rytm"], "sidhero": p.get("sidhero", "bild")}
        return ('class="har-hero" ' if har_hero else "") + " ".join(f'data-{k}="{v}"' for k, v in attr.items())

    def knapp(self, text, href, typ="primar", pil=True):
        return f'<a class="knapp knapp-{typ}" href="{href}"><span>{E(text)}</span>{PIL if pil else ""}</a>'

    def header(self, aktiv):
        b, p = self.b, self.p
        links = "".join(f'<a href="{s}.html"{" aria-current=page" if s == aktiv else ""}>{t}</a>' for s, t in SIDOR)
        topp = ""
        if p["header"] == "topbar":
            topp = ('<div class="topprad"><div class="wrap"><a href="investerare.html">Investerare</a><a href="om-oss.html#press">Press</a>'
                    '<a href="karriar.html">Lediga jobb</a><a href="om-oss.html#kontakt">Kontakt</a><a href="#" lang="en">English</a></div></div>')
        meny_huvud = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, t in SIDOR)
        omr = "".join(f'<li><a href="verksamhet.html#omr-{i}">{E(a["titel"])}</a></li>' for i, a in enumerate(b["affarsomraden"]))
        return f'''<a class="skip" href="#main">Hoppa till innehållet</a>
{topp}<header class="head" id="head">
  <div class="wrap">
    {logga(b, p, "index.html")}
    <nav class="nav" aria-label="Huvudmeny">{links}</nav>
    <div class="head-verktyg">
      <a class="sok" href="#" aria-label="Sök">{SOK}</a>
      <button class="meny-knapp" id="menyKnapp" type="button" aria-expanded="false" aria-controls="meny"><span class="ord">Meny</span><span class="streck"><i></i><i></i><i></i></span></button>
    </div>
  </div>
  <nav class="meny" id="meny" aria-label="Meny" hidden>
    <div class="wrap">
      <ul class="meny-huvud">{meny_huvud}</ul>
      <div><h4>Affärsområden</h4><ul>{omr}</ul></div>
      <div><h4>Genvägar</h4><ul><li><a href="investerare.html#rapporter">Rapporter</a></li><li><a href="om-oss.html#press">Press och nyheter</a></li><li><a href="karriar.html#jobb">Lediga jobb</a></li><li><a href="om-oss.html#kontakt">Kontakta oss</a></li></ul></div>
    </div>
  </nav>
</header>'''

    def footer(self):
        b, p, k = self.b, self.p, self.b["kontakt"]
        sid = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, t in SIDOR)
        omr = "".join(f'<li><a href="verksamhet.html#omr-{i}">{E(a["titel"])}</a></li>' for i, a in enumerate(b["affarsomraden"]))
        stor = f'<p class="stor-logga" aria-hidden="true">{E(b["kortnamn"])}</p>' if p.get("sidfot_stor_logga") else ""
        return f'''<footer class="fot">
  <div class="wrap">
    <div class="fot-topp"><div>{logga(b, p, "index.html")}<p>{E(b["hero_text"])}</p></div>{self.knapp("Kontakta oss", "om-oss.html#kontakt", "primar")}</div>
    <div class="fot-grid">
      <div><h4>{E(b["kortnamn"])}</h4><ul>{sid}</ul></div>
      <div><h4>Affärsområden</h4><ul>{omr}</ul></div>
      <div><h4>Kontakt</h4><ul><li>{E(k["adress"])}</li><li>{E(k["postnr"])} {E(k["ort"])}</li><li><a href="tel:{k["telefon"].replace(" ", "").replace("-", "")}">{E(k["telefon"])}</a></li><li><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></li></ul></div>
      <div><h4>Följ oss</h4><ul><li><a href="#">LinkedIn</a></li><li><a href="#">Instagram</a></li><li><a href="#">YouTube</a></li><li><a href="#" lang="en">English</a></li></ul></div>
    </div>
    {stor}
    <div class="fot-slut"><span>© <span data-year>2026</span> {E(b["namn"])} · Org.nr {E(k["orgnr"])}</span><span>Cookies · Integritet · Tillgänglighet</span></div>
  </div>
{ELEVATE_CREDIT}</footer>'''

    def sida(self, namn, titel, beskrivning, main, aktiv=None, har_hero=False):
        b, p = self.b, self.p
        css_v, js_v = ver(self.ut / "assets/bas.css"), ver(self.ut / "assets/sajt.js")
        tok_v = ver(self.ut / "assets/tokens.css")
        doc = f'''<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(titel)}</title>
<meta name="description" content="{E(beskrivning)}">
<meta name="theme-color" content="{p["farger"]["mork"]}">
<meta property="og:title" content="{E(titel)}"><meta property="og:description" content="{E(beskrivning)}"><meta property="og:image" content="{Bilder.prefix}{self.hero_bild["id"]}.jpg">
{google_fonts(p)}
<link rel="stylesheet" href="assets/tokens.css?v={tok_v}">
<link rel="stylesheet" href="assets/bas.css?v={css_v}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body {self.body_klass(har_hero)}>
{self.header(aktiv)}
<main id="main">
{main}
</main>
{self.footer()}
<script src="assets/sajt.js?v={js_v}" defer></script>
</body>
</html>
'''
        (self.ut / namn).write_text(doc, encoding="utf-8")

    # --- Hero-varianter -------------------------------------------------------------------------------------------
    def hero(self):
        b, p, bild = self.b, self.p, self.hero_bild
        img = self.bilder.img(bild, lazy=False)
        btns = f'<div class="knappar">{self.knapp(p.get("hero_cta", "Upptäck vår verksamhet"), "verksamhet.html", "primar" if p["hero"] in ("ruta", "statement", "mosaik", "split") else "ljus")}<a class="textlank" href="projekt.html">Se våra projekt {PIL}</a></div>'
        h = p["hero"]
        if h == "helskarm":
            return f'''<section class="hero hero-helskarm" aria-labelledby="h1"><div class="hero-bild">{img}</div>
  <div class="wrap"><div><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1></div><div><p class="ingress">{E(b["hero_text"])}</p>{btns}</div></div>
  <span class="foto-not">Illustrationsbild</span></section>'''
        if h == "centrerad":
            return f'''<section class="hero hero-centrerad" aria-labelledby="h1"><div class="hero-bild">{img}</div>
  <div class="wrap"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>{btns}</div>
  <span class="foto-not">Illustrationsbild</span></section>'''
        if h == "ruta":
            return f'''<section class="hero hero-ruta" aria-labelledby="h1"><div class="wrap">
  <div class="ruta-bild">{img}<span class="foto-not">Illustrationsbild</span></div>
  <div class="ruta-kort"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>{btns}</div></div></section>'''
        if h == "split":
            return f'''<section class="hero hero-split" aria-labelledby="h1">
  <div class="split-text"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>{btns}</div>
  <div class="split-bild">{img}<span class="foto-not">Illustrationsbild</span></div></section>'''
        if h == "statement":
            return f'''<section class="hero hero-statement" aria-labelledby="h1"><div class="wrap">
  <span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1>
  <div class="statement-rad"><p class="ingress">{E(b["hero_text"])}</p>{btns}</div>
  <div class="statement-bild">{img}</div></div></section>'''
        if h == "mosaik":
            b2, b3 = self.bilder.ta(), self.bilder.ta("people")
            return f'''<section class="hero hero-mosaik" aria-labelledby="h1"><div class="wrap">
  <span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress" style="margin-top:22px;max-width:36em">{E(b["hero_text"])}</p>{btns}
  <div class="mosaik"><figure>{img}</figure><figure>{self.bilder.img(b2, "(min-width:900px) 33vw, 50vw")}</figure><figure>{self.bilder.img(b3, "(min-width:900px) 33vw, 50vw")}</figure></div></div></section>'''
        raise ValueError(h)

    # --- Sektioner ------------------------------------------------------------------------------------------------
    def siffror(self, linjer=True):
        rad = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in self.b["nyckeltal"])
        return f'<div class="siffror{" linjer" if linjer else ""}">{rad}</div>'

    def kort(self, i, titel, text, href, bild, meta=""):
        return (f'<li class="kort reveal"><a href="{href}"><span class="nr">{i:02d}</span>{self.bilder.foto(bild, sizes="(min-width:1100px) 25vw, (min-width:680px) 50vw, 100vw")}'
                f'<div class="kort-text">{f"<span class=meta>{E(meta)}</span>" if meta else ""}<h3>{E(titel)}</h3><p>{E(text)}</p><span class="textlank">Läs mer {PIL}</span></div></a></li>')

    def sek_klass(self, idx):
        """Rytmen: vilka sektioner som får yta/mörk/primär bakgrund."""
        r = self.p["rytm"]
        if r == "ljus":
            return "sek"
        if r == "alternerande":
            return "sek sek-yta" if idx % 2 else "sek"
        if r == "morka-band":
            return {1: "sek pa-mork", 3: "sek sek-yta", 5: "sek pa-mork"}.get(idx, "sek")
        if r == "primar-band":
            return {1: "sek pa-primar", 3: "sek sek-yta", 5: "sek pa-mork"}.get(idx, "sek")
        return "sek"

    def index(self):
        b, p = self.b, self.p
        om_bild = self.bilder.ta(p.get("om_tagg", "people"))
        omr = "".join(self.kort(i + 1, a["titel"], a["text"], f"verksamhet.html#omr-{i}", self.bilder.ta(a["tagg"])) for i, a in enumerate(b["affarsomraden"]))
        utv = b["projekt"][0]
        utv_bild = self.bilder.ta(utv["tagg"])
        proj = "".join(self.kort(i + 2, x["namn"], x["text"], "projekt.html", self.bilder.ta(x["tagg"]), f'{x["ort"]} · {x["typ"]}') for i, x in enumerate(b["projekt"][1:4]))
        hb = b["hallbarhet"]
        mal = "".join(f'<li class="reveal"><b>{E(v)}</b><span>{E(t)}</span></li>' for v, t in hb["mal"])
        nyh = "".join(f'<li><a href="om-oss.html#press"><time>{E(d)}</time><b>{E(t)}</b>{PIL}</a></li>' for d, t in b["nyheter"])
        inv = b["investerare"]
        karr_bild = self.bilder.ta("people")
        s = [self.sek_klass(i) for i in range(8)]
        signatur = p.get("signatur", "nyckeltal-rad")
        intro = f'''<section class="{s[0]}" aria-labelledby="intro-h"><div class="wrap">
  <div class="delad"><div><span class="etikett">Om {E(b["kortnamn"])}</span><h2 id="intro-h">{E(b.get("intro_rubrik", b["slogan"]))}</h2></div>
  <div class="prosa"><p class="ingress">{E(b["om"][0])}</p><p class="mut">{E(b["om"][1])}</p><div class="knappar">{self.knapp("Mer om oss", "om-oss.html", "kontur")}</div></div></div>
  <div style="margin-top:clamp(56px,6vw,96px)">{self.siffror()}</div></div></section>'''
        if signatur == "stora-siffror":
            intro = f'''<section class="{s[0]}" aria-labelledby="intro-h"><div class="wrap">
  <div class="delad omvand">{self.bilder.foto(om_bild, "hog")}<div><span class="etikett">Om {E(b["kortnamn"])}</span><h2 id="intro-h">{E(b.get("intro_rubrik", b["slogan"]))}</h2>
  <p class="ingress" style="margin-top:24px">{E(b["om"][0])}</p><div class="knappar">{self.knapp("Mer om oss", "om-oss.html", "kontur")}</div></div></div></div></section>
<section class="sek pa-mork" aria-label="Nyckeltal"><div class="wrap">{self.siffror(False)}</div></section>'''
        elif signatur == "citat":
            intro = f'''<section class="{s[0]}" aria-labelledby="intro-h"><div class="wrap smal" style="text-align:center">
  <span class="etikett">Om {E(b["kortnamn"])}</span><h2 id="intro-h" style="margin-inline:auto">{E(b.get("intro_rubrik", b["slogan"]))}</h2><p class="ingress" style="margin-top:28px">{E(b["om"][0])}</p>
  <div class="knappar" style="justify-content:center">{self.knapp("Mer om oss", "om-oss.html", "kontur")}</div></div>
  <div class="wrap" style="margin-top:clamp(56px,6vw,96px)">{self.siffror()}</div></section>'''
        aktie_html = ""
        if inv.get("kurs"):
            upp = inv["forandring"].startswith("+")
            aktie_html = f'''<section class="{s[5]}" aria-labelledby="ir-h"><div class="wrap aktie">
  <div><span class="etikett">Investerare</span><h2 id="ir-h">{E(inv["aktie"])}</h2><p class="mut" style="margin-top:16px">{E(inv["lista"])}</p>
  <div class="aktieruta" style="margin-top:28px"><span>Senast betalt</span><div class="kurs">{E(inv["kurs"])} <span class="{"upp" if upp else "ned"}">{E(inv["forandring"])}</span></div>
  <svg viewBox="0 0 300 70" preserveAspectRatio="none" aria-hidden="true"><path d="M0 52 L30 48 L60 55 L90 40 L120 44 L150 30 L180 34 L210 22 L240 28 L270 14 L300 18" fill="none" stroke="currentColor" stroke-width="2" opacity=".8"/></svg><small>Fördröjd kurs, 15 min. Exempeldata.</small></div></div>
  <div><h3 style="margin-bottom:18px">Rapporter och presentationer</h3><ul class="rapporter">{"".join(f'<li><a href="investerare.html#rapporter"><span><span class="pdf">PDF</span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["rapporter"])}</ul>
  <div class="knappar">{self.knapp("Till investerarsidan", "investerare.html", "kontur")}</div></div></div></section>'''
        main = f'''{self.hero()}
{intro}
<section class="{s[1]}" aria-labelledby="omr-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Verksamhet</span><h2 id="omr-h">Våra affärsområden</h2></div>{self.knapp("Hela verksamheten", "verksamhet.html", "kontur")}</div>
  <ul class="kortlista fyra">{omr}</ul></div></section>
<section class="{s[2]}" aria-labelledby="proj-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Projekt</span><h2 id="proj-h">Det här bygger vi just nu</h2></div><a class="textlank" href="projekt.html">Alla projekt {PIL}</a></div>
  <a class="utvalt reveal" href="projekt.html">{self.bilder.foto(utv_bild, sizes="(min-width:960px) 60vw, 100vw")}<div class="utvalt-text"><span class="etikett">{E(utv["ort"])} · {E(utv["typ"])}</span><h3>{E(utv["namn"])}</h3><p class="mut">{E(utv["text"])}</p><span class="textlank" style="margin-top:24px">Om projektet {PIL}</span></div></a>
  <ul class="kortlista tre" style="margin-top:28px">{proj}</ul></div></section>
<section class="{s[3]}" aria-labelledby="hb-h"><div class="wrap">
  <div class="delad"><div><span class="etikett">Hållbarhet</span><h2 id="hb-h">{E(hb["rubrik"])}</h2></div><div><p class="ingress">{E(hb["text"])}</p><div class="knappar"><a class="textlank" href="hallbarhet.html">Så arbetar vi {PIL}</a></div></div></div>
  <ul class="mal">{mal}</ul></div></section>
{aktie_html}
<section class="{s[4]}" aria-labelledby="ny-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Aktuellt</span><h2 id="ny-h">Nyheter och pressmeddelanden</h2></div><a class="textlank" href="om-oss.html#press">Alla nyheter {PIL}</a></div>
  <ul class="nyheter">{nyh}</ul></div></section>
<section class="sek" aria-labelledby="ka-h"><div class="wrap">
  <div class="cta-band"><div class="hero-bild">{self.bilder.img(karr_bild, lazy=True)}</div><div class="cta-in"><span class="etikett" style="color:#fff;opacity:.85">Karriär</span><h2 id="ka-h">{E(b["karriar"]["rubrik"])}</h2><p class="ingress">{E(b["karriar"]["text"])}</p><div class="knappar">{self.knapp("Lediga jobb", "karriar.html", "ljus")}</div></div></div></div></section>'''
        self.sida("index.html", f'{b["namn"]} – {b["slogan"]}', b["hero_text"], main, har_hero=p["hero"] in ("helskarm", "centrerad", "split"))

    def sidhero(self, titel, ingress, tagg, aktiv_namn):
        bild = self.bilder.ta(tagg)
        return f'''<section class="sidhero" aria-labelledby="h1"><div class="hero-bild">{self.bilder.img(bild, lazy=False)}</div>
  <div class="wrap"><nav class="brodsmula" aria-label="Brödsmulor"><a href="index.html">Start</a> / <span aria-current="page">{E(aktiv_namn)}</span></nav><h1 id="h1">{E(titel)}</h1><p class="ingress">{E(ingress)}</p></div></section>'''

    def undersida(self, slug, namn, titel, ingress, tagg, innehall, beskr):
        har = self.p.get("sidhero", "bild") == "bild"
        self.sida(f"{slug}.html", f'{namn} | {self.b["namn"]}', beskr, self.sidhero(titel, ingress, tagg, namn) + innehall, aktiv=slug, har_hero=har)

    def undersidor(self):
        b = self.b
        # Verksamhet
        block = ""
        for i, a in enumerate(b["affarsomraden"]):
            block += f'''<section class="{"sek sek-yta" if i % 2 else "sek"}" id="omr-{i}"><div class="wrap delad{" omvand" if i % 2 else ""}">
  {self.bilder.foto(self.bilder.ta(a["tagg"]))}<div><span class="etikett">Affärsområde {i + 1:02d}</span><h2>{E(a["titel"])}</h2><p class="ingress" style="margin-top:22px">{E(a["text"])}</p>
  <p class="mut" style="margin-top:16px">{E(b["kortnamn"])} har lång erfarenhet inom {E(a["titel"].lower())} och arbetar nära kunder och samarbetspartner i hela landet.</p>
  <div class="knappar"><a class="textlank" href="projekt.html">Projekt inom området {PIL}</a></div></div></div></section>'''
        self.undersida("verksamhet", "Verksamhet", "Vår verksamhet", b["om"][1], b["affarsomraden"][0]["tagg"], block, f'Affärsområden inom {b["namn"]}.')
        # Projekt
        kort = "".join(self.kort(i + 1, x["namn"], x["text"], "#", self.bilder.ta(x["tagg"]), f'{x["ort"]} · {x["typ"]} · {x["ar"]}') for i, x in enumerate(b["projekt"]))
        self.undersida("projekt", "Projekt", "Våra projekt", "Ett urval av det vi bygger, utvecklar och förvaltar.", b["projekt"][1]["tagg"],
                       f'<section class="sek"><div class="wrap"><ul class="kortlista tre">{kort}</ul></div></section>', f'Projekt av {b["namn"]}.')
        # Hållbarhet
        hb = b["hallbarhet"]
        mal = "".join(f'<li><b>{E(v)}</b><span>{E(t)}</span></li>' for v, t in hb["mal"])
        self.undersida("hallbarhet", "Hållbarhet", hb["rubrik"], hb["text"], "tra", f'''<section class="sek"><div class="wrap delad"><div><span class="etikett">Våra mål</span><h2>Så mäter vi vårt arbete</h2></div>
  <p class="ingress">{E(hb["text"])}</p></div><div class="wrap"><ul class="mal">{mal}</ul></div></section>
<section class="sek sek-yta"><div class="wrap delad omvand">{self.bilder.foto(self.bilder.ta("bygg"))}<div><span class="etikett">Rapportering</span><h2>Hållbarhetsredovisning</h2><p class="ingress" style="margin-top:22px">Vi redovisar vårt hållbarhetsarbete varje år enligt GRI och EU:s taxonomi.</p><div class="knappar">{self.knapp("Ladda ner redovisningen", "investerare.html#rapporter", "primar")}</div></div></div></section>''',
                       f'Hållbarhet hos {b["namn"]}.')
        # Investerare
        inv = b["investerare"]
        rap = "".join(f'<li><a href="#"><span><span class="pdf">PDF</span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["rapporter"])
        kal = "".join(f'<li><a href="#"><span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["kalender"]) or '<li><a href="#"><span>Inga planerade händelser</span></a></li>'
        kurs = ""
        if inv.get("kurs"):
            upp = inv["forandring"].startswith("+")
            kurs = f'<div class="aktieruta"><span>{E(inv["aktie"])} · {E(inv["lista"])}</span><div class="kurs">{E(inv["kurs"])} <span class="{"upp" if upp else "ned"}">{E(inv["forandring"])}</span></div><small>Fördröjd kurs, 15 min. Exempeldata.</small></div>'
        else:
            kurs = f'<div class="aktieruta"><span>Ägande</span><div class="kurs" style="font-size:32px">{E(inv["aktie"])}</div><small>{E(inv["lista"])}</small></div>'
        self.undersida("investerare", "Investerare", "Investerare", "Finansiell information, rapporter och kalender.", "kontor", f'''<section class="sek"><div class="wrap">{self.siffror()}</div></section>
<section class="sek sek-yta" id="rapporter"><div class="wrap aktie"><div><h2>Aktien och ägandet</h2><div style="margin-top:28px">{kurs}</div></div><div><h3 style="margin-bottom:18px">Rapporter</h3><ul class="rapporter">{rap}</ul><h3 style="margin:40px 0 18px">Finansiell kalender</h3><ul class="rapporter">{kal}</ul></div></div></section>''',
                       f'Investerarinformation för {b["namn"]}.')
        # Karriär
        jobb = "".join(f'<li><a href="#"><b>{E(t)}</b><span>{E(o)} {PIL}</span></a></li>' for t, o in b["karriar"]["jobb"])
        self.undersida("karriar", "Karriär", b["karriar"]["rubrik"], b["karriar"]["text"], "people", f'''<section class="sek" id="jobb"><div class="wrap delad" style="align-items:start"><div><span class="etikett">Lediga jobb</span><h2>Just nu söker vi</h2><p class="ingress" style="margin-top:22px">Hittar du inget som passar? Skicka en spontanansökan.</p></div><ul class="jobb">{jobb}</ul></div></section>
<section class="sek sek-yta"><div class="wrap delad omvand">{self.bilder.foto(self.bilder.ta("people"))}<div><span class="etikett">Medarbetare</span><h2>Varför välja oss</h2><p class="ingress" style="margin-top:22px">Trygga anställningar, kollektivavtal, friskvård och möjlighet att växa – i en koncern med uppdrag i hela landet.</p></div></div></section>''',
                       f'Jobba hos {b["namn"]}.')
        # Om oss
        k = b["kontakt"]
        nyh = "".join(f'<li><a href="#"><time>{E(d)}</time><b>{E(t)}</b>{PIL}</a></li>' for d, t in b["nyheter"])
        self.undersida("om-oss", "Om oss", f'Om {b["kortnamn"]}', b["om"][0], "stad", f'''<section class="sek"><div class="wrap delad">{self.bilder.foto(self.bilder.ta("people"))}<div class="prosa"><span class="etikett">Vilka vi är</span><h2>{E(b["slogan"])}</h2><p class="ingress" style="margin-top:22px">{E(b["om"][0])}</p><p class="mut">{E(b["om"][1])}</p></div></div></section>
<section class="sek sek-yta"><div class="wrap">{self.siffror()}</div></section>
<section class="sek" id="press"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">Press</span><h2>Nyheter och pressmeddelanden</h2></div></div><ul class="nyheter">{nyh}</ul></div></section>
<section class="sek sek-yta" id="kontakt"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">Kontakt</span><h2>Kontakta oss</h2></div></div>
<dl class="kontaktinfo"><div><dt>Huvudkontor</dt><dd>{E(k["adress"])}<br>{E(k["postnr"])} {E(k["ort"])}</dd></div><div><dt>Telefon</dt><dd><a href="tel:{k["telefon"].replace(" ", "").replace("-", "")}">{E(k["telefon"])}</a></dd></div><div><dt>E-post</dt><dd><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></dd></div></dl></div></section>''',
                       f'Om {b["namn"]}.')

    def assets(self):
        a = self.ut / "assets"
        a.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROT / "mall/bas.css", a / "bas.css")
        shutil.copy(ROT / "mall/sajt.js", a / "sajt.js")
        (a / "tokens.css").write_text(tokens_css(self.p), encoding="utf-8")
        lg = self.p["logga"]
        m = marke(lg["form"], lg["farg"], lg["ink"]) or f'<svg viewBox="0 0 40 40"><rect width="40" height="40" fill="{lg["farg"]}"/></svg>'
        (a / "favicon.svg").write_text(m.replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ', 1).replace(' aria-hidden="true"', ""), encoding="utf-8")
        (self.ut / "paket.json").write_text(json.dumps(self.p, ensure_ascii=False, indent=1), encoding="utf-8")

    def bygg(self):
        if self.ut.exists():
            shutil.rmtree(self.ut)
        self.ut.mkdir(parents=True)
        self.bilder = Bilder(self.p.get("fro", self.b["slug"]), self.ut, self.p.get("bildtyngd", []), self.delad)
        self.hero_bild = self.bilder.ta(self.p.get("hero_tagg"))
        self.assets()
        self.index()
        self.undersidor()


def main():
    b = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    p = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    ut = pathlib.Path(sys.argv[3])
    Sajt(b, p, ut).bygg()
    print("Byggde", b["namn"], "->", ut)


if __name__ == "__main__":
    main()
