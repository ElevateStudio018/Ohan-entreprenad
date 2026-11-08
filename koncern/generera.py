"""Bygger en koncernhemsida från ett innehåll (brief) och ett grafiskt paket. Version 2.

Kör:  python3 koncern/generera.py <brief.json> <paket.json> <utmapp>

brief.json  – företagets innehåll (se koncern/exempel/*.json för formatet)
paket.json  – det grafiska paketet (koncern/paket.py skapar unika paket)

Sajten blir statisk HTML/CSS/JS utan beroenden: index, verksamhet, projekt, hallbarhet, investerare, karriar, om-oss.
Startsidan följer hur de bästa svenska koncernsajterna är uppbyggda (se research/): topprad för koncernen, hero med
bildspel, vägval med ikoner, berättelser, bild + färgpanel, våra bolag, nyckeltal, projekt med status, hållbarhet,
investerare, nyheter med bild, snabbrutor och helfärgad sidfot.
"""
import hashlib
import html
import json
import pathlib
import random
import shutil
import sys

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT / "mall"))
from ikoner import ikon  # noqa: E402

BANK = ROT / "bildbank"
E = html.escape

ELEVATE_CREDIT = '''<!-- elevate-credit -->
<style>.elevate-credit{max-width:1240px;margin:24px auto 0;padding:20px 16px 0;border-top:1px solid rgba(128,128,128,.25);display:flex;justify-content:center;box-sizing:border-box}.elevate-credit a{display:inline-flex;align-items:center;gap:10px;padding:8px 0;font:inherit;font-size:15px;line-height:1;color:inherit;opacity:.55;text-decoration:none;transition:opacity .2s}.elevate-credit a:hover,.elevate-credit a:focus-visible{opacity:1}.elevate-credit svg{width:20px;height:20px;flex:none;display:block}@media(min-width:1024px){.elevate-credit a{font-size:16px}}</style>
<div class="elevate-credit"><a href="https://elevatestudio.nu" target="_blank" rel="noopener"><svg viewBox="0 0 1884.3 1353.9" aria-hidden="true"><path d="M0.0 1353.9 L1218.7 0.0 L1218.7 329.1 L479.7 1136.4 L786.7 1132.4 L1215.5 687.4 L1884.3 1349.9 L1590.1 1349.9 L1218.6 994.7 L865.4 1349.9Z" fill="currentColor"/></svg>Byggd av Elevate Studio</a></div>
'''

PIL = ikon("pil", "pil")
SIDOR = [("verksamhet", "Vår verksamhet"), ("bolag", "Våra bolag"), ("projekt", "Projekt"), ("hallbarhet", "Vårt ansvar"),
         ("investerare", "Investerare"), ("karriar", "Jobba hos oss"), ("om-oss", "Om oss")]
NAV = [("verksamhet", "Vår verksamhet"), ("bolag", "Våra bolag"), ("hallbarhet", "Vårt ansvar"), ("karriar", "Jobba hos oss"), ("om-oss", "Om oss")]


# --- Logga ----------------------------------------------------------------------------------------------------------
def marke(form, farg, ink):
    f = {
        "ring": f'<circle cx="20" cy="20" r="14" fill="none" stroke="{farg}" stroke-width="7"/>',
        "kvadrat": f'<rect x="3" y="3" width="34" height="34" fill="{farg}"/><path d="M11 29V11h7l11 18V11" fill="none" stroke="{ink}" stroke-width="3.2"/>',
        "tak": f'<path d="M3 21 20 6l17 15v14H3z" fill="{farg}"/><path d="M15 35V24h10v11" fill="{ink}"/>',
        "bage": f'<path d="M4 34V20a16 16 0 0 1 32 0v14h-8V20a8 8 0 0 0-16 0v14z" fill="{farg}"/>',
        "staplar": f'<rect x="4" y="18" width="8" height="18" fill="{farg}"/><rect x="16" y="10" width="8" height="26" fill="{farg}"/><rect x="28" y="3" width="8" height="33" fill="{farg}"/>',
        "blad": f'<path d="M6 34C6 16 18 5 36 5c0 18-11 29-29 29z" fill="{farg}"/><path d="M8 32 26 14" stroke="{ink}" stroke-width="2.5"/>',
        "romb": f'<path d="M20 2 38 20 20 38 2 20z" fill="{farg}"/><path d="M20 12 28 20 20 28 12 20z" fill="{ink}"/>',
        "vag": f'<rect width="40" height="40" rx="10" fill="{farg}"/><path d="M8 26c6-10 10-10 12-6s6 4 12-6" fill="none" stroke="{ink}" stroke-width="3.5" stroke-linecap="round"/>',
        "punkt": f'<circle cx="20" cy="20" r="17" fill="{farg}"/><circle cx="20" cy="20" r="6" fill="{ink}"/>',
        "streck": f'<rect x="4" y="6" width="6" height="28" fill="{farg}"/><rect x="14" y="6" width="6" height="28" fill="{farg}" opacity=".6"/>',
    }.get(form)
    return f'<svg class="marke" viewBox="0 0 40 40" aria-hidden="true">{f}</svg>' if f else ""


def logga(b, p, href):
    lg = p["logga"]
    m = marke(lg["form"], lg["farg"], lg["ink"])
    ord_ = b["kortnamn"].lower() if lg.get("gemener") else b["kortnamn"]
    tag = f'<span class="tag">{E(b.get("tagline", ""))}</span>' if b.get("tagline") and lg.get("tagline", True) else ""
    return f'<a class="logga" href="{href}" aria-label="{E(b["namn"])}, till startsidan">{m}<span class="ord">{E(ord_)}</span>{tag}</a>'


