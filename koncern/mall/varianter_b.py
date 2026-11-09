"""Sektionsvarianter B: berättelser, projekt, hållbarhet och karriärpanel i nya layouter.

Klassprefix per variant (se varianter_b.css):
  berattelser: zigzag .bzig-  lista .blis-  overlap .bovl-  kolumner .bkol-
  projekt:     mosaik .pmos-  zigzag .pzig-  stor .psto-     tabell .ptab-
  hb:          citat .hcit-   tre .htre-     band .hban-
  panel:       kort .pkor-    delad .pdel-   kultur .pkul-
"""
import re

from varianter import variant, E, PIL


# --- Gemensamt ------------------------------------------------------------------------------------------------------
def _ber_huvud(s, id_):
    rubrik = s.b.get("berattelser_rubrik") or s.T("ber_rubrik")
    return s.huvud(s.T("ber_etikett"), rubrik, id_, s.textlank(s.T("ber_lank"), "projekt.html"))


def _lank_span(s, text):
    """Textlänk som span (inne i en annan länk)."""
    return f'<span class="textlank"><span>{E(text)}</span>{PIL}</span>'


def _status(s, x):
    ar = x.get("ar", "")
    pag = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2026)
    st = x.get("status") or (s.T("status_pagaende") if pag else s.T("status_klart"))
    return st, st == s.T("status_pagaende")


def _status_html(s, x, kl):
    st, pag = _status(s, x)
    return f'<span class="{kl}{" pag" if pag else ""}">{E(st)}</span>'


def _proj_huvud(s, id_, lista=False):
    rubrik = s.b.get("projekt_rubrik") or s.T("proj_rubrik_lista" if lista else "proj_rubrik")
    return s.huvud(s.T("proj_etikett"), rubrik, id_, s.textlank(s.T("proj_lank"), "projekt.html"))


def _kol(s):
    k = s.T("proj_kol")
    return k if isinstance(k, list) and len(k) >= 5 else ["Projekt", "Ort", "Typ", "Status", "År"]


# --- Berättelser ----------------------------------------------------------------------------------------------------
@variant("berattelser", "zigzag")
def berattelser_zigzag(s):
    ber = s.berattelser()[:3]
    rader = ""
    for i, x in enumerate(ber):
        bild = s.bilder.ta(x.get("tagg"))
        rader += (f'<li class="bzig-rad reveal"><a href="projekt.html"><div class="bzig-bild">{s.bilder.img(bild, "(min-width:900px) 58vw, 100vw")}</div>'
                  f'<div class="bzig-text"><span class="bzig-nr">{i + 1:02d}<i>/ {len(ber):02d}</i></span><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p>'
                  f'{_lank_span(s, s.T("las_mer"))}</div></a></li>')
    return (f'<section class="sek {s.bg("berattelser")}" aria-labelledby="bzig-h"><div class="wrap bzig-w">{_ber_huvud(s, "bzig-h")}'
            f'<ul class="bzig">{rader}</ul></div></section>')


@variant("berattelser", "lista")
def berattelser_lista(s):
    ber = s.berattelser()[:3]
    rubrik = s.b.get("berattelser_rubrik") or s.T("ber_rubrik")
    rader = "".join(
        f'<li><a href="projekt.html"><span class="blis-nr" aria-hidden="true">{i + 1:02d}</span><div class="blis-text"><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p></div>'
        f'<span class="blis-pil">{PIL}</span></a></li>' for i, x in enumerate(ber))
    return (f'<section class="sek {s.bg("berattelser")}" aria-labelledby="blis-h"><div class="wrap blis">'
            f'<div class="blis-huvud"><span class="etikett">{E(s.T("ber_etikett"))}</span><h2 id="blis-h">{E(rubrik)}</h2>'
            f'<div class="knappar">{s.textlank(s.T("ber_lank"), "projekt.html")}</div></div>'
            f'<ol class="blis-lista">{rader}</ol></div></section>')


