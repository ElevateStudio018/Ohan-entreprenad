"""Sektionsvarianter, omgång E: vägval, bolag och nyckeltal.

Alla klasser börjar på "e" (sektionerna får dessutom klassen .ev). Prefix per variant i varianter_e.css:
  vagval/e-vitrin .evi-   vagval/e-tidning .eti-   vagval/e-mening .eme-   vagval/e-snapp .esn-   vagval/e-panel .epa-
  vagval/e-lameller .ela-
  bolag/e-stapel .est-   bolag/e-org .eor-   bolag/e-dragspel .edr-   bolag/e-kolumner .eko-   bolag/e-forskjuten .efo-
  siffror/e-staplar .esp-   siffror/e-faktaruta .efa-   siffror/e-trappa .etr-   siffror/e-text .ete-   siffror/e-split .esl-
"""
from varianter import variant, E, ikon, PIL


# --- Gemensamt ---------------------------------------------------------------------------------------------------------
def _fraga(s):
    return s.b.get("vagval_rubrik") or s.T("vagval_rubrik")


def _href(x):
    return x.get("href", "verksamhet.html")


def _ik(x, cls="ik"):
    return ikon(x.get("ikon", "kugge"), cls)


def _ttext(s, x):
    return x.get("text") or s.T("expertis_text", titel=x["titel"].lower())


def _bolag_rubrik(s):
    return s.b.get("bolag_rubrik") or s.T("bolag_rubrik")


def _bolag_mal(s):
    return "om-oss.html" if s.pr is not None and "verksamhet" not in s.slugs else "verksamhet.html"


def _bolag_knapp(s, typ="kontur"):
    return s.knapp(s.T("bolag_knapp"), _bolag_mal(s), typ)


def _bolag_huvud(s):
    return s.huvud(s.T("bolag_etikett"), _bolag_rubrik(s), "bo-h", _bolag_knapp(s))


def _si_rubrik(s):
    return s.b.get("intro_rubrik", s.b["slogan"])


def _si_om(s):
    om = s.b.get("om") or [""]
    return om[0] if om else ""


def _tal(n, cls=""):
    enhet = f'<small>{E(n["enhet"])}</small>' if n.get("enhet") else ""
    return f'<b class="{cls}">{E(n["varde"])}{enhet}</b>'


def _nyckeltal_lank(s):
    return s.textlank(s.T("nyckeltal_lank"), "investerare.html" if "investerare" in s.slugs else "om-oss.html")


def _bild(s, tagg, sizes):
    return s.bilder.img(s.bilder.ta(tagg), sizes)


# --- Vägval ------------------------------------------------------------------------------------------------------------
@variant("vagval", "e-vitrin")
def vagval_vitrin(s):
    """Lista med stora titlar till vänster, en scen till höger där bilden och texten byts när man pekar på en rad."""
    t = s.tjanster()
    n = len(t)
    rad = ""
    for i, x in enumerate(t):
        bild = s.bilder.ta(x.get("tagg"))
        rad += (f'<li><a class="evi-rad" href="{_href(x)}"><span class="evi-nr">{i + 1:02d}</span><span class="evi-t">{E(x["titel"])}</span>'
                f'<span class="evi-pil">{PIL}</span></a>'
                f'<figure class="evi-scen">{s.bilder.img(bild, "(min-width:1000px) 55vw, 100vw")}'
                f'<figcaption>{_ik(x, "ik evi-ik")}<span class="evi-st">{E(x["titel"])}</span><span class="evi-text">{E(_ttext(s, x))}</span></figcaption></figure></li>')
    return (f'<section class="ev sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", s.textlank(s.T("fot_lank"), "verksamhet.html"))}'
            f'<ul class="evi" style="--n:{n}">{rad}</ul></div></section>')


