"""Varianter H: genvägar (snabb), omdömen, process och citat.

Prefix (alla börjar på h): .hv (gemensamma lokala färger), .hsb- (snabb/h-bento), .hso- (snabb/h-ord), .hsf- (snabb/h-flyt),
.hoc- (omdomen/h-chatt), .hot- (omdomen/h-tidning), .hoe- (omdomen/h-trappa), .hof- (omdomen/h-flik),
.hps- (process/h-stapel), .hpd- (process/h-dragspel), .hpp- (process/h-pilar), .hpb- (process/h-helbild), .hpz- (process/h-slinga),
.hcs- (citat/h-snitt), .hck- (citat/h-kort), .hcm- (citat/h-markor), .hcp- (citat/h-premium).
"""
import re

from varianter import variant, E, ikon, PIL

CIT = ('<svg class="{c}" viewBox="0 0 120 96" aria-hidden="true"><path fill="currentColor" d="M0 96V58C0 25 15 6 46 0l6 13C35 19 '
       '27 31 26 48h22v48zm68 0V58c0-33 15-52 46-58l6 13c-17 6-25 18-26 35h22v48z"/></svg>')
CIT_KONTUR = ('<svg class="{c}" viewBox="-4 -4 128 104" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M0 96V58C0 25 15 6 46 0l6 13C35 19 '
              '27 31 26 48h22v48zm68 0V58c0-33 15-52 46-58l6 13c-17 6-25 18-26 35h22v48z"/></svg>')


