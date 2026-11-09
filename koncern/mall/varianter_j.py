"""Varianter J: bokning, certifikat, kunder, uppmaning (cta), bolag, nyckeltal och projekt.

Prefix per variant (CSS i varianter_j.css):
  boka/j-bild .jbb-   boka/j-mork .jbm-   boka/j-flik .jbf-
  certifikat/j-sigill .jcs-   certifikat/j-register .jcr-
  logos/j-rutnat .jlr-   logos/j-ordbild .jlo-
  cta/j-telefon .jct-   cta/j-diagonal .jcd-   cta/j-biljett .jcb-   cta/j-kontur .jck-
  bolag/j-fack .jbo-   siffror/j-trappa .jst-   projekt/j-index .jpi-
"""
from varianter import variant, E, ikon, PIL


def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _info(s):
    """Kontaktvägar för bokningsvarianterna: (etikett, html)."""
    k = s.b["kontakt"]
    ut = [("Telefon", f'<a href="tel:{_tel(k["telefon"])}">{E(k["telefon"])}</a>')]
    if k.get("epost"):
        ut.append(("E-post", f'<a href="mailto:{E(k["epost"])}">{E(k["epost"])}</a>'))
    if s.b.get("oppettider"):
        ut.append(("Öppettider", E(s.b["oppettider"])))
    return ut


def _falt(s, pre, rader=4):
    falt = s.T("boka_falt")
    typer = [("text", "name"), ("tel", "tel"), ("email", "email")]
    inp = "".join(f'<label class="{pre}-f {pre}-f{i}"><span>{E(f)}</span><input type="{t}" name="f{i}" autocomplete="{ac}"></label>'
                  for i, (f, (t, ac)) in enumerate(zip(falt[:3], typer)))
    inp += f'<label class="{pre}-f {pre}-f3"><span>{E(falt[3])}</span><textarea name="f3" rows="{rader}"></textarea></label>'
    return inp


def _skicka(s, pre, typ="primar"):
    return (f'<div class="{pre}-skicka"><button class="knapp knapp-{typ}" type="submit"><span>{E(s.T("boka_knapp"))}</span>{PIL}</button>'
            f'<p class="{pre}-tack" id="{pre}-tack" role="status">Tack! Det här är en exempelsajt – formuläret skickar inget.</p></div>')


def _rubrik_boka(s):
    return s.b.get("boka_rubrik") or s.T("boka_rubrik")


def _text_boka(s):
    return s.b.get("boka_text") or s.T("boka_text")


# --- Bokning ------------------------------------------------------------------------------------------------------------
@variant("boka", "j-bild")
def boka_bild(s):
    """Helhöjdsbild kant i kant till vänster med kontaktuppgifterna på en panel, formulär med linjefält till höger."""
    bild = s.bilder.ta(s.bt("sida_om"))
    dl = "".join(f'<div><dt>{a}</dt><dd>{b_}</dd></div>' for a, b_ in _info(s))
    return f'''<section class="jbb {s.bg("boka")}" aria-labelledby="jbb-h" id="boka">
  <div class="jbb-bild">{s.bilder.fyll(bild, "(min-width:1000px) 50vw, 100vw", note=True)}<dl class="jbb-info">{dl}</dl></div>
  <div class="jbb-hoger"><div class="jbb-inner"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jbb-h">{E(_rubrik_boka(s))}</h2><p class="ingress">{E(_text_boka(s))}</p>
  <form class="jbb-form" action="#jbb-tack" method="get">{_falt(s, "jbb", 3)}{_skicka(s, "jbb")}</form></div></div></section>'''


@variant("boka", "j-mork")
def boka_mork(s):
    """Mörk premiumsektion: rubrik och jättestort telefonnummer överst, formuläret som en enda rad fält under en linje."""
    k = s.b["kontakt"]
    ovr = "".join(f'<li><small>{a}</small>{b_}</li>' for a, b_ in _info(s)[1:])
    return f'''<section class="sek jbm pa-mork" aria-labelledby="jbm-h" id="boka"><div class="wrap">
  <div class="jbm-topp"><div><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jbm-h">{E(_rubrik_boka(s))}</h2><p class="jbm-text">{E(_text_boka(s))}</p></div>
  <div class="jbm-ring"><small>Ring direkt</small><a class="jbm-tel" href="tel:{_tel(k["telefon"])}">{E(k["telefon"])}</a><ul class="jbm-ovr">{ovr}</ul></div></div>
  <form class="jbm-form" action="#jbm-tack" method="get">{_falt(s, "jbm", 1)}{_skicka(s, "jbm", "ljus")}</form></div></section>'''