@variant("vagval", "e-tidning")
def vagval_tidning(s):
    """Tidningsuppslag: dubbel linje och rubrikhuvud, en ledare över två spalter och resten i spalter med spaltlinjer."""
    t = s.tjanster()
    if not t:
        return ""
    lead, rest = t[0], t[1:]
    r = len(rest)
    if r >= 4:
        lead_cls, sp = "eti-lead eti-l22", [1] * r
        k = (r - 4) % 4
        if k:
            sp[-1] = 4 - k + 1
    else:
        lead_cls, sp = f"eti-lead eti-l{4 - r}1", [1] * r
    bild = s.bilder.ta(lead.get("tagg"))
    celler = (f'<li class="{lead_cls}"><a href="{_href(lead)}"><span class="eti-kicker">{_ik(lead, "ik")}<span>01</span></span>'
              f'<h3>{E(lead["titel"])}</h3><p class="eti-ingress">{E(_ttext(s, lead))}</p>'
              f'<span class="eti-foto">{s.bilder.img(bild, "(min-width:1100px) 45vw, 100vw")}</span>'
              f'<span class="textlank"><span>{E(s.T("las_mer"))}</span>{PIL}</span></a></li>')
    for i, (x, spn) in enumerate(zip(rest, sp)):
        start = " eti-r0" if r >= 4 and i >= 4 and (i - 4) % 4 == 0 else ""
        celler += (f'<li class="eti-cell{start}" style="--sp:{spn}"><a href="{_href(x)}"><span class="eti-kicker">{_ik(x, "ik")}<span>{i + 2:02d}</span></span>'
                   f'<h3>{E(x["titel"])}</h3><p>{E(_ttext(s, x))}</p><span class="eti-pil">{PIL}</span></a></li>')
    return (f'<section class="ev sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'<header class="eti-mast"><div class="eti-mast-rad"><span>{E(s.T("vagval_etikett"))}</span><span>{E(s.b.get("kortnamn", ""))} · {len(t):02d}</span></div>'
            f'<h2 id="vv-h">{E(_fraga(s))}</h2></header>'
            f'<div class="eti-ram"><ul class="eti">{celler}</ul></div></div></section>')


@variant("vagval", "e-mening")
def vagval_mening(s):
    """Centrerad ordbild: alla tjänster som en löpande mening i stor stil, med ikoner och nummer inbäddade."""
    t = s.tjanster()
    ord_ = ""
    for i, x in enumerate(t):
        sep = '<span class="eme-sep" aria-hidden="true">/</span>' if i < len(t) - 1 else ""
        ord_ += (f'<li><a href="{_href(x)}"><span class="eme-ik">{_ik(x, "ik")}</span><span class="eme-t">{E(x["titel"])}</span>'
                 f'<sup>{i + 1:02d}</sup></a>{sep}</li>')
    return (f'<section class="ev sek eme {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'<div class="eme-topp"><span class="etikett">{E(s.T("vagval_etikett"))}</span><h2 id="vv-h">{E(_fraga(s))}</h2></div>'
            f'<ul class="eme-ord">{ord_}</ul>'
            f'<div class="eme-fot">{s.knapp(s.T("fot_lank"), "verksamhet.html", "kontur")}</div></div></section>')


@variant("vagval", "e-snapp")
def vagval_snapp(s):
    """Horisontell rad med höga kort i tre färger som snäpper på plats; huvudet ligger i en spalt till vänster på dator."""
    t = s.tjanster()
    kort = ""
    for i, x in enumerate(t):
        kort += (f'<li class="esn-f{i % 3}"><a href="{_href(x)}"><span class="esn-topp">{_ik(x, "ik esn-ik")}<span class="esn-nr">{i + 1:02d}</span></span>'
                 f'<span class="esn-text"><h3>{E(x["titel"])}</h3><p>{E(_ttext(s, x))}</p></span>'
                 f'<span class="esn-mer"><span>{E(s.T("las_mer"))}</span>{PIL}</span></a></li>')
    return (f'<section class="ev sek esn {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap esn-huvud">'
            f'<div><span class="etikett">{E(s.T("vagval_etikett"))}</span><h2 id="vv-h">{E(_fraga(s))}</h2></div>'
            f'<div class="esn-info"><span class="esn-antal">{len(t):02d}</span><span class="esn-linje" aria-hidden="true"></span>{s.textlank(s.T("fot_lank"), "verksamhet.html")}</div></div>'
            f'<ul class="esn-spar" tabindex="0" aria-label="{E(_fraga(s))}">{kort}</ul></section>')


@variant("vagval", "e-panel")
def vagval_panel(s):
    """Färgat band med rubrik och ingress; under det en ljus tavla med rutnät av tjänster som överlappar bandet."""
    t = s.tjanster()
    ingress = s.b.get("vagval_text") or s.b.get("slogan") or ""
    celler = ""
    for i, x in enumerate(t):
        celler += (f'<li><a href="{_href(x)}"><span class="epa-rad1">{_ik(x, "ik epa-ik")}<span class="epa-nr">{i + 1:02d}</span></span>'
                   f'<h3>{E(x["titel"])}</h3><p>{E(_ttext(s, x))}</p><span class="epa-pil">{PIL}</span></a></li>')
    return (f'<section class="ev sek epa {s.bg("vagval")}" aria-labelledby="vv-h"><div class="epa-band" aria-hidden="true"></div><div class="wrap">'
            f'<div class="epa-huvud"><div><span class="etikett">{E(s.T("vagval_etikett"))}</span><h2 id="vv-h">{E(_fraga(s))}</h2></div>'
            f'<div class="epa-ingress"><p>{E(ingress)}</p>{s.textlank(s.T("fot_lank"), "verksamhet.html")}</div></div>'
            f'<ul class="epa-tavla epa-n{len(t)}">{celler}</ul></div></section>')


