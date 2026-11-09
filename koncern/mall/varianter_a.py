"""Sektionsvarianter, omgång A: vägval, bolag och nyckeltal.

Varje variant har ett eget klassprefix i varianter_a.css:
  vagval/kakel .vk-   vagval/rullband .vrb-   vagval/typo .vty-   vagval/kort .vko-   vagval/duo .vdu-
  bolag/karusell .bka-   bolag/zigzag .bzz-   bolag/mosaik .bmo-   bolag/namnlista .bnl-
  siffror/cirklar .sci-   siffror/kort .sko-   siffror/vertikal .sve-   siffror/bild .sbi-
"""
from varianter import variant, E, ikon, PIL


# --- Gemensamt ---------------------------------------------------------------------------------------------------------
def _fraga(s):
    return s.b.get("vagval_rubrik") or s.T("vagval_rubrik")


def _href(x):
    return x.get("href", "verksamhet.html")


def _bolag_rubrik(s):
    return s.b.get("bolag_rubrik") or s.T("bolag_rubrik")


def _bolag_knapp(s, typ="kontur"):
    mal = "om-oss.html" if s.pr is not None and "verksamhet" not in s.slugs else "verksamhet.html"
    return s.knapp(s.T("bolag_knapp"), mal, typ)


def _tal(n, cls=""):
    enhet = f'<small>{E(n["enhet"])}</small>' if n.get("enhet") else ""
    return f'<b class="{cls}">{E(n["varde"])}{enhet}</b>'


def _nyckeltal_lank(s):
    return s.textlank(s.T("nyckeltal_lank"), "investerare.html" if "investerare" in s.slugs else "om-oss.html")


# --- Vägval ------------------------------------------------------------------------------------------------------------
def _kakel_storlekar(n):
    """Storlekar som fyller ett fyrkolumnsrutnät utan hål: först ett block om 2x2 + 1x2 + 1 + 1, sedan resten."""
    if n <= 0:
        return []
    forsta = ["s22", "s12", "s11", "s11"][:n]
    m = n - len(forsta)
    rest = []
    while m >= 4:
        rest += ["s12", "s21", "s12", "s21"]
        m -= 4
    rest += {3: ["s21", "s11", "s11"], 2: ["s21", "s21"], 1: ["s41"], 0: []}[m]
    if n == 3:
        forsta = ["s22", "s12", "s12"]
    if n == 2:
        forsta = ["s22", "s22"]
    return forsta + rest


@variant("vagval", "kakel")
def vagval_kakel(s):
    t = s.tjanster()
    farg = ["vk-p", "vk-m", "vk-t"]
    kakel = ""
    for i, (x, st) in enumerate(zip(t, _kakel_storlekar(len(t)))):
        text = x.get("text") or s.T("expertis_text", titel=x["titel"].lower())
        kakel += (f'<li class="vk-{st} {farg[i % 3]}"><a href="{_href(x)}"><span class="vk-topp">{ikon(x.get("ikon", "kugge"), "ik vk-ik")}'
                  f'<span class="vk-pil">{PIL}</span></span><span class="vk-text"><span class="vk-t">{E(x["titel"])}</span>'
                  f'<span class="vk-rad">{E(text)}</span></span></a></li>')
    return (f'<section class="va sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", s.textlank(s.T("fot_lank"), "verksamhet.html"))}'
            f'<ul class="vk-kakel">{kakel}</ul></div></section>')