@variant("boka", "j-flik")
def boka_flik(s):
    """Färgat band med rubriken, ett kort som överlappar bandet: smal infokolumn i tonfärg och formulär bredvid."""
    dl = "".join(f'<li><small>{a}</small><span>{b_}</span></li>' for a, b_ in _info(s))
    return f'''<section class="jbf {s.bg("boka")}" aria-labelledby="jbf-h" id="boka">
  <div class="jbf-band pa-farg"><div class="wrap jbf-bandin"><div><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jbf-h">{E(_rubrik_boka(s))}</h2></div><p class="ingress">{E(_text_boka(s))}</p></div></div>
  <div class="wrap"><div class="jbf-kort"><aside class="jbf-sida">{ikon("telefon")}<ul>{dl}</ul></aside>
  <form class="jbf-form" action="#jbf-tack" method="get">{_falt(s, "jbf", 4)}{_skicka(s, "jbf")}</form></div></div></section>'''


# --- Certifikat ---------------------------------------------------------------------------------------------------------
def _cert(s):
    return s.b.get("certifikat") or [], s.b.get("certifikat_rubrik") or s.T("certifikat_rubrik")


@variant("certifikat", "j-sigill")
def certifikat_sigill(s):
    """Centrerat: varje certifikat som ett runt sigill med streckad ring, titel och text under."""
    c, rubrik = _cert(s)
    li = "".join(f'<li class="reveal"><span class="jcs-sigill" aria-hidden="true"><span class="jcs-ring"></span>{ikon(x.get("ikon", "skold"))}<small>{i + 1:02d}</small></span>'
                 f'<b>{E(x["titel"])}</b>{f"""<span>{E(x["text"])}</span>""" if x.get("text") else ""}</li>' for i, x in enumerate(c))
    return f'''<section class="sek {s.bg("certifikat")}" aria-labelledby="jcs-h"><div class="wrap">
  {s.huvud(s.T("certifikat_etikett"), rubrik, "jcs-h", mitt=True)}<ul class="jcs n{len(c)}">{li}</ul></div></section>'''


@variant("certifikat", "j-register")
def certifikat_register(s):
    """Delad 40/60: klistrad rubrikkolumn med antal, till höger ett register med stora konturnummer och raka linjer."""
    c, rubrik = _cert(s)
    li = "".join(f'<li class="reveal"><span class="jcr-nr" aria-hidden="true">{i + 1:02d}</span><div class="jcr-txt"><h3>{E(x["titel"])}</h3>'
                 f'{f"""<p>{E(x["text"])}</p>""" if x.get("text") else ""}</div><span class="jcr-ik">{ikon(x.get("ikon", "skold"))}</span></li>' for i, x in enumerate(c))
    return f'''<section class="sek {s.bg("certifikat")}" aria-labelledby="jcr-h"><div class="wrap jcr">
  <div class="jcr-huvud"><span class="etikett">{E(s.T("certifikat_etikett"))}</span><h2 id="jcr-h">{E(rubrik)}</h2>
</div><ol class="jcr-lista">{li}</ol></div></section>'''


# --- Kunder -------------------------------------------------------------------------------------------------------------
def _kunder(s):
    return s.b.get("kunder") or [], s.b.get("kunder_rubrik") or s.T("logos_rubrik")


@variant("logos", "j-rutnat")
def logos_rutnat(s):
    """Logovägg: rubrikruta i färg följd av ett rutnät med hårfina linjer där varje namn sätts som ett ordmärke."""
    ls, rubrik = _kunder(s)
    stil = ["jlr-a", "jlr-b", "jlr-c"]
    li = "".join(f'<li class="{stil[i % 3]}"><span>{E(n)}</span></li>' for i, n in enumerate(ls))
    k = 3 if len(ls) % 3 == 0 and len(ls) % 4 else 4
    return f'''<section class="sek sek-tat {s.bg("logos")}" aria-labelledby="jlr-h"><div class="wrap"><div class="jlr">
  <div class="jlr-forsta pa-farg"><span class="etikett">{E(s.T("logos_etikett"))}</span><h2 id="jlr-h">{E(rubrik)}</h2><b class="jlr-antal" aria-hidden="true">{len(ls):02d}</b></div>
  <ul class="jlr-lista k{k}">{li}</ul></div></div></section>'''