@variant("berattelser", "overlap")
def berattelser_overlap(s):
    ber = s.berattelser()[:3]
    bilder = [s.bilder.ta(x.get("tagg")) for x in ber]
    f = ber[0]
    stor = (f'<div class="bovl-topp"><div class="bovl-bild">{s.bilder.fyll(bilder[0], "(min-width:960px) 70vw, 100vw", note=True)}</div>'
            f'<a class="bovl-kort reveal" href="projekt.html"><span class="bovl-meta">{E(s.T("ber_utvalt"))}</span><h3>{E(f["rubrik"])}</h3><p>{E(f["text"])}</p>'
            f'{_lank_span(s, s.T("las_mer"))}</a></div>')
    sma = "".join(
        f'<li><a href="projekt.html"><div class="bovl-foto">{s.bilder.img(bi, "(min-width:760px) 18vw, 34vw")}</div><div><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p>'
        f'{_lank_span(s, s.T("las_mer"))}</div></a></li>' for x, bi in zip(ber[1:], bilder[1:]))
    return (f'<section class="sek {s.bg("berattelser")}" aria-labelledby="bovl-h"><div class="wrap bovl-w">{_ber_huvud(s, "bovl-h")}'
            f'{stor}<ul class="bovl-sma">{sma}</ul></div></section>')


@variant("berattelser", "kolumner")
def berattelser_kolumner(s):
    ber = s.berattelser()[:3]
    bild = s.bilder.ta(ber[0].get("tagg") if ber else None)
    kol = "".join(
        f'<li class="reveal"><a href="projekt.html"><span class="bkol-nr">{i + 1:02d}</span><h3>{E(x["rubrik"])}</h3><p>{E(x["text"])}</p>{_lank_span(s, s.T("las_mer"))}</a></li>'
        for i, x in enumerate(ber))
    return (f'<section class="sek {s.bg("berattelser")}" aria-labelledby="bkol-h"><div class="wrap bkol-w">{_ber_huvud(s, "bkol-h")}'
            f'<div class="bkol-bild">{s.bilder.fyll(bild, "(min-width:1360px) 1300px, 100vw", note=True)}</div>'
            f'<ul class="bkol">{kol}</ul></div></section>')


# --- Projekt --------------------------------------------------------------------------------------------------------
@variant("projekt", "mosaik")
def projekt_mosaik(s):
    pr = s.b["projekt"][:7]
    li = ""
    for i, x in enumerate(pr):
        bild = s.bilder.ta(x.get("tagg"))
        sz = "(min-width:1100px) 50vw, 100vw" if i == 0 else "(min-width:1100px) 25vw, 100vw"
        li += (f'<li class="pmos-{i + 1}"><a href="projekt.html"><div class="pmos-bild">{s.bilder.img(bild, sz, lazy=i > 1)}</div>{_status_html(s, x, "pmos-status")}'
               f'<div class="pmos-text"><span class="pmos-ort">{E(x["ort"])} · {E(x.get("ar", ""))}</span><h3>{E(x["namn"])}</h3></div><span class="pmos-pil">{PIL}</span></a></li>')
    return (f'<section class="sek {s.bg("projekt")}" aria-labelledby="pmos-h"><div class="wrap pmos-w">{_proj_huvud(s, "pmos-h")}'
            f'<ul class="pmos pmos-n{len(pr)}">{li}</ul></div></section>')


@variant("projekt", "zigzag")
def projekt_zigzag(s):
    pr = s.b["projekt"][:4]
    kol = _kol(s)
    rader = ""
    for i, x in enumerate(pr):
        bild = s.bilder.ta(x.get("tagg"))
        rader += (f'<li class="reveal"><a href="projekt.html"><div class="pzig-bild">{s.bilder.img(bild, "(min-width:900px) 50vw, 100vw")}</div>'
                  f'<div class="pzig-text"><div class="pzig-topp"><span class="pzig-nr">{i + 1:02d}</span>{_status_html(s, x, "pzig-status")}</div>'
                  f'<h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p>'
                  f'<dl class="pzig-fakta"><div><dt>{E(kol[1])}</dt><dd>{E(x["ort"])}</dd></div><div><dt>{E(kol[2])}</dt><dd>{E(x["typ"])}</dd></div>'
                  f'<div><dt>{E(kol[4])}</dt><dd>{E(x.get("ar", ""))}</dd></div></dl></div></a></li>')
    return (f'<section class="sek {s.bg("projekt")}" aria-labelledby="pzig-h"><div class="wrap pzig-w">{_proj_huvud(s, "pzig-h")}'
            f'<ul class="pzig">{rader}</ul></div></section>')