@variant("vagval", "e-lameller")
def vagval_lameller(s):
    """Horisontellt dragspel: smala lameller med stående titlar som vidgas när man pekar; den första är öppen."""
    t = s.tjanster()
    rad = ""
    for i, x in enumerate(t):
        rad += (f'<li><a href="{_href(x)}"><span class="ela-topp"><span class="ela-nr">{i + 1:02d}</span>{_ik(x, "ik ela-ik")}</span>'
                f'<span class="ela-lod" aria-hidden="true">{E(x["titel"])}</span>'
                f'<span class="ela-inne"><h3>{E(x["titel"])}</h3><p>{E(_ttext(s, x))}</p><span class="ela-mer"><span>{E(s.T("las_mer"))}</span>{PIL}</span></span></a></li>')
    return (f'<section class="ev sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">'
            f'{s.huvud(s.T("vagval_etikett"), _fraga(s), "vv-h", s.textlank(s.T("fot_lank"), "verksamhet.html"))}'
            f'<ul class="ela">{rad}</ul></div></section>')


# --- Bolag -------------------------------------------------------------------------------------------------------------
@variant("bolag", "e-stapel")
def bolag_stapel(s):
    """Kort som staplas på varandra när man skrollar (position: sticky), med bild och text kant i kant."""
    bl = s.bolagslista()
    kort = ""
    for i, x in enumerate(bl):
        rubrik = x.get("rubrik") or ""
        kort += (f'<li style="--i:{i}"><article class="est-kort"><div class="est-bild">{_bild(s, x.get("tagg"), "(min-width:960px) 50vw, 100vw")}</div>'
                 f'<div class="est-text"><div class="est-rad"><span class="est-seg">{E(x.get("segment", ""))}</span><span class="est-nr">/ {len(bl):02d}</span></div>'
                 f'<h3>{E(x["namn"])}</h3>{f"<p class=est-rubrik>{E(rubrik)}</p>" if rubrik else ""}<p>{E(x["text"])}</p>'
                 f'<div class="est-fot">{s.textlank(s.T("bolag_till", namn=x["namn"]), f"bolag.html#bolag-{i}")}<span class="est-stor" aria-hidden="true">{i + 1:02d}</span></div></div></article></li>')
    return (f'<section class="ev sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">{_bolag_huvud(s)}'
            f'<ul class="est">{kort}</ul></div></section>')


@variant("bolag", "e-org")
def bolag_org(s):
    """Organisationsschema: moderbolaget överst och linjer som grenar ut till varje bolag."""
    bl = s.bolagslista()
    noder = ""
    for i, x in enumerate(bl):
        noder += (f'<li><a href="bolag.html#bolag-{i}"><span class="eor-seg">{E(x.get("segment", ""))}</span><h3>{E(x["namn"])}</h3>'
                  f'<p>{E(x["text"])}</p><span class="eor-fot"><span class="eor-nr">{i + 1:02d}</span><span class="rundpil">{PIL}</span></span></a></li>')
    namn = s.b.get("namn") or s.b.get("kortnamn", "")
    return (f'<section class="ev sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'{s.huvud(s.T("bolag_etikett"), _bolag_rubrik(s), "bo-h", mitt=True)}'
            f'<div class="eor"><div class="eor-topp"><span class="eor-topp-et">{E(s.T("bolag_etikett"))}</span><b>{E(namn)}</b></div>'
            f'<ul class="eor-gren" style="--n:{max(1, len(bl))}">{noder}</ul></div>'
            f'<div class="eor-knapp">{_bolag_knapp(s)}</div></div></section>')