# --- Bilder ---------------------------------------------------------------------------------------------------------
def bildbank():
    rader = []
    for line in (ROT / "bildbank.tsv").read_text(encoding="utf-8").splitlines():
        if line.strip():
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
        self.ut, self.tyngd, self.delad = ut, tyngd, delad
        if delad:
            Bilder.prefix = delad[1]
            delad[0].mkdir(parents=True, exist_ok=True)
        else:
            Bilder.prefix = "img/"
            (ut / "img").mkdir(parents=True, exist_ok=True)

    def ta(self, tagg=None):
        taggar = ([tagg] if tagg else []) + self.tyngd + ["people", "bygg", "kontor", "bostad", "stad", "natur", "tra", "infra", "interior", "hem", "industri", "el", "anlaggning"]
        b = None
        for t in taggar:
            kand = [x for x in self.bank if x["tagg"] == t and x["id"] not in self.anvanda]
            if kand:
                b = self.rng.choice(kand)
                break
        if b is None:
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
    def img(b, sizes="100vw", lazy=True):
        q = Bilder.prefix
        return (f'<img src="{q}{b["id"]}.jpg" srcset="{q}{b["id"]}-s.jpg 700w, {q}{b["id"]}.jpg 1600w" sizes="{sizes}" alt="{E(b["alt"])}" '
                f'{"loading=lazy " if lazy else "fetchpriority=high "}decoding="async">')

    def fyll(self, b, sizes="100vw", lazy=True, note=False):
        return f'<div class="bild-fyll">{self.img(b, sizes, lazy)}</div>' + ('<span class="figtext">Illustrationsbild</span>' if note else "")


# --- Tokens ---------------------------------------------------------------------------------------------------------
def tokens_css(p):
    f, t, fo = p["farger"], p["typsnitt"], p["form"]
    g = f.get
    font_r = f'"{t["rubrik"]}", {t.get("rubrik_fallback", "system-ui, sans-serif")}'
    font_t = f'"{t["text"]}", {t.get("text_fallback", "system-ui, sans-serif")}'
    v = {
        "--font-r": font_r, "--font-t": font_t, "--font-logo": font_r if t.get("logo_font", "rubrik") == "rubrik" else font_t,
        "--w-r": t["rubrik_vikt"], "--tr-r": t["spatiering"], "--tt-r": "uppercase" if t.get("versaler") else "none",
        "--skala-r": t.get("skala", 1), "--t-text": f'{t.get("textstorlek", 17)}px', "--w-siffra": t.get("siffra_vikt", t["rubrik_vikt"]),
        "--w-logo": t.get("logo_vikt", 700), "--tr-logo": t.get("logo_spatiering", "-0.01em"), "--tt-logo": "uppercase" if t.get("logo_versaler") else "none",
        "--tt-nav": "uppercase" if t.get("nav_versaler") else "none", "--tr-nav": ".06em" if t.get("nav_versaler") else "0",
        "--tt-btn": "uppercase" if t.get("knapp_versaler") else "none", "--tr-btn": ".06em" if t.get("knapp_versaler") else "0",
        "--c-p": f["primar"], "--c-p2": g("primar2", f["primar"]), "--c-p-ink": f["primar_ink"], "--c-p-text": g("primar_text", f["primar"]),
        "--c-a": f["accent"], "--c-a-ink": g("accent_ink", "#14171b"), "--c-ton": f["ton"], "--c-ton2": g("ton2", f["ton"]),
        "--c-bg": f["bg"], "--c-yta": f["yta"], "--c-ink": f["ink"], "--c-rubrik": g("rubrik", f["ink"]), "--c-mut": f["mut"], "--c-line": f["linje"],
        "--c-etikett": g("etikett", g("primar_text", f["primar"])), "--c-siffra": g("siffra", g("primar_text", f["primar"])),
        "--c-dark": f["mork"], "--c-dark-ink": f["mork_ink"],
        "--c-knapp": g("knapp", f["primar"]), "--c-knapp2": g("knapp2", g("primar2", f["primar"])), "--c-knapp-ink": g("knapp_ink", f["primar_ink"]),
        "--c-ruta": g("ruta", f["primar"]), "--c-ruta-ink": g("ruta_ink", f["primar_ink"]), "--c-ruta-hover": g("ruta_hover", g("primar2", f["primar"])),
        "--c-panel": g("panel", f["primar"]), "--c-panel-ink": g("panel_ink", f["primar_ink"]),
        "--c-topp": g("topp", f["yta"]), "--c-topp-ink": g("topp_ink", f["ink"]),
        "--c-head": g("head", f["bg"]), "--c-head-ink": g("head_ink", f["ink"]), "--c-head-fast": g("head_fast", f["bg"]), "--c-head-fast-ink": g("head_fast_ink", f["ink"]),
        "--c-meny": g("meny", f["mork"]), "--c-meny-ink": g("meny_ink", f["mork_ink"]),
        "--c-split": g("split", f["primar"]), "--c-split-ink": g("split_ink", f["primar_ink"]), "--c-statement": g("statement", f["bg"]),
        "--c-band": g("band", f["primar"]), "--c-band2": g("band2", f["accent"]),
        "--c-fot": f["sidfot"], "--c-fot-ink": f["sidfot_ink"], "--c-fot-linje": g("sidfot_linje", "rgba(255,255,255,.18)"),
        "--c-fot-knapp": g("sidfot_knapp", f["accent"]), "--c-fot-knapp-ink": g("sidfot_knapp_ink", g("accent_ink", "#14171b")),
        "--r-btn": f'{fo["knapp"]}px', "--r-card": f'{fo["kort"]}px', "--r-img": f'{fo["bild"]}px', "--r-hero": f'{fo.get("hero", 0)}px',
        "--maxw": f'{p.get("maxbredd", 1360)}px', "--head-h": f'{p.get("header_hojd", 80)}px',
    }
    return ":root{" + ";".join(f"{k}:{val}" for k, val in v.items()) + "}\n"