@variant("vagval", "rullband")
def vagval_rullband(s):
    t = s.tjanster()
    n = max(1, len(t))
    upprepa = max(1, -(-8 // n))  # minst åtta ord per varv så att bandet alltid är bredare än skärmen

    def band(lista, synlig):
        ord_ = ""
        for x in lista * upprepa:
            attr = "" if synlig else ' tabindex="-1"'
            ord_ += (f'<li><a href="{_href(x)}"{attr}><span>{E(x["titel"])}</span></a>'
                     f'<span class="vrb-sep">{ikon(x.get("ikon", "kugge"), "ik")}</span></li>')
        return ord_

    rad1 = f'<ul class="vrb-varv">{band(t, True)}</ul><ul class="vrb-varv vrb-kopia" aria-hidden="true">{band(t, False)}</ul>'
    omv = list(reversed(t))
    rad2 = f'<ul class="vrb-varv">{band(omv, False)}</ul><ul class="vrb-varv vrb-kopia">{band(omv, False)}</ul>'
    return (f'<section class="va sek vrb {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", mitt=True)}</div>'
            f'<nav class="vrb-band" aria-label="{E(_fraga(s))}"><div class="vrb-spar vrb-v">{rad1}</div>'
            f'<div class="vrb-spar vrb-h" aria-hidden="true">{rad2}</div></nav>'
            f'<div class="wrap vrb-fot"><span class="vrb-antal">{len(t):02d}</span>{s.knapp(s.T("fot_lank"), "verksamhet.html", "kontur")}</div></section>')


@variant("vagval", "typo")
def vagval_typo(s):
    t = s.tjanster()
    rad = ""
    for i, x in enumerate(t):
        rad += (f'<li><a href="{_href(x)}"><span class="vty-ik">{ikon(x.get("ikon", "kugge"), "ik")}</span>'
                f'<span class="vty-t">{E(x["titel"])}<sup>{i + 1:02d}</sup></span>'
                f'<span class="vty-text">{E(x.get("text", ""))}</span><span class="vty-pil">{PIL}</span></a></li>')
    return (f'<section class="va sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", s.textlank(s.T("fot_lank"), "verksamhet.html"))}'
            f'<ul class="vty-lista">{rad}</ul></div></section>')


@variant("vagval", "kort")
def vagval_kort(s):
    t = s.tjanster()
    kort = ""
    for x in t:
        text = x.get("text") or s.T("expertis_text", titel=x["titel"].lower())
        kort += (f'<li class="reveal"><a href="{_href(x)}"><span class="vko-cirkel">{ikon(x.get("ikon", "kugge"), "ik")}</span>'
                 f'<h3>{E(x["titel"])}</h3><p>{E(text)}</p><span class="vko-mer"><span>{E(s.T("las_mer"))}</span>{PIL}</span></a></li>')
    return (f'<section class="va sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", mitt=True)}'
            f'<ul class="vko-grid{" vko-n" + str(len(t)) if len(t) in (3, 5, 6, 7) else ""}">{kort}</ul></div></section>')


@variant("vagval", "duo")
def vagval_duo(s):
    t = s.tjanster()
    ingress = s.b.get("vagval_text") or s.b.get("slogan") or ""
    rad = ""
    for i, x in enumerate(t):
        text = x.get("text") or s.T("expertis_text", titel=x["titel"].lower())
        rad += (f'<li><a href="{_href(x)}"><span class="vdu-nr">{i + 1:02d}</span><h3>{E(x["titel"])}</h3>'
                f'<p>{E(text)}</p><span class="vdu-pil">{PIL}</span></a></li>')
    return (f'<section class="va sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap vdu">'
            f'<div class="vdu-vanster"><div class="vdu-sticky"><span class="etikett">{E(s.T("vagval_etikett"))}</span><h2 id="vv-h">{E(_fraga(s))}</h2>'
            f'<p class="ingress">{E(ingress)}</p><div class="knappar">{s.knapp(s.T("fot_lank"), "verksamhet.html")}</div></div></div>'
            f'<ol class="vdu-lista">{rad}</ol></div></section>')


# --- Bolag -------------------------------------------------------------------------------------------------------------
@variant("bolag", "karusell")
def bolag_karusell(s):
    bl = s.bolagslista()
    kort = ""
    for i, x in enumerate(bl):
        bild = s.bilder.ta(x.get("tagg"))
        kort += (f'<li><a href="bolag.html#bolag-{i}"><div class="bka-bild">{s.bilder.img(bild, "(min-width:1100px) 40vw, 85vw")}'
                 f'<span class="bka-nr">{i + 1:02d} / {len(bl):02d}</span></div><div class="bka-text"><span class="bka-seg">{E(x.get("segment", ""))}</span>'
                 f'<h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p><span class="textlank"><span>{E(s.T("bolag_till", namn=x["namn"]))}</span>{PIL}</span></div></a></li>')
    return (f'<section class="va sek bka {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'{s.huvud(s.T("bolag_etikett"), _bolag_rubrik(s), "bo-h", _bolag_knapp(s))}</div>'
            f'<ul class="bka-spar" tabindex="0" aria-label="{E(_bolag_rubrik(s))}">{kort}</ul>'
            f'<div class="wrap"><div class="bka-hint" aria-hidden="true"><span class="bka-linje"></span><span>{len(bl):02d}</span></div></div></section>')


@variant("bolag", "zigzag")
def bolag_zigzag(s):
    bl = s.bolagslista()
    rad = ""
    for i, x in enumerate(bl):
        bild = s.bilder.ta(x.get("tagg"))
        rubrik = x.get("rubrik")
        rad += (f'<li><div class="bzz-bild">{s.bilder.img(bild, "(min-width:960px) 55vw, 100vw", lazy=False).replace("fetchpriority=high ", "")}</div>'
                f'<div class="bzz-text reveal"><span class="bzz-nr">{i + 1:02d}</span><span class="bzz-seg">{E(x.get("segment", ""))}</span>'
                f'<h3>{E(x["namn"])}</h3>{f"<p class=bzz-rubrik>{E(rubrik)}</p>" if rubrik else ""}<p>{E(x["text"])}</p>'
                f'{s.textlank(s.T("bolag_till", namn=x["namn"]), f"bolag.html#bolag-{i}")}</div></li>')
    return (f'<section class="va sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'{s.huvud(s.T("bolag_etikett"), _bolag_rubrik(s), "bo-h", _bolag_knapp(s))}'
            f'<ul class="bzz">{rad}</ul></div></section>')


@variant("bolag", "mosaik")
def bolag_mosaik(s):
    bl = s.bolagslista()
    ruta = ""
    for i, x in enumerate(bl):
        bild = s.bilder.ta(x.get("tagg"))
        stor = i == 0
        text = f'<p>{E(x["text"])}</p>' if stor else ""
        rubrik = x.get("rubrik") or x.get("segment", "")
        ruta += (f'<li class="{"bmo-stor" if stor else "bmo-liten"}"><a href="bolag.html#bolag-{i}">'
                 f'{s.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw" if stor else "(min-width:960px) 25vw, 100vw")}'
                 f'<div class="bmo-text"><span class="bmo-seg">{E(x.get("segment", ""))}</span><h3>{E(x["namn"])}</h3>'
                 f'{f"<span class=bmo-rubrik>{E(rubrik)}</span>" if stor and rubrik else ""}{text}</div><span class="rundpil">{PIL}</span></a></li>')
    return (f'<section class="va sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'{s.huvud(s.T("bolag_etikett"), _bolag_rubrik(s), "bo-h", _bolag_knapp(s))}'
            f'<ul class="bmo bmo-n{min(len(bl), 5)}">{ruta}</ul></div></section>')


@variant("bolag", "namnlista")
def bolag_namnlista(s):
    bl = s.bolagslista()
    rad = ""
    for i, x in enumerate(bl):
        rad += (f'<li><a href="bolag.html#bolag-{i}"><span class="bnl-nr">{i + 1:02d}</span><span class="bnl-namn">{E(x["namn"])}</span>'
                f'<span class="bnl-meta"><b>{E(x.get("segment", ""))}</b><span>{E(x["text"])}</span></span>'
                f'<span class="rundpil">{PIL}</span></a></li>')
    return (f'<section class="va sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'<div class="bnl-huvud"><span class="etikett">{E(s.T("bolag_etikett"))}</span><h2 id="bo-h">{E(_bolag_rubrik(s))}</h2>{_bolag_knapp(s)}</div>'
            f'<ul class="bnl">{rad}</ul></div></section>')


# --- Siffror -----------------------------------------------------------------------------------------------------------
@variant("siffror", "cirklar")
def siffror_cirklar(s):
    b = s.b
    nt = b["nyckeltal"]
    rubrik = b.get("intro_rubrik", b["slogan"])
    ringar = ""
    for i, n in enumerate(nt):
        vinkel = (35 + i * 83) % 360
        ringar += (f'<li class="reveal"><div class="sci-ring" style="--sci-v:{vinkel}deg"><span class="sci-prick" aria-hidden="true"></span>'
                   f'{_tal(n, "sci-tal")}</div><span class="sci-et">{E(n["etikett"])}</span></li>')
    return (f'<section class="va sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">'
            f'<div class="sek-huvud mitt"><div><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(rubrik)}</h2>'
            f'<p class="ingress sci-ingress">{E(b["om"][0])}</p></div></div>'
            f'<ul class="sci sci-n{len(nt)}">{ringar}</ul></div></section>')


@variant("siffror", "kort")
def siffror_kort(s):
    b = s.b
    nt = b["nyckeltal"]
    rubrik = b.get("intro_rubrik", b["slogan"])
    kort = "".join(f'<li class="reveal"><span class="sko-nr">{i + 1:02d}</span>{_tal(n, "sko-tal")}<span class="sko-et">{E(n["etikett"])}</span></li>'
                   for i, n in enumerate(nt))
    return (f'<section class="va sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap sko">'
            f'<div class="sko-huvud"><span class="etikett">{E(s.T("nyckeltal_etikett"))}</span><h2 id="si-h">{E(rubrik)}</h2>'
            f'<p class="mut">{E(b["om"][0])}</p><div class="knappar">{_nyckeltal_lank(s)}</div></div>'
            f'<ul class="sko-grid sko-n{len(nt)}">{kort}</ul></div></section>')


@variant("siffror", "vertikal")
def siffror_vertikal(s):
    b = s.b
    nt = b["nyckeltal"]
    rubrik = b.get("intro_rubrik", b["slogan"])
    rad = ""
    for i, n in enumerate(nt):
        mening = n.get("text") or ""
        rad += (f'<li class="reveal">{_tal(n, "sve-tal")}<div class="sve-text"><span class="sve-nr">{i + 1:02d} / {len(nt):02d}</span><h3>{E(n["etikett"])}</h3>'
                f'{f"<p>{E(mening)}</p>" if mening else ""}</div></li>')
    return (f'<section class="va sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">'
            f'<div class="sve-huvud"><div><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(rubrik)}</h2></div>'
            f'<p class="ingress">{E(b["om"][0])}</p></div><ul class="sve">{rad}</ul></div></section>')


@variant("siffror", "bild")
def siffror_bild(s):
    b = s.b
    nt = b["nyckeltal"]
    rubrik = b.get("intro_rubrik", b["slogan"])
    bild = s.bilder.ta()
    tal = "".join(f'<li>{_tal(n, "sbi-tal")}<span class="sbi-et">{E(n["etikett"])}</span></li>' for n in nt)
    return (f'<section class="va sbi" aria-labelledby="si-h">{s.bilder.fyll(bild, note=True)}<div class="wrap sbi-inre">'
            f'<div class="sbi-huvud"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(rubrik)}</h2></div>'
            f'<ul class="sbi-rad sbi-n{len(nt)}">{tal}</ul></div></section>')
