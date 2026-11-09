"""Sektionsvarianter F: nyheter, berättelser och projekt i nya layouter.

Klassprefix per variant (se varianter_f.css). Gemensamt: .fv ger lokala färger som följer sektionens bakgrund.
  nyheter:     f-tidslinje .fnt-   f-block .fnb-     f-rullband .fnr-   f-spalt .fns-    f-dragspel .fnd-
  berattelser: f-diagonal .fbd-    f-polaroid .fbp-  f-sticky .fbs-     f-paneler .fbq-  f-flikar .fbf-   f-trappa .fbt-
  projekt:     f-karta .fpk-       f-ar .fpa-        f-remsor .fpr-     f-bento .fpb-    f-rulle .fpu-    f-index .fpi-
"""
import hashlib
import re

from varianter import variant, E, PIL

MAN = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
MAN_LANG = ["januari", "februari", "mars", "april", "maj", "juni", "juli", "augusti", "september", "oktober", "november", "december"]


# --- Gemensamt ------------------------------------------------------------------------------------------------------
def _nb(text):
    """Escapar och håller ihop tal som "21 000" och "4 900 kr" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", " ", E(text))


def _datum(d):
    """'2026-10-23' -> ('23', 'okt', '2026'); annat format -> (d, '', '')."""
    try:
        a, m, dag = d.split("-")
        return str(int(dag)), MAN[int(m) - 1], a
    except (ValueError, IndexError, AttributeError):
        return d, "", ""


def _datum_text(d):
    dag, man, ar = _datum(d)
    return " ".join(x for x in (dag, man, ar) if x)


def _ingress(rad):
    return rad[2] if len(rad) > 2 and rad[2] else ""


def _nybild(s, rad):
    return s.bilder.ta(rad[3] if len(rad) > 3 and rad[3] else s.b.get("nyhet_tagg"))


def _ny_huvud(s, id_, etikett="ny_etikett2", rubrik="ny_senaste"):
    return s.huvud(s.T(etikett), s.T(rubrik), id_, s.textlank(s.T("ny_lank"), "om-oss.html#press"))


def _lank_span(text):
    return f'<span class="textlank"><span>{E(text)}</span>{PIL}</span>'


def _ber_rubrik(s):
    return s.b.get("berattelser_rubrik") or s.T("ber_rubrik")


def _ber_huvud(s, id_, mitt=False):
    return s.huvud(s.T("ber_etikett"), _ber_rubrik(s), id_, "" if mitt else s.textlank(s.T("ber_lank"), "projekt.html"), mitt=mitt)


def _status(s, x):
    ar = x.get("ar", "")
    pag = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2026)
    st = x.get("status") or (s.T("status_pagaende") if pag else s.T("status_klart"))
    return st, st == s.T("status_pagaende")


def _status_html(s, x, kl):
    st, pag = _status(s, x)
    return f'<span class="{kl}{" pag" if pag else ""}">{E(st)}</span>'


def _proj_rubrik(s, lista=False):
    return s.b.get("projekt_rubrik") or s.T("proj_rubrik_lista" if lista else "proj_rubrik")


def _proj_huvud(s, id_, lista=False):
    return s.huvud(s.T("proj_etikett"), _proj_rubrik(s, lista), id_, s.textlank(s.T("proj_lank"), "projekt.html"))


def _meta(x, *falt):
    return " · ".join(E(x.get(f, "")) for f in falt if x.get(f))


def _utan_alt(img):
    return re.sub(r'alt="[^"]*"', 'alt=""', img)


# ===================================================================================================================
# NYHETER
# ===================================================================================================================
@variant("nyheter", "f-tidslinje")
def nyheter_f_tidslinje(s):
    """Sticky rubrikkolumn till vänster, lodrät tidslinje med årsmarkeringar och prickar till höger."""
    rader, forra_ar = "", None
    for rad in s.b["nyheter"]:
        d, t = rad[0], rad[1]
        dag, man, ar = _datum(d)
        if ar and ar != forra_ar:
            rader += f'<li class="fnt-ar" aria-hidden="true"><span>{E(ar)}</span></li>'
            forra_ar = ar
        ing = _ingress(rad)
        rader += (f'<li class="fnt-punkt"><a href="om-oss.html#press"><time datetime="{E(d)}"><b>{E(dag)}</b> {E(man)}</time>'
                  f'<div class="fnt-text"><h3>{_nb(t)}</h3>{f"<p>{_nb(ing)}</p>" if ing else ""}</div><span class="fnt-pil">{PIL}</span></a></li>')
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="fnt-h"><div class="wrap fv fnt">
  <div class="fnt-sido"><span class="etikett">{E(s.T("ny_etikett"))}</span><h2 id="fnt-h">{E(s.T("ny_rubrik"))}</h2>
    <div class="knappar">{s.knapp(s.T("ny_lank"), "om-oss.html#press", "kontur")}</div></div>
  <ol class="fnt-linje">{rader}</ol></div></section>'''


@variant("nyheter", "f-block")
def nyheter_f_block(s):
    """Bento med färgblock: stor bildruta med text över, en färgad textruta och mindre rutor i ton och mörkt."""
    ny = s.b["nyheter"][:4]
    rutor = ""
    for i, rad in enumerate(ny):
        d, t = rad[0], rad[1]
        ing = _ingress(rad)
        tid = f'<time datetime="{E(d)}">{E(_datum_text(d))}</time>'
        if i == 0:
            bild = _nybild(s, rad)
            rutor += (f'<a class="fnb-ruta fnb-stor" href="om-oss.html#press"><div class="fnb-bild">{s.bilder.img(bild, "(min-width:1000px) 50vw, 100vw")}</div>'
                      f'<div class="fnb-over">{tid}<h3>{_nb(t)}</h3>{f"<p>{_nb(ing)}</p>" if ing else ""}</div></a>')
        elif i == 1:
            rutor += (f'<a class="fnb-ruta fnb-farg" href="om-oss.html#press">{tid}<h3>{_nb(t)}</h3>{f"<p>{_nb(ing)}</p>" if ing else ""}'
                      f'<span class="fnb-rund">{PIL}</span></a>')
        else:
            kl = "fnb-ton" if i == 2 else "fnb-mork"
            rutor += f'<a class="fnb-ruta {kl}" href="om-oss.html#press">{tid}<h3>{_nb(t)}</h3><span class="fnb-rund">{PIL}</span></a>'
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="fnb-h"><div class="wrap fv">
  {_ny_huvud(s, "fnb-h")}
  <div class="fnb fnb-n{len(ny)}">{rutor}</div></div></section>'''


@variant("nyheter", "f-rullband")
def nyheter_f_rullband(s):
    """Horisontell scroll-snap-rad som går ut i kanten, kort med datumstämpel som överlappar bilden."""
    kort = ""
    for rad in s.b["nyheter"]:
        d, t = rad[0], rad[1]
        dag, man, ar = _datum(d)
        bild = _nybild(s, rad)
        ing = _ingress(rad)
        kort += (f'<li><a href="om-oss.html#press"><div class="fnr-foto">{s.bilder.img(bild, "(min-width:1000px) 30vw, 80vw")}</div>'
                 f'<time class="fnr-stampel" datetime="{E(d)}"><b>{E(dag)}</b><span>{E(man)} {E(ar)}</span></time>'
                 f'<div class="fnr-text"><h3>{_nb(t)}</h3>{f"<p>{_nb(ing)}</p>" if ing else ""}{_lank_span(s.T("las_mer"))}</div></a></li>')
    return f'''<section class="sek {s.bg("nyheter")} fnr-sek" aria-labelledby="fnr-h"><div class="wrap fv">
  {_ny_huvud(s, "fnr-h", "ny_etikett", "ny_rubrik")}</div>
  <div class="fv fnr-ram"><ul class="fnr" tabindex="0" aria-label="{E(s.T("ny_rubrik"))}">{kort}</ul></div></section>'''


@variant("nyheter", "f-spalt")
def nyheter_f_spalt(s):
    """Tidningssida: centrerat sidhuvud mellan dubbla linjer, huvudartikel med anfang och övriga i spalter med lodräta linjer."""
    ny = s.b["nyheter"]
    f = ny[0]
    bild = _nybild(s, f)
    ing = _ingress(f)
    spalter = ""
    for rad in ny[1:4]:
        d, t = rad[0], rad[1]
        i2 = _ingress(rad)
        spalter += (f'<li><a href="om-oss.html#press"><time datetime="{E(d)}">{E(_datum_text(d))}</time><h3>{_nb(t)}</h3>'
                    f'{f"<p>{_nb(i2)}</p>" if i2 else ""}</a></li>')
    dag, man, ar = _datum(f[0])
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="fns-h"><div class="wrap fv fns">
  <header class="fns-huvud"><span class="etikett">{E(s.T("ny_etikett2"))}</span><h2 id="fns-h">{E(s.T("ny_senaste"))}</h2>
    <div class="fns-rad"><span>{E(" ".join(x for x in (dag, MAN_LANG[MAN.index(man)] if man in MAN else "", ar) if x))}</span>{s.textlank(s.T("ny_lank"), "om-oss.html#press")}</div></header>
  <div class="fns-grid">
    <a class="fns-lead" href="om-oss.html#press"><div class="fns-foto">{s.bilder.img(bild, "(min-width:1000px) 45vw, 100vw")}</div>
      <div class="fns-lead-text"><time datetime="{E(f[0])}">{E(_datum_text(f[0]))}</time><h3>{_nb(f[1])}</h3>{f'<p class="fns-anfang">{_nb(ing)}</p>' if ing else ""}
      {_lank_span(s.T("las_mer"))}</div></a>
    <ul class="fns-spalter fns-n{len(ny[1:4])}">{spalter}</ul>
  </div></div></section>'''


@variant("nyheter", "f-dragspel")
def nyheter_f_dragspel(s):
    """Dragspel (details/summary): datum, rubrik och plus per rad – öppnad rad visar bild, ingress och länk."""
    rader = ""
    for i, rad in enumerate(s.b["nyheter"]):
        d, t = rad[0], rad[1]
        dag, man, ar = _datum(d)
        ing = _ingress(rad)
        bild = _nybild(s, rad)
        rader += (f'<details class="fnd-rad"{" open" if i == 0 else ""}><summary><time datetime="{E(d)}"><b>{E(dag)}</b><span>{E(man)} {E(ar)}</span></time>'
                  f'<h3>{_nb(t)}</h3><span class="fnd-plus" aria-hidden="true"></span></summary>'
                  f'<div class="fnd-inne"><div class="fnd-foto">{s.bilder.img(bild, "(min-width:900px) 360px, 100vw")}</div>'
                  f'<div class="fnd-text">{f"<p>{_nb(ing)}</p>" if ing else ""}{s.textlank(s.T("las_mer"), "om-oss.html#press")}</div></div></details>')
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="fnd-h"><div class="wrap fv fnd">
  {_ny_huvud(s, "fnd-h", "ny_etikett", "ny_rubrik")}
  <div class="fnd-lista">{rader}</div></div></section>'''


# ===================================================================================================================
# BERÄTTELSER
# ===================================================================================================================
@variant("berattelser", "f-diagonal")
def berattelser_f_diagonal(s):
    """Split 60/40: bild med diagonalt snitt mot en numrerad berättelsestapel där den första är framlyft."""
    ber = s.berattelser()[:3]
    bild = s.bilder.ta(ber[0].get("tagg"))
    rader = ""
    for i, x in enumerate(ber):
        rader += (f'<li class="{"fbd-forst" if i == 0 else ""}"><a href="projekt.html"><span class="fbd-nr">{i + 1:02d}</span>'
                  f'<div><h3>{E(x["rubrik"])}</h3><p>{_nb(x["text"])}</p>{_lank_span(s.T("las_mer")) if i == 0 else ""}</div></a></li>')
    return f'''<section class="sek {s.bg("berattelser")}" aria-labelledby="fbd-h"><div class="wrap fv">
  {_ber_huvud(s, "fbd-h")}
  <div class="fbd"><div class="fbd-bild">{s.bilder.fyll(bild, "(min-width:960px) 58vw, 100vw", note=True)}<span class="fbd-kil" aria-hidden="true"></span></div>
    <ol class="fbd-lista">{rader}</ol></div></div></section>'''


@variant("berattelser", "f-polaroid")
def berattelser_f_polaroid(s):
    """Kollage av lätt vridna polaroider med tejpbit och handskriven känsla, rätas upp vid hovring."""
    ber = s.berattelser()[:4]
    kort = ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        kort += (f'<li class="fbp-k{i + 1}"><a href="projekt.html"><span class="fbp-tejp" aria-hidden="true"></span>'
                 f'<div class="fbp-foto">{s.bilder.img(bild, "(min-width:1000px) 30vw, 90vw")}</div>'
                 f'<div class="fbp-text"><h3>{E(x["rubrik"])}</h3><p>{_nb(x["text"])}</p></div></a></li>')
    return f'''<section class="sek {s.bg("berattelser")} fbp-sek" aria-labelledby="fbp-h"><div class="wrap fv">
  {_ber_huvud(s, "fbp-h", mitt=True)}
  <ul class="fbp fbp-n{len(ber)}">{kort}</ul>
  <div class="fbp-fot">{s.knapp(s.T("ber_lank"), "projekt.html", "kontur")}</div></div></section>'''


@variant("berattelser", "f-sticky")
def berattelser_f_sticky(s):
    """Sticky sidokolumn med rubrik och innehållsförteckning, stora bildkort som rullar förbi till höger."""
    ber = s.berattelser()[:4]
    index, kort = "", ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        index += f'<li><a href="#fbs-{i + 1}"><span>{i + 1:02d}</span>{E(x["rubrik"])}</a></li>'
        kort += (f'<li id="fbs-{i + 1}"><a href="projekt.html"><div class="fbs-foto">{s.bilder.img(bild, "(min-width:960px) 55vw, 100vw")}'
                 f'<span class="fbs-nr">{i + 1:02d}</span></div><div class="fbs-text"><h3>{E(x["rubrik"])}</h3><p>{_nb(x["text"])}</p>'
                 f'{_lank_span(s.T("las_mer"))}</div></a></li>')
    return f'''<section class="sek {s.bg("berattelser")}" aria-labelledby="fbs-h"><div class="wrap fv fbs">
  <div class="fbs-sido"><div class="fbs-klister"><span class="etikett">{E(s.T("ber_etikett"))}</span><h2 id="fbs-h">{E(_ber_rubrik(s))}</h2>
    <ol class="fbs-index">{index}</ol><div class="knappar">{s.textlank(s.T("ber_lank"), "projekt.html")}</div></div></div>
  <ul class="fbs-kort">{kort}</ul></div></section>'''


@variant("berattelser", "f-paneler")
def berattelser_f_paneler(s):
    """Mörk premiumruta med höga bildpaneler sida vid sida – panelen man pekar på vidgas och visar texten."""
    ber = s.berattelser()[:4]
    pan = ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        pan += (f'<li><a href="projekt.html">{s.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw")}<span class="fbq-nr">{i + 1:02d}</span>'
                f'<div class="fbq-text"><h3>{E(x["rubrik"])}</h3><div class="fbq-mer"><p>{_nb(x["text"])}</p>{_lank_span(s.T("las_mer"))}</div></div></a></li>')
    return f'''<section class="sek {s.bg("berattelser")}" aria-labelledby="fbq-h"><div class="wrap">
  <div class="fbq-ruta"><div class="fbq-huvud"><div><span class="etikett">{E(s.T("ber_etikett"))}</span><h2 id="fbq-h">{E(_ber_rubrik(s))}</h2></div>
    {s.textlank(s.T("ber_lank"), "projekt.html")}</div>
  <ul class="fbq fbq-n{len(ber)}">{pan}</ul></div></div></section>'''


@variant("berattelser", "f-flikar")
def berattelser_f_flikar(s):
    """Flikar i ren CSS (radioknappar): numrerade flikar överst, vald berättelse som bild + text under."""
    ber = s.berattelser()[:4]
    radio = "".join(f'<input class="fbf-r fbf-r{i + 1}" type="radio" name="fbf-val" id="fbf-r{i + 1}"{" checked" if i == 0 else ""}>' for i in range(len(ber)))
    flikar = "".join(f'<label for="fbf-r{i + 1}"><span>{i + 1:02d}</span><b>{E(x["rubrik"])}</b></label>' for i, x in enumerate(ber))
    paneler = ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        paneler += (f'<div class="fbf-panel"><div class="fbf-foto">{s.bilder.img(bild, "(min-width:960px) 55vw, 100vw")}</div>'
                    f'<div class="fbf-text"><span class="fbf-stor-nr" aria-hidden="true">{i + 1:02d}</span><h3>{E(x["rubrik"])}</h3><p>{_nb(x["text"])}</p>'
                    f'{s.textlank(s.T("las_mer"), "projekt.html")}</div></div>')
    return f'''<section class="sek {s.bg("berattelser")}" aria-labelledby="fbf-h"><div class="wrap fv">
  {_ber_huvud(s, "fbf-h")}
  <div class="fbf fbf-n{len(ber)}">{radio}<div class="fbf-flikar" role="presentation">{flikar}</div><div class="fbf-paneler">{paneler}</div></div></div></section>'''


@variant("berattelser", "f-trappa")
def berattelser_f_trappa(s):
    """Färgband i primärfärg med rubriken, kort som reser sig ur bandet i trappsteg."""
    ber = s.berattelser()[:3]
    kort = ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        kort += (f'<li><a href="projekt.html"><div class="fbt-foto">{s.bilder.img(bild, "(min-width:1000px) 30vw, 90vw")}</div>'
                 f'<div class="fbt-text"><span class="fbt-nr">{i + 1:02d}</span><h3>{E(x["rubrik"])}</h3><p>{_nb(x["text"])}</p>{_lank_span(s.T("las_mer"))}</div></a></li>')
    return f'''<section class="fbt-sek {s.bg("berattelser")}" aria-labelledby="fbt-h">
  <div class="fbt-band"><div class="wrap"><div class="sek-huvud"><div><span class="etikett">{E(s.T("ber_etikett"))}</span><h2 id="fbt-h">{E(_ber_rubrik(s))}</h2></div>
    {s.textlank(s.T("ber_lank"), "projekt.html")}</div></div></div>
  <div class="wrap fv"><ul class="fbt fbt-n{len(ber)}">{kort}</ul></div></section>'''


# ===================================================================================================================
# PROJEKT
# ===================================================================================================================
# Positioner (x %, y %) på den stiliserade kartan, spridda så att nålarna inte krockar.
KARTPLATS = [(22, 30), (64, 22), (44, 56), (80, 60), (16, 74), (58, 82), (34, 14), (84, 44)]


@variant("projekt", "f-karta")
def projekt_f_karta(s):
    """Kartliknande yta med numrerade nålar per ort och en lista bredvid – hovring i listan lyfter rätt nål."""
    pr = s.b["projekt"][:8]
    start = int(hashlib.md5(s.b.get("namn", "").encode()).hexdigest(), 16) % len(KARTPLATS)
    nalar, rader = "", ""
    for i, x in enumerate(pr):
        px, py = KARTPLATS[(start + i) % len(KARTPLATS)]
        nalar += (f'<li class="fpk-nal" style="--x:{px}%;--y:{py}%"><span class="fpk-prick">{i + 1}</span>'
                  f'<span class="fpk-ort">{E(x.get("ort", ""))}</span></li>')
        rader += (f'<li><a href="projekt.html"><span class="fpk-nr">{i + 1}</span><div class="fpk-info"><h3>{E(x["namn"])}</h3>'
                  f'<span>{_meta(x, "ort", "typ", "ar")}</span></div>{_status_html(s, x, "fpk-status")}</a></li>')
    return f'''<section class="sek {s.bg("projekt")}" aria-labelledby="fpk-h"><div class="wrap fv">
  {_proj_huvud(s, "fpk-h", lista=True)}
  <div class="fpk"><div class="fpk-karta" aria-hidden="true"><span class="fpk-ros">N</span><ul>{nalar}</ul></div><ol class="fpk-lista">{rader}</ol></div></div></section>'''


@variant("projekt", "f-ar")
def projekt_f_ar(s):
    """Projekten grupperade per år: stora konturårtal i en sticky kolumn, projektrader med bild och status bredvid."""
    pr = s.b["projekt"]
    grupper = {}
    for x in pr:
        grupper.setdefault(x.get("ar", "") or "–", []).append(x)
    ordn = sorted(grupper, key=lambda a: (a[:4].isdigit(), a), reverse=True)
    block = ""
    for ar in ordn:
        rader = ""
        for x in grupper[ar]:
            bild = s.bilder.ta(x.get("tagg"))
            rader += (f'<li><a href="projekt.html"><div class="fpa-foto">{s.bilder.img(bild, "(min-width:900px) 220px, 34vw")}</div>'
                      f'<div class="fpa-info"><span class="fpa-meta">{_meta(x, "ort", "typ")}</span><h3>{E(x["namn"])}</h3><p>{_nb(x.get("text", ""))}</p></div>'
                      f'{_status_html(s, x, "fpa-status")}</a></li>')
        block += f'<div class="fpa-grupp"><div class="fpa-ar"><span>{E(ar)}</span></div><ul class="fpa-lista">{rader}</ul></div>'
    return f'''<section class="sek {s.bg("projekt")}" aria-labelledby="fpa-h"><div class="wrap fv">
  {_proj_huvud(s, "fpa-h", lista=True)}
  <div class="fpa">{block}</div></div></section>'''


@variant("projekt", "f-remsor")
def projekt_f_remsor(s):
    """Helbreddsremsor: varje projekt är en bred bildremsa med stort namn och fakta, remsan vidgas vid hovring."""
    pr = s.b["projekt"][:5]
    rem = ""
    for i, x in enumerate(pr):
        bild = s.bilder.ta(x.get("tagg"))
        rem += (f'<li><a href="projekt.html">{s.bilder.fyll(bild, "100vw", lazy=i > 1)}<div class="wrap fpr-inne"><span class="fpr-nr">{i + 1:02d}</span>'
                f'<h3>{E(x["namn"])}</h3><div class="fpr-fakta">{_status_html(s, x, "fpr-status")}<span>{_meta(x, "ort", "typ", "ar")}</span></div>'
                f'<span class="fpr-pil">{PIL}</span></div></a></li>')
    return f'''<section class="sek {s.bg("projekt")} fpr-sek" aria-labelledby="fpr-h"><div class="wrap">{_proj_huvud(s, "fpr-h")}</div>
  <ul class="fpr">{rem}</ul></section>'''


@variant("projekt", "f-bento")
def projekt_f_bento(s):
    """Bento-rutnät: stor projektbild, färgruta med antal projekt och pågående, breda och små bildrutor."""
    pr = s.b["projekt"]
    antal_pag = sum(1 for x in pr if _status(s, x)[1])
    tre_rader = len(pr) >= 6
    vis = pr[:6] if tre_rader else pr[:3]
    form = ["stor", "", "bred", "", "bred", ""] if tre_rader else ["stor", "", "bred"]

    def ruta(x, kl, i):
        bild = s.bilder.ta(x.get("tagg"))
        sz = "(min-width:1000px) 50vw, 100vw" if kl in ("stor", "bred") else "(min-width:1000px) 25vw, 50vw"
        return (f'<a class="fpb-ruta fpb-{kl or "liten"}" href="projekt.html"><div class="fpb-bild">{s.bilder.img(bild, sz, lazy=i > 1)}</div>'
                f'{_status_html(s, x, "fpb-status")}<div class="fpb-text"><span>{_meta(x, "ort", "ar")}</span><h3>{E(x["namn"])}</h3></div></a>')
    rutor = ruta(vis[0], form[0], 0)
    rutor += (f'<a class="fpb-ruta fpb-siffra" href="projekt.html"><b>{len(pr)}</b><span>{E(s.T("proj_etikett"))}</span>'
              f'<em>{antal_pag} {E(s.T("status_pagaende").lower())}</em><span class="fpb-rund">{PIL}</span></a>')
    for i, (x, kl) in enumerate(zip(vis[1:], form[1:]), start=1):
        rutor += ruta(x, kl, i)
    return f'''<section class="sek {s.bg("projekt")}" aria-labelledby="fpb-h"><div class="wrap fv">
  {_proj_huvud(s, "fpb-h")}
  <div class="fpb{" fpb-tre" if tre_rader else ""}">{rutor}</div></div></section>'''


@variant("projekt", "f-rulle")
def projekt_f_rulle(s):
    """Höga stående kort i en scroll-snap-rad som löper ut till skärmkanten, med räknare och text över bilden."""
    pr = s.b["projekt"]
    kort = ""
    for i, x in enumerate(pr):
        bild = s.bilder.ta(x.get("tagg"))
        kort += (f'<li><a href="projekt.html">{s.bilder.fyll(bild, "(min-width:1000px) 26vw, 75vw", lazy=i > 2)}<div class="fpu-topp"><span>{i + 1:02d} / {len(pr):02d}</span>'
                 f'{_status_html(s, x, "fpu-status")}</div><div class="fpu-text"><span>{_meta(x, "ort", "typ")}</span><h3>{E(x["namn"])}</h3><p>{_nb(x.get("text", ""))}</p></div></a></li>')
    return f'''<section class="sek {s.bg("projekt")} fpu-sek" aria-labelledby="fpu-h"><div class="wrap">{_proj_huvud(s, "fpu-h")}</div>
  <div class="fpu-ram"><ul class="fpu" tabindex="0" aria-label="{E(_proj_rubrik(s))}">{kort}</ul></div></section>'''


@variant("projekt", "f-index")
def projekt_f_index(s):
    """Register med stora projektnamn till vänster och en bildram till höger som byter bild när man pekar på ett namn."""
    pr = s.b["projekt"][:8]
    rader = ""
    for i, x in enumerate(pr):
        bild = s.bilder.ta(x.get("tagg"))
        rader += (f'<li><a href="projekt.html"><span class="fpi-nr">{i + 1:02d}</span><h3>{E(x["namn"])}</h3><span class="fpi-meta">{_meta(x, "ort", "ar")}</span>'
                  f'<span class="fpi-pil">{PIL}</span></a><div class="fpi-bild">{_utan_alt(s.bilder.img(bild, "(min-width:960px) 50vw, 100vw", lazy=i > 0))}'
                  f'<div class="fpi-bildtext">{_status_html(s, x, "fpi-status")}<p>{_nb(x.get("text", ""))}</p></div></div></li>')
    return f'''<section class="sek {s.bg("projekt")}" aria-labelledby="fpi-h"><div class="wrap fv">
  {_proj_huvud(s, "fpi-h", lista=True)}
  <ol class="fpi">{rader}</ol></div></section>'''
