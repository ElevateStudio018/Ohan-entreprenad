"""Varianter M: nyckeltal, hållbarhet, karriärpanel och servicerad i bildtunga layouter (kort, bento, överlapp, karusell).

Prefix per variant (CSS i varianter_m.css):
  siffror: m-bildkort .msb-   m-bento .msn-   m-overlap .mso-   m-karusell .msk-
  hb:      m-bento .mhn-      m-bildkort .mhk-   m-overlap .mho-
  panel:   m-bildkort .mpk-   m-bento .mpn-      m-overlap .mpo-
  service: m-fotorad .mse-
"""
from varianter import variant, E, ikon, PIL


# --- Hjälpare ----------------------------------------------------------------------------------------------------------
def _tal(n, cls=""):
    enhet = f'<small>{E(n["enhet"])}</small>' if n.get("enhet") else ""
    return f'<b class="{cls}">{E(n["varde"])}{enhet}</b>'


def _si_rubrik(s):
    return s.b.get("intro_rubrik", s.b["slogan"])


def _si_om(s):
    om = s.b.get("om") or [""]
    return om[0] if om else ""


def _nyckeltal_lank(s):
    return s.textlank(s.T("nyckeltal_lank"), "investerare.html" if "investerare" in s.slugs else "om-oss.html")


def _lank_span(text):
    return f'<span class="textlank"><span>{E(text)}</span>{PIL}</span>'


def _jobb(s):
    return (s.b["karriar"].get("jobb") or [])[:4]


def _kultur(s):
    return s.b.get("kultur") or s.T("kultur")


def _lediga(n):
    return "ledig tjänst" if n == 1 else "lediga tjänster"


def _service(s):
    return s.b.get("service") or [("Lediga lägenheter", "hus", "projekt.html"), ("Felanmälan", "kugge", "om-oss.html#kontakt"),
                                  ("Bostadskö", "dokument", "om-oss.html#kontakt"), ("Mina sidor", "nyckel", "#")]


# =====================================================================================================================
# Siffror
# =====================================================================================================================
@variant("siffror", "m-bildkort")
def siffror_bildkort(s):
    """Varje nyckeltal i ett högt bildkort: foto som fyller kortet, talet stort nederst på bilden och etiketten under."""
    nt = s.b["nyckeltal"]
    kort = ""
    for i, n in enumerate(nt):
        bild = s.bilder.ta()
        kort += (f'<li class="msb-kort reveal"><div class="msb-foto">{s.bilder.img(bild, "(min-width:1000px) 25vw, (min-width:600px) 50vw, 100vw")}</div>'
                 f'<span class="msb-nr">{i + 1:02d}</span><div class="msb-text">{_tal(n, "msb-tal")}<span class="msb-et">{E(n["etikett"])}</span></div></li>')
    return (f'<section class="sek {s.bg("siffror")}" aria-labelledby="msb-h"><div class="wrap">'
            f'<div class="msb-huvud"><div><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="msb-h">{E(_si_rubrik(s))}</h2></div>'
            f'<div class="msb-ingress"><p>{E(_si_om(s))}</p>{_nyckeltal_lank(s)}</div></div>'
            f'<ul class="msb msb-n{len(nt)}">{kort}</ul><p class="msb-not">Illustrationsbilder</p></div></section>')


@variant("siffror", "m-bento")
def siffror_bento(s):
    """Bento-rutnät: stor bildruta med rubriken i en färgruta, nyckeltalen som rutor i färg, på bild och i ljus yta."""
    nt = s.b["nyckeltal"]
    stor = s.bilder.ta()
    rutor = ""
    for i, n in enumerate(nt):
        typ = ("farg", "pafoto", "ljus", "accent")[i % 4]
        foto = (f'<div class="msn-foto">{s.bilder.img(s.bilder.ta(), "(min-width:1000px) 25vw, 50vw")}</div>' if typ == "pafoto" else "")
        rutor += (f'<li class="msn-ruta msn-tal msn-{typ} msn-t{i + 1}">{foto}<span class="msn-nr">{i + 1:02d}</span>'
                  f'<div class="msn-txt">{_tal(n, "msn-v")}<span class="msn-et">{E(n["etikett"])}</span></div></li>')
    return (f'<section class="sek {s.bg("siffror")}" aria-labelledby="msn-h"><div class="wrap"><ul class="msn msn-n{len(nt)}">'
            f'<li class="msn-ruta msn-stor"><div class="msn-foto">{s.bilder.img(stor, "(min-width:1000px) 50vw, 100vw")}</div><span class="figtext">Illustrationsbild</span>'
            f'<div class="msn-rub"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="msn-h">{E(_si_rubrik(s))}</h2></div></li>'
            f'{rutor}<li class="msn-ruta msn-om"><p>{E(_si_om(s))}</p>{_nyckeltal_lank(s)}</li></ul></div></section>')