def nb(text):
    """Escapar och håller ihop tal som "21 000" och "4 900 kr" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", " ", E(text))


def stj(cls="stjarnor"):
    return f'<div class="{cls}" role="img" aria-label="5 av 5 stjärnor">{"".join(ikon("stjarna", "stj") for _ in range(5))}</div>'


def genvagar(s):
    """Samma genvägar som den inbyggda snabb-sektionen."""
    snabb = list(s.pr["snabb"])
    if snabb and snabb[-1][2] == "investerare" and not s.b.get("investerare", {}).get("kurs"):
        snabb[-1] = ("telefon", "Kontakta oss", "om-oss#kontakt")
    return snabb


def stegen(s):
    return s.b.get("process") or [{"titel": a["titel"], "text": a["text"], "tagg": a.get("tagg")} for a in s.b["affarsomraden"]]


def process_rubrik(s):
    return s.b.get("process_rubrik") or s.T("process_rubrik")


def citatet(s):
    return s.b.get("citat") or {"text": s.b["om"][1], "namn": "Vd", "roll": s.b["namn"]}


def omd(s):
    return s.b.get("omdomen") or []


def initial(namn):
    d = [w for w in re.split(r"[\s.]+", namn) if w]
    return E("".join(w[0] for w in d[:2]).upper() or "?")


def dela_citat(text):
    """Delar citatet i en inledning (första meningen/satsen) och resten."""
    m = re.search(r"(?<=[.!?:–])\s+", text)
    if m and 18 <= m.start() <= len(text) - 12:
        return text[:m.start()], text[m.end():]
    m = re.search(r"(?<=,)\s+", text)
    if m and 18 <= m.start() <= len(text) - 12:
        return text[:m.start()], text[m.end():]
    return text, ""


# =====================================================================================================================
# Snabb (genvägar)
# =====================================================================================================================
@variant("snabb", "h-bento")
def snabb_bento(s):
    sn = genvagar(s)
    a = ""
    for i, (ik, t, h) in enumerate(sn):
        a += (f'<a class="hsb-ruta" href="{s.u(h)}"><span class="hsb-topp">{ikon(ik, "ik hsb-ik")}<span class="hsb-pil">{PIL}</span></span>'
              f'{ikon(ik, "hsb-bak") if i == 0 else ""}<span class="hsb-fot"><span class="hsb-nr">{i + 1:02d}</span><b>{E(t)}</b></span></a>')
    return f'''<section class="sek sek-tat {s.bg("snabb")}" aria-label="{E(s.T("genvagar_etikett"))}"><div class="wrap hv">
  <nav class="hsb n{len(sn)}" aria-label="{E(s.T("genvagar_etikett"))}">{a}</nav></div></section>'''


@variant("snabb", "h-ord")
def snabb_ord(s):
    sn = genvagar(s)
    sep = '<span class="hso-sep" aria-hidden="true">/</span>'
    ord_ = " ".join(f'<a href="{s.u(h)}"><sup>{i + 1:02d}</sup><span>{E(t)}</span>{PIL}</a>{sep if i < len(sn) - 1 else ""}' for i, (_, t, h) in enumerate(sn))
    return f'''<section class="sek sek-tat {s.bg("snabb")}" aria-labelledby="hso-h"><div class="wrap hv hso">
  <div class="hso-topp"><span class="etikett" id="hso-h">{E(s.T("genvagar_etikett"))}</span><span class="hso-antal" aria-hidden="true">{len(sn):02d}</span></div>
  <nav class="hso-ord" aria-labelledby="hso-h">{ord_}</nav></div></section>'''


@variant("snabb", "h-flyt")
def snabb_flyt(s):
    sn = genvagar(s)
    a = "".join(f'<a href="{s.u(h)}"><span class="hsf-ik">{ikon(ik)}</span><span class="hsf-t"><small>{i + 1:02d}</small><b>{E(t)}</b></span><span class="hsf-pil">{PIL}</span></a>'
                for i, (ik, t, h) in enumerate(sn))
    return f'''<section class="hsf {s.bg("snabb")}" aria-label="{E(s.T("genvagar_etikett"))}"><div class="hsf-farg" aria-hidden="true"></div><div class="wrap hv">
  <span class="etikett hsf-et">{E(s.T("genvagar_etikett"))}</span>
  <nav class="hsf-kort n{len(sn)}" aria-label="{E(s.T("genvagar_etikett"))}">{a}</nav></div></section>'''


# =====================================================================================================================
# Omdömen
# =====================================================================================================================
@variant("omdomen", "h-chatt")
def omdomen_chatt(s):
    om = omd(s)
    li = ""
    for i, x in enumerate(om):
        ort = f'<span class="hoc-ort">{E(x["ort"])}</span>' if x.get("ort") else ""
        li += (f'<li class="hoc-rad reveal{" hoc-h" if i % 2 else ""}"><span class="hoc-av" aria-hidden="true">{initial(x["namn"])}</span>'
               f'<figure class="hoc-bubbla"><blockquote><p>{nb(x["text"])}</p></blockquote>'
               f'<figcaption><b>{E(x["namn"])}</b>{ort}{stj("stjarnor hoc-stj")}</figcaption></figure></li>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="hoc-h"><div class="wrap hv hoc">
  {s.huvud(s.T("omdomen_etikett"), s.T("omdomen_rubrik"), "hoc-h", mitt=True)}
  <ul class="hoc-trad">{li}</ul>
  <div class="hoc-svar"><span class="hoc-skriv" aria-hidden="true"><i></i><i></i><i></i></span>{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></section>'''


@variant("omdomen", "h-tidning")
def omdomen_tidning(s):
    om = omd(s)
    li = ""
    for x in om:
        ort = f', {E(x["ort"])}' if x.get("ort") else ""
        li += (f'<li class="reveal"><blockquote><p>{nb(x["text"].strip())}</p></blockquote>'
               f'<p class="hot-vem"><b>{E(x["namn"])}</b>{ort}</p></li>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="hot-h"><div class="wrap hv hot">
  <header class="hot-mast"><span class="hot-mast-et">{E(s.T("omdomen_etikett"))}</span><h2 id="hot-h">{E(s.T("omdomen_rubrik"))}</h2>
    <span class="hot-mast-fot">{stj("stjarnor hot-stj")}<span>{len(om)} röster</span></span></header>
  <ul class="hot-spalter n{len(om)}">{li}</ul></div></section>'''


@variant("omdomen", "h-trappa")
def omdomen_trappa(s):
    om = omd(s)
    li = ""
    for i, x in enumerate(om):
        ort = f'<span>{E(x["ort"])}</span>' if x.get("ort") else ""
        li += (f'<li class="hoe-kort reveal"><span class="hoe-bokstav" aria-hidden="true">{E(x["namn"][:1])}</span>'
               f'<span class="hoe-nr">{i + 1:02d} / {len(om):02d}</span><blockquote><p>”{nb(x["text"])}”</p></blockquote>'
               f'<div class="hoe-fot"><span class="hoe-vem"><b>{E(x["namn"])}</b>{ort}</span>{stj("stjarnor hoe-stj")}</div></li>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="hoe-h"><div class="wrap hv">
  {s.huvud(s.T("omdomen_etikett"), s.T("omdomen_rubrik"), "hoe-h", s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "kontur"))}
  <ul class="hoe-grid n{len(om)}">{li}</ul></div></section>'''


@variant("omdomen", "h-flik")
def omdomen_flik(s):
    om = omd(s)[:8]
    inp = "".join(f'<input class="hof-r" type="radio" name="hof-val" id="hof-{i}"{" checked" if i == 0 else ""} aria-label="{E(x["namn"])}">' for i, x in enumerate(om))
    scen = ""
    for i, x in enumerate(om):
        ort = f'<span>{E(x["ort"])}</span>' if x.get("ort") else ""
        scen += (f'<figure class="hof-p hof-p{i}">{stj("stjarnor hof-stj")}<blockquote><p>{nb(x["text"])}</p></blockquote>'
                 f'<figcaption><b>{E(x["namn"])}</b>{ort}</figcaption></figure>')
    flikar = "".join(f'<label class="hof-l hof-l{i}" for="hof-{i}"><span class="hof-av" aria-hidden="true">{initial(x["namn"])}</span>'
                     f'<span class="hof-lt"><b>{E(x["namn"])}</b>{f"<small>{E(x["ort"])}</small>" if x.get("ort") else ""}</span></label>' for i, x in enumerate(om))
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="hof-h"><div class="wrap hv">
  {s.huvud(s.T("omdomen_etikett"), s.T("omdomen_rubrik"), "hof-h")}
  <div class="hof n{len(om)}">{inp}
    <div class="hof-flikar">{flikar}</div>
    <div class="hof-scen">{CIT.format(c="hof-tecken")}{scen}</div></div></div></section>'''


# =====================================================================================================================
# Process
# =====================================================================================================================
@variant("process", "h-stapel")
def process_stapel(s):
    st = stegen(s)
    n = len(st)
    li = ""
    for i, x in enumerate(st):
        h = round(28 + 72 * (i + 1) / n) if n > 1 else 100
        li += (f'<li class="reveal" style="--h:{h}"><div class="hps-yta"><span class="hps-nr">{i + 1:02d}</span><span class="hps-bar" aria-hidden="true"></span></div>'
               f'<div class="hps-text"><h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></div></li>')
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="hps-h"><div class="wrap hv">
  {s.huvud(s.T("process_etikett"), process_rubrik(s), "hps-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ol class="hps n{n}">{li}</ol></div></section>'''


@variant("process", "h-dragspel")
def process_dragspel(s):
    st = stegen(s)
    bild = s.bilder.ta(st[0].get("tagg") if st else None)
    rad = ""
    for i, x in enumerate(st):
        rad += (f'<details class="hpd-rad"{" open" if i == 0 else ""}><summary><span class="hpd-nr" aria-hidden="true">{i + 1:02d}</span>'
                f'<span class="hpd-t"><small>Steg {i + 1} av {len(st)}</small><b>{E(x["titel"])}</b></span><span class="hpd-plus" aria-hidden="true"></span></summary>'
                f'<div class="hpd-in"><p>{nb(x["text"])}</p></div></details>')
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="hpd-h"><div class="wrap hv hpd">
  <div class="hpd-sida"><span class="etikett">{E(s.T("process_etikett"))}</span><h2 id="hpd-h">{E(process_rubrik(s))}</h2>
    <div class="hpd-bild">{s.bilder.fyll(bild, "(min-width:1000px) 36vw, 100vw", note=True)}</div>
    <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <div class="hpd-lista">{rad}</div></div></section>'''


@variant("process", "h-pilar")
def process_pilar(s):
    st = stegen(s)
    li = "".join(f'<li class="reveal"><div class="hpp-pil"><span class="hpp-nr">{i + 1:02d}</span><h3>{E(x["titel"])}</h3></div><p>{nb(x["text"])}</p></li>'
                 for i, x in enumerate(st))
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="hpp-h"><div class="wrap hv">
  {s.huvud(s.T("process_etikett"), process_rubrik(s), "hpp-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ol class="hpp n{len(st)}">{li}</ol></div></section>'''


@variant("process", "h-helbild")
def process_helbild(s):
    st = stegen(s)
    bild = s.bilder.ta(st[-1].get("tagg") if st else None)
    li = "".join(f'<li class="reveal"><span class="hpb-nr">{i + 1:02d}</span><h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></li>' for i, x in enumerate(st))
    return f'''<section class="hpb" aria-labelledby="hpb-h">{s.bilder.fyll(bild, "100vw")}<div class="hpb-skugga" aria-hidden="true"></div>
  <div class="wrap hpb-in"><div class="hpb-huvud"><span class="etikett">{E(s.T("process_etikett"))}</span><h2 id="hpb-h">{E(process_rubrik(s))}</h2>
    {s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}</div>
  <ol class="hpb-steg n{len(st)}">{li}</ol></div><span class="foto-not">Illustrationsbild</span></section>'''


@variant("process", "h-slinga")
def process_slinga(s):
    st = stegen(s)
    li = ""
    for i, x in enumerate(st):
        bild = s.bilder.ta(x.get("tagg"))
        li += (f'<li class="hpz-steg reveal{" hpz-v" if i % 2 else ""}"><span class="hpz-nod" aria-hidden="true">{i + 1}</span>'
               f'<div class="hpz-bild">{s.bilder.img(bild, "(min-width:900px) 34vw, 85vw")}</div>'
               f'<div class="hpz-text"><span class="hpz-steg-nr">Steg {i + 1:02d}</span><h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></div></li>')
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="hpz-h"><div class="wrap hv">
  {s.huvud(s.T("process_etikett"), process_rubrik(s), "hpz-h", mitt=True)}
  <ol class="hpz">{li}</ol>
  <div class="hpz-slut"><span class="hpz-slut-nod" aria-hidden="true">{ikon("pil", "pil")}</span>{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></section>'''


# =====================================================================================================================
# Citat
# =====================================================================================================================
@variant("citat", "h-snitt")
def citat_snitt(s):
    c = citatet(s)
    bild = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    return f'''<section class="hcs" aria-label="Citat"><div class="hcs-panel"><div class="hcs-in reveal">{CIT_KONTUR.format(c="hcs-tecken")}
    <figure><blockquote><p>{nb(c["text"])}</p></blockquote><figcaption><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></figure></div></div>
  <div class="hcs-bild">{s.bilder.fyll(bild, "(min-width:900px) 45vw, 100vw", note=True)}</div></section>'''


@variant("citat", "h-kort")
def citat_kort(s):
    c = citatet(s)
    bild = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap hv hck">
  <div class="hck-bild">{s.bilder.fyll(bild, "(min-width:900px) 66vw, 100vw", note=True)}</div>
  <figure class="hck-kort reveal">{CIT.format(c="hck-tecken")}<blockquote><p>{nb(c["text"])}</p></blockquote>
    <figcaption><span class="hck-av" aria-hidden="true">{initial(c["namn"])}</span><span><b>{E(c["namn"])}</b><small>{E(c["roll"])}</small></span></figcaption></figure></div></section>'''


@variant("citat", "h-markor")
def citat_markor(s):
    c = citatet(s)
    a, b = dela_citat(c["text"])
    rest = f' {nb(b)}' if b else ""
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap hv hcm">
  <div class="hcm-sida" aria-hidden="true"><span class="hcm-lodrat">{E(c["namn"])} — {E(c["roll"])}</span></div>
  <figure class="hcm-fig reveal"><span class="hcm-tecken" aria-hidden="true">”</span>
    <blockquote><p><mark>{nb(a)}</mark>{rest}</p></blockquote>
    <figcaption><span class="hcm-streck" aria-hidden="true"></span><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></figure></div></section>'''


@variant("citat", "h-premium")
def citat_premium(s):
    c = citatet(s)
    a, b = dela_citat(c["text"])
    rest = f' <span class="hcp-dim">{nb(b)}</span>' if b else ""
    return f'''<section class="hcp" aria-label="Citat"><div class="hcp-glyf" aria-hidden="true">{CIT_KONTUR.format(c="hcp-svg")}</div><div class="wrap hcp-in">
  <figure class="hcp-fig reveal"><span class="hcp-monogram" aria-hidden="true">{initial(c["namn"])}</span>
    <blockquote><p>{nb(a)}{rest}</p></blockquote>
    <figcaption><span class="hcp-linje" aria-hidden="true"></span><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span><span class="hcp-linje" aria-hidden="true"></span></figcaption></figure></div></section>'''
