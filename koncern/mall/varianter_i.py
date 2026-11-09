"""Varianter I: tidslinje, kontor, priser, frågor och galleri.

Prefix per variant (CSS i varianter_i.css). Gemensamt: .iv ger lokala färger som följer sektionens bakgrund.
  tidslinje/i-sicksack .its-   tidslinje/i-trappa .itr-   tidslinje/i-ordbild .ito-
  kontor/i-nav .ikn-           kontor/i-tavla .ikt-       kontor/i-ordvagg .iko-
  priser/i-dragspel .ipd-      priser/i-flikar .ipf-      priser/i-biljett .ipb-     priser/i-huvudpaket .iph-
  faq/i-fokus .iff-            faq/i-bento .ifb-          faq/i-samtal .ifs-
  galleri/i-kollage .igk-      galleri/i-film .igf-       galleri/i-snitt .igs-
"""
import math
import re

from varianter import variant, E, ikon, PIL

BOCK = ('<svg class="{c}" viewBox="0 0 24 24" aria-hidden="true"><path d="m5 12.5 4.5 4.5L19 7.5" fill="none" stroke="currentColor" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def _nb(text):
    """Escapar och håller ihop tal som "21 000" och "4 900 kr" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", " ", E(text))


def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _ingress(text, klass=""):
    return f'<p class="ingress {klass}">{E(text)}</p>' if text else ""


# --- Tidslinje ------------------------------------------------------------------------------------------------------
def _tl(s):
    tl = s.b.get("tidslinje") or []
    return (tl, s.T("tidslinje_etikett"), s.b.get("tidslinje_rubrik") or s.T("tidslinje_rubrik"), s.b.get("tidslinje_text", ""))


@variant("tidslinje", "i-sicksack")
def tidslinje_sicksack(s):
    """Mittlinje där årtalen står som stora konturtal på ena sidan och händelsen på den andra, växelvis."""
    tl, et, rub, text = _tl(s)
    n = len(tl)
    li = "".join(f'<li class="its-rad{" its-sist" if i == n - 1 else ""} reveal"><b class="its-ar">{E(a)}</b><span class="its-prick" aria-hidden="true"></span>'
                 f'<div class="its-text"><span class="its-nr">{i + 1:02d}</span><p>{E(t)}</p></div></li>' for i, (a, t) in enumerate(tl))
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="its-h"><div class="wrap iv its">
  <div class="its-huvud"><span class="etikett">{E(et)}</span><h2 id="its-h">{E(rub)}</h2>{_ingress(text)}</div>
  <ol class="its-lista">{li}</ol></div></section>'''


@variant("tidslinje", "i-trappa")
def tidslinje_trappa(s):
    """Stapeldiagram i ren CSS: varje händelse står på en stapel som växer med tiden, som en trappa uppåt."""
    tl, et, rub, text = _tl(s)
    n = max(len(tl), 1)
    li = ""
    for i, (a, t) in enumerate(tl):
        andel = 22 + round(78 * i / max(n - 1, 1))
        li += (f'<li class="itr-steg reveal" style="--i:{i};--andel:{andel}%"><div class="itr-text"><b class="itr-ar">{E(a)}</b><p>{E(t)}</p></div>'
               f'<span class="itr-stapel" aria-hidden="true"></span></li>')
    hoger = _ingress(text, "itr-ingress")
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="itr-h"><div class="wrap iv itr">
  {s.huvud(et, rub, "itr-h", hoger)}
  <ol class="itr-trappa" style="--n:{n}">{li}</ol></div></section>'''


@variant("tidslinje", "i-ordbild")
def tidslinje_ordbild(s):
    """Första och sista årtalet som en jättelik ordbild över hela bredden, händelserna i tidningsspalter under."""
    tl, et, rub, text = _tl(s)
    forst, sist = (tl[0][0], tl[-1][0]) if tl else ("", "")
    ord_ = f"{forst}–{sist}" if forst != sist else forst
    li = "".join(f'<li class="ito-post reveal"><b class="ito-ar">{E(a)}</b><p>{E(t)}</p></li>' for a, t in tl)
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="ito-h"><div class="wrap iv ito">
  <div class="ito-topp"><div><span class="etikett">{E(et)}</span><h2 id="ito-h">{E(rub)}</h2></div>{_ingress(text, "ito-ingress")}</div>
  <p class="ito-ord" aria-hidden="true" style="--l:{max(len(ord_), 4)}"><span class="ito-kontur">{E(forst)}</span>{f'<span class="ito-streck"></span><span class="ito-fylld">{E(sist)}</span>' if forst != sist else ""}</p>
  <ol class="ito-spalter">{li}</ol></div></section>'''


# --- Kontor ---------------------------------------------------------------------------------------------------------
def _ko(s):
    ko = s.b.get("kontor_lista") or []
    rader = []
    for n, a in ko:
        ort, _, roll = n.partition(" – ")
        rader.append((ort, roll, a))
    return (rader, s.T("kontor_etikett"), s.b.get("kontor_rubrik") or s.T("kontor_rubrik"), s.b.get("kontor_text", ""))


@variant("kontor", "i-nav")
def kontor_nav(s):
    """Nätverksdiagram: huvudkontoret i mitten, övriga kontor i en ring med ekrar, numrerad lista bredvid."""
    rader, et, rub, text = _ko(s)
    if not rader:
        return ""
    hq, ovr = rader[0], rader[1:]
    m = max(len(ovr), 1)
    linjer, noder = "", ""
    for i, (ort, roll, _) in enumerate(ovr):
        v = -math.pi / 2 + 2 * math.pi * i / m
        x, y = 50 + 39 * math.cos(v), 50 + 39 * math.sin(v)
        linjer += f'<line x1="50" y1="50" x2="{x:.2f}" y2="{y:.2f}"/>'
        sida = "h" if x > 56 else ("v" if x < 44 else ("o" if y < 50 else "u"))
        noder += (f'<li class="ikn-nod ikn-{sida}" style="left:{x:.2f}%;top:{y:.2f}%"><span class="ikn-punkt">{i + 2}</span>'
                  f'<span class="ikn-ort">{E(ort.split(",")[0])}</span></li>')
    karta = (f'<div class="ikn-karta" aria-hidden="true"><svg class="ikn-svg" viewBox="0 0 100 100" preserveAspectRatio="none">'
             f'<circle cx="50" cy="50" r="39"/><circle cx="50" cy="50" r="22"/>{linjer}</svg>'
             f'<div class="ikn-hq"><span class="ikn-hq-nr">1</span><b>{E(hq[0].split(",")[0])}</b><small>{E(hq[1] or "Huvudkontor")}</small></div>'
             f'<ul class="ikn-noder">{noder}</ul></div>')
    li = "".join(f'<li class="ikn-rad{" ikn-forsta" if i == 0 else ""}"><span class="ikn-nr">{i + 1}</span><div><h3>{E(ort)}{f"""<small>{E(roll)}</small>""" if roll else ""}</h3>'
                 f'<p>{_nb(a)}</p></div></li>' for i, (ort, roll, a) in enumerate(rader))
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="ikn-h"><div class="wrap iv ikn">
  {s.huvud(et, rub, "ikn-h", _ingress(text, "ikn-ingress"))}
  <div class="ikn-grid">{karta}<ol class="ikn-lista">{li}</ol></div></div></section>'''


@variant("kontor", "i-tavla")
def kontor_tavla(s):
    """Kontoren som en mörk avgångstavla: plattformsnummer, ort i versaler, verksamhet och telefon längst ned."""
    rader, et, rub, text = _ko(s)
    k = s.b["kontakt"]
    li = "".join(f'<li class="ikt-rad"><span class="ikt-plats">{i + 1:02d}</span><b class="ikt-ort">{E(ort)}</b>'
                 f'<span class="ikt-roll">{E(roll) if roll else ""}</span><p class="ikt-text">{_nb(a)}</p></li>' for i, (ort, roll, a) in enumerate(rader))
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="ikt-h"><div class="wrap iv ikt">
  {s.huvud(et, rub, "ikt-h", _ingress(text, "ikt-ingress"))}
  <div class="ikt-tavla reveal"><div class="ikt-topp"><span class="ikt-kol" aria-hidden="true">Nr</span><span class="ikt-kol" aria-hidden="true">Ort</span><span class="ikt-sista"><span class="ikt-kol" aria-hidden="true">Verksamhet</span><span class="ikt-antal"><i class="ikt-lampa" aria-hidden="true"></i>{len(rader)} orter</span></span></div>
  <ol class="ikt-lista">{li}</ol>
  <div class="ikt-fot"><a href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></div></section>'''


@variant("kontor", "i-ordvagg")
def kontor_ordvagg(s):
    """Orterna som en stor typografisk vägg med fotnotsnummer; beskrivningarna som fotnoter i spalter under."""
    rader, et, rub, text = _ko(s)
    ord_ = ' <span class="iko-sep" aria-hidden="true">/</span> '.join(f'<span class="iko-ord{" iko-hq" if i == 0 else ""}">{E(ort)}<sup>{i + 1}</sup></span>' for i, (ort, _, _) in enumerate(rader))
    li = "".join(f'<li class="reveal"><span class="iko-nr">{i + 1}</span><div><b>{E(ort)}</b>{f"""<em>{E(roll)}</em>""" if roll else ""}<p>{_nb(a)}</p></div></li>'
                 for i, (ort, roll, a) in enumerate(rader))
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="iko-h"><div class="wrap iv iko">
  <div class="iko-topp"><span class="etikett">{E(et)}</span><h2 id="iko-h">{E(rub)}</h2></div>
  <p class="iko-vagg">{ord_}</p>
  <div class="iko-under">{f'<p class="iko-text">{E(text)}</p>' if text else ""}<ol class="iko-lista n{len(rader)}">{li}</ol></div>
  <div class="iko-fot">{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></section>'''


# --- Priser ---------------------------------------------------------------------------------------------------------
def _pr(s):
    return (s.b.get("priser") or [], s.T("priser_etikett"), s.b.get("priser_rubrik") or s.T("priser_rubrik"), s.b.get("priser_not") or s.T("priser_not"))


def _utvald_index(pr):
    for i, x in enumerate(pr):
        if x.get("utvald"):
            return i
    return 0


@variant("priser", "i-dragspel")
def priser_dragspel(s):
    """Sticky rubrikkolumn till vänster, paketen som stora dragspelsrader med pris i raden; det utvalda står öppet."""
    pr, et, rub, noten = _pr(s)
    u = _utvald_index(pr)
    rad = ""
    for i, x in enumerate(pr):
        utv = x.get("utvald")
        pkt = "".join(f'<li>{BOCK.format(c="ipd-bock")}<span>{E(p)}</span></li>' for p in x.get("punkter", []))
        flagga = f'<span class="ipd-flagga">{E(s.T("priser_utvald"))}</span>' if utv else ""
        rad += (f'<details class="ipd-paket{" utv" if utv else ""}"{" open" if i == u else ""}><summary><span class="ipd-nr" aria-hidden="true">{i + 1:02d}</span>'
                f'<span class="ipd-namn">{E(x["namn"])}{flagga}</span><span class="ipd-pris">{_nb(x["pris"])}<small>{E(x.get("enhet", ""))}</small></span><span class="ipd-tecken" aria-hidden="true"></span></summary>'
                f'<div class="ipd-inne"><div class="ipd-info"><p class="ipd-text">{E(x.get("text", ""))}</p></div>'
                f'<ul class="ipd-punkter">{pkt}</ul><div class="ipd-kop">{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt", "primar" if utv else "kontur")}</div></div></details>')
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="ipd-h"><div class="wrap iv ipd">
  <div class="ipd-huvud"><span class="etikett">{E(et)}</span><h2 id="ipd-h">{E(rub)}</h2><p class="ipd-not">{E(noten)}</p>
  <div class="knappar">{s.textlank("Alla priser", "priser.html")}</div></div>
  <div class="ipd-lista">{rad}</div></div></section>'''


@variant("priser", "i-flikar")
def priser_flikar(s):
    """Segmenterad flikrad (ren CSS med radioknappar) och en stor delad panel 60/40 för det valda paketet."""
    pr, et, rub, noten = _pr(s)
    u = _utvald_index(pr)
    inp, flikar, paneler = "", "", ""
    for i, x in enumerate(pr[:6]):
        utv = x.get("utvald")
        inp += f'<input class="ipf-in" type="radio" name="ipf-val" id="ipf-{i}"{" checked" if i == u else ""}>'
        flikar += (f'<label for="ipf-{i}" class="ipf-flik ipf-f{i}"><span class="ipf-fnamn">{E(x["namn"])}</span>'
                   f'<span class="ipf-fpris">{_nb(x["pris"])}</span>{"<i class=ipf-prick aria-hidden=true></i>" if utv else ""}</label>')
        pkt = "".join(f'<li>{BOCK.format(c="ipf-bock")}<span>{E(p)}</span></li>' for p in x.get("punkter", []))
        flagga = f'<span class="ipf-flagga">{E(s.T("priser_utvald"))}</span>' if utv else ""
        paneler += (f'<div class="ipf-panel ipf-p{i}"><div class="ipf-vanster">{flagga}<h3>{E(x["namn"])}</h3><p class="ipf-text">{E(x.get("text", ""))}</p>'
                    f'<ul class="ipf-punkter">{pkt}</ul></div><div class="ipf-hoger"><span class="ipf-fran">Pris</span><b class="ipf-pris">{_nb(x["pris"])}</b>'
                    f'<span class="ipf-enhet">{E(x.get("enhet", ""))}</span>{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt", "ljus")}</div></div>')
    n = min(len(pr), 6)
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="ipf-h"><div class="wrap iv ipf">
  {s.huvud(et, rub, "ipf-h", s.textlank("Alla priser", "priser.html"), mitt=True)}
  <div class="ipf-ram">{inp}<div class="ipf-flikar" style="--n:{n}">{flikar}</div><div class="ipf-paneler">{paneler}</div></div>
  <p class="ipf-not">{E(noten)}</p></div></section>'''


@variant("priser", "i-biljett")
def priser_biljett(s):
    """Paketen som biljetter: innehåll överst, perforerad kant med urnypta hörn och en prisstub med streckkod nederst."""
    pr, et, rub, noten = _pr(s)
    li = ""
    for i, x in enumerate(pr):
        utv = x.get("utvald")
        pkt = "".join(f'<li>{E(p)}</li>' for p in x.get("punkter", []))
        flagga = f'<span class="ipb-flagga">{E(s.T("priser_utvald"))}</span>' if utv else ""
        li += (f'<li class="ipb-biljett{" utv" if utv else ""} reveal"><div class="ipb-topp"><div class="ipb-rad"><span class="ipb-kod">Nr {i + 1:03d}</span>{flagga}</div>'
               f'<h3>{E(x["namn"])}</h3><p class="ipb-text">{E(x.get("text", ""))}</p><ul class="ipb-punkter">{pkt}</ul></div>'
               f'<div class="ipb-stub"><div class="ipb-belopp"><b>{_nb(x["pris"])}</b><span>{E(x.get("enhet", ""))}</span></div>'
               f'<div class="ipb-kop">{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt", "primar" if utv else "kontur")}<span class="ipb-streck" aria-hidden="true"></span></div></div></li>')
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="ipb-h"><div class="wrap iv ipb">
  {s.huvud(et, rub, "ipb-h", s.textlank("Alla priser", "priser.html"))}
  <ul class="ipb-lista n{len(pr)}">{li}</ul><p class="ipb-not">{E(noten)}</p></div></section>'''


@variant("priser", "i-huvudpaket")
def priser_huvudpaket(s):
    """Det utvalda paketet som ett stort delat färgblock (innehåll + prisruta), övriga paket som smala rader under."""
    pr, et, rub, noten = _pr(s)
    if not pr:
        return ""
    u = _utvald_index(pr)
    x = pr[u]
    pkt = "".join(f'<li>{BOCK.format(c="iph-bock")}<span>{E(p)}</span></li>' for p in x.get("punkter", []))
    stor = (f'<article class="iph-stor reveal"><div class="iph-innehall"><span class="iph-flagga">{E(s.T("priser_utvald"))}</span><h3>{E(x["namn"])}</h3>'
            f'<p class="iph-text">{E(x.get("text", ""))}</p><ul class="iph-punkter">{pkt}</ul></div>'
            f'<div class="iph-prisruta"><b class="iph-pris">{_nb(x["pris"])}</b><span class="iph-enhet">{E(x.get("enhet", ""))}</span>'
            f'{s.knapp(s.T("priser_knapp"), "om-oss.html#kontakt")}</div></article>')
    ovr = ""
    for i, y in enumerate(pr):
        if i == u:
            continue
        ovr += (f'<li class="iph-rad reveal"><div class="iph-rnamn"><h3>{E(y["namn"])}</h3><p>{E(y.get("text", ""))}</p></div>'
                f'<p class="iph-rpkt">{" · ".join(E(p) for p in y.get("punkter", [])[:3])}</p>'
                f'<div class="iph-rpris"><b>{_nb(y["pris"])}</b><span>{E(y.get("enhet", ""))}</span></div>'
                f'<a class="iph-rlank" href="om-oss.html#kontakt" aria-label="{E(s.T("priser_knapp"))}: {E(y["namn"])}"><span>{E(s.T("priser_knapp"))}</span>{PIL}</a></li>')
    return f'''<section class="sek {s.bg("priser")}" aria-labelledby="iph-h"><div class="wrap iv iph">
  {s.huvud(et, rub, "iph-h", s.textlank("Alla priser", "priser.html"))}
  {stor}{f'<p class="iph-etikett">Fler alternativ</p><ul class="iph-ovr">{ovr}</ul>' if ovr else ""}<p class="iph-not">{E(noten)}</p></div></section>'''


# --- Frågor och svar ------------------------------------------------------------------------------------------------
def _fq(s, n=8):
    return ((s.b.get("faq") or [])[:n], s.T("faq_etikett"), s.T("faq_rubrik"), s.b.get("faq_text", "Hittar du inte svaret? Ring eller mejla oss."))


def _faq_lank(s):
    return s.textlank("Alla frågor", "faq.html") if "faq" in s.slugs else ""


@variant("faq", "i-fokus")
def faq_fokus(s):
    """Frågorna som en numrerad meny till vänster och svaret i en stor färgad panel till höger (ren CSS, radioknappar)."""
    fq, et, rub, text = _fq(s)
    k = s.b["kontakt"]
    rad = ""
    for i, (q, a) in enumerate(fq):
        rad += (f'<input class="iff-in" type="radio" name="iff-val" id="iff-{i}"{" checked" if i == 0 else ""}>'
                f'<label class="iff-q" for="iff-{i}"><span class="iff-nr">{i + 1:02d}</span><span class="iff-t">{E(q)}</span>{PIL}</label>'
                f'<div class="iff-a"><span class="iff-tecken" aria-hidden="true">?</span><p class="iff-fraga">{E(q)}</p><p class="iff-svar">{E(a)}</p></div>')
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="iff-h"><div class="wrap iv iff">
  {s.huvud(et, rub, "iff-h", f'<p class="iff-hjalp">{E(text)} <a href="tel:{_tel(k["telefon"])}">{E(k["telefon"])}</a></p>')}
  <div class="iff-panel" style="--n:{max(len(fq), 1)}">{rad}</div>
  <div class="iff-fot">{_faq_lank(s)}{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></section>'''


@variant("faq", "i-bento")
def faq_bento(s):
    """Murverk av frågekort i olika ytor (färg, ton, mörk) med stora frågetecken; rubrikkortet ingår i murverket."""
    fq, et, rub, text = _fq(s)
    toner = ["ifb-farg", "ifb-ljus", "ifb-ton", "ifb-ljus", "ifb-mork", "ifb-ton", "ifb-ljus", "ifb-farg"]
    rest = (len(fq) + 2) % 3
    sist = {1: " ifb-s3", 2: " ifb-s2"}.get(rest, "")
    li = "".join(f'<li class="ifb-kort {toner[i % len(toner)]}{sist if i == len(fq) - 1 else ""} reveal"><span class="ifb-tecken" aria-hidden="true">?</span><h3>{E(q)}</h3><p>{E(a)}</p></li>'
                 for i, (q, a) in enumerate(fq))
    forsta = (f'<li class="ifb-kort ifb-rubrik"><span class="etikett">{E(et)}</span><h2 id="ifb-h">{E(rub)}</h2><p class="ifb-hjalp">{E(text)}</p>'
              f'<div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}{_faq_lank(s)}</div></li>')
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="ifb-h"><div class="wrap iv ifb">
  <ul class="ifb-mur">{forsta}{li}</ul></div></section>'''


@variant("faq", "i-samtal")
def faq_samtal(s):
    """Frågor och svar som ett samtal: besökarens fråga i en färgad bubbla till höger, företagets svar till vänster."""
    fq, et, rub, text = _fq(s, 5)
    initial = E((s.b.get("kortnamn") or s.b["namn"])[:1].upper())
    k = s.b["kontakt"]
    rad = ""
    for q, a in fq:
        rad += (f'<li class="ifs-par reveal"><div class="ifs-fraga"><p>{E(q)}</p></div>'
                f'<div class="ifs-svar"><span class="ifs-avatar" aria-hidden="true">{initial}</span><p>{E(a)}</p></div></li>')
    slut = (f'<li class="ifs-par ifs-slut"><div class="ifs-svar"><span class="ifs-avatar" aria-hidden="true">{initial}</span>'
            f'<div class="ifs-sista"><p>{E(text)}</p><div class="ifs-knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}'
            f'<a class="ifs-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a></div></div></div></li>')
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="ifs-h"><div class="wrap iv ifs">
  {s.huvud(et, rub, "ifs-h", mitt=True)}
  <ol class="ifs-trad">{rad}{slut}</ol><div class="ifs-fot">{_faq_lank(s)}</div></div></section>'''


# --- Galleri --------------------------------------------------------------------------------------------------------
def _gb(s, n):
    taggar = s.b.get("galleri_taggar") or [s.p.get("hero_tagg") or "people"]
    return [s.bilder.ta(taggar[i % len(taggar)]) for i in range(n)]


def _ga(s):
    return s.T("galleri_etikett"), s.b.get("galleri_rubrik") or s.T("galleri_rubrik")


@variant("galleri", "i-kollage")
def galleri_kollage(s):
    """Polaroidkollage: bilder i vita ramar med bildtext, lätt roterade och överlappande; rätas upp vid hover."""
    bilder = _gb(s, 7)
    et, rub = _ga(s)
    li = "".join(f'<li class="igk-foto igk-{i} reveal"><figure><div class="igk-bild">{s.bilder.img(x, "(min-width:960px) 30vw, 46vw")}</div>'
                 f'<figcaption>{E(x["alt"])}</figcaption></figure></li>' for i, x in enumerate(bilder))
    return f'''<section class="sek {s.bg("galleri")}" aria-labelledby="igk-h"><div class="wrap iv igk">
  {s.huvud(et, rub, "igk-h", s.textlank(s.T("proj_lank"), "projekt.html"))}
  <ul class="igk-bord">{li}</ul><p class="igk-not">Illustrationsbilder</p></div></section>'''


@variant("galleri", "i-film")
def galleri_film(s):
    """Helbredd: en stor bild med rubriken ovanpå och en filmremsa med fem bilder som överlappar bildens nederkant."""
    bilder = _gb(s, 6)
    et, rub = _ga(s)
    stor, ovr = bilder[0], bilder[1:]
    li = "".join(f'<li class="igf-ruta"><span class="igf-nr" aria-hidden="true">{i + 2:02d}</span>{s.bilder.img(x, "(min-width:960px) 20vw, 60vw")}</li>' for i, x in enumerate(ovr))
    return f'''<section class="igf {s.bg("galleri")}" aria-labelledby="igf-h">
  <div class="igf-scen"><div class="igf-bild">{s.bilder.img(stor, "100vw")}</div>
  <div class="wrap igf-text"><span class="etikett">{E(et)}</span><h2 id="igf-h">{E(rub)}</h2><div class="knappar">{s.textlank(s.T("proj_lank"), "projekt.html")}</div></div></div>
  <div class="wrap igf-remsa-ram"><ul class="igf-remsa" tabindex="0" aria-label="Fler bilder, bläddra i sidled">{li}</ul><p class="igf-not">Illustrationsbilder</p></div></section>'''


@variant("galleri", "i-snitt")
def galleri_snitt(s):
    """Bilder som diagonala skivor kant i kant (clip-path); skivan under pekaren breddas. Staplas med sneda snitt på mobil."""
    bilder = _gb(s, 5)
    et, rub = _ga(s)
    li = "".join(f'<li class="igs-skiva reveal">{s.bilder.img(x, "(min-width:960px) 34vw, 100vw")}<span class="igs-nr" aria-hidden="true">{i + 1:02d}</span></li>'
                 for i, x in enumerate(bilder))
    return f'''<section class="sek {s.bg("galleri")}" aria-labelledby="igs-h"><div class="wrap iv igs">
  {s.huvud(et, rub, "igs-h", mitt=True)}
  <ul class="igs-rad">{li}</ul>
  <div class="igs-fot"><span class="igs-not">Illustrationsbilder</span>{s.textlank(s.T("proj_lank"), "projekt.html")}</div></div></section>'''