@variant("siffror", "m-overlap")
def siffror_overlap(s):
    """Text till vänster; till höger en hög bild där nyckeltalen ligger som en trappa av kort över bildens vänsterkant."""
    nt = s.b["nyckeltal"]
    bild = s.bilder.ta()
    kort = "".join(f'<li class="mso-kort mso-k{i % 4 + 1}"><span class="mso-nr">{i + 1:02d}</span>{_tal(n, "mso-tal")}<span class="mso-et">{E(n["etikett"])}</span></li>'
                   for i, n in enumerate(nt))
    return (f'<section class="sek {s.bg("siffror")}" aria-labelledby="mso-h"><div class="wrap mso">'
            f'<div class="mso-text"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="mso-h">{E(_si_rubrik(s))}</h2>'
            f'<p class="ingress">{E(_si_om(s))}</p><div class="knappar">{_nyckeltal_lank(s)}</div></div>'
            f'<div class="mso-scen"><div class="mso-bild">{s.bilder.fyll(bild, "(min-width:1000px) 50vw, 100vw", note=True)}</div>'
            f'<ul class="mso-kortlista mso-n{len(nt)}">{kort}</ul></div></div></section>')


@variant("siffror", "m-karusell")
def siffror_karusell(s):
    """Horisontell scroll-snap-rad: ett bildkort per nyckeltal (bild överst, talet i en ruta under) och ett avslutande färgkort."""
    nt = s.b["nyckeltal"]
    kort = ""
    for i, n in enumerate(nt):
        bild = s.bilder.ta()
        kort += (f'<li class="msk-kort"><div class="msk-foto">{s.bilder.img(bild, "(min-width:1000px) 30vw, 80vw")}'
                 f'<span class="msk-nr">{i + 1:02d} / {len(nt):02d}</span></div>'
                 f'<div class="msk-text">{_tal(n, "msk-tal")}<span class="msk-et">{E(n["etikett"])}</span></div></li>')
    lank = "investerare.html" if "investerare" in s.slugs else "om-oss.html"
    kort += (f'<li class="msk-kort msk-sista"><a href="{lank}"><p>{E(_si_om(s))}</p>'
             f'<span class="msk-cta"><span>{E(s.T("nyckeltal_lank"))}</span><span class="rundpil">{PIL}</span></span></a></li>')
    return (f'<section class="sek {s.bg("siffror")}" aria-labelledby="msk-h"><div class="wrap">'
            f'{s.huvud(s.T("siffror_etikett"), _si_rubrik(s), "msk-h", _nyckeltal_lank(s))}'
            f'<ul class="msk" tabindex="0" aria-label="{E(s.T("nyckeltal_etikett"))}, bläddra i sidled">{kort}</ul>'
            f'<div class="msk-fot"><span class="msk-dra" aria-hidden="true">Dra för fler {PIL}</span><span class="msk-not">Illustrationsbilder</span></div>'
            f'</div></section>')


# =====================================================================================================================
# Hållbarhet
# =====================================================================================================================
@variant("hb", "m-bento")
def hb_bento(s):
    """Bento: stor bild med rubriken i en färgruta, textkort, målen som färgrutor och ett mål på en andra bild."""
    hb = s.b["hallbarhet"]
    mal = hb["mal"]
    stor = s.bilder.ta(s.bt("hb"))
    rutor = [f'<li class="mhn-ruta mhn-stor"><div class="mhn-foto">{s.bilder.img(stor, "(min-width:1000px) 50vw, 100vw")}</div><span class="figtext">Illustrationsbild</span>'
             f'<div class="mhn-rub"><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="mhn-h">{E(hb["rubrik"])}</h2></div></li>',
             f'<li class="mhn-ruta mhn-txt"><p>{E(hb["text"])}</p>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</li>']
    for i, (a, t) in enumerate(mal):
        foto = ""
        if i == 1:
            foto = f'<div class="mhn-foto">{s.bilder.img(s.bilder.ta(s.bt("hb")), "(min-width:1000px) 50vw, 100vw")}</div>'
        rutor.append(f'<li class="mhn-ruta mhn-mal mhn-m{i + 1}{" mhn-pafoto" if foto else ""}">{foto}<span class="mhn-nr">{i + 1:02d}</span>'
                     f'<div class="mhn-mtxt"><b>{E(a)}</b><span>{E(t)}</span></div></li>')
    if len(mal) < 3:
        rutor.append(f'<li class="mhn-ruta mhn-extra"><div class="mhn-foto">{s.bilder.img(s.bilder.ta(s.bt("hb")), "(min-width:1000px) 25vw, 50vw")}</div></li>')
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="mhn-h"><div class="wrap">'
            f'<ul class="mhn mhn-n{min(len(mal), 3)}">{"".join(rutor)}</ul></div></section>')


