"""Varianter D: frågor, galleri, certifikat, kunder, kontor, tidslinje, bokning och en ny uppmaningssektion (cta).

Prefix per variant (CSS i varianter_d.css):
  faq/tva .dft-  faq/centrerad .dfc-  galleri/rad .dgr-  galleri/rutnat .dgn-  certifikat/rad .dcr-  logos/band .dlb-
  kontor/lista .dkl-  tidslinje/horisontell .dth-  boka/centrerad .dbc-  cta/band .dcb-  cta/bild .dci-  cta/delad .dcd-
"""
from varianter import variant, E, ikon, PIL


def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _faq_lank(s):
    return s.textlank("Alla frågor", "faq.html") if "faq" in s.slugs else ""


# --- Frågor och svar ------------------------------------------------------------------------------------------------
@variant("faq", "tva")
def faq_tva(s):
    fq = (s.b.get("faq") or [])[:8]
    li = "".join(f'<li class="dft-rad reveal"><span class="dft-nr" aria-hidden="true">{i + 1:02d}</span><div><h3>{E(q)}</h3><p>{E(a)}</p></div></li>'
                 for i, (q, a) in enumerate(fq))
    text = s.b.get("faq_text", "Hittar du inte svaret? Ring eller mejla oss.")
    fot = (f'<div class="dft-fot"><p>{E(text)}</p><div class="dft-lankar">{_faq_lank(s)}'
           f'{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "kontur")}</div></div>')
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="dft-h"><div class="wrap">
  {s.huvud(s.T("faq_etikett"), s.T("faq_rubrik"), "dft-h")}<ol class="dft-lista">{li}</ol>{fot}</div></section>'''


@variant("faq", "centrerad")
def faq_centrerad(s):
    fq = (s.b.get("faq") or [])[:7]
    rad = "".join(f'<details class="dfc-fraga"{" open" if i == 0 else ""}><summary><span class="dfc-t">{E(q)}</span><span class="dfc-tecken" aria-hidden="true"></span></summary>'
                  f'<div class="dfc-svar"><p>{E(a)}</p></div></details>' for i, (q, a) in enumerate(fq))
    text = s.b.get("faq_text", "Hittar du inte svaret? Ring eller mejla oss.")
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="dfc-h"><div class="wrap dfc">
  <div class="dfc-huvud"><span class="etikett">{E(s.T("faq_etikett"))}</span><h2 id="dfc-h">{E(s.T("faq_rubrik"))}</h2><p class="ingress">{E(text)}</p></div>
  <div class="dfc-lista">{rad}</div><div class="dfc-fot">{_faq_lank(s)}{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></section>'''


# --- Galleri ------------------------------------------------------------------------------------------------------------
def _galleri_bilder(s, n):
    taggar = s.b.get("galleri_taggar") or [s.p.get("hero_tagg") or "people"]
    return [s.bilder.ta(taggar[i % len(taggar)]) for i in range(n)]


@variant("galleri", "rad")
def galleri_rad(s):
    bilder = _galleri_bilder(s, 8)
    n = len(bilder)
    li = "".join(f'<li class="dgr-bild{" dgr-bred" if i % 3 == 1 else ""}">{s.bilder.img(x, "(min-width:960px) 34vw, 78vw")}'
                 f'<span class="dgr-nr" aria-hidden="true">{i + 1:02d} / {n:02d}</span></li>' for i, x in enumerate(bilder))
    rubrik = s.b.get("galleri_rubrik") or s.T("galleri_rubrik")
    return f'''<section class="sek dgr {s.bg("galleri")}" aria-labelledby="dgr-h"><div class="wrap">
  {s.huvud(s.T("galleri_etikett"), rubrik, "dgr-h", s.textlank(s.T("proj_lank"), "projekt.html"))}</div>
  <ul class="dgr-remsa" tabindex="0" aria-label="Bildgalleri, bläddra i sidled">{li}</ul>
  <div class="wrap dgr-fot"><span class="mut">Illustrationsbilder</span><span class="dgr-dra" aria-hidden="true">Dra för fler {PIL}</span></div></section>'''


@variant("galleri", "rutnat")
def galleri_rutnat(s):
    bilder = _galleri_bilder(s, 7)
    li = "".join(f'<li class="dgn-bild dgn-b{i}">{s.bilder.img(x, "(min-width:1100px) 25vw, (min-width:700px) 33vw, 50vw")}</li>' for i, x in enumerate(bilder))
    rubrik = s.b.get("galleri_rubrik") or s.T("galleri_rubrik")
    kort = (f'<li class="dgn-kort"><span class="etikett">{E(s.T("galleri_etikett"))}</span><h2 id="dgn-h">{E(rubrik)}</h2>'
            f'<div class="dgn-kort-fot">{s.textlank(s.T("proj_lank"), "projekt.html")}<small>Illustrationsbilder</small></div></li>')
    return f'''<section class="sek {s.bg("galleri")}" aria-labelledby="dgn-h"><div class="wrap"><ul class="dgn">{kort}{li}</ul></div></section>'''