@variant("projekt", "stor")
def projekt_stor(s):
    pr = s.b["projekt"]
    f = pr[0]
    kol = _kol(s)
    bild0 = s.bilder.ta(f.get("tagg"))
    stor = (f'<a class="psto-stor reveal" href="projekt.html"><div class="psto-bild">{s.bilder.fyll(bild0, "(min-width:960px) 66vw, 100vw")}</div>'
            f'<div class="psto-text">{_status_html(s, f, "psto-status")}<h3>{E(f["namn"])}</h3><p>{E(f["text"])}</p>'
            f'<dl class="psto-fakta"><div><dt>{E(kol[1])}</dt><dd>{E(f["ort"])}</dd></div><div><dt>{E(kol[2])}</dt><dd>{E(f["typ"])}</dd></div>'
            f'<div><dt>{E(kol[4])}</dt><dd>{E(f.get("ar", ""))}</dd></div></dl>{_lank_span(s, s.T("las_mer"))}</div></a>')
    sma = "".join(
        f'<li><a href="projekt.html"><div class="psto-foto">{s.bilder.img(s.bilder.ta(x.get("tagg")), "(min-width:1100px) 18vw, 45vw")}</div>'
        f'<h3>{E(x["namn"])}</h3><span>{E(x["ort"])} · {E(x.get("ar", ""))}</span></a></li>' for x in pr[1:6])
    return (f'<section class="sek {s.bg("projekt")}" aria-labelledby="psto-h"><div class="wrap psto-w">{_proj_huvud(s, "psto-h")}'
            f'{stor}<ul class="psto-sma psto-n{len(pr[1:6])}">{sma}</ul></div></section>')


@variant("projekt", "tabell")
def projekt_tabell(s):
    pr = s.b["projekt"]
    kol = _kol(s)
    rader = ""
    for x in pr:
        bild = s.bilder.ta(x.get("tagg"))
        rader += (f'<tr><th scope="row"><a href="projekt.html"><span class="ptab-foto">{s.bilder.img(bild, "80px")}</span><span class="ptab-namn">{E(x["namn"])}</span><span class="ptab-hover" aria-hidden="true">{re.sub(r'alt="[^"]*"', 'alt=""', s.bilder.img(bild, "240px"))}</span></a></th>'
                  f'<td class="ptab-ort" data-k="{E(kol[1])}">{E(x["ort"])}</td><td class="ptab-typ" data-k="{E(kol[2])}">{E(x["typ"])}</td>'
                  f'<td class="ptab-ar" data-k="{E(kol[4])}">{E(x.get("ar", ""))}</td><td class="ptab-st">{_status_html(s, x, "ptab-status")}</td>'
                  f'<td class="ptab-pil" aria-hidden="true">{PIL}</td></tr>')
    huvud = (f'<thead><tr><th scope="col">{E(kol[0])}</th><th scope="col">{E(kol[1])}</th><th scope="col">{E(kol[2])}</th>'
             f'<th scope="col">{E(kol[4])}</th><th scope="col">{E(kol[3])}</th><th scope="col"><span class="ptab-dold">{E(s.T("las_mer"))}</span></th></tr></thead>')
    rubrik = s.b.get("projekt_rubrik") or s.T("proj_rubrik_lista")
    return (f'<section class="sek {s.bg("projekt")}" aria-labelledby="ptab-h"><div class="wrap ptab-w">'
            f'<div class="ptab-huvud"><div><span class="etikett">{E(s.T("proj_etikett"))}</span><h2 id="ptab-h">{E(rubrik)}</h2></div>'
            f'<div class="ptab-antal"><b>{len(pr)}</b><span>{E(kol[0])}</span></div>{s.textlank(s.T("proj_lank"), "projekt.html")}</div>'
            f'<table class="ptab">{huvud}<tbody>{rader}</tbody></table></div></section>')


# --- Hållbarhet -----------------------------------------------------------------------------------------------------
@variant("hb", "citat")
def hb_citat(s):
    hb = s.b["hallbarhet"]
    mal = "".join(f'<li class="reveal"><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="hcit-h"><div class="wrap">'
            f'<span class="etikett">{E(s.T("hb_etikett"))}</span>'
            f'<figure class="hcit-fig"><span class="hcit-tecken" aria-hidden="true">&ldquo;</span><h2 id="hcit-h" class="hcit-rubrik">{E(hb["rubrik"])}</h2></figure>'
            f'<div class="hcit-under"><p class="ingress">{E(hb["text"])}</p><div>{s.knapp(s.T("hb_lank"), "hallbarhet.html", "kontur")}</div></div>'
            f'<ul class="hcit-mal hcit-n{len(hb["mal"])}">{mal}</ul></div></section>')


