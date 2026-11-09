"""Varianter C: nyheter, citat, process, omdömen och priser.

Prefix: .nk- (nyheter/kort), .nm- (nyheter/minimal), .ns- (nyheter/sida), .cs- (citat/stor), .cb- (citat/bild),
.cd- (citat/sida), .pl- (process/linje), .pv- (process/vertikal), .pk- (process/kort), .or- (omdomen/rad),
.ob- (omdomen/betyg), .pt- (priser/tabell), .pp- (priser/lista). Gemensam färghjälp: .vc (lokala variabler för mut/linje).
"""
import re

from varianter import variant, E, ikon, PIL

MAN = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
CITATTECKEN = ('<svg class="{c}" viewBox="0 0 120 96" aria-hidden="true"><path fill="currentColor" d="M0 96V58C0 25 15 6 46 0l6 13C35 19 '
               '27 31 26 48h22v48zm68 0V58c0-33 15-52 46-58l6 13c-17 6-25 18-26 35h22v48z"/></svg>')
BOCK = '<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def nb(text):
    """Escapar och håller ihop tal som "21 000" och "4 900 kr" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", "\u00a0", E(text))


def datum(d, kort=False):
    """2026-10-23 -> '23 okt 2026' (eller ('23', 'okt 2026') med kort=True). Annat format lämnas orört."""
    try:
        a, m, dag = d.split("-")
        dag_ = str(int(dag))
        ut = (dag_, f"{MAN[int(m) - 1]} {a}")
    except (ValueError, IndexError):
        ut = (d, "")
    return ut if kort else " ".join(x for x in ut if x)


def nyhetsbild(s, rad):
    return s.bilder.ta(rad[3] if len(rad) > 3 and rad[3] else s.b.get("nyhet_tagg"))


def citatet(s):
    return s.b.get("citat") or {"text": s.b["om"][1], "namn": "Vd", "roll": s.b["namn"]}


def stegen(s):
    return s.b.get("process") or [{"titel": a["titel"], "text": a["text"], "tagg": a.get("tagg")} for a in s.b["affarsomraden"]]


def process_huvud(s, id_, hoger=""):
    return s.huvud(s.T("process_etikett"), s.b.get("process_rubrik") or s.T("process_rubrik"), id_, hoger)


def stjarnor(cls="stjarnor"):
    return f'<div class="{cls}" role="img" aria-label="5 av 5 stjärnor">{"".join(ikon("stjarna", "stj") for _ in range(5))}</div>'


# --- Nyheter ------------------------------------------------------------------------------------------------------
@variant("nyheter", "kort")
def nyheter_kort(s):
    ny = s.b["nyheter"][:3]
    kort = ""
    for rad in ny:
        d, t = rad[0], rad[1]
        bild = nyhetsbild(s, rad)
        ingress = f'<p class="nk-ingress">{nb(rad[2])}</p>' if len(rad) > 2 and rad[2] else ""
        kort += (f'<li class="nk-kort reveal"><a href="om-oss.html#press"><div class="nk-foto">{s.bilder.img(bild, "(min-width:1000px) 31vw, (min-width:700px) 46vw, 92vw")}</div>'
                 f'<div class="nk-text"><time datetime="{E(d)}">{E(datum(d))}</time><h3>{nb(t)}</h3>{ingress}<span class="nk-las">Läs mer {PIL}</span></div></a></li>')
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="nk-h"><div class="wrap vc">
  {s.huvud(s.T("ny_etikett2"), s.T("ny_senaste"), "nk-h", s.textlank(s.T("ny_lank"), "om-oss.html#press"))}
  <ul class="nk-grid n{len(ny)}">{kort}</ul></div></section>'''


@variant("nyheter", "minimal")
def nyheter_minimal(s):
    rader = ""
    for rad in s.b["nyheter"]:
        d, t = rad[0], rad[1]
        dag, rest = datum(d, kort=True)
        rader += (f'<li><a href="om-oss.html#press"><time class="nm-datum" datetime="{E(d)}"><b>{E(dag)}</b><span>{E(rest)}</span></time>'
                  f'<h3>{nb(t)}</h3><span class="nm-pil">{PIL}</span></a></li>')
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="nm-h"><div class="wrap vc">
  {s.huvud(s.T("ny_etikett"), s.T("ny_rubrik"), "nm-h", s.textlank(s.T("ny_lank"), "om-oss.html#press"))}
  <ol class="nm-lista">{rader}</ol></div></section>'''


@variant("nyheter", "sida")
def nyheter_sida(s):
    ny = s.b["nyheter"]
    forsta = ny[0]
    bild = nyhetsbild(s, forsta)
    ingress = f'<p>{E(forsta[2])}</p>' if len(forsta) > 2 and forsta[2] else ""
    lista = ""
    for rad in ny[1:]:
        d, t = rad[0], rad[1]
        ing = f'<p>{E(rad[2])}</p>' if len(rad) > 2 and rad[2] else ""
        lista += f'<li><a href="om-oss.html#press"><time datetime="{E(d)}">{E(datum(d))}</time><h3>{nb(t)}</h3>{ing}</a></li>'
    return f'''<section class="sek {s.bg("nyheter")}" aria-labelledby="ns-h"><div class="wrap vc">
  {s.huvud(s.T("ny_etikett2"), s.T("ny_rubrik"), "ns-h")}
  <div class="ns-grid">
    <a class="ns-stor reveal" href="om-oss.html#press"><div class="ns-foto">{s.bilder.img(bild, "(min-width:1000px) 58vw, 100vw")}</div>
      <div class="ns-panel"><time datetime="{E(forsta[0])}">{E(datum(forsta[0]))}</time><h3>{E(forsta[1])}</h3>{ingress}<span class="ns-las">Läs nyheten {PIL}</span></div></a>
    <div class="ns-sido"><ul class="ns-lista">{lista}</ul><div class="ns-fot">{s.knapp(s.T("ny_lank"), "om-oss.html#press", "kontur")}</div></div>
  </div></div></section>'''


# --- Citat --------------------------------------------------------------------------------------------------------
@variant("citat", "stor")
def citat_stor(s):
    c = citatet(s)
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap vc">
  <figure class="cs-fig reveal">{CITATTECKEN.format(c="cs-tecken")}
    <blockquote><p>{nb(c["text"])}</p></blockquote>
    <figcaption><span class="cs-streck" aria-hidden="true"></span><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></figure></div></section>'''


@variant("citat", "bild")
def citat_bild(s):
    c = citatet(s)
    bild = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    return f'''<section class="cb" aria-label="Citat"><div class="cb-bild">{s.bilder.fyll(bild, "100vw", note=True)}</div>
  <div class="wrap cb-inne"><figure class="cb-fig reveal">{CITATTECKEN.format(c="cb-tecken")}
    <blockquote><p>{nb(c["text"])}</p></blockquote>
    <figcaption><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></figure></div></section>'''


@variant("citat", "sida")
def citat_sida(s):
    c = citatet(s)
    bild = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap vc cd-grid">
  <figure class="cd-fig reveal"><span class="etikett">{E(s.b.get("kortnamn", ""))}</span>
    <blockquote><p>”{nb(c["text"])}”</p></blockquote>
    <figcaption><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></figure>
  <div class="cd-bild reveal">{s.bilder.fyll(bild, "(min-width:900px) 45vw, 100vw", note=True)}</div></div></section>'''


# --- Process ------------------------------------------------------------------------------------------------------
@variant("process", "linje")
def process_linje(s):
    st = stegen(s)
    li = "".join(f'<li class="reveal"><span class="pl-nr">{i + 1:02d}</span><h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></li>' for i, x in enumerate(st))
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="pl-h"><div class="wrap vc">
  {process_huvud(s, "pl-h")}
  <ol class="pl-lista" style="--n:{len(st)}">{li}</ol></div></section>'''


@variant("process", "vertikal")
def process_vertikal(s):
    st = stegen(s)
    li = "".join(f'<li class="reveal"><span class="pv-nr" aria-hidden="true">{i + 1:02d}</span><div class="pv-text"><span class="pv-steg">Steg {i + 1} av {len(st)}</span>'
                 f'<h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></div></li>' for i, x in enumerate(st))
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="pv-h"><div class="wrap vc pv-grid">
  <div class="pv-huvud"><span class="etikett">{E(s.T("process_etikett"))}</span><h2 id="pv-h">{E(s.b.get("process_rubrik") or s.T("process_rubrik"))}</h2>
    <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <ol class="pv-lista">{li}</ol></div></section>'''


@variant("process", "kort")
def process_kort(s):
    st = stegen(s)
    li = "".join(f'<li class="pk-kort reveal"><div class="pk-topp"><span class="pk-nr">{i + 1:02d}</span><span class="pk-form f{i % 4}" aria-hidden="true"><i></i><i></i></span></div>'
                 f'<h3>{E(x["titel"])}</h3><p>{nb(x["text"])}</p></li>' for i, x in enumerate(st))
    bg = s.bg("process") or "pa-farg"
    return f'''<section class="sek {bg}" aria-labelledby="pk-h"><div class="wrap vc">
  {process_huvud(s, "pk-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ol class="pk-grid n{len(st)}">{li}</ol></div></section>'''


# --- Omdömen ------------------------------------------------------------------------------------------------------
@variant("omdomen", "rad")
def omdomen_rad(s):
    om = s.b.get("omdomen") or []
    li = ""
    for x in om:
        ort = f'<small>{E(x["ort"])}</small>' if x.get("ort") else ""
        li += (f'<li class="or-kort">{CITATTECKEN.format(c="or-tecken")}<blockquote><p>{nb(x["text"])}</p></blockquote>'
               f'<div class="or-fot"><span class="or-initial" aria-hidden="true">{E(x["namn"][:1])}</span><span class="or-vem"><b>{E(x["namn"])}</b>{ort}</span>'
               f'{stjarnor("stjarnor or-stj")}</div></li>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="or-h"><div class="wrap vc">
  {s.huvud(s.T("omdomen_etikett"), s.T("omdomen_rubrik"), "or-h", '<p class="or-tips" aria-hidden="true">Dra i sidled</p>')}
  <ul class="or-rad n{len(om)}" tabindex="0" aria-label="{E(s.T("omdomen_rubrik"))}">{li}</ul></div></section>'''


@variant("omdomen", "betyg")
def omdomen_betyg(s):
    om = s.b.get("omdomen") or []
    li = "".join(f'<li class="reveal">{stjarnor("stjarnor ob-stj")}<blockquote><p>”{nb(x["text"])}”</p></blockquote>'
                 f'<span class="ob-namn"><b>{E(x["namn"])}</b>{(" · " + E(x["ort"])) if x.get("ort") else ""}</span></li>' for x in om)
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="ob-h"><div class="wrap vc ob-grid">
  <div class="ob-sam"><span class="etikett">{E(s.T("omdomen_etikett"))}</span><h2 id="ob-h">{E(s.T("omdomen_rubrik"))}</h2>
    <div class="ob-betyg"><b>5,0</b><div>{stjarnor("stjarnor ob-stora")}<span>Snittbetyg i {len(om)} utvalda omdömen</span></div></div>
    <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <ul class="ob-lista">{li}</ul></div></section>'''


# --- Priser -------------------------------------------------------------------------------------------------------
def priser_huvud(s, id_):
    return s.huvud(s.T("priser_etikett"), s.b.get("priser_rubrik") or s.T("priser_rubrik"), id_, s.textlank("Alla priser", "priser.html"))


def punkter_med_arv(pr, x, djup=0):
    """Punkterna för ett paket, där "Allt i <paket>" ersätts med det paketets punkter (så att tabellen blir rättvisande)."""
    namn = {y["namn"].lower(): y for y in pr}
    ut = []
    for p in x.get("punkter", []):
        m = re.match(r"(?:allt|allt som ingår) i (.+)$", p.strip(), re.I)
        if m and m.group(1).strip().lower() in namn and djup < 3:
            ut += [q for q in punkter_med_arv(pr, namn[m.group(1).strip().lower()], djup + 1) if q not in ut]
        elif p not in ut:
            ut.append(p)
    return ut


@variant("priser", "tabell")
def priser_tabell(s):
    pr = s.b.get("priser") or []
    n = len(pr)
    ingar = [punkter_med_arv(pr, x) for x in pr]
    rader = []
    for pk in ingar:
        for p in pk:
            if p not in rader:
                rader.append(p)
    kol = ""
    for x in pr:
        utv = x.get("utvald")
        flagga = f'<span class="pt-utvald">{E(s.T("priser_utvald"))}</span>' if utv else ""
        kol += (f'<th scope="col" class="pt-paket{" utv" if utv else ""}">{flagga}<span class="pt-namn">{E(x["namn"])}</span>'
                f'<span class="pt-pris">{nb(x["pris"])}</span><span class="pt-enhet">{E(x.get("enhet", ""))}</span></th>')
    text = "".join(f'<td class="{"utv" if x.get("utvald") else ""}">{E(x.get("text", ""))}</td>' for x in pr)
    body = f'<tr class="pt-textrad"><th scope="row">Passar för</th>{text}</tr>'
    for r in rader:
        celler = "".join(f'<td class="{"utv" if x.get("utvald") else ""}">' + (BOCK.format(c="pt-bock") + '<span class="pt-sr">Ingår</span>' if r in pk else '<span class="pt-nej" aria-hidden="true"></span><span class="pt-sr">Ingår inte</span>') + '</td>' for x, pk in zip(pr, ingar))
        body += f'<tr><th scope="row">{E(r)}</th>{celler}</tr>'
    knappar = "".join(f'<td class="{"utv" if x.get("utvald") else ""}">{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt", "primar" if x.get("utvald") else "kontur")}</td>' for x in pr)
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="pt-h"><div class="wrap vc">
  {priser_huvud(s, "pt-h")}
  <table class="pt-tabell" style="--n:{n}"><thead><tr><td class="pt-horn"></td>{kol}</tr></thead><tbody>{body}</tbody>
  <tfoot><tr><td class="pt-horn"></td>{knappar}</tr></tfoot></table>
  <p class="pt-not">{E(s.b.get("priser_not") or s.T("priser_not"))}</p></div></section>'''


@variant("priser", "lista")
def priser_lista(s):
    pr = s.b.get("priser") or []
    li = ""
    for x in pr:
        utv = x.get("utvald")
        pkt = "".join(f"<li>{BOCK.format(c='pp-bock')}<span>{E(p)}</span></li>" for p in x.get("punkter", []))
        flagga = f'<span class="pp-utvald">{E(s.T("priser_utvald"))}</span>' if utv else ""
        li += (f'<li class="pp-rad{" utv" if utv else ""} reveal"><div class="pp-info"><div class="pp-namnrad"><h3>{E(x["namn"])}</h3>{flagga}</div>'
               f'<p class="pp-text">{E(x.get("text", ""))}</p><ul class="pp-punkter">{pkt}</ul></div>'
               f'<div class="pp-kop"><b class="pp-pris">{nb(x["pris"])}</b><span class="pp-enhet">{E(x.get("enhet", ""))}</span>'
               f'{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt", "primar" if utv else "kontur")}</div></li>')
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="pp-h"><div class="wrap vc">
  {priser_huvud(s, "pp-h")}
  <ul class="pp-lista">{li}</ul>
  <p class="pp-not">{E(s.b.get("priser_not") or s.T("priser_not"))}</p></div></section>'''