@variant("logos", "j-ordbild")
def logos_ordbild(s):
    """Ordbild: alla uppdragsgivare som en löpande, stor typografisk text med snedstreck, varannan nedtonad."""
    ls, rubrik = _kunder(s)
    ord_ = "".join(f'<li><span>{E(n)}</span></li>' for n in ls)
    return f'''<section class="sek {s.bg("logos")}" aria-labelledby="jlo-h"><div class="wrap jlo">
  <div class="jlo-sida"><span class="etikett">{E(s.T("logos_etikett"))}</span><h2 id="jlo-h">{E(rubrik)}</h2><span class="jlo-antal mut">{len(ls)} i urval</span></div>
  <ul class="jlo-ord">{ord_}</ul></div></section>'''


# --- Uppmaning (cta) ----------------------------------------------------------------------------------------------------
def _cta(s):
    return s.b.get("fot_cta") or s.T("fot_cta")


@variant("cta", "j-telefon")
def cta_telefon(s):
    """Centrerad och minimalistisk: uppmaningen som ingress, telefonnumret som jätterubrik och en knapp under."""
    k = s.b["kontakt"]
    return f'''<section class="sek jct {s.bg("cta") or "pa-ton"}" aria-labelledby="jct-h"><div class="wrap jct-in">
  <span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jct-h">{E(_cta(s))}</h2>
  <a class="jct-tel" href="tel:{_tel(k["telefon"])}"><span class="jct-ik">{ikon("telefon")}</span><span>{E(k["telefon"])}</span></a>
  <div class="jct-fot">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}{f'<a class="jct-mejl" href="mailto:{E(k["epost"])}">{E(k["epost"])}</a>' if k.get("epost") else ""}</div></div></section>'''


@variant("cta", "j-diagonal")
def cta_diagonal(s):
    """Mörkt färgblock med text till vänster och en bild som skärs av med ett diagonalt snitt till höger."""
    k = s.b["kontakt"]
    bild = s.bilder.ta(s.bt("sida_om"))
    return f'''<section class="jcd pa-mork" aria-labelledby="jcd-h"><div class="jcd-bild">{s.bilder.fyll(bild, "(min-width:900px) 50vw, 100vw", note=True)}</div>
  <div class="wrap jcd-wrap"><div class="jcd-text"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jcd-h">{E(_cta(s))}</h2>
  <div class="jcd-vagar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<a class="jcd-tel" href="tel:{_tel(k["telefon"])}"><small>Ring oss</small><span>{E(k["telefon"])}</span></a></div></div></div></section>'''


@variant("cta", "j-biljett")
def cta_biljett(s):
    """En biljett: ett kort med perforerad skiljelinje, uppmaningen på huvuddelen och telefon och knapp på stubben."""
    k = s.b["kontakt"]
    return f'''<section class="sek jcb {s.bg("cta")}" aria-labelledby="jcb-h"><div class="wrap">
  <div class="jcb-kort"><div class="jcb-huvud"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="jcb-h">{E(_cta(s))}</h2></div>
  <div class="jcb-stubbe"><small>Ring oss</small><a class="jcb-tel" href="tel:{_tel(k["telefon"])}">{E(k["telefon"])}</a>
  {s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></div></section>'''


@variant("cta", "j-kontur")
def cta_kontur(s):
    """Ett enormt konturord i bakgrunden bakom uppmaningen, med kontaktvägarna i en rad längst ned."""
    k = s.b["kontakt"]
    ord_ = s.T("boka_etikett")
    return f'''<section class="sek jck pa-farg" aria-labelledby="jck-h"><div class="jck-ord" aria-hidden="true">{E(ord_)}</div><div class="wrap jck-in">
  <h2 id="jck-h">{E(_cta(s))}</h2>
  <div class="jck-rad">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<a class="jck-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>
  {f'<a class="jck-tel" href="mailto:{E(k["epost"])}">{ikon("dokument")}<span>{E(k["epost"])}</span></a>' if k.get("epost") else ""}</div></div></section>'''