@variant("hb", "tre")
def hb_tre(s):
    hb = s.b["hallbarhet"]
    bild = s.bilder.ta(s.bt("hb"))
    mal = "".join(f'<li class="reveal"><span class="htre-nr">{i + 1:02d}</span><b>{E(a)}</b><span class="htre-t">{E(t)}</span></li>' for i, (a, t) in enumerate(hb["mal"]))
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="htre-h"><div class="wrap">'
            f'<div class="htre-huvud"><div><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="htre-h">{E(hb["rubrik"])}</h2></div>'
            f'<div><p>{E(hb["text"])}</p><div class="knappar">{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div></div></div>'
            f'<div class="htre-bild">{s.bilder.fyll(bild, "(min-width:1360px) 1300px, 100vw", note=True)}</div>'
            f'<ul class="htre-mal htre-n{len(hb["mal"])}">{mal}</ul></div></section>')


@variant("hb", "band")
def hb_band(s):
    hb = s.b["hallbarhet"]
    mal = "".join(f'<li class="reveal"><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
    return (f'<section class="sek hban {s.bg("hb")}" aria-labelledby="hban-h"><div class="wrap hban-topp">'
            f'<div><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="hban-h">{E(hb["rubrik"])}</h2></div>'
            f'<div class="hban-text"><p class="ingress">{E(hb["text"])}</p><div class="knappar">{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div></div></div>'
            f'<div class="hban-band"><div class="wrap"><ul class="hban-mal hban-n{len(hb["mal"])}">{mal}</ul></div></div></section>')


# --- Karriärpanel ---------------------------------------------------------------------------------------------------
@variant("panel", "kort")
def panel_kort(s):
    b, k = s.b, s.b["karriar"]
    bild = s.bilder.ta(s.bt("panel"))
    jobb = k.get("jobb") or []
    rad = ""
    if jobb:
        rad = '<ul class="pkor-jobb">' + "".join(f'<li><b>{E(t)}</b><span>{E(o)}</span></li>' for t, o in jobb[:3]) + "</ul>"
    return (f'<section class="pkor" aria-labelledby="pkor-h">{s.bilder.fyll(bild, note=True)}<div class="wrap">'
            f'<div class="pkor-kort reveal"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="pkor-h">{E(k["rubrik"])}</h2>'
            f'<p class="pkor-ingress">{E(k["text"])}</p><p class="pkor-kultur">{E(b.get("kultur") or s.T("kultur"))}</p>{rad}'
            f'<div class="knappar">{s.knapp(s.T("panel_knapp"), "karriar.html")}</div></div></div></section>')


@variant("panel", "delad")
def panel_delad(s):
    b, k = s.b, s.b["karriar"]
    bild = s.bilder.ta(s.bt("panel"))
    jobb = k.get("jobb") or []
    if jobb:
        lista = ('<ul class="pdel-jobb">' + "".join(
            f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span>{PIL}</a></li>' for t, o in jobb[:4]) + "</ul>")
    else:
        lista = f'<p class="pdel-kultur">{E(b.get("kultur") or s.T("kultur"))}</p>'
    knapp = s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html", "ljus")
    return (f'<section class="pdel" aria-labelledby="pdel-h"><div class="pdel-falt"><div class="pdel-inner reveal">'
            f'<span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="pdel-h">{E(k["rubrik"])}</h2><p class="pdel-text">{E(k["text"])}</p>'
            f'{lista}<div class="knappar">{knapp}</div></div></div>'
            f'<div class="pdel-bild">{s.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</div></section>')


@variant("panel", "kultur")
def panel_kultur(s):
    b, k = s.b, s.b["karriar"]
    bild = s.bilder.ta(s.bt("panel"))
    jobb = k.get("jobb") or []
    orter = list(dict.fromkeys(o for _, o in jobb if o))
    fakta = [f'<li class="pkul-f1"><p>{E(b.get("kultur") or s.T("kultur"))}</p></li>']
    if jobb:
        fakta.append(f'<li class="pkul-f2"><b>{len(jobb)}</b><span>{"ledig tjänst" if len(jobb) == 1 else "lediga tjänster"} just nu</span></li>')
        if orter:
            fakta.append(f'<li class="pkul-f3"><b>{len(orter)}</b><span>{"ort" if len(orter) == 1 else "orter"}: {E(", ".join(orter[:4]))}</span></li>')
    fakta_html = f'<ul class="pkul-fakta pkul-n{len(fakta)}">{"".join(fakta)}</ul>'
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="pkul-h"><div class="wrap pkul">'
            f'<div class="pkul-bild reveal">{s.bilder.fyll(bild, "(min-width:960px) 40vw, 100vw", note=True)}</div>'
            f'<div class="pkul-text"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="pkul-h">{E(k["rubrik"])}</h2>'
            f'<p class="ingress">{E(k["text"])}</p>{fakta_html}'
            f'<div class="knappar">{s.knapp(s.T("panel_knapp"), "karriar.html")}</div></div></div></section>')