@variant("bolag", "e-dragspel")
def bolag_dragspel(s):
    """Dragspel med stora bolagsnamn; den öppna raden visar bild, rubrik och text sida vid sida. Första raden är öppen."""
    bl = s.bolagslista()
    rad = ""
    for i, x in enumerate(bl):
        rubrik = x.get("rubrik") or x.get("segment", "")
        rad += (f'<details class="edr-rad"{" open" if i == 0 else ""}><summary><span class="edr-nr">{i + 1:02d}</span><span class="edr-namn">{E(x["namn"])}</span>'
                f'<span class="edr-seg">{E(x.get("segment", ""))}</span><span class="edr-plus" aria-hidden="true"></span></summary>'
                f'<div class="edr-inne"><div class="edr-bild">{_bild(s, x.get("tagg"), "(min-width:960px) 40vw, 100vw")}</div>'
                f'<div class="edr-text"><h3>{E(rubrik)}</h3><p>{E(x["text"])}</p>{s.textlank(s.T("bolag_till", namn=x["namn"]), f"bolag.html#bolag-{i}")}</div></div></details>')
    return (f'<section class="ev sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap edr-wrap">'
            f'<div class="edr-sida"><span class="etikett">{E(s.T("bolag_etikett"))}</span><h2 id="bo-h">{E(_bolag_rubrik(s))}</h2>'
            f'<span class="edr-antal" aria-hidden="true">{len(bl):02d}</span><div class="knappar">{_bolag_knapp(s)}</div></div>'
            f'<div class="edr">{rad}</div></div></section>')


@variant("bolag", "e-kolumner")
def bolag_kolumner(s):
    """Likvärdiga spalter med spaltlinjer: stort konturnummer, namn och text överst och en hög bild som avslutar varje spalt."""
    bl = s.bolagslista()
    kol = ""
    for i, x in enumerate(bl):
        kol += (f'<li><a href="bolag.html#bolag-{i}"><span class="eko-nr" aria-hidden="true">{i + 1:02d}</span>'
                f'<span class="eko-seg">{E(x.get("segment", ""))}</span><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p>'
                f'<span class="eko-bild">{_bild(s, x.get("tagg"), "(min-width:1000px) 25vw, 100vw")}<span class="eko-pil">{PIL}</span></span></a></li>')
    return (f'<section class="ev sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">{_bolag_huvud(s)}'
            f'<ul class="eko eko-n{len(bl)}">{kol}</ul></div></section>')


@variant("bolag", "e-forskjuten")
def bolag_forskjuten(s):
    """Två förskjutna spalter: bilder med en textruta som överlappar bildens nederkant, varannan spalt nedflyttad."""
    bl = s.bolagslista()
    kort = ""
    for i, x in enumerate(bl):
        rubrik = x.get("rubrik") or ""
        kort += (f'<li><a href="bolag.html#bolag-{i}"><span class="efo-bild">{_bild(s, x.get("tagg"), "(min-width:900px) 45vw, 100vw")}</span>'
                 f'<span class="efo-ruta"><span class="efo-seg">{i + 1:02d} · {E(x.get("segment", ""))}</span><h3>{E(x["namn"])}</h3>'
                 f'{f"<span class=efo-rubrik>{E(rubrik)}</span>" if rubrik else ""}<span class="efo-txt">{E(x["text"])}</span>'
                 f'<span class="textlank"><span>{E(s.T("bolag_till", namn=x["namn"]))}</span>{PIL}</span></span></a></li>')
    return (f'<section class="ev sek {s.bg("bolag")}" aria-labelledby="bo-h"><div class="wrap">'
            f'<ul class="efo"><li class="efo-huvud"><span class="etikett">{E(s.T("bolag_etikett"))}</span><h2 id="bo-h">{E(_bolag_rubrik(s))}</h2>'
            f'<p class="mut">{E(s.T("vagg_text"))}</p><div class="knappar">{_bolag_knapp(s)}</div></li>{kort}</ul></div></section>')


# --- Siffror -----------------------------------------------------------------------------------------------------------
@variant("siffror", "e-staplar")
def siffror_staplar(s):
    """Tabellrader i full bredd: stort tal, etikett och ett stapeldiagram i ren CSS av utvecklingen (om briefen har trend)."""
    nt = s.b["nyckeltal"]
    rad = ""
    for i, n in enumerate(nt):
        trend = [v for v in (n.get("trend") or []) if isinstance(v, (int, float))]
        diagram = ""
        if len(trend) > 1:
            hi = max(trend) or 1
            lo = min(trend) - (hi - min(trend)) * 0.7 if hi != min(trend) else 0
            staplar = "".join(f'<i style="--h:{max(6, round(100 * (v - lo) / ((hi - lo) or 1)))}%"></i>' for v in trend)
            diagram = (f'<div class="esp-diagram" aria-hidden="true">{staplar}</div>'
                       f'<span class="esp-not">{E(n.get("trend_text", ""))}</span>')
        rad += (f'<li class="{"esp-med" if diagram else "esp-utan"}"><span class="esp-nr">{i + 1:02d}</span>{_tal(n, "esp-tal")}'
                f'<span class="esp-et">{E(n["etikett"])}</span><div class="esp-graf">{diagram}</div></li>')
    return (f'<section class="ev sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap">'
            f'{s.huvud(s.T("nyckeltal_etikett"), _si_rubrik(s), "si-h", _nyckeltal_lank(s))}'
            f'<ul class="esp">{rad}</ul></div></section>')


