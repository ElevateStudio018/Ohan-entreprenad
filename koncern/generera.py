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
sys.path.insert(0, str(ROT))
from ikoner import ikon  # noqa: E402
from profiler import KONCERN_T, hamta as hamta_profil  # noqa: E402
import re  # noqa: E402

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

    def __init__(self, fro, ut, tyngd, delad=None, reserv=None):
        self.reserv = reserv
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
        taggar = ([tagg] if tagg else []) + self.tyngd + (self.reserv or ["people", "bygg", "kontor", "bostad", "stad", "natur", "tra", "infra", "interior", "hem", "industri", "el", "anlaggning"])
        b = None
        for t in taggar:
            kand = [x for x in self.bank if x["tagg"] == t and x["id"] not in self.anvanda]
            if kand:
                b = self.rng.choice(kand)
                break
        if b is None:
            bas = [x for x in self.bank if x["tagg"] == (tagg or self.tyngd[0] if (tagg or self.tyngd) else None)] or [x for x in self.bank if x["tagg"] in (self.reserv or [])] or self.bank
            self.anvanda -= {x["id"] for x in bas}
            b = self.rng.choice(bas)
        self.anvanda.add(b["id"])
        mal = self.delad[0] if self.delad else self.ut / "img"
        for suf in ("", "-s"):
            src = BANK / f'{b["id"]}{suf}.jpg'
            if not src.exists():
                src = ROT.parent / "site" / "bildbank" / src.name
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
        self.pr = hamta_profil(b.get("profil"))
        self.sidor = list(self.b.get("sidor") or self.pr["sidor"])
        if self.b.get("priser") and not any(t == "priser" for _, _, t in self.sidor):
            # Nischföretag med fasta priser får en prissida efter tjänster/referenser
            self.sidor.insert(2, ("priser", "Priser", "priser"))
        self.slugs = {s_ for s_, _, _ in self.sidor}

    def T(self, nyckel, **kw):
        """Text för en sektion: briefens "text" > profilens text > koncernstandard."""
        v = self.b.get("text", {}).get(nyckel)
        if v is None:
            v = self.pr["t"].get(nyckel)
        if v is None:
            v = KONCERN_T[nyckel]
        if isinstance(v, str):
            try:
                return v.format(**{"kortnamn": self.b["kortnamn"], "namn": self.b["namn"], **kw})
            except (KeyError, IndexError, ValueError):
                return v
        return v

    def u(self, ref):
        s_, _, ankare = ref.partition("#")
        return f"{s_}.html" + (f"#{ankare}" if ankare else "")

    def bt(self, roll):
        """Bildtagg för en roll (panel, hb, om …) enligt profilen; briefen kan skriva över i "bild"."""
        return self.b.get("bild", {}).get(roll) or self.pr["bild"].get(roll) or "people"

    def fixa_lankar(self, doc):
        """Länkar till sidor som profilen saknar pekar om till kontakt (eller priser i stället för investerare)."""
        def ers(m):
            slug, ankare = m.group(1), m.group(2) or ""
            if slug in self.slugs:
                return m.group(0)
            if slug == "investerare" and "priser" in self.slugs:
                return 'href="priser.html"'
            return 'href="om-oss.html#kontakt"'
        return re.sub(r'href="(verksamhet|bolag|projekt|hallbarhet|investerare|karriar|om-oss|priser|faq)\.html(#[\w-]*)?"', ers, doc)

    def blk(self, namn, standard):
        """Vilken variant ett block har i det här paketet (p["block"]); standard om inget anges."""
        return self.p.get("block", {}).get(namn, standard)

    # Grundbitar
    def knapp(self, text, href, typ="primar"):
        return f'<a class="knapp knapp-{typ}" href="{href}"><span>{E(text)}</span>{PIL}</a>'

    def textlank(self, text, href):
        return f'<a class="textlank" href="{href}"><span>{E(text)}</span>{PIL}</a>'

    def demo_rad(self):
        d = self.b.get("demo")
        if not d:
            return ""
        return f'<div class="demo-rad" role="note">{E(d)}</div>'

    def body_attr(self, har_hero):
        p = self.p
        attr = {"hero": p["hero"], "header": "transparent" if har_hero and p["hero"] != "split" else ("ljus" if p["header"] == "transparent" else p["header"]), "meny": p["meny"], "ruta": p.get("ruta", "solid"), "kort": p.get("kort", "overlay"),
                "knapp": p.get("knappstil", "fylld"), "projekt": p.get("projekt", "karusell"), "nyheter": p.get("nyheter", "lista"),
                "sidhero": p.get("sidhero", "bild"), "motiv": p.get("motiv", "inget")}
        return ('class="har-hero" ' if har_hero else "") + " ".join(f'data-{k}="{v}"' for k, v in attr.items())

    def header(self, aktiv):
        b, p = self.b, self.p
        etiketter = {s_: t for s_, t, _ in self.sidor}
        nav = self.b.get("nav") or self.pr["nav"]
        links = "".join(f'<a href="{s}.html"{" aria-current=page" if s == aktiv else ""}>{E(etiketter[s])}</a>' for s in nav if s in etiketter)
        k = b["kontakt"]
        if self.pr["topp"] == "koncern":
            topp = (f'<div class="topprad"><div class="wrap"><a href="index.html">{ikon("hem")}<span>{E(self.T("topp_hem"))}</span></a>'
                    f'<a class="t-dold" href="bolag.html">{E(etiketter.get("bolag", "Våra bolag"))}</a><a class="t-dold" href="investerare.html">Investerare</a>'
                    f'<a href="#" lang="en">{ikon("glob")}<span>Language/Språk</span></a></div></div>')
        else:
            omr = self.b.get("omrade") or k["ort"]
            topp = (f'<div class="topprad"><div class="wrap"><a href="om-oss.html#kontakt">{ikon("karta")}<span>{E(omr)}</span></a>'
                    f'<a class="t-dold" href="tel:{tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>'
                    f'{f"""<a class="t-dold" href="mailto:{k["epost"]}">{E(k["epost"])}</a>""" if k.get("epost") else ""}'
                    f'<span class="t-dold">{E(self.b.get("oppettider", ""))}</span></div></div>')
        meny_huvud = "".join(f'<li><a href="{s}.html">{E(t)}</a></li>' for s, t, _ in self.sidor)
        omr = "".join(f'<li><a href="bolag.html#bolag-{i}">{E(x["namn"])}</a></li>' for i, x in enumerate(bolagslista(b)))
        return f'''<a class="skip" href="#main">Hoppa till innehållet</a>
{topp}<header class="head" id="head">
  <div class="wrap">
    {logga(b, p, "index.html")}
    <nav class="nav" aria-label="Huvudmeny">{links}</nav>
    <div class="head-verktyg">
      <a class="knapp knapp-primar head-kontakt" href="om-oss.html#kontakt">{E(self.T("kontakt_knapp"))}</a>
      <a class="sok" href="#" aria-label="Sök">{ikon("sok")}<span>Sök</span></a>
      <button class="meny-knapp" id="menyKnapp" type="button" aria-expanded="false" aria-controls="meny" aria-label="Öppna menyn"><span class="ord">Meny</span><span class="streck"><i></i><i></i><i></i></span></button>
    </div>
  </div>
  <nav class="meny" id="meny" aria-label="Meny" hidden>
    <div class="wrap">
      <ul class="meny-huvud">{meny_huvud}</ul>
      <div><h4>{E(self.T("meny_bolag"))}</h4><ul>{omr}</ul></div>
      <div><h4>{E(self.T("fot_genvagar"))}</h4><ul>{"".join(f'<li><a href="{self.u(h)}">{E(t)}</a></li>' for t, h in self.pr["meny_genvagar"])}</ul></div>
    </div>
  </nav>
</header>'''

    def footer(self):
        b, p, k = self.b, self.p, self.b["kontakt"]
        v = p.get("fot", "standard")
        stor = f'<p class="stor-logga" aria-hidden="true">{E(b["kortnamn"])}</p>' if p.get("sidfot_stor_logga") else ""
        tag = f'<span class="fot-tag">{E(b["tagline"])}</span>' if b.get("tagline") else f'<span>{E(b["namn"])}</span>'
        juridik = '<nav aria-label="Juridiskt">' + "".join(f'<a href="#"{" lang=en" if j == "English" else ""}>{E(j)}</a>' for j in self.pr["juridik"]) + '</nav>'
        upp = f'<a class="fot-upp" href="#top">{E(self.T("fot_upp"))} {ikon("upp")}</a>'
        if v == "centrerad":
            lankar = "".join(f'<a href="{s_}.html">{E(t)}</a>' for s_, t, _ in self.sidor)
            return f'''<footer class="fot fot-centrerad">
  <div class="wrap">
    <p class="fot-namn">{E(b["kortnamn"])}</p><p class="fot-mitt-text">{E(b.get("fot_text", b["hero_text"]))}</p>
    <nav class="fot-mitt-nav" aria-label="Sidfot">{lankar}</nav>
    <p class="fot-mitt-kontakt">{E(k["adress"])}, {E(k["postnr"])} {E(k["ort"])} · <a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a>{f' · <a href="mailto:{k["epost"]}">{E(k["epost"])}</a>' if k.get("epost") else ""}{f" · Org.nr {E(k['orgnr'])}" if k.get("orgnr") else ""}</p>
    {stor}
    <div class="fot-slut">{tag}{juridik}<span>© <span data-year>2026</span> {E(b["namn"])}</span></div>
  </div>
{ELEVATE_CREDIT}</footer>'''
        cta = ""
        if v == "cta":
            cta = (f'<div class="fot-cta"><h2>{E(b.get("fot_cta") or self.T("fot_cta"))}</h2>'
                   f'<div class="knappar">{self.knapp(self.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<a class="textlank" href="tel:{tel(k["telefon"])}"><span>{E(k["telefon"])}</span>{PIL}</a></div></div>')
        return f'''<footer class="fot{" fot-med-cta" if cta else ""}">
  {upp}
  <div class="wrap">
    {cta}
    <div class="fot-grid">
      <div class="fot-om"><p class="fot-namn">{E(b["kortnamn"])}</p><p>{E(b.get("fot_text", b["hero_text"]))}</p>{self.textlank(self.T("fot_lank"), "verksamhet.html")}</div>
      <div><h4>{E(self.T("fot_kontakt"))}</h4><ul><li>{E(b["namn"])}</li><li><a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a></li>{f'<li><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></li>' if k.get("epost") else ""}</ul></div>
      <div><h4>{E(self.T("fot_adress"))}</h4><ul><li>{E(k["adress"])}</li><li>{E(k["postnr"])} {E(k["ort"])}</li>{f'<li>Org.nr {E(k["orgnr"])}</li>' if k.get("orgnr") else ""}</ul></div>
      <div><h4>{E(self.T("fot_genvagar"))}</h4><ul>{"".join(f'<li><a href="{self.u(h)}">{E(t.format(kortnamn=b["kortnamn"]))}</a></li>' for t, h in self.pr["genvagar"])}</ul></div>
    </div>
    {stor}
    <div class="fot-slut">{tag}{juridik}<span>© <span data-year>2026</span> {E(b["namn"])}</span></div>
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
<meta name="theme-color" content="{p["farger"]["primar"]}">{'<meta name="robots" content="noindex, nofollow">' if self.b.get("demo") else ""}
<meta property="og:title" content="{E(titel)}"><meta property="og:description" content="{E(beskrivning)}"><meta property="og:image" content="{Bilder.prefix}{self.hero_bild["id"]}.jpg">
{google_fonts(p)}
<link rel="stylesheet" href="assets/tokens.css?v={ver(a / "tokens.css")}">
<link rel="stylesheet" href="assets/bas.css?v={ver(a / "bas.css")}">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body {self.body_attr(har_hero)}>
{self.demo_rad()}{self.header(aktiv)}
<main id="main">
{main}
</main>
{self.footer()}
<script src="assets/sajt.js?v={ver(a / "sajt.js")}" defer></script>
</body>
</html>
'''
        (self.ut / namn).write_text(self.fixa_lankar(doc), encoding="utf-8")

    # --- Hero -----------------------------------------------------------------------------------------------------
    def slides(self):
        """Tre bilder i heron: företagets budskap och två berättelser."""
        b = self.b
        ber = berattelser(b)
        s = [dict(rubrik=b["hero_rubrik"], text=b["hero_text"], bild=self.hero_bild, lank=(self.T("hero_knapp"), "verksamhet.html"), h1=True)]
        for x in ber[:2]:
            s.append(dict(rubrik=x["rubrik"], text=x["text"], bild=self.bilder.ta(x["tagg"]), lank=(self.T("las_mer"), "projekt.html"), h1=False))
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
        btns = f'<div class="knappar">{self.knapp(self.T("hero_knapp"), "verksamhet.html")}{self.textlank(self.T("hero_lank"), self.b.get("hero_lank_href", "investerare.html" if "priser" in self.slugs else "projekt.html"))}</div>'
        img = self.bilder.img(self.hero_bild, lazy=False)
        if h == "split":
            return f'''<section class="hero hero-split" aria-labelledby="h1"><div class="split-text"><span class="etikett" style="color:inherit;opacity:.8">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>{btns}</div>
  <div class="split-bild"><div class="bild-fyll">{img}</div><span class="foto-not">Illustrationsbild</span></div></section>'''
        if h == "sok":
            b2 = self.b.get("sok", {})
            ort = "".join(f"<option>{E(o)}</option>" for o in b2.get("orter", ["Stockholm", "Uppsala", "Göteborg", "Malmö"]))
            typ = "".join(f"<option>{E(o)}</option>" for o in b2.get("typer", ["Lägenhet", "Radhus", "Parhus"]))
            return f'''<section class="hero hero-sok full" aria-labelledby="h1"><div class="sok-bild"><div class="bild-fyll">{img}</div><span class="foto-not">Illustrationsbild</span></div>
  <div class="wrap sok-in"><div class="sok-kort"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>
  <form class="sok-form" action="projekt.html"><label><span>Var?</span><select name="ort"><option>Alla orter</option>{ort}</select></label><label><span>Typ</span><select name="typ"><option>Alla typer</option>{typ}</select></label>
  <button class="knapp knapp-primar" type="submit">{ikon("sok")}<span>{E(b2.get("knapp", "Sök"))}</span></button></form></div></div></section>'''
        if h == "kurs":
            inv = b["investerare"]
            upp = inv.get("forandring", "+").startswith("+")
            return f'''<section class="hero hero-kurs" aria-labelledby="h1"><div class="bild-fyll skugga-vanster">{img}</div>
  <div class="wrap kurs-in"><div class="kurs-text"><span class="etikett" style="color:#fff;opacity:.85">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1><p class="ingress">{E(b["hero_text"])}</p>
  <div class="knappar">{self.knapp("Till investerare", "investerare.html", "ljus")}{self.textlank("Våra bolag", "bolag.html")}</div></div>
  <aside class="aktiekort" aria-label="Aktien"><span class="ak-namn">{E(inv["aktie"])} · {E(inv["lista"])}</span><div class="ak-kurs">{E(inv.get("kurs", ""))} <small>SEK</small></div><span class="{"upp" if upp else "ned"}">{E(inv.get("forandring", ""))} idag</span>
  <svg viewBox="0 0 300 80" preserveAspectRatio="none" aria-hidden="true"><path d="M0 64 L25 58 L50 62 L75 48 L100 52 L125 40 L150 44 L175 30 L200 34 L225 22 L250 26 L275 12 L300 16" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M0 64 L25 58 L50 62 L75 48 L100 52 L125 40 L150 44 L175 30 L200 34 L225 22 L250 26 L275 12 L300 16 V80 H0Z" fill="currentColor" opacity=".12"/></svg>
  <dl>{"".join(f"<div><dt>{E(n['etikett'])}</dt><dd>{E(n['varde'])} {E(n['enhet'])}</dd></div>" for n in b["nyckeltal"][:3])}</dl><small>Fördröjd kurs. Exempeldata.</small></aside></div><span class="foto-not">Illustrationsbild</span></section>'''
        if h == "statement":
            return f'''<section class="hero hero-statement full" aria-labelledby="h1"><div class="bild-fyll">{img}</div><div class="wrap"><span class="etikett">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1>
  <div class="statement-rad"><p class="ingress">{E(b["hero_text"])}</p><div class="knappar">{self.knapp(self.T("hero_knapp"), "verksamhet.html", "ljus")}{self.textlank(self.T("hero_lank"), self.b.get("hero_lank_href", "investerare.html" if "priser" in self.slugs else "projekt.html"))}</div></div></div><span class="foto-not">Illustrationsbild</span></section>'''
        if h == "mosaik":
            extra = [self.bilder.ta(t) for t in self.p.get("mosaik_taggar", ["people", "natur"])]
            bg = "".join(f'<div class="bild-fyll" style="position:relative">{self.bilder.img(x, "(min-width:700px) 50vw, 100vw", lazy=k > 0)}</div>' for k, x in enumerate([self.hero_bild] + extra))
            return f'''<section class="hero hero-mosaik full" aria-labelledby="h1"><div class="mosaik-bg">{bg}</div><div class="wrap"><span class="etikett" style="color:#fff;opacity:.85">{E(b["typ"])}</span><h1 id="h1">{E(b["hero_rubrik"])}</h1>
  <p class="ingress">{E(b["hero_text"])}</p><div class="knappar">{self.knapp(self.T("hero_knapp"), "verksamhet.html", "ljus")}{self.textlank(self.T("hero_lank"), self.b.get("hero_lank_href", "investerare.html" if "priser" in self.slugs else "projekt.html"))}</div></div><span class="foto-not">Illustrationsbild</span></section>'''
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
        egen = self.p.get("bakgrund", {})
        if roll in egen:
            return egen[roll]
        return tabell.get(r, tabell["ton"]).get(roll, "")

    def s_vagval(self):
        b = self.b
        t = tjanster(b)
        v = self.blk("vagval", "rutor")
        fraga = b.get("vagval_rubrik") or self.T("vagval_rubrik")
        huvud_mitt = f'<div class="sek-huvud mitt"><h2 id="vv-h">{E(fraga)}</h2></div>'
        huvud = f'<div class="sek-huvud"><div><span class="etikett">{E(self.T("vagval_etikett"))}</span><h2 id="vv-h">{E(fraga)}</h2></div></div>'
        if v == "rader":
            rad = "".join(f'<li><a href="{x.get("href", "verksamhet.html")}"><span class="nr">{i + 1:02d}</span><span class="t">{E(x["titel"])}</span>{ikon(x.get("ikon", "kugge"))}<span class="rundpil">{PIL}</span></a></li>' for i, x in enumerate(t))
            inner = f'{huvud}<ul class="vv-rader">{rad}</ul>'
        elif v == "chips":
            rad = "".join(f'<a href="{x.get("href", "verksamhet.html")}">{ikon(x.get("ikon", "kugge"))}<span>{E(x["titel"])}</span></a>' for x in t)
            inner = f'{huvud_mitt}<nav class="vv-chips" aria-label="Vägval">{rad}</nav>'
        elif v == "nummer":
            rad = "".join(f'<a href="{x.get("href", "verksamhet.html")}"><span class="nr">{i + 1:02d}</span>{ikon(x.get("ikon", "kugge"))}<span class="t">{E(x["titel"])}</span></a>' for i, x in enumerate(t))
            inner = f'{huvud}<nav class="vv-nummer" aria-label="Vägval">{rad}</nav>'
        elif v == "cirklar":
            rad = "".join(f'<a href="{x.get("href", "verksamhet.html")}"><span class="cirkel">{ikon(x.get("ikon", "kugge"))}</span><span>{E(x["titel"])}</span></a>' for x in t)
            inner = f'{huvud_mitt}<nav class="vv-cirklar" aria-label="Vägval">{rad}</nav>'
        elif v == "bildrutor":
            rad = ""
            for x in t[:8]:
                bild = self.bilder.ta(x.get("tagg"))
                rad += f'<a href="{x.get("href", "verksamhet.html")}">{self.bilder.fyll(bild, "(min-width:1100px) 25vw, 50vw")}<span class="t">{E(x["titel"])}</span><span class="rundpil">{PIL}</span></a>'
            inner = f'{huvud}<nav class="vv-bild" aria-label="Vägval">{rad}</nav>'
        elif v == "lankar":
            rad = "".join(f'<li><a href="{x.get("href", "verksamhet.html")}">{ikon(x.get("ikon", "kugge"))}<span>{E(x["titel"])}</span>{PIL}</a></li>' for x in t)
            inner = f'<div class="vv-lank-rad"><div><span class="etikett">{E(self.T("genvagar_etikett"))}</span><h2 id="vv-h">{E(fraga)}</h2></div><ul class="vv-lankar">{rad}</ul></div>'
        elif v == "register":
            rad = "".join(f'<li><a href="{x.get("href", "verksamhet.html")}"><span class="nr">{i + 1}</span><span class="t">{E(x["titel"])}</span><span class="prick"></span><span class="sid">s. {4 + i * 3}</span></a></li>' for i, x in enumerate(t))
            inner = f'<div class="vv-reg-rad"><div><span class="etikett">{E(self.T("register_etikett"))}</span><h2 id="vv-h">{E(fraga)}</h2></div><ol class="vv-register">{rad}</ol></div>'
        elif v == "expertis":
            rad = "".join(f'<details><summary><span class="nr">{i + 1:02d}</span><span class="t">{E(x["titel"])}</span><span class="plus" aria-hidden="true"></span></summary><div class="ex-text"><p>{E(x.get("text") or self.T("expertis_text", titel=x["titel"].lower()))}</p>{self.textlank(self.T("las_mer"), x.get("href", "verksamhet.html"))}</div></details>' for i, x in enumerate(t))
            inner = f'<div class="vv-ex-rad"><div><span class="etikett">{E(self.T("expertis_etikett"))}</span><h2 id="vv-h">{E(fraga)}</h2></div><div class="vv-expertis">{rad}</div></div>'
        else:
            rutor = "".join(f'<a href="{x.get("href", "verksamhet.html")}">{ikon(x.get("ikon", "kugge"))}<span>{E(x["titel"])}</span></a>' for x in t)
            inner = f'{huvud_mitt}<nav class="vagval" aria-label="Vägval">{rutor}</nav>'
        return f'''<section class="sek {self.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">{inner}</div></section>'''

    def s_berattelser(self):
        v = self.blk("berattelser", "tre")
        ber = berattelser(self.b)[:3]
        rubrik = E(self.b.get("berattelser_rubrik") or self.T("ber_rubrik"))
        huvud = f'<div class="sek-huvud"><div><span class="etikett">{E(self.T("ber_etikett"))}</span><h2 id="be-h">{rubrik}</h2></div>{self.textlank(self.T("ber_lank"), "projekt.html")}</div>'
        if v == "stor":
            bilder = [self.bilder.ta(x["tagg"]) for x in ber]
            stor = (f'<a class="be-stor reveal" href="projekt.html">{self.bilder.fyll(bilder[0], "(min-width:960px) 60vw, 100vw")}<div class="be-text"><span class="meta">{E(self.T("ber_utvalt"))}</span>'
                    f'<h3>{E(ber[0]["rubrik"])}</h3><p>{E(ber[0]["text"])}</p><span class="textlank"><span>{E(self.T("las_mer"))}</span>{PIL}</span></div></a>')
            sma = "".join(f'<a class="be-liten reveal" href="projekt.html"><div class="foto">{self.bilder.img(bi, "(min-width:960px) 20vw, 40vw")}</div><div><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p></div></a>' for x, bi in zip(ber[1:], bilder[1:]))
            return f'''<section class="sek {self.bg("berattelser")}" aria-labelledby="be-h"><div class="wrap">{huvud}<div class="be-stor-grid">{stor}<div class="be-sma">{sma}</div></div></div></section>'''
        if v == "rad":
            rad = "".join(f'<li><a href="projekt.html"><span class="nr">{i + 1:02d}</span><div class="foto">{self.bilder.img(self.bilder.ta(x["tagg"]), "160px")}</div><div class="be-r-text"><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p></div><span class="rundpil">{PIL}</span></a></li>' for i, x in enumerate(ber))
            return f'''<section class="sek {self.bg("berattelser")}" aria-labelledby="be-h"><div class="wrap">{huvud}<ul class="be-rad">{rad}</ul></div></section>'''
        if v == "band":
            bild = self.bilder.ta(ber[0]["tagg"])
            ovr = "".join(f'<a href="projekt.html"><b>{E(x["rubrik"])}</b><span>{E(x["text"])}</span></a>' for x in ber[1:])
            return f'''<section class="be-band {self.bg("berattelser")}" aria-labelledby="be-h">{self.bilder.fyll(bild, note=True)}<div class="wrap"><div class="be-band-kort reveal"><span class="etikett">{E(self.T("ber_etikett"))}</span>
  <h2 id="be-h">{E(ber[0]["rubrik"])}</h2><p>{E(ber[0]["text"])}</p>{self.textlank(self.T("las_mer"), "projekt.html")}<div class="be-band-ovr">{ovr}</div></div></div></section>'''
        kort = ""
        for x in berattelser(self.b)[:3]:
            bild = self.bilder.ta(x["tagg"])
            kl = "overlay" if self.p.get("kort", "overlay") == "overlay" else "berattelse"
            kort += (f'<li class="kort {kl} reveal"><a href="projekt.html"><div class="foto">{self.bilder.img(bild, "(min-width:1100px) 33vw, 100vw")}</div>'
                     f'<div class="kort-text"><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p>{self.textlank(self.T("las_mer"), "projekt.html").replace("<a ", "<span ").replace("</a>", "</span>")}</div></a></li>')
        return f'''<section class="sek {self.bg("berattelser")}" aria-labelledby="be-h"><div class="wrap">
  {huvud}
  <ul class="kortlista tre">{kort}</ul></div></section>'''

    def s_panel(self, omvand=False):
        b = self.b
        k = b["karriar"]
        v = self.blk("panel", "panel")
        if v == "helbild":
            return f'''<section class="pa-helbild" aria-labelledby="pa-h">{self.bilder.fyll(self.bilder.ta(self.bt("panel")), note=True)}<div class="wrap"><div class="pa-hb-text reveal"><span class="etikett">{E(self.T("panel_etikett"))}</span>
  <h2 id="pa-h">{E(k["rubrik"])}</h2><p>{E(k["text"])}</p><div class="knappar">{self.knapp(self.T("panel_knapp"), "karriar.html", "ljus")}</div></div></div></section>'''
        if v == "jobb":
            jobb = "".join(f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span><span class="rundpil">{PIL}</span></a></li>' for t, o in k["jobb"])
            return f'''<section class="sek {self.bg("panel")}" aria-labelledby="pa-h"><div class="wrap pa-jobb"><div><span class="etikett">{E(self.T("panel_etikett"))}</span><h2 id="pa-h">{E(k["rubrik"])}</h2><p class="ingress" style="margin-top:18px">{E(k["text"])}</p>
  <div class="knappar">{self.knapp(self.T("panel_alla"), "karriar.html")}</div></div><ul class="pa-jobb-lista">{jobb}</ul></div></section>'''
        bild = self.bilder.ta(self.bt("panel"))
        ljus = " ljus" if self.p.get("panel") == "ton" else ""
        return f'''<section class="sek {self.bg("panel")}" aria-labelledby="pa-h"><div class="wrap">
  <div class="panel{" omvand" if omvand else ""}{ljus} reveal"><div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>
  <div class="panel-text"><span class="etikett">{E(self.T("panel_etikett"))}</span><h2 id="pa-h">{E(k["rubrik"])}</h2><p>{E(k["text"])}</p><p>{E(b.get("kultur") or self.T("kultur"))}</p>
  <div class="knappar">{self.textlank(self.T("panel_knapp"), "karriar.html")}</div></div></div></div></section>'''

    def s_bolag(self):
        bl = bolagslista(self.b)
        v = self.blk("bolag", "kort")
        huvud = f'<div class="sek-huvud"><div><span class="etikett">{E(self.T("bolag_etikett"))}</span><h2 id="bo-h">{E(self.b.get("bolag_rubrik") or self.T("bolag_rubrik"))}</h2></div>{self.knapp(self.T("bolag_knapp"), "om-oss.html" if self.pr is not None and "verksamhet" not in self.slugs else "verksamhet.html", "kontur")}</div>'
        if v == "flikar":
            knappar, paneler = "", ""
            for i, x in enumerate(bl):
                bild = self.bilder.ta(x.get("tagg"))
                knappar += f'<button type="button" role="tab" id="flik-{i}" aria-controls="flikpanel-{i}" aria-selected="{"true" if i == 0 else "false"}"><span class="nr">{i + 1:02d}</span><span>{E(x["namn"])}</span></button>'
                paneler += (f'<div class="flikpanel" role="tabpanel" id="flikpanel-{i}" aria-labelledby="flik-{i}"{"" if i == 0 else " hidden"}>{self.bilder.fyll(bild, "(min-width:960px) 60vw, 100vw")}'
                            f'<div class="flik-text"><span class="bolagsnamn">{E(x.get("segment", ""))}</span><h3>{E(x.get("rubrik", x["namn"]))}</h3><p>{E(x["text"])}</p>{self.textlank(self.T("bolag_till", namn=x["namn"]), "bolag.html#bolag-" + str(i))}</div></div>')
            inner = f'{huvud}<div class="bo-flikar" data-flikar><div class="flik-lista" role="tablist" aria-label="{E(self.T("bolag_rubrik"))}">{knappar}</div><div class="flik-paneler">{paneler}</div></div>'
        elif v == "lista":
            rad = ""
            for i, x in enumerate(bl):
                bild = self.bilder.ta(x.get("tagg"))
                rad += (f'<li><a href="bolag.html#bolag-{i}"><span class="bo-seg">{E(x.get("segment", ""))}</span><span class="bo-namn">{E(x["namn"])}</span>'
                        f'<span class="bo-txt">{E(x["text"])}</span><span class="bo-bild">{self.bilder.img(bild, "160px")}</span></a></li>')
            inner = f'{huvud}<ul class="bo-lista">{rad}</ul>'
        elif v == "tabell":
            rad = "".join(f'<tr><th scope="row"><a href="bolag.html#bolag-{i}">{E(x["namn"])}</a></th><td>{E(x.get("segment", ""))}</td><td>{E(x["text"])}</td><td><a class="rundpil" href="bolag.html#bolag-{i}" aria-label="Till {E(x["namn"])}">{PIL}</a></td></tr>' for i, x in enumerate(bl))
            inner = f'{huvud}<div class="bo-tabell-ram"><table class="bo-tabell"><thead><tr>{"".join(f'<th scope="col">{E(c)}</th>' for c in self.T("bolag_kol"))}<th scope="col"><span class="sr">Länk</span></th></tr></thead><tbody>{rad}</tbody></table></div>'
        elif v == "rund":
            rad = ""
            for i, x in enumerate(bl):
                bild = self.bilder.ta(x.get("tagg"))
                rad += f'<li><a href="bolag.html#bolag-{i}"><span class="rund-bild">{self.bilder.img(bild, "240px")}</span><span class="bolagsnamn">{E(x.get("segment", ""))}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p></a></li>'
            inner = f'{huvud}<ul class="bo-rund">{rad}</ul>'
        elif v == "vagg":
            namn = self.b.get("lokala_bolag", [x["namn"] for x in bl])
            vagg = "".join(f'<li><a href="bolag.html"><span>{E(n)}</span></a></li>' for n in namn)
            kort = self._bolagskort(bl)
            inner = (f'{huvud}{kort}<div class="bo-vagg-rubrik"><h3>{E(self.T("vagg_rubrik", n=len(namn)))}</h3><p class="mut">{E(self.b.get("vagg_text") or self.T("vagg_text"))}</p></div>'
                     f'<ul class="bo-vagg">{vagg}</ul>')
        else:
            inner = huvud + self._bolagskort(bl)
        return f'''<section class="sek {self.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">{inner}</div></section>'''

    def _bolagskort(self, bl):
        li = ""
        for i, x in enumerate(bl):
            bild = self.bilder.ta(x.get("tagg"))
            li += (f'<li class="reveal"><a href="bolag.html#bolag-{i}">{self.bilder.fyll(bild, "(min-width:760px) 50vw, 100vw")}<div class="bolag-text">'
                   f'<span class="bolagsnamn">{E(x["namn"])}</span><h3>{E(x.get("rubrik", x.get("segment", "")))}</h3><p>{E(x["text"])}</p>'
                   f'<span class="textlank"><span>{E(self.T("bolag_till", namn=x["namn"]))}</span>{PIL}</span></div></a></li>')
        return f'<ul class="bolag{" fyra" if len(bl) == 4 else " tre" if len(bl) == 3 else ""}">{li}</ul>'

    def s_siffror(self):
        b = self.b
        v = self.blk("siffror", "rad")
        nt = b["nyckeltal"]
        rubrik = E(b.get("intro_rubrik", b["slogan"]))
        if v == "jatte":
            forsta, rest = nt[0], nt[1:]
            sma = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in rest)
            return f'''<section class="sek {self.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">
  <div class="si-jatte"><div><span class="etikett">{E(self.T("siffror_etikett"))}</span><h2 id="si-h">{rubrik}</h2><p class="ingress" style="margin-top:18px">{E(b["om"][0])}</p></div>
  <div class="jatte-tal" aria-label="{E(forsta["varde"])} {E(forsta["enhet"])} {E(forsta["etikett"])}"><b>{E(forsta["varde"])}</b><span>{E(forsta["enhet"])} · {E(forsta["etikett"])}</span></div></div>
  <div class="siffror tre">{sma}</div></div></section>'''
        if v == "band":
            en = "".join(f'<span class="bt"><b>{E(n["varde"])}{(" " + E(n["enhet"])) if n["enhet"] else ""}</b> {E(n["etikett"])}</span><span class="bt-sep" aria-hidden="true">/</span>' for n in nt)
            return f'''<section class="si-band {self.bg("siffror") or "pa-mork"}" aria-label="Nyckeltal"><div class="band-spar"><div class="band-rull">{en}{en}{en}</div></div></section>'''
        if v == "dashboard":
            kort = ""
            for n in nt:
                trend = n.get("trend")  # valfri lista med värden i briefen; utan den ritas ingen kurva
                svg = ""
                if trend and len(trend) > 1:
                    lo, hi = min(trend), max(trend)
                    d = " ".join(f"{'M' if k == 0 else 'L'}{k * 300 / (len(trend) - 1):.0f} {64 - 56 * (y - lo) / ((hi - lo) or 1):.0f}" for k, y in enumerate(trend))
                    svg = f'<svg viewBox="0 0 300 72" preserveAspectRatio="none" aria-hidden="true"><path d="{d}" fill="none" stroke="currentColor" stroke-width="2"/></svg><span class="db-not">{E(n.get("trend_text", "Utveckling"))}</span>'
                kort += f'<div class="db-kort"><span class="db-et">{E(n["etikett"])}</span><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b>{svg}</div>'
            return f'''<section class="sek {self.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("nyckeltal_etikett"))}</span><h2 id="si-h">{rubrik}</h2></div>{self.textlank(self.T("nyckeltal_lank"), "investerare.html" if "investerare" in self.slugs else "om-oss.html")}</div><div class="db-grid">{kort}</div></div></section>'''
        rad = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in nt)
        return f'''<section class="sek {self.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("siffror_etikett"))}</span><h2 id="si-h">{rubrik}</h2></div><p class="ingress" style="max-width:32em">{E(b["om"][0])}</p></div>
  <div class="siffror">{rad}</div></div></section>'''

    def s_process(self):
        b = self.b
        steg = b.get("process") or [{"titel": a["titel"], "text": a["text"]} for a in b["affarsomraden"]]
        li = ""
        for i, x in enumerate(steg):
            bild = self.bilder.ta(x.get("tagg"))
            li += (f'<li class="reveal"><div class="pr-bild">{self.bilder.img(bild, "(min-width:1100px) 25vw, 80vw")}</div><span class="pr-nr">{i + 1}</span>'
                   f'<h3>{E(x["titel"])}</h3><p>{E(x["text"])}</p></li>')
        return f'''<section class="sek {self.bg("process")}" aria-labelledby="pr2-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("process_etikett"))}</span><h2 id="pr2-h">{E(b.get("process_rubrik") or self.T("process_rubrik"))}</h2></div></div><ol class="process">{li}</ol></div></section>'''

    def s_citat(self):
        c = self.b.get("citat") or {"text": self.b["om"][1], "namn": "Vd", "roll": self.b["namn"]}
        bild = self.bilder.ta(c.get("tagg") or self.bt("citat"))
        return f'''<section class="sek {self.bg("citat")}" aria-label="Citat"><div class="wrap"><figure class="citat reveal"><div class="citat-bild">{self.bilder.img(bild, "320px")}</div>
  <div><blockquote><p>”{E(c["text"])}”</p></blockquote><figcaption><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></div></figure></div></section>'''

    def s_tidslinje(self):
        tl = self.b.get("tidslinje") or []
        li = "".join(f'<li class="reveal"><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in tl)
        return f'''<section class="sek {self.bg("tidslinje")}" aria-labelledby="tl-h"><div class="wrap tl-grid"><div class="tl-head"><span class="etikett">{E(self.T("tidslinje_etikett"))}</span><h2 id="tl-h">{E(self.b.get("tidslinje_rubrik") or self.T("tidslinje_rubrik"))}</h2>
  <p class="ingress" style="margin-top:18px">{E(self.b.get("tidslinje_text", ""))}</p></div><ol class="tidslinje">{li}</ol></div></section>'''

    def s_kontor(self):
        ko = self.b.get("kontor_lista") or []
        li = "".join(f'<li><b>{E(n)}</b><span>{E(a)}</span></li>' for n, a in ko)
        return f'''<section class="sek {self.bg("kontor")}" aria-labelledby="ko-h"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">{E(self.T("kontor_etikett"))}</span><h2 id="ko-h">{E(self.b.get("kontor_rubrik") or self.T("kontor_rubrik"))}</h2></div>
  <p class="ingress" style="max-width:32em">{E(self.b.get("kontor_text", ""))}</p></div><ul class="kontor n{len(ko)}">{li}</ul></div></section>'''

    def s_service(self):
        r = self.b.get("service") or [("Lediga lägenheter", "hus", "projekt.html"), ("Felanmälan", "kugge", "om-oss.html#kontakt"), ("Bostadskö", "dokument", "om-oss.html#kontakt"), ("Mina sidor", "nyckel", "#")]
        a = "".join(f'<a href="{h}">{ikon(i)}<span>{E(t)}</span>{PIL}</a>' for t, i, h in r)
        return f'<div class="service-rad"><div class="wrap"><nav class="service" aria-label="Snabbtjänster">{a}</nav></div></div>'

    def s_projekt(self):
        v = self.blk("projekt", "")
        def status_for(x):
            ar = x.get("ar", "")
            pag = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2026)
            return x.get("status") or (self.T("status_pagaende") if pag else self.T("status_klart"))
        if v == "lista":
            rad = ""
            for x in self.b["projekt"]:
                bild = self.bilder.ta(x["tagg"])
                st = status_for(x)
                rad += (f'<li><a href="projekt.html"><span class="pl-bild">{self.bilder.img(bild, "120px")}</span><span class="pl-namn">{E(x["namn"])}</span><span class="pl-ort">{E(x["ort"])}</span>'
                        f'<span class="pl-typ">{E(x["typ"])}</span><span class="status{" pagaende" if st == self.T("status_pagaende") else ""}">{E(st)}</span><span class="pl-ar">{E(x["ar"])}</span>{PIL}</a></li>')
            return f'''<section class="sek {self.bg("projekt")}" aria-labelledby="pr-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("proj_etikett"))}</span><h2 id="pr-h">{E(self.b.get("projekt_rubrik") or self.T("proj_rubrik_lista"))}</h2></div>{self.textlank(self.T("proj_lank"), "projekt.html")}</div>
  <div class="pl-huvud" aria-hidden="true"><span></span>{"".join(f"<span>{E(c)}</span>" for c in self.T("proj_kol"))}</div><ul class="pl-lista">{rad}</ul></div></section>'''
        if v == "feature":
            pr = self.b["projekt"]
            bild0 = self.bilder.ta(pr[0]["tagg"])
            stor = (f'<a class="pf-stor reveal" href="projekt.html">{self.bilder.fyll(bild0, "(min-width:960px) 55vw, 100vw")}<span class="status pagaende">{E(status_for(pr[0]))}</span>'
                    f'<div class="pf-text"><span class="meta">{E(pr[0]["ort"])} · {E(pr[0]["typ"])}</span><h3>{E(pr[0]["namn"])}</h3><p>{E(pr[0]["text"])}</p></div></a>')
            sma = "".join(f'<li><a href="projekt.html"><div class="foto">{self.bilder.img(self.bilder.ta(x["tagg"]), "200px")}</div><div><span class="meta">{E(x["ort"])} · {E(status_for(x))}</span><h3>{E(x["namn"])}</h3></div></a></li>' for x in pr[1:5])
            return f'''<section class="sek {self.bg("projekt")}" aria-labelledby="pr-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("proj_etikett"))}</span><h2 id="pr-h">{E(self.b.get("projekt_rubrik") or self.T("proj_rubrik"))}</h2></div>{self.textlank(self.T("proj_lank"), "projekt.html")}</div>
  <div class="pf-grid">{stor}<ul class="pf-sma">{sma}</ul></div></div></section>'''
        li = ""
        for i, x in enumerate(self.b["projekt"]):
            bild = self.bilder.ta(x["tagg"])
            ar = x.get("ar", "")
            pagaende = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2026)
            status = x.get("status") or (self.T("status_pagaende") if pagaende else self.T("status_klart"))
            li += (f'<li class="kort"><a href="projekt.html"><div class="foto"><span class="status{" pagaende" if status == self.T("status_pagaende") else ""}">{E(status)}</span>{self.bilder.img(bild, "(min-width:1100px) 33vw, 80vw", lazy=i > 2)}</div>'
                   f'<div class="kort-text"><span class="meta">{E(x["ort"])} · {E(x["typ"])}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p></div></a></li>')
        return f'''<section class="sek {self.bg("projekt")}" aria-labelledby="pr-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("proj_etikett"))}</span><h2 id="pr-h">{E(self.b.get("projekt_rubrik") or self.T("proj_rubrik"))}</h2></div><div style="display:flex;gap:20px;align-items:center">{self.textlank(self.T("proj_lank"), "projekt.html")}<div class="spel-pilar" data-karusell="projektlista"><button class="bak" type="button" aria-label="Föregående">{PIL}</button><button type="button" aria-label="Nästa">{PIL}</button></div></div></div>
  <ul class="projekt" id="projektlista">{li}</ul></div></section>'''

    def s_hb(self):
        v = self.blk("hb", "split")
        hb = self.b["hallbarhet"]
        if v == "helbild":
            mal = "".join(f'<li><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
            return f'''<section class="hb-helbild" aria-labelledby="hb-h">{self.bilder.fyll(self.bilder.ta(self.bt("hb")), note=True)}<div class="wrap"><div class="hb-kort reveal"><span class="etikett">{E(self.T("hb_etikett"))}</span>
  <h2 id="hb-h">{E(hb["rubrik"])}</h2><p>{E(hb["text"])}</p><ul class="mal">{mal}</ul>{self.textlank(self.T("hb_lank"), "hallbarhet.html")}</div></div></section>'''
        if v == "siffror":
            mal = "".join(f'<li class="reveal"><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
            return f'''<section class="sek {self.bg("hb")}" aria-labelledby="hb-h"><div class="wrap mitt"><span class="etikett">{E(self.T("hb_etikett"))}</span><h2 id="hb-h" class="hb-stor" style="margin-inline:auto;max-width:14em">{E(hb["rubrik"])}</h2>
  <p class="ingress" style="margin:22px auto 0;max-width:40em">{E(hb["text"])}</p><ul class="hb-mal-stor">{mal}</ul><div class="knappar" style="justify-content:center">{self.knapp(self.T("hb_lank"), "hallbarhet.html", "kontur")}</div></div></section>'''
        if v == "kort":
            kort = ""
            for a, t in hb["mal"]:
                bild = self.bilder.ta(self.bt("hb"))
                kort += f'<li class="reveal"><div class="foto">{self.bilder.img(bild, "(min-width:900px) 33vw, 100vw")}</div><b>{E(a)}</b><span>{E(t)}</span></li>'
            return f'''<section class="sek {self.bg("hb")}" aria-labelledby="hb-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("hb_etikett"))}</span><h2 id="hb-h">{E(hb["rubrik"])}</h2></div><p class="ingress" style="max-width:32em">{E(hb["text"])}</p></div><ul class="hb-kort-lista">{kort}</ul></div></section>'''
        mal = "".join(f'<li><b>{E(v)}</b><span>{E(t)}</span></li>' for v, t in hb["mal"])
        bild = self.bilder.ta(self.bt("hb"))
        return f'''<section class="sek {self.bg("hb")}" aria-labelledby="hb-h"><div class="wrap hb">
  <div class="reveal"><span class="etikett">{E(self.T("hb_etikett"))}</span><h2 id="hb-h" class="hb-stor">{E(hb["rubrik"])}</h2><p class="ingress" style="margin-top:22px">{E(hb["text"])}</p><ul class="mal">{mal}</ul>
  <div class="knappar">{self.textlank(self.T("hb_lank"), "hallbarhet.html")}</div></div>
  <div class="hb-bild reveal">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div></div></section>'''

    def s_ir(self):
        inv = self.b["investerare"]
        v = self.blk("ir", "kort")
        if v in ("tabell", "kompakt"):
            upp = inv.get("forandring", "+").startswith("+")
            kurs = (f'<div class="ir-kurs"><span class="aktie-namn">{E(inv["aktie"])}</span><b>{E(inv["kurs"])} <small>SEK</small></b><span class="{"upp" if upp else "ned"}">{E(inv["forandring"])}</span><small>{E(inv["lista"])} · exempeldata</small></div>'
                    if inv.get("kurs") else f'<div class="ir-kurs"><span class="aktie-namn">Ägande</span><b style="font-size:26px">{E(inv["aktie"])}</b><small>{E(inv["lista"])}</small></div>')
            if v == "kompakt":
                return f'''<section class="sek sek-tat {self.bg("ir")}" aria-label="Investerare"><div class="wrap"><div class="ir-kompakt">{kurs}<div class="ir-k-text"><span class="etikett">Investerare</span><b>{E(inv["rapporter"][0][0])}</b><span class="mut">{E(inv["rapporter"][0][1])}</span></div>{self.knapp("Finansiell information", "investerare.html", "kontur")}</div></div></section>'''
            rap = "".join(f'<li><a href="investerare.html#rapporter"><span><span class="pdf">PDF</span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["rapporter"])
            kal = "".join(f'<li><a href="investerare.html"><span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["kalender"]) or '<li><a href="investerare.html"><span>Inga planerade händelser</span></a></li>'
            return f'''<section class="sek {self.bg("ir")}" aria-labelledby="ir-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">Investerare</span><h2 id="ir-h">Aktien, rapporter och kalender</h2></div>{self.textlank("Till investerarsidan", "investerare.html")}</div>
  <div class="ir-tabell">{kurs}<div><h3>Rapporter</h3><ul class="rapporter">{rap}</ul></div><div><h3>Kalender</h3><ul class="rapporter">{kal}</ul></div></div></div></section>'''
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
        if self.blk("nyheter", "") == "rad":
            rad = "".join(f'<li><a href="om-oss.html#press"><time>{E(d)}</time><b>{E(t)}</b>{PIL}</a></li>' for d, t, *_ in self.b["nyheter"])
            return f'''<section class="sek {self.bg("nyheter")}" aria-labelledby="ny-h"><div class="wrap ny-rad-grid"><div><span class="etikett">{E(self.T("ny_etikett"))}</span><h2 id="ny-h">{E(self.T("ny_rubrik"))}</h2>
  <div class="knappar">{self.textlank(self.T("ny_lank"), "om-oss.html#press")}</div></div><ul class="ny-rad">{rad}</ul></div></section>'''
        if self.blk("nyheter", "") == "tidning":
            ny = self.b["nyheter"]
            stor_bild = self.bilder.ta(self.b.get("nyhet_tagg"))
            d0, t0 = ny[0][0], ny[0][1]
            sma = "".join(f'<a class="tn-liten" href="om-oss.html#press"><time>{E(d)}</time><b>{E(t)}</b></a>' for d, t, *_ in ny[1:])
            return f'''<section class="sek {self.bg("nyheter")}" aria-labelledby="ny-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("ny_etikett2"))}</span><h2 id="ny-h">{E(self.T("ny_senaste"))}</h2></div>{self.textlank(self.T("ny_lank"), "om-oss.html#press")}</div>
  <div class="tidning"><a class="tn-stor" href="om-oss.html#press"><div class="foto">{self.bilder.img(stor_bild, "(min-width:960px) 60vw, 100vw")}</div><time>{E(d0)}</time><b>{E(t0)}</b>{f"<p>{E(ny[0][2])}</p>" if len(ny[0]) > 2 else ""}</a><div class="tn-lista">{sma}</div></div></div></section>'''
        ny = ""
        for rad in self.b["nyheter"]:
            d, t = rad[0], rad[1]
            ingress = f"<p>{E(rad[2])}</p>" if len(rad) > 2 else ""
            bild = self.bilder.ta(rad[3] if len(rad) > 3 else self.b.get("nyhet_tagg"))
            ny += (f'<a class="nyhet reveal" href="om-oss.html#press"><div class="foto">{self.bilder.img(bild, "220px")}</div><div><time>{E(d)}</time><b>{E(t)}</b>{ingress}</div></a>')
        return f'''<section class="sek {self.bg("nyheter")}" aria-labelledby="ny-h"><div class="wrap smal" style="max-width:1100px">
  <div class="sek-huvud"><h2 id="ny-h">{E(self.T("ny_rubrik_lista"))}</h2></div><div class="nyheter">{ny}</div>
  <div class="knappar">{self.knapp(self.T("ny_knapp"), "om-oss.html#press")}</div></div></section>'''

    def s_snabb(self):
        snabb = list(self.pr["snabb"])
        if snabb[-1][2] == "investerare" and not self.b.get("investerare", {}).get("kurs"):
            snabb[-1] = ("telefon", "Kontakta oss", "om-oss#kontakt")
        if self.blk("snabb", "rutor") == "band":
            a = "".join(f'<a href="{self.u(h)}"><span>{E(t)}</span>{PIL}</a>' for _, t, h in snabb)
            return f'<section class="snabb-band pa-accent" aria-label="Genvägar"><div class="wrap"><nav>{a}</nav></div></section>'
        a = "".join(f'<a href="{self.u(h)}"><div>{ikon(i)}<b>{E(t)}</b></div><span class="rundpil">{PIL}</span></a>' for i, t, h in snabb)
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
                 "nyheter": self.s_nyheter, "snabb": self.s_snabb, "process": self.s_process, "citat": self.s_citat, "service": self.s_service, "tidslinje": self.s_tidslinje, "kontor": self.s_kontor,
                 "priser": self.s_priser, "omdomen": self.s_omdomen, "faq": self.s_faq, "galleri": self.s_galleri, "boka": self.s_boka, "certifikat": self.s_certifikat, "logos": self.s_logos}
        ordning = p.get("ordning_lista") or self.ORDNING[p.get("ordning", "a")]
        main = self.hero() + "\n" + "\n".join(delar[d]() for d in ordning)
        har = True
        self.sida("index.html", f'{self.b["namn"]} – {self.b["slogan"]}', self.b["hero_text"], main, har_hero=har)

    # --- Nya block för små företag och nischer --------------------------------------------------------------------
    def s_priser(self, sida=False):
        pr = self.b.get("priser") or []
        kort = ""
        for x in pr:
            pkt = "".join(f"<li>{E(p)}</li>" for p in x.get("punkter", []))
            utv = x.get("utvald")
            kort += (f'<li class="pris-kort{" utvald" if utv else ""} reveal">{f"""<span class="pris-utvald">{E(self.T("priser_utvald"))}</span>""" if utv else ""}'
                     f'<h3>{E(x["namn"])}</h3><p class="pris-text">{E(x.get("text", ""))}</p><div class="pris-belopp"><b>{E(x["pris"])}</b><span>{E(x.get("enhet", ""))}</span></div>'
                     f'<ul class="pris-punkter">{pkt}</ul>{self.knapp(self.T("priser_knapp"), "om-oss.html#kontakt", "primar" if utv else "kontur")}</li>')
        extra = ""
        if sida and self.b.get("prislista"):
            rader = "".join(f'<tr><th scope="row">{E(a)}</th><td>{E(b_)}</td></tr>' for a, b_ in self.b["prislista"])
            extra = f'<div class="prislista-ram"><h3>{E(self.b.get("prislista_rubrik", "Fler priser"))}</h3><table class="prislista"><tbody>{rader}</tbody></table></div>'
        rubrik = self.b.get("priser_rubrik") or self.T("priser_rubrik")
        lank = "" if sida else self.textlank("Alla priser", "priser.html")
        return f'''<section class="sek {self.bg("priser")}" aria-labelledby="pris-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("priser_etikett"))}</span><h2 id="pris-h">{E(rubrik)}</h2></div>{lank}</div>
  <ul class="priser n{len(pr)}">{kort}</ul>{extra}<p class="pris-not mut">{E(self.b.get("priser_not") or self.T("priser_not"))}</p></div></section>'''

    def s_omdomen(self):
        om = self.b.get("omdomen") or []
        v = self.blk("omdomen", "kort")
        stj = "".join(ikon("stjarna", "stj") for _ in range(5))
        if v == "stor" and om:
            forsta = om[0]
            ovr = "".join(f'<li><blockquote><p>”{E(x["text"])}”</p></blockquote><span><b>{E(x["namn"])}</b> · {E(x.get("ort", ""))}</span></li>' for x in om[1:])
            return f'''<section class="sek {self.bg("omdomen")}" aria-labelledby="om-h"><div class="wrap om-stor">
  <div><span class="etikett">{E(self.T("omdomen_etikett"))}</span><h2 id="om-h">{E(self.T("omdomen_rubrik"))}</h2><div class="stjarnor" aria-label="5 av 5">{stj}</div></div>
  <figure class="om-forsta reveal"><blockquote><p>”{E(forsta["text"])}”</p></blockquote><figcaption><b>{E(forsta["namn"])}</b><span>{E(forsta.get("ort", ""))}</span></figcaption></figure>
  <ul class="om-ovr">{ovr}</ul></div></section>'''
        li = "".join(f'<li class="reveal"><div class="stjarnor" aria-label="5 av 5">{stj}</div><blockquote><p>”{E(x["text"])}”</p></blockquote><span><b>{E(x["namn"])}</b>{(" · " + E(x["ort"])) if x.get("ort") else ""}</span></li>' for x in om)
        return f'''<section class="sek {self.bg("omdomen")}" aria-labelledby="om-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("omdomen_etikett"))}</span><h2 id="om-h">{E(self.T("omdomen_rubrik"))}</h2></div></div><ul class="omdomen">{li}</ul></div></section>'''

    def s_faq(self, sida=False):
        fq = self.b.get("faq") or []
        rad = "".join(f'<details{" open" if i == 0 else ""}><summary><span class="t">{E(q)}</span><span class="plus" aria-hidden="true"></span></summary><div class="ex-text"><p>{E(a)}</p></div></details>' for i, (q, a) in enumerate(fq if sida else fq[:6]))
        lank = "" if sida or "faq" not in self.slugs else self.textlank("Alla frågor", "faq.html")
        return f'''<section class="sek {self.bg("faq")}" aria-labelledby="faq-h"><div class="wrap faq-grid"><div><span class="etikett">{E(self.T("faq_etikett"))}</span><h2 id="faq-h">{E(self.T("faq_rubrik"))}</h2>
  <p class="ingress" style="margin-top:18px">{E(self.b.get("faq_text", "Hittar du inte svaret? Ring eller mejla oss."))}</p><div class="knappar">{lank}</div></div><div class="vv-expertis faq">{rad}</div></div></section>'''

    def s_galleri(self):
        taggar = self.b.get("galleri_taggar") or [self.p.get("hero_tagg") or "people"]
        n = 7
        bilder = [self.bilder.ta(taggar[i % len(taggar)]) for i in range(n)]
        li = "".join(f'<li class="g{i} reveal">{self.bilder.img(x, "(min-width:960px) 33vw, 50vw")}</li>' for i, x in enumerate(bilder))
        return f'''<section class="sek {self.bg("galleri")}" aria-labelledby="ga-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("galleri_etikett"))}</span><h2 id="ga-h">{E(self.b.get("galleri_rubrik") or self.T("galleri_rubrik"))}</h2></div>{self.textlank(self.T("proj_lank"), "projekt.html")}</div>
  <ul class="galleri">{li}</ul><p class="figtext-rad mut">Illustrationsbilder</p></div></section>'''

    def s_boka(self):
        k = self.b["kontakt"]
        falt = self.T("boka_falt")
        typer = ["text", "tel", "email", "text"]
        inp = "".join(f'<label><span>{E(f)}</span><input type="{t}" name="f{i}" autocomplete="off"></label>' for i, (f, t) in enumerate(zip(falt[:3], typer)))
        inp += f'<label class="hel"><span>{E(falt[3])}</span><textarea name="f3" rows="3"></textarea></label>'
        return f'''<section class="sek {self.bg("boka") or "pa-ton"}" aria-labelledby="bo2-h" id="boka"><div class="wrap boka">
  <div><span class="etikett">{E(self.T("boka_etikett"))}</span><h2 id="bo2-h">{E(self.b.get("boka_rubrik") or self.T("boka_rubrik"))}</h2><p class="ingress" style="margin-top:18px">{E(self.b.get("boka_text") or self.T("boka_text"))}</p>
  <dl class="boka-info"><div><dt>Telefon</dt><dd><a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a></dd></div>{f'<div><dt>E-post</dt><dd><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></dd></div>' if k.get("epost") else ""}{f'<div><dt>Öppettider</dt><dd>{E(self.b["oppettider"])}</dd></div>' if self.b.get("oppettider") else ""}</dl></div>
  <form class="boka-form" onsubmit="event.preventDefault();this.querySelector('.boka-tack').hidden=false;this.reset();">{inp}<button class="knapp knapp-primar" type="submit"><span>{E(self.T("boka_knapp"))}</span>{PIL}</button><p class="boka-tack" hidden role="status">Tack! Det här är en exempelsajt – formuläret skickar inget.</p></form></div></section>'''

    def s_certifikat(self):
        c = self.b.get("certifikat") or []
        li = "".join(f'<li class="reveal">{ikon(x.get("ikon", "skold"))}<b>{E(x["titel"])}</b><span>{E(x.get("text", ""))}</span></li>' for x in c)
        return f'''<section class="sek sek-tat {self.bg("certifikat")}" aria-labelledby="ce-h"><div class="wrap">
  <div class="sek-huvud"><div><span class="etikett">{E(self.T("certifikat_etikett"))}</span><h2 id="ce-h">{E(self.b.get("certifikat_rubrik") or self.T("certifikat_rubrik"))}</h2></div></div><ul class="certifikat n{len(c)}">{li}</ul></div></section>'''

    def s_logos(self):
        ls = self.b.get("kunder") or []
        li = "".join(f'<li><span>{E(n)}</span></li>' for n in ls)
        return f'''<section class="sek sek-tat {self.bg("logos")}" aria-labelledby="lo-h"><div class="wrap">
  <div class="sek-huvud mitt"><span class="etikett">{E(self.T("logos_etikett"))}</span><h2 id="lo-h">{E(self.b.get("kunder_rubrik") or self.T("logos_rubrik"))}</h2></div><ul class="logos">{li}</ul></div></section>'''

    # --- Undersidor -----------------------------------------------------------------------------------------------
    def sidhero(self, titel, ingress, tagg, namn):
        bild = self.bilder.ta(tagg)
        return f'''<section class="sidhero" aria-labelledby="h1">{self.bilder.fyll(bild, lazy=False)}
  <div class="wrap"><nav class="brodsmula" aria-label="Brödsmulor"><a href="index.html">Start</a> / <span aria-current="page">{E(namn)}</span></nav><h1 id="h1">{E(titel)}</h1><p class="ingress">{E(ingress)}</p></div></section>'''

    def undersida(self, slug, namn, titel, ingress, tagg, innehall, beskr):
        self.sida(f"{slug}.html", f'{namn} | {self.b["namn"]}', beskr, self.sidhero(titel, ingress, tagg, namn) + innehall, aktiv=slug,
                  har_hero=False)

    def undersidor(self):
        for slug, namn, typ in self.sidor:
            getattr(self, "sida_" + typ.replace("-", "_"))(slug, namn)

    def sida_verksamhet(self, slug, namn):
        b = self.b
        block = ""
        for i, a in enumerate(b["affarsomraden"]):
            bild = self.bilder.ta(a["tagg"])
            ljus = " ljus" if i % 2 else ""
            block += (f'<section class="sek-tat" id="omr-{i}"><div class="wrap"><div class="panel{" omvand" if i % 2 else ""}{ljus} reveal">'
                      f'<div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>'
                      f'<div class="panel-text"><span class="etikett">{E(self.T("sida_verksamhet_etikett"))} {i + 1:02d}</span><h2>{E(a["titel"])}</h2><p>{E(a["text"])}</p>'
                      f'<p>{E(a.get("text2") or self.T("sida_verksamhet_text2", titel=a["titel"].lower()))}</p>'
                      f'<div class="knappar">{self.textlank(self.T("sida_verksamhet_lank"), "projekt.html")}</div></div></div></div></section>')
        extra = (self.s_process() if b.get("process") else "") + (self.s_certifikat() if b.get("certifikat") else "")
        self.undersida(slug, namn, b.get("sida_verksamhet_titel", namn), b["om"][1], b["affarsomraden"][0]["tagg"],
                       self.s_vagval() + block + extra + '<div style="height:clamp(40px,6vw,96px)"></div>', f'{namn} – {b["namn"]}.')

    def sida_bolag(self, slug, namn):
        b = self.b
        bl = bolagslista(b)
        rader = ""
        for i, x in enumerate(bl):
            bild = self.bilder.ta(x.get("tagg"))
            rader += (f'<section class="sek-tat" id="bolag-{i}"><div class="wrap"><div class="panel{" omvand" if i % 2 else ""}{" ljus" if i % 2 == 0 else ""} reveal">'
                      f'<div class="panel-bild">{self.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div>'
                      f'<div class="panel-text"><span class="etikett">{E(x.get("segment", ""))}</span><h2>{E(x["namn"])}</h2><p>{E(x.get("rubrik", ""))}</p><p>{E(x["text"])}</p>'
                      f'<div class="knappar">{self.textlank(self.T("sida_bolag_lank"), "#" if self.pr["topp"] == "koncern" else "om-oss.html#kontakt")}</div></div></div></div></section>')
        vagg = ""
        if b.get("lokala_bolag"):
            vagg = f'<section class="sek"><div class="wrap"><ul class="bo-vagg">{"".join(f"<li><a href=\'#\'><span>{E(n)}</span></a></li>" for n in b["lokala_bolag"])}</ul></div></section>'
        self.undersida(slug, namn, namn, self.T("sida_bolag_ingress", n=len(bl)), self.bt("sida_bolag"),
                       '<div style="height:clamp(24px,3vw,48px)"></div>' + rader + vagg + '<div style="height:clamp(40px,6vw,96px)"></div>', f'{namn} – {b["namn"]}.')

    def sida_projekt(self, slug, namn):
        b = self.b
        kort = ""
        for x in b["projekt"]:
            bild = self.bilder.ta(x["tagg"])
            kort += (f'<li class="kort reveal"><a href="#"><div class="foto"><span class="status">{E(x["ar"])}</span>{self.bilder.img(bild, "(min-width:1100px) 33vw, 100vw")}</div>'
                     f'<div class="kort-text"><span class="meta">{E(x["ort"])} · {E(x["typ"])}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p></div></a></li>')
        extra = (self.s_galleri() if b.get("galleri_taggar") else "") + (self.s_omdomen() if b.get("omdomen") else "")
        self.undersida(slug, namn, self.T("sida_projekt_titel"), self.T("sida_projekt_ingress"), b["projekt"][1]["tagg"],
                       f'<section class="sek"><div class="wrap"><ul class="kortlista tre">{kort}</ul></div></section>' + extra, f'{namn} – {b["namn"]}.')

    def sida_hallbarhet(self, slug, namn):
        b = self.b
        self.undersida(slug, namn, b["hallbarhet"]["rubrik"], b["hallbarhet"]["text"], self.bt("sida_hb"),
                       self.s_hb() + (self.s_certifikat() if b.get("certifikat") else "") + self.s_panel(True).replace(f'{self.T("panel_etikett")}</span>', f'{self.T("medarbetare")}</span>', 1),
                       f'{namn} – {b["namn"]}.')

    def sida_investerare(self, slug, namn):
        b = self.b
        inv = b["investerare"]
        rap = "".join(f'<li><a href="#"><span><span class="pdf">PDF</span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["rapporter"])
        kal = "".join(f'<li><a href="#"><span>{E(t)}</span><time>{E(d)}</time></a></li>' for t, d in inv["kalender"]) or '<li><a href="#"><span>Inga planerade händelser</span></a></li>'
        rad = "".join(f'<div class="siffra"><b>{E(n["varde"])}<small>{E(n["enhet"])}</small></b><span>{E(n["etikett"])}</span></div>' for n in b["nyckeltal"])
        self.undersida(slug, namn, namn, "Finansiell information, rapporter och kalender.", self.bt("sida_inv"),
                       f'''{self.s_ir()}<section class="sek pa-farg"><div class="wrap"><div class="siffror">{rad}</div></div></section>
<section class="sek" id="rapporter"><div class="wrap hb" style="align-items:start"><div><h2>Rapporter och presentationer</h2><ul class="rapporter" style="margin-top:24px">{rap}</ul></div><div><h2>Finansiell kalender</h2><ul class="rapporter" style="margin-top:24px">{kal}</ul></div></div></section>''',
                       f'Investerarinformation för {b["namn"]}.')

    def sida_priser(self, slug, namn):
        b = self.b
        self.undersida(slug, namn, b.get("sida_priser_titel", namn), self.T("sida_priser_ingress"), self.bt("sida_priser"),
                       self.s_priser(True) + (self.s_process() if b.get("process") else "") + (self.s_faq() if b.get("faq") else ""), f'{namn} – {b["namn"]}.')

    def sida_faq(self, slug, namn):
        b = self.b
        self.undersida(slug, namn, namn, self.T("sida_faq_ingress"), self.bt("sida_faq"), self.s_faq(True) + self.s_boka(), f'{namn} – {b["namn"]}.')

    def sida_karriar(self, slug, namn):
        b = self.b
        jobb = "".join(f'<li><a href="#"><b>{E(t)}</b><span>{E(o)} {PIL}</span></a></li>' for t, o in b["karriar"]["jobb"])
        self.undersida(slug, namn, b["karriar"]["rubrik"], b["karriar"]["text"], self.bt("sida_karriar"),
                       f'''<section class="sek" id="jobb"><div class="wrap hb" style="align-items:start"><div><span class="etikett">{E(self.T("sida_karriar_etikett"))}</span><h2>{E(self.T("sida_karriar_rubrik"))}</h2><p class="ingress" style="margin-top:18px">{E(self.T("sida_karriar_text"))}</p></div><ul class="jobb">{jobb}</ul></div></section>
{self.s_panel(False)}{self.s_snabb()}''', f'{namn} – {b["namn"]}.')

    def sida_om_oss(self, slug, namn):
        b = self.b
        k = b["kontakt"]
        tl = self.s_tidslinje() if b.get("tidslinje") else ""
        ko = self.s_kontor() if b.get("kontor_lista") else ""
        boka = self.s_boka() if self.pr["topp"] != "koncern" else ""
        self.undersida(slug, namn, self.T("sida_om_titel"), b["om"][0], self.bt("sida_om"), f'''<section class="sek"><div class="wrap hb"><div class="prosa"><span class="etikett">{E(self.T("sida_om_etikett"))}</span><h2>{E(b["slogan"])}</h2><p class="ingress" style="margin-top:20px">{E(b["om"][0])}</p><p class="mut">{E(b["om"][1])}</p></div><div class="hb-bild">{self.bilder.fyll(self.bilder.ta(self.bt("om")), "(min-width:960px) 50vw, 100vw", note=True)}</div></div></section>
{self.s_siffror()}{tl}{ko}<div id="press">{self.s_nyheter()}</div>{boka}
<section class="sek pa-ton" id="kontakt"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">Kontakt</span><h2>{E(self.T("sida_kontakt_rubrik"))}</h2></div></div>
<dl class="kontaktinfo"><div><dt>{E(self.T("fot_adress"))}</dt><dd>{E(k["adress"])}<br>{E(k["postnr"])} {E(k["ort"])}</dd></div><div><dt>Telefon</dt><dd><a href="tel:{tel(k["telefon"])}">{E(k["telefon"])}</a></dd></div>{f'<div><dt>E-post</dt><dd><a href="mailto:{k["epost"]}">{E(k["epost"])}</a></dd></div>' if k.get("epost") else ""}{f'<div><dt>Öppettider</dt><dd>{E(b["oppettider"])}</dd></div>' if b.get("oppettider") else ""}</dl></div></section>''',
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
        self.bilder = Bilder(self.p.get("fro", self.b["slug"]), self.ut, self.p.get("bildtyngd", []), self.delad, self.p.get("bildreserv"))
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