# --- Bolag --------------------------------------------------------------------------------------------------------------
@variant("bolag", "j-fack")
def bolag_fack(s):
    """Horisontellt dragspel: höga bildfack sida vid sida där det som hålls över (eller fokuseras) vidgas och visar texten."""
    bl = s.bolagslista()
    knapp = s.knapp(s.T("bolag_knapp"), "verksamhet.html", "kontur")
    li = ""
    for i, x in enumerate(bl):
        bild = s.bilder.ta(x.get("tagg"))
        li += (f'<li class="jbo-fack"><a href="bolag.html#bolag-{i}">{s.bilder.fyll(bild, "(min-width:900px) 50vw, 100vw")}'
               f'<span class="jbo-nr">{i + 1:02d}</span><span class="jbo-stod">{E(x["namn"])}</span>'
               f'<span class="jbo-text"><small>{E(x.get("segment", ""))}</small><b>{E(x["namn"])}</b><span class="jbo-p">{E(x["text"])}</span>'
               f'<span class="textlank"><span>{E(s.T("bolag_till", namn=x["namn"]))}</span>{PIL}</span></span></a></li>')
    rubrik = s.b.get("bolag_rubrik") or s.T("bolag_rubrik")
    return f'''<section class="sek {s.bg("bolag")}" aria-labelledby="jbo-h"><div class="wrap">
  {s.huvud(s.T("bolag_etikett"), rubrik, "jbo-h", knapp)}<ul class="jbo n{len(bl)}">{li}</ul></div></section>'''


# --- Nyckeltal ----------------------------------------------------------------------------------------------------------
@variant("siffror", "j-trappa")
def siffror_trappa(s):
    """Trappa: nyckeltalen som stigande färgblock (som ett podium) med värdet ovanpå och texten om företaget till vänster."""
    b = s.b
    nt = b["nyckeltal"]
    n = len(nt)
    li = "".join(f'<li style="--j:{i};--n:{n}"><div class="jst-tal"><b>{E(x["varde"])}<small>{E(x["enhet"])}</small></b><span>{E(x["etikett"])}</span></div>'
                 f'<span class="jst-steg" aria-hidden="true"><i>{i + 1:02d}</i></span></li>' for i, x in enumerate(nt))
    rubrik = b.get("intro_rubrik", b["slogan"])
    return f'''<section class="sek jst {s.bg("siffror")}" aria-labelledby="jst-h"><div class="wrap jst-grid">
  <div class="jst-huvud"><span class="etikett">{E(s.T("siffror_etikett"))}</span><h2 id="jst-h">{E(rubrik)}</h2><p class="mut">{E(b["om"][0])}</p></div>
  <ol class="jst-trappa n{n}">{li}</ol></div></section>'''


# --- Projekt ------------------------------------------------------------------------------------------------------------
@variant("projekt", "j-index")
def projekt_index(s):
    """Klistrad sidokolumn med rubrik och numrerat projektregister, höga bildkort staplade i högerkolumnen."""
    pr = s.b["projekt"][:6]

    def status_for(x):
        ar = x.get("ar", "")
        pag = any(w in ar.lower() for w in ("pågående", "nu", "säljstart")) or (ar[:4].isdigit() and int(ar[:4]) >= 2027)
        return x.get("status") or (s.T("status_pagaende") if pag else s.T("status_klart")), pag
    reg, kort = "", ""
    for i, x in enumerate(pr):
        st, pag = status_for(x)
        reg += f'<li><a href="#jpi-{i}"><span>{i + 1:02d}</span>{E(x["namn"])}</a></li>'
        bild = s.bilder.ta(x["tagg"])
        kort += (f'<li class="jpi-kort reveal" id="jpi-{i}"><a href="projekt.html"><div class="jpi-foto">{s.bilder.img(bild, "(min-width:960px) 58vw, 100vw", lazy=i > 0).replace('decoding="async"', 'decoding="sync"')}'
                 f'<span class="status{" pagaende" if pag else ""}">{E(st)}</span><span class="jpi-stornr" aria-hidden="true">{i + 1:02d}</span></div>'
                 f'<div class="jpi-text"><h3>{E(x["namn"])}</h3><p>{E(x["text"])}</p><dl><div><dt>{E(s.T("proj_kol")[1])}</dt><dd>{E(x["ort"])}</dd></div>'
                 f'<div><dt>{E(s.T("proj_kol")[2])}</dt><dd>{E(x["typ"])}</dd></div><div><dt>{E(s.T("proj_kol")[4])}</dt><dd>{E(x["ar"])}</dd></div></dl></div></a></li>')
    rubrik = s.b.get("projekt_rubrik") or s.T("proj_rubrik")
    return f'''<section class="sek {s.bg("projekt")}" aria-labelledby="jpi-h"><div class="wrap jpi">
  <div class="jpi-sida"><div class="jpi-klister"><span class="etikett">{E(s.T("proj_etikett"))}</span><h2 id="jpi-h">{E(rubrik)}</h2>
  <ol class="jpi-reg">{reg}</ol>{s.textlank(s.T("proj_lank"), "projekt.html")}</div></div>
  <ul class="jpi-lista">{kort}</ul></div></section>'''