def google_fonts(p):
    t = p["typsnitt"]
    fams = []
    for namn, vikter in ((t["rubrik"], t.get("rubrik_vikter", "400;500;600;700")), (t["text"], t.get("text_vikter", "400;500;600;700"))):
        if t.get("google", True) and namn not in [x[0] for x in fams]:
            fams.append((namn, vikter))
    if not fams:
        return ""
    q = "&".join(f"family={n.replace(' ', '+')}:wght@{w}" for n, w in fams)
    return (f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{q}&display=swap">')


def ver(path):
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


def tel(t):
    return t.replace(" ", "").replace("-", "")


# --- Innehåll med reservvärden (äldre briefs utan de nya fälten fungerar också) ----------------------------------
IKON_FOR = {"bygg": "kran", "infra": "vag", "bostad": "hus", "kontor": "kontor", "tra": "skog", "people": "folk", "stad": "karta",
            "interior": "portfolj", "hem": "hus", "anlaggning": "hjalm", "industri": "fabrik", "el": "blixt", "natur": "lov"}


def tjanster(b):
    if b.get("tjanster"):
        return b["tjanster"]
    t = [{"titel": a["titel"], "ikon": IKON_FOR.get(a["tagg"], "kugge"), "href": f"verksamhet.html#omr-{i}"} for i, a in enumerate(b["affarsomraden"])]
    t += [{"titel": "Projekt", "ikon": "ritning", "href": "projekt.html"}, {"titel": "Hållbarhet", "ikon": "lov", "href": "hallbarhet.html"},
          {"titel": "Investerare", "ikon": "graf", "href": "investerare.html"}, {"titel": "Lediga jobb", "ikon": "sok", "href": "karriar.html"}]
    return t


def bolagslista(b):
    if b.get("bolag"):
        return b["bolag"]
    return [{"namn": f'{b["kortnamn"]} {a["titel"]}', "segment": a["titel"], "text": a["text"], "tagg": a["tagg"]} for a in b["affarsomraden"]]


def berattelser(b):
    if b.get("berattelser"):
        return b["berattelser"]
    return [{"rubrik": x["namn"], "text": x["text"], "tagg": x["tagg"]} for x in b["projekt"][:3]]


# --- Sajten ---------------------------------------------------------------------------------------------------------
class Sajt:
    def __init__(self, b, p, ut, delad=None):
        self.b, self.p, self.ut, self.delad = b, p, ut, delad

    # Grundbitar
    def knapp(self, text, href, typ="primar"):
        return f'<a class="knapp knapp-{typ}" href="{href}"><span>{E(text)}</span>{PIL}</a>'

    def textlank(self, text, href):
        return f'<a class="textlank" href="{href}"><span>{E(text)}</span>{PIL}</a>'

    def body_attr(self, har_hero):
        p = self.p
        attr = {"hero": p["hero"], "header": p["header"], "meny": p["meny"], "ruta": p.get("ruta", "solid"), "kort": p.get("kort", "overlay"),
                "knapp": p.get("knappstil", "fylld"), "projekt": p.get("projekt", "karusell"), "nyheter": p.get("nyheter", "lista"),
                "sidhero": p.get("sidhero", "bild")}
        return ('class="har-hero" ' if har_hero else "") + " ".join(f'data-{k}="{v}"' for k, v in attr.items())

    def header(self, aktiv):
        b, p = self.b, self.p
        links = "".join(f'<a href="{s}.html"{" aria-current=page" if s == aktiv else ""}>{t}</a>' for s, t in NAV)
        topp = (f'<div class="topprad"><div class="wrap"><a href="index.html">{ikon("hem")}<span>{E(b["kortnamn"])}-koncernen</span></a>'
                f'<a class="t-dold" href="bolag.html">Våra bolag</a><a class="t-dold" href="investerare.html">Investerare</a>'
                f'<a href="#" lang="en">{ikon("glob")}<span>Language/Språk</span></a></div></div>')
        meny_huvud = "".join(f'<li><a href="{s}.html">{t}</a></li>' for s, t in SIDOR)
        omr = "".join(f'<li><a href="bolag.html#bolag-{i}">{E(x["namn"])}</a></li>' for i, x in enumerate(bolagslista(b)))
        return f'''<a class="skip" href="#main">Hoppa till innehållet</a>
{topp}<header class="head" id="head">
  <div class="wrap">
    {logga(b, p, "index.html")}
    <nav class="nav" aria-label="Huvudmeny">{links}</nav>
    <div class="head-verktyg">
      <a class="knapp knapp-primar head-kontakt" href="om-oss.html#kontakt">Kontakta oss</a>
      <a class="sok" href="#" aria-label="Sök">{ikon("sok")}<span>Sök</span></a>
      <button class="meny-knapp" id="menyKnapp" type="button" aria-expanded="false" aria-controls="meny" aria-label="Öppna menyn"><span class="ord">Meny</span><span class="streck"><i></i><i></i><i></i></span></button>
    </div>
  </div>
  <nav class="meny" id="meny" aria-label="Meny" hidden>
    <div class="wrap">
      <ul class="meny-huvud">{meny_huvud}</ul>
      <div><h4>Våra bolag</h4><ul>{omr}</ul></div>
      <div><h4>Genvägar</h4><ul><li><a href="investerare.html#rapporter">Rapporter</a></li><li><a href="om-oss.html#press">Nyheter och press</a></li><li><a href="karriar.html#jobb">Lediga jobb</a></li><li><a href="om-oss.html#kontakt">Kontakta oss</a></li></ul></div>
    </div>
  </nav>
</header>'''

    def footer(self):
        b, p, k = self.b, self.p, self.b["kontakt"]
        stor = f'<p class="stor-logga" aria-hidden="true">{E(b["kortnamn"])}</p>' if p.get("sidfot_stor_logga") else ""
        tag = f'<span class="fot-tag">{E(b["tagline"])}</span>' if b.get("tagline") else f'<span>{E(b["namn"])}</span>'
        return f'''<footer class="fot">
  <a class="fot-upp" href="#top">Scrolla till toppen {ikon("upp")}</a>
  <div class="wrap">
    <div class="fot-grid">
      <div class="fot-om"><p class="fot-namn">{E(b["kortnamn"])}</p><p>{E(b.get("fot_text", b["hero_text"]))}</p>{self.textlank("Läs om vår verksamhet", "verksamhet.html")}</div>
      <div><h4>Kontakta oss</h4><ul><li>{E(b["namn"])}</li><li><a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a></li><li><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></li></ul></div>
      <div><h4>Huvudkontor</h4><ul><li>{E(k["adress"])}</li><li>{E(k["postnr"])} {E(k["ort"])}</li><li>Org.nr {E(k["orgnr"])}</li></ul></div>
      <div><h4>Genvägar</h4><ul><li><a href="om-oss.html">Om {E(b["kortnamn"])}</a></li><li><a href="karriar.html">Lediga jobb</a></li><li><a href="om-oss.html#press">Nyheter och press</a></li><li><a href="investerare.html">Investerare</a></li></ul></div>
    </div>
    {stor}
    <div class="fot-slut">{tag}<nav aria-label="Juridiskt"><a href="#">Integritets- och cookiepolicy</a><a href="#">Visselblåsarfunktion</a><a href="#">LinkedIn</a><a href="#" lang="en">English</a></nav><span>© <span data-year>2026</span> {E(b["namn"])}</span></div>
  </div>
{ELEVATE_CREDIT}</footer>'''

    def sida(self, namn, titel, beskrivning, main, aktiv=None, har_hero=False):
        p = self.p
        a = self.ut / "assets"
        doc = f'''<!doctype html>
<html lang="sv" id="top">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(titel)}</title>
<meta name="description" content="{E(beskrivning)}">
<meta name="theme-color" content="{p["farger"]["primar"]}">
<meta property="og:title" content="{E(titel)}"><meta property="og:description" content="{E(beskrivning)}"><meta property="og:image" content="{Bilder.prefix}{self.hero_bild["id"]}.jpg">
{google_fonts(p)}
<link rel="stylesheet" href="assets/tokens.css?v={ver(a / "tokens.css")}">
<link rel="stylesheet" href="assets/bas.css?v={ver(a / "bas.css")}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body {self.body_attr(har_hero)}>
{self.header(aktiv)}
<main id="main">
{main}
</main>
{self.footer()}
<script src="assets/sajt.js?v={ver(a / "sajt.js")}" defer></script>
</body>
</html>
'''
        (self.ut / namn).write_text(doc, encoding="utf-8")

    # --- Hero -----------------------------------------------------------------------------------------------------
    def slides(self):
        """Tre bilder i heron: företagets budskap och två berättelser."""
        b = self.b
        ber = berattelser(b)
        s = [dict(rubrik=b["hero_rubrik"], text=b["hero_text"], bild=self.hero_bild, lank=("Upptäck vår verksamhet", "verksamhet.html"), h1=True)]
        for x in ber[:2]:
            s.append(dict(rubrik=x["rubrik"], text=x["text"], bild=self.bilder.ta(x["tagg"]), lank=("Läs mer", "projekt.html"), h1=False))
        return s

    def spelkontroll(self, n, med_nasta=True):
        pr = "".join(f'<button type="button" aria-label="Visa bild {i + 1}"></button>' for i in range(n))
        nasta = f'<button class="spel-nasta" type="button" aria-label="Nästa bild">{PIL}</button>' if med_nasta else ""
        return f'<div class="spel-kontroll"><div class="spel-prickar">{pr}</div>{nasta}</div>'

    def hero(self):
        b, p = self.b, self.p
        h = p["hero"]
        if h in ("band", "helskarm", "centrerad"):
            sl = self.slides()
            inner = ""
            for i, s in enumerate(sl):
                tag = "h1" if s["h1"] else "h2"
                if h == "band":
                    txt = f'<div class="slide-text"><{tag}>{E(s["rubrik"])}</{tag}>{self.textlank(s["lank"][0], s["lank"][1])}</div>'
                elif h == "helskarm":
                    txt = (f'<div class="slide-text"><div class="wrap"><div><span class="etikett" style="color:#fff;opacity:.85">{E(b["typ"])}</span><{tag}>{E(s["rubrik"])}</{tag}></div>'
                           f'<div><p class="ingress">{E(s["text"])}</p><div class="knappar">{self.knapp(s["lank"][0], s["lank"][1], "ljus")}</div></div></div></div>')
                else:
                    txt = (f'<div class="slide-text"><div><{tag}>{E(s["rubrik"])}</{tag}><p class="ingress">{E(s["text"])}</p>'
                           f'<div class="knappar">{self.knapp(s["lank"][0], s["lank"][1], "ljus")}</div></div></div>')
                skugga = " skugga-bild" if h == "helskarm" else ""
                inner += f'<div class="bild-slide{" aktiv" if i == 0 else ""}"><div class="bild-fyll{skugga}">{self.bilder.img(s["bild"], lazy=i > 0)}</div>{txt}</div>'
            ctrl = self.spelkontroll(len(sl), h == "band")
            if h == "band":
                return f'''<section class="hero hero-band" aria-label="Aktuellt"><div class="band-ram"><div class="band-bild bildspel" data-bildspel>{inner}{ctrl}<span class="foto-not">Illustrationsbild</span></div></div></section>'''
            return f'<section class="hero hero-{h}" aria-label="Aktuellt"><div class="bildspel" data-bildspel>{inner}{ctrl}<span class="foto-not">Illustrationsbild</span></div></section>'
        btns = f'<div class="knappar">{self.knapp("Upptäck vår verksamhet", "verksamhet.html")}{self.textlank("Se våra projekt", "projekt.html")}</div>'
        img = self.bilder.img(self.hero_bild, lazy=False)
        if h == "split":
            return f'''<section class="hero hero-split" aria-labelledby="h1"><div class="split-text"><span class="etikett" style="color:inherit;opacity:.8">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>{btns}</div>
  <div class="split-bild"><div class="bild-fyll">{img}</div><span class="foto-not">Illustrationsbild</span></div></section>'''
        if h == "statement":
            return f'''<section class="hero hero-statement" aria-labelledby="h1"><div class="wrap"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1>
  <div class="statement-rad"><p class="ingress">{E(b["hero_text"])}</p>{btns}</div><div class="statement-bild"><div class="bild-fyll">{img}</div><span class="foto-not">Illustrationsbild</span></div></div></section>'''
        if h == "mosaik":
            fig = "".join(f'<figure><div class="bild-fyll">{self.bilder.img(x, "(min-width:900px) 33vw, 50vw")}</div></figure>' for x in [self.hero_bild, self.bilder.ta("people"), self.bilder.ta(), self.bilder.ta("natur")])
            return f'''<section class="hero hero-mosaik" aria-labelledby="h1"><div class="wrap"><div class="mosaik-topp"><div><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1></div>
  <div><p class="ingress">{E(b["hero_text"])}</p>{btns}</div></div><div class="mosaik">{fig}</div></div></section>'''
        raise ValueError(h)

    # --- Sektioner ------------------------------------------------------------------------------------------------
    def bg(self, roll):
        """Rytmen: vilken bakgrund en sektion får, enligt paketets rytm."""
        r = self.p.get("rytm", "ton")
        tabell = {
            "ton": {"vagval": "", "berattelser": "", "panel": "", "bolag": "pa-ton", "siffror": "pa-farg", "projekt": "", "hb": "pa-ton", "ir": "", "nyheter": "", "snabb": ""},
            "mork": {"vagval": "", "berattelser": "pa-yta", "panel": "", "bolag": "", "siffror": "pa-mork", "projekt": "pa-yta", "hb": "pa-mork", "ir": "", "nyheter": "pa-yta", "snabb": ""},
            "farg": {"vagval": "pa-ton", "berattelser": "", "panel": "", "bolag": "", "siffror": "pa-farg", "projekt": "pa-ton", "hb": "", "ir": "pa-ton", "nyheter": "", "snabb": ""},
            "ljus": {"vagval": "", "berattelser": "", "panel": "", "bolag": "pa-yta", "siffror": "", "projekt": "", "hb": "pa-ton", "ir": "", "nyheter": "pa-yta", "snabb": ""},
        }
        return tabell.get(r, tabell["ton"]).get(roll, "")

    def s_vagval(self):
        b = self.b
        t = tjanster(b)
        rutor = "".join(f'<a href="{x.get("href", "verksamhet.html")}">{ikon(x.get("ikon", "kugge"))}<span>{E(x["titel"])}</span></a>' for x in t)
        fraga = b.get("vagval_rubrik", "Vad kan vi hjälpa dig med?")
        return f'''<section class="sek {self.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">
  <div class="sek-huvud mitt"><h2 id="vv-h">{E(fraga)}</h2></div><nav class="vagval" aria-label="Vägval">{rutor}</nav></div></section>'''

    def s_berattelser(self):
        kort = ""
        for x in berattelser(self.b)[:3]:
            bild = self.bilder.ta(x["tagg"])
            kl = "overlay" if self.p.get("kort", "overlay") == "overlay" else "berattelse"
            kort += (f'<li class="kort {kl} reveal"><a href="projekt.html"><div class="foto">{self.bilder.img(bild, "(min-width:1100px) 33vw, 100vw")}</div>'
                     f'<div class="kort-text"><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p>{self.textlank("Läs mer", "projekt.html").replace("<a ", "<span ").replace("</a>", "</span>")}</div></a></li>')
        return f'''<section class="sek {self.bg("berattelser")}" aria-labelledby="be-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Aktuellt från koncernen</span><h2 id="be-h">{E(self.b.get("berattelser_rubrik", "Det här gör vi just nu"))}</h2></div>{self.textlank("Alla projekt", "projekt.html")}</div>
  <ul class="kortlista tre">{kort}</ul></div></section>'''

    def s_panel(self, omvand=False):
        b = self.b
        k = b["karriar"]
        bild = self.bilder.ta("people")
        ljus = " ljus" if self.p.get("panel") == "ton" else ""
        return f'''<section class="sek {self.bg("panel")}" aria-labelledby="pa-h"><div class="wrap">
  <div class="panel{" omvand" if omvand else ""}{ljus} reveal"><div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>
  <div class="panel-text"><span class="etikett">Jobba hos oss</span><h2 id="pa-h">{E(k["rubrik"])}</h2><p>{E(k["text"])}</p><p>{E(b.get("kultur", "Som en del av koncernen får du kollegor i hela landet, utvecklingsvägar inom flera bolag och utrymme att växa."))}</p>
  <div class="knappar">{self.textlank("Se lediga jobb", "karriar.html")}</div></div></div></div></section>'''

    def s_bolag(self):
        bl = bolagslista(self.b)
        li = ""
        for i, x in enumerate(bl):
            bild = self.bilder.ta(x.get("tagg"))
            li += (f'<li class="reveal"><a href="bolag.html#bolag-{i}">{self.bilder.fyll(bild, "(min-width:760px) 50vw, 100vw")}<div class="bolag-text">'
                   f'<span class="bolagsnamn">{E(x["namn"])}</span><h3>{E(x.get("rubrik", x.get("segment", "")))}</h3><p>{E(x["text"])}</p>'
                   f'<span class="textlank"><span>Till {E(x["namn"])}</span>{PIL}</span></div></a></li>')
        return f'''<section class="sek {self.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Koncernen</span><h2 id="bo-h">Våra bolag</h2></div>{self.knapp("Läs om vår verksamhet", "verksamhet.html", "kontur")}</div>
  <ul class="bolag{" fyra" if len(bl) == 4 else " tre" if len(bl) == 3 else ""}">{li}</ul></div></section>'''

    def s_siffror(self):
        rad = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in self.b["nyckeltal"])
        return f'''<section class="sek {self.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.b["kortnamn"])} i siffror</span><h2 id="si-h">{E(self.b.get("intro_rubrik", self.b["slogan"]))}</h2></div><p class="ingress" style="max-width:32em">{E(self.b["om"][0])}</p></div>
  <div class="siffror">{rad}</div></div></section>'''

    def s_projekt(self):
        li = ""
        for i, x in enumerate(self.b["projekt"]):
            bild = self.bilder.ta(x["tagg"])
            ar = x.get("ar", "")
            pagaende = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2026)
            status = x.get("status") or ("Pågående" if pagaende else "Färdigt")
            li += (f'<li class="kort"><a href="projekt.html"><div class="foto"><span class="status{" pagaende" if status == "Pågående" else ""}">{E(status)}</span>{self.bilder.img(bild, "(min-width:1100px) 33vw, 80vw", lazy=i > 2)}</div>'
                   f'<div class="kort-text"><span class="meta">{E(x["ort"])} · {E(x["typ"])}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p></div></a></li>')
        return f'''<section class="sek {self.bg("projekt")}" aria-labelledby="pr-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Projekt</span><h2 id="pr-h">Några av våra projekt</h2></div><div style="display:flex;gap:20px;align-items:center">{self.textlank("Se alla projekt", "projekt.html")}<div class="spel-pilar" data-karusell="projektlista"><button class="bak" type="button" aria-label="Föregående">{PIL}</button><button type="button" aria-label="Nästa">{PIL}</button></div></div></div>
  <ul class="projekt" id="projektlista">{li}</ul></div></section>'''

    def s_hb(self):
        hb = self.b["hallbarhet"]
        mal = "".join(f'<li><b>{E(v)}</b><span>{E(t)}</span></li>' for v, t in hb["mal"])
        bild = self.bilder.ta("natur")
        return f'''<section class="sek {self.bg("hb")}" aria-labelledby="hb-h"><div class="wrap hb">
  <div class="reveal"><span class="etikett">Vårt ansvar</span><h2 id="hb-h" class="hb-stor">{E(hb["rubrik"])}</h2><p class="ingress" style="margin-top:22px">{E(hb["text"])}</p><ul class="mal">{mal}</ul>
  <div class="knappar">{self.textlank("Läs om vårt hållbarhetsarbete", "hallbarhet.html")}</div></div>
  <div class="hb-bild reveal">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div></div></section>'''

    def s_ir(self):
        inv = self.b["investerare"]
        kort = "".join(f'<a class="ir-kort" href="investerare.html#rapporter"><time>{E(d)}</time><b>{E(t)}</b><span class="rundpil">{PIL}</span></a>' for t, d in inv["rapporter"][:3])
        if inv.get("kurs"):
            upp = inv["forandring"].startswith("+")
            band = (f'<div class="kursband"><span class="aktie-namn">{E(inv["aktie"])}</span><span class="kurs">{E(inv["kurs"])} SEK</span><span class="{"upp" if upp else "ned"}">{E(inv["forandring"])}</span>'
                    f'<small>{E(inv["lista"])} · fördröjd kurs, exempeldata</small>{self.textlank("Till investerarsidan", "investerare.html")}</div>')
        else:
            band = f'<div class="kursband"><span class="aktie-namn">{E(inv["aktie"])}</span><small>{E(inv["lista"])}</small>{self.textlank("Finansiell information", "investerare.html")}</div>'
        return f'''<section class="sek {self.bg("ir")}" aria-labelledby="ir-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Investerare</span><h2 id="ir-h">Finansiell information</h2></div></div>{band}<div class="ir">{kort}</div></div></section>'''

    def s_nyheter(self):
        ny = ""
        for d, t in self.b["nyheter"]:
            bild = self.bilder.ta()
            ny += (f'<a class="nyhet reveal" href="om-oss.html#press"><div class="foto">{self.bilder.img(bild, "220px")}</div><div><time>{E(d)}</time><b>{E(t)}</b>'
                   f'<p>{E(self.b["kortnamn"])} berättar mer om nyheten i pressmeddelandet.</p></div></a>')
        return f'''<section class="sek {self.bg("nyheter")}" aria-labelledby="ny-h"><div class="wrap smal" style="max-width:1100px">
  <div class="sek-huvud"><h2 id="ny-h">Senaste nyheterna och pressmeddelanden</h2></div><div class="nyheter">{ny}</div>
  <div class="knappar">{self.knapp("Se alla nyheter och pressmeddelanden", "om-oss.html#press")}</div></div></section>'''

    def s_snabb(self):
        r = [("folk", "Jobba hos oss", "karriar.html"), ("lov", "Hållbarhet", "hallbarhet.html"), ("megafon", "Pressrum", "om-oss.html#press"), ("graf", "Aktieinformation & rapporter", "investerare.html")]
        a = "".join(f'<a href="{h}"><div>{ikon(i)}<b>{E(t)}</b></div><span class="rundpil">{PIL}</span></a>' for i, t, h in r)
        return f'<section class="sek sek-tat {self.bg("snabb")}" aria-label="Genvägar"><div class="wrap"><nav class="snabb">{a}</nav></div></section>'

    ORDNING = {
        "a": ["vagval", "berattelser", "panel", "bolag", "siffror", "projekt", "hb", "ir", "nyheter", "snabb"],
        "b": ["siffror", "bolag", "vagval", "projekt", "panel", "hb", "berattelser", "nyheter", "ir", "snabb"],
        "c": ["berattelser", "vagval", "siffror", "panel", "projekt", "bolag", "hb", "nyheter", "snabb"],
    }

    def index(self):
        p = self.p
        delar = {"vagval": self.s_vagval, "berattelser": self.s_berattelser, "panel": lambda: self.s_panel(p.get("panel_omvand", False)),
                 "bolag": self.s_bolag, "siffror": self.s_siffror, "projekt": self.s_projekt, "hb": self.s_hb, "ir": self.s_ir,
                 "nyheter": self.s_nyheter, "snabb": self.s_snabb}
        main = self.hero() + "\n" + "\n".join(delar[d]() for d in self.ORDNING[p.get("ordning", "a")])
        har = p["hero"] in ("helskarm", "centrerad")
        self.sida("index.html", f'{self.b["namn"]} – {self.b["slogan"]}', self.b["hero_text"], main, har_hero=har)

    # --- Undersidor -----------------------------------------------------------------------------------------------
    def sidhero(self, titel, ingress, tagg, namn):
        bild = self.bilder.ta(tagg)
        return f'''<section class="sidhero" aria-labelledby="h1">{self.bilder.fyll(bild, lazy=False)}
  <div class="wrap"><nav class="brodsmula" aria-label="Brödsmulor"><a href="index.html">Start</a> / <span aria-current="page">{E(namn)}</span></nav><h1 id="h1">{E(titel)}</h1><p class="ingress">{E(ingress)}</p></div></section>'''

    def undersida(self, slug, namn, titel, ingress, tagg, innehall, beskr):
        self.sida(f"{slug}.html", f'{namn} | {self.b["namn"]}', beskr, self.sidhero(titel, ingress, tagg, namn) + innehall, aktiv=slug,
                  har_hero=False)

    def undersidor(self):
        b = self.b
        # Verksamhet
        block = ""
        for i, a in enumerate(b["affarsomraden"]):
            bild = self.bilder.ta(a["tagg"])
            ljus = " ljus" if i % 2 else ""
            block += (f'<section class="sek-tat" id="omr-{i}"><div class="wrap"><div class="panel{" omvand" if i % 2 else ""}{ljus} reveal">'
                      f'<div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>'
                      f'<div class="panel-text"><span class="etikett">Affärsområde {i + 1:02d}</span><h2>{E(a["titel"])}</h2><p>{E(a["text"])}</p>'
                      f'<p>{E(b["kortnamn"])} arbetar inom {E(a["titel"].lower())} i hela landet, nära kunder och samarbetspartner.</p>'
                      f'<div class="knappar">{self.textlank("Projekt inom området", "projekt.html")}</div></div></div></div></section>')
        self.undersida("verksamhet", "Vår verksamhet", "Vår verksamhet", b["om"][1], b["affarsomraden"][0]["tagg"],
                       self.s_vagval() + block + '<div style="height:clamp(40px,6vw,96px)"></div>', f'Verksamheten inom {b["namn"]}.')
        # Våra bolag
        bl = bolagslista(b)
        rader = ""
        for i, x in enumerate(bl):
            bild = self.bilder.ta(x.get("tagg"))
            rader += (f'<section class="sek-tat" id="bolag-{i}"><div class="wrap"><div class="panel{" omvand" if i % 2 else ""}{" ljus" if i % 2 == 0 else ""} reveal">'
                      f'<div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>'
                      f'<div class="panel-text"><span class="etikett">{E(x.get("segment", ""))}</span><h2>{E(x["namn"])}</h2><p>{E(x["text"])}</p>'
                      f'<div class="knappar">{self.textlank("Till bolagets webbplats", "#")}</div></div></div></div></section>')
        self.undersida("bolag", "Våra bolag", "Våra bolag", f'{b["kortnamn"]} är en koncern med {len(bl)} bolag som tillsammans täcker hela kedjan.', "kontor",
                       '<div style="height:clamp(24px,3vw,48px)"></div>' + rader + '<div style="height:clamp(40px,6vw,96px)"></div>', f'Bolagen i {b["namn"]}.')
        # Projekt
        kort = ""
        for x in b["projekt"]:
            bild = self.bilder.ta(x["tagg"])
            kort += (f'<li class="kort reveal"><a href="#"><div class="foto"><span class="status">{E(x["ar"])}</span>{self.bilder.img(bild, "(min-width:1100px) 33vw, 100vw")}</div>'
                     f'<div class="kort-text"><span class="meta">{E(x["ort"])} · {E(x["typ"])}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p></div></a></li>')
        self.undersida("projekt", "Projekt", "Våra projekt", "Ett urval av det vi bygger, utvecklar och förvaltar.", b["projekt"][1]["tagg"],
                       f'<section class="sek"><div class="wrap"><ul class="kortlista tre">{kort}</ul></div></section>', f'Projekt av {b["namn"]}.')
        # Hållbarhet
        self.undersida("hallbarhet", "Vårt ansvar", b["hallbarhet"]["rubrik"], b["hallbarhet"]["text"], "natur",
                       self.s_hb() + self.s_panel(True).replace("Jobba hos oss</span>", "Medarbetare</span>"), f'Hållbarhet hos {b["namn"]}.')
        # Investerare
        inv = b["investerare"]
        rap = "".join(f'<li><a href="#"><span><span class="pdf">PDF</span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["rapporter"])
        kal = "".join(f'<li><a href="#"><span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["kalender"]) or '<li><a href="#"><span>Inga planerade händelser</span></a></li>'
        rad = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in b["nyckeltal"])
        self.undersida("investerare", "Investerare", "Investerare", "Finansiell information, rapporter och kalender.", "kontor",
                       f'''{self.s_ir()}<section class="sek pa-farg"><div class="wrap"><div class="siffror">{rad}</div></div></section>
<section class="sek" id="rapporter"><div class="wrap hb" style="align-items:start"><div><h2>Rapporter och presentationer</h2><ul class="rapporter" style="margin-top:24px">{rap}</ul></div><div><h2>Finansiell kalender</h2><ul class="rapporter" style="margin-top:24px">{kal}</ul></div></div></section>''',
                       f'Investerarinformation för {b["namn"]}.')
        # Karriär
        jobb = "".join(f'<li><a href="#"><b>{E(t)}</b><span>{E(o)} {PIL}</span></a></li>' for t, o in b["karriar"]["jobb"])
        self.undersida("karriar", "Jobba hos oss", b["karriar"]["rubrik"], b["karriar"]["text"], "people",
                       f'''<section class="sek" id="jobb"><div class="wrap hb" style="align-items:start"><div><span class="etikett">Lediga jobb</span><h2>Just nu söker vi</h2><p class="ingress" style="margin-top:18px">Hittar du inget som passar? Skicka en spontanansökan till något av våra bolag.</p></div><ul class="jobb">{jobb}</ul></div></section>
{self.s_panel(False)}{self.s_snabb()}''', f'Jobba hos {b["namn"]}.')
        # Om oss
        k = b["kontakt"]
        self.undersida("om-oss", "Om oss", f'Om {b["kortnamn"]}', b["om"][0], "stad", f'''<section class="sek"><div class="wrap hb"><div class="prosa"><span class="etikett">Vilka vi är</span><h2>{E(b["slogan"])}</h2><p class="ingress" style="margin-top:20px">{E(b["om"][0])}</p><p class="mut">{E(b["om"][1])}</p></div><div class="hb-bild">{self.bilder.fyll(self.bilder.ta("people"), "(min-width:960px) 50vw, 100vw", note=True)}</div></div></section>
{self.s_siffror()}<div id="press">{self.s_nyheter()}</div>
<section class="sek pa-ton" id="kontakt"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">Kontakt</span><h2>Kontakta oss</h2></div></div>
<dl class="kontaktinfo"><div><dt>Huvudkontor</dt><dd>{E(k["adress"])}<br>{E(k["postnr"])} {E(k["ort"])}</dd></div><div><dt>Telefon</dt><dd><a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a></dd></div><div><dt>E-post</dt><dd><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></dd></div></dl></div></section>''',
                       f'Om {b["namn"]}.')

    def assets(self):
        a = self.ut / "assets"
        a.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROT / "mall/bas.css", a / "bas.css")
        shutil.copy(ROT / "mall/sajt.js", a / "sajt.js")
        (a / "tokens.css").write_text(tokens_css(self.p), encoding="utf-8")
        lg = self.p["logga"]
        m = marke(lg["form"], lg["farg"], lg["ink"]) or f'<svg viewBox="0 0 40 40"><rect width="40" height="40" rx="8" fill="{lg["farg"]}"/><text x="20" y="28" text-anchor="middle" font-family="Arial" font-weight="700" font-size="22" fill="{lg["ink"]}">{E(self.b["kortnamn"][0])}</text></svg>'
        (a / "favicon.svg").write_text(m.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1).replace(' aria-hidden="true"', "").replace(' class="marke"', ""), encoding="utf-8")
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