@variant("hb", "m-bildkort")
def hb_bildkort(s):
    """Ett högt bildkort per mål: fotot fyller kortet och målet står i en färgruta som ligger över bildens nederkant."""
    hb = s.b["hallbarhet"]
    kort = ""
    for i, (a, t) in enumerate(hb["mal"]):
        bild = s.bilder.ta(s.bt("hb"))
        kort += (f'<li class="mhk-kort mhk-k{i % 3 + 1} reveal"><div class="mhk-foto">{s.bilder.img(bild, "(min-width:1000px) 33vw, 85vw")}</div>'
                 f'<div class="mhk-ruta"><span class="mhk-nr">{i + 1:02d}</span><b>{E(a)}</b><span class="mhk-t">{E(t)}</span></div></li>')
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="mhk-h"><div class="wrap">'
            f'<div class="mhk-huvud"><div><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="mhk-h">{E(hb["rubrik"])}</h2></div>'
            f'<div class="mhk-ingress"><p>{E(hb["text"])}</p>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div></div>'
            f'<ul class="mhk mhk-n{len(hb["mal"])}" tabindex="0" aria-label="{E(s.T("hb_etikett"))}">{kort}</ul>'
            f'<p class="mhk-not">Illustrationsbilder</p></div></section>')


@variant("hb", "m-overlap")
def hb_overlap(s):
    """Bild i mitten, inramad av två överlappande paneler: rubrik och text i färg upptill till vänster, målen i ett kort nedtill till höger."""
    hb = s.b["hallbarhet"]
    bild = s.bilder.ta(s.bt("hb"))
    mal = "".join(f'<li><span class="mho-nr">{i + 1:02d}</span><b>{E(a)}</b><span class="mho-t">{E(t)}</span></li>' for i, (a, t) in enumerate(hb["mal"]))
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="mho-h"><div class="wrap mho">'
            f'<div class="mho-bild">{s.bilder.fyll(bild, "(min-width:1000px) 60vw, 100vw", note=True)}</div>'
            f'<div class="mho-panel reveal"><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="mho-h">{E(hb["rubrik"])}</h2>'
            f'<p>{E(hb["text"])}</p></div>'
            f'<div class="mho-mal reveal"><ul>{mal}</ul>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div></div></section>')