# --- Certifikat ---------------------------------------------------------------------------------------------------------
@variant("certifikat", "rad")
def certifikat_rad(s):
    c = s.b.get("certifikat") or []
    li = "".join(f'<li title="{E(x.get("text", ""))}"><span class="dcr-ik">{ikon(x.get("ikon", "skold"))}</span><b>{E(x["titel"])}</b></li>' for x in c)
    rubrik = s.b.get("certifikat_rubrik") or s.T("certifikat_rubrik")
    return f'''<section class="sek sek-tat {s.bg("certifikat")}" aria-labelledby="dcr-h"><div class="wrap"><div class="dcr">
  <div class="dcr-huvud"><span class="etikett">{E(s.T("certifikat_etikett"))}</span><h2 id="dcr-h">{E(rubrik)}</h2></div><ul class="dcr-lista n{len(c)}">{li}</ul></div></div></section>'''


# --- Kunder -------------------------------------------------------------------------------------------------------------
@variant("logos", "band")
def logos_band(s):
    ls = s.b.get("kunder") or []

    def spar(namn, cls, dold=False):
        li = "".join(f'<li><span>{E(n)}</span></li>' for n in namn)
        return f'<ul class="dlb-spar {cls}"{" aria-hidden=true" if dold else ""}>{li}</ul>'
    rev = list(reversed(ls))
    rubrik = s.b.get("kunder_rubrik") or s.T("logos_rubrik")
    return f'''<section class="sek sek-tat dlb {s.bg("logos")}" aria-labelledby="dlb-h"><div class="wrap dlb-huvud"><span class="etikett">{E(s.T("logos_etikett"))}</span><h2 id="dlb-h">{E(rubrik)}</h2><span class="dlb-antal mut">{len(ls)} uppdragsgivare i urval</span></div>
  <div class="dlb-band"><div class="dlb-rad">{spar(ls, "dlb-a")}{spar(ls, "dlb-a dlb-kopia", True)}</div>
  <div class="dlb-rad dlb-omvand" aria-hidden="true">{spar(rev, "dlb-b")}{spar(rev, "dlb-b dlb-kopia", True)}</div></div></section>'''