@variant("siffror", "e-faktaruta")
def siffror_faktaruta(s):
    """Redaktionellt uppslag: rubrik och brödtext i två spalter med anfang, och en faktaruta med nyckeltalen."""
    b = s.b
    nt = b["nyckeltal"]
    om = [p for p in (b.get("om") or []) if p][:2]
    text = "".join(f"<p>{E(p)}</p>" for p in om)
    fakta = "".join(f'<div class="efa-post"><dt>{E(n["etikett"])}</dt><dd>{_tal(n, "efa-tal")}</dd></div>' for n in nt)
    return (f'<section class="ev sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap efa">'
            f'<div class="efa-artikel"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(_si_rubrik(s))}</h2>'
            f'<div class="efa-brod">{text}</div></div>'
            f'<aside class="efa-ruta" aria-label="{E(s.T("nyckeltal_etikett"))}"><span class="efa-rubrik">{E(s.T("nyckeltal_etikett"))}</span>'
            f'<dl>{fakta}</dl><div class="efa-lank">{_nyckeltal_lank(s)}</div></aside></div></section>')


@variant("siffror", "e-trappa")
def siffror_trappa(s):
    """Nyckeltalen som en stigande trappa av pelare med talet överst; på mobil blir pelarna allt längre staplar."""
    nt = s.b["nyckeltal"]
    n = max(1, len(nt))
    steg = ""
    for i, x in enumerate(nt):
        h = 34 + round(66 * i / max(1, n - 1)) if n > 1 else 100
        steg += (f'<li style="--h:{h}%"><div class="etr-pelare"><span class="etr-nr">{i + 1:02d}</span>{_tal(x, "etr-tal")}'
                 f'<span class="etr-et">{E(x["etikett"])}</span></div></li>')
    return (f'<section class="ev sek etr-sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap etr">'
            f'<div class="etr-huvud"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(_si_rubrik(s))}</h2>'
            f'<p class="etr-ingress">{E(_si_om(s))}</p></div>'
            f'<ol class="etr-trappa" style="--n:{n}">{steg}</ol></div></section>')


def _gemen(t):
    return t[0].lower() + t[1:] if len(t) > 1 and t[1].islower() else t


@variant("siffror", "e-text")
def siffror_text(s):
    """Centrerad ordbild: nyckeltalen vävs in i en enda stor mening, talen markerade med accentfärgad understrykning."""
    nt = s.b["nyckeltal"]
    delar = []
    for n in nt:
        enhet = f' {E(n["enhet"])}' if n.get("enhet") else ""
        delar.append(f'<span class="ete-del"><b>{E(n["varde"])}{enhet}</b> <span class="ete-et">{E(_gemen(n["etikett"]))}</span></span>')
    mening = ""
    for i, d in enumerate(delar):
        if i and i == len(delar) - 1:
            mening += '<span class="ete-bind"> &amp; </span>'
        elif i:
            mening += '<span class="ete-bind">, </span>'
        mening += d
    return (f'<section class="ev sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap ete">'
            f'<span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h" class="ete-h">{E(_si_rubrik(s))}</h2>'
            f'<p class="ete-mening">{mening}<span class="ete-bind">.</span></p>'
            f'<div class="ete-fot"><p class="mut">{E(_si_om(s))}</p>{_nyckeltal_lank(s)}</div></div></section>')


@variant("siffror", "e-split")
def siffror_split(s):
    """Split 60/40: stor bild med det första nyckeltalet i en överlappande färgruta, övriga tal i rader bredvid."""
    nt = s.b["nyckeltal"]
    if not nt:
        return ""
    forsta, rest = nt[0], nt[1:]
    bild = s.bilder.ta()
    rader = "".join(f'<li>{_tal(n, "esl-tal")}<span class="esl-et">{E(n["etikett"])}</span></li>' for n in rest)
    return (f'<section class="ev sek {s.bg("siffror")}" aria-labelledby="si-h"><div class="wrap esl">'
            f'<div class="esl-bild">{s.bilder.fyll(bild, "(min-width:1000px) 58vw, 100vw", note=True)}'
            f'<div class="esl-bricka">{_tal(forsta, "esl-stort")}<span>{E(forsta["etikett"])}</span></div></div>'
            f'<div class="esl-text"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="si-h">{E(_si_rubrik(s))}</h2>'
            f'<ul class="esl-rader">{rader}</ul><div class="knappar">{_nyckeltal_lank(s)}</div></div></div></section>')