# =====================================================================================================================
# Karriärpanel
# =====================================================================================================================
@variant("panel", "m-bildkort")
def panel_bildkort(s):
    """Varje ledigt jobb som ett bildkort (foto, ort som märke, titel på bilden), med text och knapp i huvudet ovanför."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    if jobb:
        kort = "".join(f'<li class="mpk-kort reveal"><a href="karriar.html"><div class="mpk-foto">{s.bilder.img(s.bilder.ta(s.bt("panel")), "(min-width:1000px) 25vw, (min-width:600px) 50vw, 100vw")}</div>'
                       f'<span class="mpk-ort">{E(o)}</span><div class="mpk-text"><b>{E(t)}</b>{_lank_span("Läs mer och ansök")}</div></a></li>'
                       for t, o in jobb)
    else:
        kort = (f'<li class="mpk-kort mpk-ensam"><a href="karriar.html"><div class="mpk-foto">{s.bilder.img(s.bilder.ta(s.bt("panel")), "100vw")}</div>'
                f'<div class="mpk-text"><b>{E(_kultur(s))}</b>{_lank_span(s.T("panel_knapp"))}</div></a></li>')
    kultur = f'<p class="mpk-kultur">{E(_kultur(s))}</p>' if jobb else ""
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="mpk-h"><div class="wrap">'
            f'<div class="mpk-huvud"><div><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="mpk-h">{E(k["rubrik"])}</h2></div>'
            f'<div class="mpk-ingress"><p>{E(k["text"])}</p>{kultur}<div class="knappar">{s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div></div></div>'
            f'<ul class="mpk mpk-n{len(jobb)}">{kort}</ul><p class="mpk-not">Illustrationsbilder</p></div></section>')


@variant("panel", "m-bento")
def panel_bento(s):
    """Bento: färgruta med rubrik, stor bild, jobben som rutor med pil, kulturen i accentfärg och en ruta med antalet lediga jobb."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    n = len(jobb)
    rutor = [f'<li class="mpn-ruta mpn-rub mpn-w2"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="mpn-h">{E(k["rubrik"])}</h2><p>{E(k["text"])}</p></li>',
             f'<li class="mpn-ruta mpn-bild"><div class="mpn-foto">{s.bilder.img(s.bilder.ta(s.bt("panel")), "(min-width:1000px) 50vw, 100vw")}</div><span class="figtext">Illustrationsbild</span></li>']
    jobbrutor = [f'<li class="mpn-ruta mpn-jobb"><a href="karriar.html"><span class="mpn-ort">{E(o)}</span><b>{E(t)}</b><span class="rundpil">{PIL}</span></a></li>'
                 for t, o in jobb]

    def kultur(w):
        return f'<li class="mpn-ruta mpn-kultur mpn-w{w}"><p>{E(_kultur(s))}</p></li>'

    def foto(w):
        return f'<li class="mpn-ruta mpn-foto2 mpn-w{w}"><div class="mpn-foto">{s.bilder.img(s.bilder.ta(s.bt("panel")), "(min-width:1000px) 25vw, 100vw")}</div></li>'

    def cta(w):
        inne = (f'<b class="mpn-antal">{n}</b><span>{_lediga(n)} just nu</span>' if n else f'<b class="mpn-cta-t">{E(s.T("panel_knapp"))}</b>')
        return f'<li class="mpn-ruta mpn-cta mpn-w{w}"><a href="karriar.html">{inne}<span class="rundpil">{PIL}</span></a></li>'

    # Fyll raderna utan hål: rad 2 har två platser bredvid bilden, rad 3 har fyra.
    if n >= 4:
        resten = jobbrutor[:4] + [kultur(1), cta(1)]
    elif n == 3:
        resten = jobbrutor + [kultur(2), cta(1)]
    elif n == 2:
        resten = jobbrutor + [kultur(2), foto(1), cta(1)]
    elif n == 1:
        resten = jobbrutor + [cta(1), kultur(2), foto(2)]
    else:
        resten = [kultur(2), foto(2), cta(2)]
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="mpn-h"><div class="wrap">'
            f'<ul class="mpn mpn-n{min(n, 4)}">{"".join(rutor + resten)}</ul></div></section>')


@variant("panel", "m-overlap")
def panel_overlap(s):
    """Stor bild till vänster, ett textkort som skjuter in över bildens högra kant och jobben i en färgad list över bildens nederkant."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    bild = s.bilder.ta(s.bt("panel"))
    if jobb:
        list_ = ('<ul class="mpo-jobb">' + "".join(f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span>{PIL}</a></li>' for t, o in jobb) + "</ul>")
    else:
        list_ = f'<div class="mpo-jobb mpo-tom"><p>{E(_kultur(s))}</p></div>'
    kultur = f'<p class="mpo-kultur">{E(_kultur(s))}</p>' if jobb else ""
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="mpo-h"><div class="wrap mpo">'
            f'<div class="mpo-bild">{s.bilder.fyll(bild, "(min-width:1000px) 65vw, 100vw", note=True)}</div>'
            f'<div class="mpo-kort reveal"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="mpo-h">{E(k["rubrik"])}</h2>'
            f'<p class="mpo-text">{E(k["text"])}</p>{kultur}<div class="knappar">{s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div></div>'
            f'<div class="mpo-list">{list_}</div></div></section>')


# =====================================================================================================================
# Servicerad
# =====================================================================================================================
@variant("service", "m-fotorad")
def service_fotorad(s):
    """Tonat band med genvägarna som små bildkort: foto med ikon i en färgruta, titel och pil; scroll-snap i mobil."""
    r = _service(s)
    a = ""
    for t, i, h in r:
        bild = s.bilder.ta()
        a += (f'<li><a href="{E(h)}"><span class="mse-foto">{s.bilder.img(bild, "160px")}<span class="mse-ik">{ikon(i, "ik")}</span></span>'
              f'<span class="mse-t">{E(t)}</span><span class="mse-pil">{PIL}</span></a></li>')
    return (f'<div class="mse"><div class="wrap"><nav aria-label="Snabbtjänster"><ul class="mse-rad mse-n{len(r)}">{a}</ul></nav></div></div>')