# --- Kontor -------------------------------------------------------------------------------------------------------------
@variant("kontor", "lista")
def kontor_lista(s):
    ko = s.b.get("kontor_lista") or []
    li = ""
    for n, a in ko:
        ort, _, roll = n.partition(" – ")
        li += (f'<li class="reveal"><h3>{E(ort)}{f"""<small>{E(roll)}</small>""" if roll else ""}</h3><p>{E(a)}</p></li>')
    bild = s.bilder.ta(s.bt("sida_bolag"))
    rubrik = s.b.get("kontor_rubrik") or s.T("kontor_rubrik")
    text = s.b.get("kontor_text", "")
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="dkl-h"><div class="wrap dkl">
  <div class="dkl-huvud"><span class="etikett">{E(s.T("kontor_etikett"))}</span><h2 id="dkl-h">{E(rubrik)}</h2>{f'<p class="ingress">{E(text)}</p>' if text else ""}
  <div class="knappar">{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <div class="dkl-bild">{s.bilder.fyll(bild, "(min-width:1000px) 36vw, 100vw", note=True)}</div>
  <ul class="dkl-lista n{len(ko)}">{li}</ul></div></section>'''


# --- Tidslinje ----------------------------------------------------------------------------------------------------------
@variant("tidslinje", "horisontell")
def tidslinje_horisontell(s):
    tl = s.b.get("tidslinje") or []
    li = "".join(f'<li><b class="dth-ar">{E(a)}</b><span class="dth-axel" aria-hidden="true"></span><p>{E(t)}</p></li>' for a, t in tl)
    rubrik = s.b.get("tidslinje_rubrik") or s.T("tidslinje_rubrik")
    text = s.b.get("tidslinje_text", "")
    hoger = f'<p class="ingress dth-ingress">{E(text)}</p>' if text else ""
    return f'''<section class="sek dth {s.bg("tidslinje")}" aria-labelledby="dth-h"><div class="wrap">
  {s.huvud(s.T("tidslinje_etikett"), rubrik, "dth-h", hoger)}</div>
  <div class="dth-ram" tabindex="0" aria-label="Tidslinje, bläddra i sidled"><ol class="dth-lista n{len(tl)}">{li}</ol></div></section>'''


# --- Bokning ------------------------------------------------------------------------------------------------------------
@variant("boka", "centrerad")
def boka_centrerad(s):
    k = s.b["kontakt"]
    falt = s.T("boka_falt")
    typer = [("text", "name"), ("tel", "tel"), ("email", "email")]
    inp = "".join(f'<label class="dbc-f{i}"><span>{E(f)}</span><input type="{t}" name="f{i}" autocomplete="{ac}"></label>'
                  for i, (f, (t, ac)) in enumerate(zip(falt[:3], typer)))
    inp += f'<label class="dbc-f3"><span>{E(falt[3])}</span><textarea name="f3" rows="4"></textarea></label>'
    info = [("Telefon", f'<a href="tel:{_tel(k["telefon"])}">{E(k["telefon"])}</a>')]
    if k.get("epost"):
        info.append(("E-post", f'<a href="mailto:{E(k["epost"])}">{E(k["epost"])}</a>'))
    if s.b.get("oppettider"):
        info.append(("Öppettider", E(s.b["oppettider"])))
    dl = "".join(f'<div><dt>{a}</dt><dd>{b_}</dd></div>' for a, b_ in info)
    return f'''<section class="sek {s.bg("boka") or "pa-ton"}" aria-labelledby="dbc-h" id="boka"><div class="wrap dbc">
  <div class="dbc-huvud"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="dbc-h">{E(s.b.get("boka_rubrik") or s.T("boka_rubrik"))}</h2><p class="ingress">{E(s.b.get("boka_text") or s.T("boka_text"))}</p></div>
  <form class="dbc-kort" action="#dbc-tack" method="get">{inp}<button class="knapp knapp-primar" type="submit"><span>{E(s.T("boka_knapp"))}</span>{PIL}</button>
  <p class="dbc-tack" id="dbc-tack" role="status">Tack! Det här är en exempelsajt – formuläret skickar inget.</p></form>
  <dl class="dbc-info">{dl}</dl></div></section>'''


# --- Uppmaning (cta) – ny sektion ----------------------------------------------------------------------------------------
def _cta_text(s):
    return s.b.get("fot_cta") or s.T("fot_cta")


@variant("cta", "band")
def cta_band(s):
    k = s.b["kontakt"]
    return f'''<section class="sek dcb pa-farg" aria-labelledby="dcb-h"><div class="wrap dcb-grid">
  <div class="dcb-text"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="dcb-h">{E(_cta_text(s))}</h2></div>
  <div class="dcb-vagar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}
  <a class="dcb-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span><small>Ring oss</small>{E(k["telefon"])}</span></a></div></div></section>'''


@variant("cta", "bild")
def cta_bild(s):
    k = s.b["kontakt"]
    bild = s.bilder.ta(s.bt("sida_om"))
    return f'''<section class="dci" aria-labelledby="dci-h">{s.bilder.fyll(bild, "100vw")}<div class="wrap dci-text">
  <span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="dci-h">{E(_cta_text(s))}</h2>
  <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<a class="dci-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a></div></div>
  <span class="figtext">Illustrationsbild</span></section>'''


@variant("cta", "delad")
def cta_delad(s):
    k = s.b["kontakt"]
    vagar = [("telefon", "Ring", k["telefon"], f'tel:{_tel(k["telefon"])}', s.b.get("oppettider", ""))]
    if k.get("epost"):
        vagar.append(("dokument", "Mejla", k["epost"], f'mailto:{k["epost"]}', "Svar inom en arbetsdag"))
    adr = ", ".join(x for x in (k.get("adress"), " ".join(y for y in (k.get("postnr"), k.get("ort")) if y)) if x)
    vagar.append(("karta", "Besök", adr or k.get("ort", ""), "om-oss.html#kontakt", ""))
    rutor = "".join(f'<li><a href="{E(h)}">{ikon(ik)}<span class="dcd-txt"><small>{E(et)}</small><b>{E(v)}</b>{f"""<span>{E(u)}</span>""" if u else ""}</span>'
                    f'<span class="rundpil">{PIL}</span></a></li>' for ik, et, v, h, u in vagar)
    return f'''<section class="sek dcd {s.bg("cta")}" aria-labelledby="dcd-h"><div class="wrap dcd-grid">
  <div class="dcd-text"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="dcd-h">{E(_cta_text(s))}</h2>
  <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <ul class="dcd-rutor n{len(vagar)}">{rutor}</ul></div></section>'''
