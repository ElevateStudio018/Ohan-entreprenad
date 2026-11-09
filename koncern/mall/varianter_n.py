"""Varianter N: uppmaning (cta), bokning, galleri, process och omdömen – bildtunga kort, bento och karuseller.

Prefix (alla börjar på n): .nv (gemensamma lokala färger)
  cta/n-bildkort .ncb-   cta/n-bento .ncn-   cta/n-overlap .nco-
  boka/n-fotokort .nbf-  boka/n-bento .nbb-
  galleri/n-bento .ngb-  galleri/n-karusell .ngk-
  process/n-bildkort .npb-  process/n-karusell .npk-
  omdomen/n-bildkort .nob-  omdomen/n-bento .non-
"""
import re

from varianter import variant, E, ikon, PIL


# --- Gemensamma hjälpare ------------------------------------------------------------------------------------------------
def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _nb(text):
    """Escapar och håller ihop tal som "21 000" och "4 900 kr" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", " ", E(text))


def _stj(cls="stjarnor"):
    return f'<div class="{cls}" role="img" aria-label="5 av 5 stjärnor">{"".join(ikon("stjarna", "stj") for _ in range(5))}</div>'


def _initial(namn):
    d = [w for w in re.split(r"[\s.]+", namn) if w]
    return E("".join(w[0] for w in d[:2]).upper() or "?")


def _cta(s):
    return s.b.get("fot_cta") or s.T("fot_cta")


def _adress(k):
    return ", ".join(x for x in (k.get("adress"), " ".join(y for y in (k.get("postnr"), k.get("ort")) if y)) if x) or k.get("ort", "")


def _vagar(s):
    """Kontaktvägar: (ikon, etikett, värde, href, undertext)."""
    k = s.b["kontakt"]
    v = [("telefon", "Ring oss", k["telefon"], f'tel:{_tel(k["telefon"])}', s.b.get("oppettider", ""))]
    if k.get("epost"):
        v.append(("dokument", "Mejla oss", k["epost"], f'mailto:{k["epost"]}', "Svar inom en arbetsdag"))
    adr = _adress(k)
    if adr:
        v.append(("karta", "Besök oss", adr, "om-oss.html#kontakt", ""))
    return v


def _rubrik_boka(s):
    return s.b.get("boka_rubrik") or s.T("boka_rubrik")


def _text_boka(s):
    return s.b.get("boka_text") or s.T("boka_text")


def _falt(s, p):
    falt = s.T("boka_falt")
    typer = [("text", "name"), ("tel", "tel"), ("email", "email")]
    ut = "".join(f'<label class="{p}-f {p}-f{i}"><span>{E(f)}</span><input type="{t}" name="f{i}" autocomplete="{ac}"></label>'
                 for i, (f, (t, ac)) in enumerate(zip(falt[:3], typer)))
    if len(falt) > 3:
        ut += f'<label class="{p}-f {p}-f3"><span>{E(falt[3])}</span><textarea name="f3" rows="4"></textarea></label>'
    return ut


def _skicka(s, p):
    return (f'<div class="{p}-skicka"><button class="knapp knapp-primar" type="submit"><span>{E(s.T("boka_knapp"))}</span>{PIL}</button>'
            f'<p class="{p}-tack" id="{p}-tack" role="status">Tack! Det här är en exempelsajt – formuläret skickar inget.</p></div>')


def _galleri(s, n):
    taggar = s.b.get("galleri_taggar") or [s.p.get("hero_tagg") or "people"]
    return [s.bilder.ta(taggar[i % len(taggar)]) for i in range(n)]


def _ga(s):
    return s.T("galleri_etikett"), s.b.get("galleri_rubrik") or s.T("galleri_rubrik")


def _steg(s):
    return s.b.get("process") or [{"titel": a["titel"], "text": a["text"], "tagg": a.get("tagg")} for a in s.b["affarsomraden"]]


def _process_rubrik(s):
    return s.b.get("process_rubrik") or s.T("process_rubrik")


# =====================================================================================================================
# Uppmaning (cta)
# =====================================================================================================================
@variant("cta", "n-bildkort")
def cta_bildkort(s):
    """Rubrikkolumn till vänster, till höger stående bildkort – ett per kontaktväg – med värdet i en färgruta på bilden."""
    vagar = _vagar(s)
    kort = ""
    for i, (ik, et, v, h, u) in enumerate(vagar):
        bild = s.bilder.ta(s.bt("sida_om") if i == 0 else (s.bt("om") if i == 1 else s.bt("panel")))
        kort += (f'<li class="ncb-kort reveal"><a href="{E(h)}"><div class="ncb-bild">{s.bilder.img(bild, "(min-width:1000px) 22vw, 80vw")}</div>'
                 f'<div class="ncb-ruta"><span class="ncb-ik">{ikon(ik)}</span><small>{E(et)}</small><b>{_nb(v)}</b>'
                 f'{f"""<span class="ncb-u">{E(u)}</span>""" if u else ""}<span class="ncb-pil">{PIL}</span></div></a></li>')
    return f'''<section class="sek {s.bg("cta")}" aria-labelledby="ncb-h"><div class="wrap nv ncb">
  <div class="ncb-text"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="ncb-h">{E(_cta(s))}</h2>
  <div class="knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div>
  <ul class="ncb-rad n{len(vagar)}">{kort}</ul><span class="ncb-not">Illustrationsbilder</span></div></section>'''


@variant("cta", "n-bento")
def cta_bento(s):
    """Bento: en stor bildruta med uppmaningen i en färgruta, telefon i accentfärg, mejl, adress och en andra bild runt om."""
    k = s.b["kontakt"]
    b1 = s.bilder.ta(s.bt("sida_om"))
    b2 = s.bilder.ta(s.bt("panel"))
    rutor = [f'<a class="ncn-ruta ncn-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span><small>Ring oss</small><b>{_nb(k["telefon"])}</b>'
             f'{f"""<em>{E(s.b["oppettider"])}</em>""" if s.b.get("oppettider") else ""}</span><span class="rundpil">{PIL}</span></a>']
    if k.get("epost"):
        rutor.append(f'<a class="ncn-ruta ncn-mejl" href="mailto:{E(k["epost"])}">{ikon("dokument")}<span><small>Mejla oss</small><b>{E(k["epost"])}</b></span>'
                     f'<span class="rundpil">{PIL}</span></a>')
    adr = _adress(k)
    if adr:
        rutor.append(f'<a class="ncn-ruta ncn-adr" href="om-oss.html#kontakt">{ikon("karta")}<span><small>Besök oss</small><b>{_nb(adr)}</b></span>'
                     f'<span class="rundpil">{PIL}</span></a>')
    return f'''<section class="sek {s.bg("cta")}" aria-labelledby="ncn-h"><div class="wrap nv">
  <div class="ncn n{len(rutor)}">
    <div class="ncn-stor">{s.bilder.fyll(b1, "(min-width:1000px) 50vw, 100vw")}<div class="ncn-farg"><span class="etikett">{E(s.T("boka_etikett"))}</span>
      <h2 id="ncn-h">{E(_cta(s))}</h2>{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}</div><span class="figtext">Illustrationsbild</span></div>
    {"".join(rutor)}
    <div class="ncn-bild2">{s.bilder.fyll(b2, "(min-width:1000px) 25vw, 50vw")}</div>
  </div></div></section>'''


@variant("cta", "n-overlap")
def cta_overlap(s):
    """Bred bild inom spalten och ett färgkort som överlappar bildens nederkant med uppmaning, knapp och kontaktvägar på rad."""
    bild = s.bilder.ta(s.bt("sida_om"))
    vagar = _vagar(s)[:2]
    rad = "".join(f'<a class="nco-vag" href="{E(h)}">{ikon(ik)}<span><small>{E(et)}</small><b>{_nb(v)}</b></span></a>' for ik, et, v, h, u in vagar)
    return f'''<section class="sek {s.bg("cta")}" aria-labelledby="nco-h"><div class="wrap nv nco">
  <div class="nco-bild">{s.bilder.fyll(bild, "(min-width:1000px) 80vw, 100vw", note=True)}</div>
  <div class="nco-kort reveal"><div class="nco-topp"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="nco-h">{E(_cta(s))}</h2></div>
    <div class="nco-fot">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<div class="nco-vagar">{rad}</div></div></div></div></section>'''


# =====================================================================================================================
# Bokning
# =====================================================================================================================
@variant("boka", "n-fotokort")
def boka_fotokort(s):
    """Rubrik och ett stort bildkort med kontaktuppgifter i en färgruta till vänster; formuläret i ett upphöjt kort som överlappar bilden."""
    bild = s.bilder.ta(s.bt("om"))
    info = "".join(f'<li><a href="{E(h)}">{ikon(ik)}<span><small>{E(et)}</small><b>{_nb(v)}</b></span></a></li>' for ik, et, v, h, u in _vagar(s)[:2])
    tider = f'<p class="nbf-tider"><small>Öppettider</small>{E(s.b["oppettider"])}</p>' if s.b.get("oppettider") else ""
    return f'''<section class="sek {s.bg("boka") or "pa-ton"}" aria-labelledby="nbf-h" id="boka"><div class="wrap nv nbf">
  <div class="nbf-huvud"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="nbf-h">{E(_rubrik_boka(s))}</h2><p class="ingress">{E(_text_boka(s))}</p></div>
  <div class="nbf-bild">{s.bilder.fyll(bild, "(min-width:1000px) 55vw, 100vw", note=True)}<div class="nbf-info"><ul>{info}</ul>{tider}</div></div>
  <form class="nbf-kort reveal" action="#nbf-tack" method="get"><p class="nbf-kh">{E(s.T("boka_knapp"))}</p>{_falt(s, "nbf")}{_skicka(s, "nbf")}</form></div></section>'''


@variant("boka", "n-bento")
def boka_bento(s):
    """Bento: formuläret som största rutan, runt om en rubrikruta i färg, en bildruta och små rutor för telefon, mejl och öppettider."""
    k = s.b["kontakt"]
    bild = s.bilder.ta(s.bt("sida_om"))
    sma = [f'<a class="nbb-sma nbb-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<small>Telefon</small><b>{_nb(k["telefon"])}</b></a>']
    if k.get("epost"):
        sma.append(f'<a class="nbb-sma" href="mailto:{E(k["epost"])}">{ikon("dokument")}<small>E-post</small><b>{E(k["epost"])}</b></a>')
    if s.b.get("oppettider"):
        sma.append(f'<div class="nbb-sma">{ikon("kalender")}<small>Öppettider</small><b>{E(s.b["oppettider"])}</b></div>')
    elif _adress(k):
        sma.append(f'<div class="nbb-sma">{ikon("karta")}<small>Adress</small><b>{_nb(_adress(k))}</b></div>')
    return f'''<section class="sek {s.bg("boka")}" aria-labelledby="nbb-h" id="boka"><div class="wrap nv">
  <div class="nbb n{len(sma)}">
    <div class="nbb-rubrik"><span class="etikett">{E(s.T("boka_etikett"))}</span><h2 id="nbb-h">{E(_rubrik_boka(s))}</h2><p>{E(_text_boka(s))}</p></div>
    <div class="nbb-bild">{s.bilder.fyll(bild, "(min-width:1000px) 30vw, 100vw", note=True)}</div>
    <form class="nbb-form" action="#nbb-tack" method="get">{_falt(s, "nbb")}{_skicka(s, "nbb")}</form>
    {"".join(sma)}
  </div></div></section>'''


# =====================================================================================================================
# Galleri
# =====================================================================================================================
@variant("galleri", "n-bento")
def galleri_bento(s):
    """Asymmetriskt bentorutnät: en stor kvadrat, höga och breda bilder med bildtext i en ruta och en färgruta som länkar vidare."""
    bilder = _galleri(s, 6)
    et, rub = _ga(s)
    li = "".join(f'<li class="ngb-b ngb-{i} reveal">{s.bilder.img(x, "(min-width:960px) 50vw, 100vw" if i == 0 else "(min-width:960px) 25vw, 50vw")}'
                 f'<span class="ngb-txt">{E(x["alt"])}</span></li>' for i, x in enumerate(bilder))
    lank = (f'<li class="ngb-farg reveal"><a href="projekt.html"><span class="ngb-antal">{len(bilder):02d}</span><span class="ngb-fl">'
            f'<b>{E(s.T("proj_lank"))}</b><small>Illustrationsbilder</small></span><span class="rundpil">{PIL}</span></a></li>')
    return f'''<section class="sek {s.bg("galleri")}" aria-labelledby="ngb-h"><div class="wrap nv">
  {s.huvud(et, rub, "ngb-h", s.textlank(s.T("proj_lank"), "projekt.html"))}
  <ul class="ngb">{li}{lank}</ul></div></section>'''


@variant("galleri", "n-karusell")
def galleri_karusell(s):
    """Scroll-snap-karusell: en färgad introruta först i raden, sedan stora stående bildkort med nummer och bildtext i en vit ruta."""
    bilder = _galleri(s, 8)
    et, rub = _ga(s)
    n = len(bilder)
    li = "".join(f'<li class="ngk-kort"><figure><div class="ngk-bild">{s.bilder.img(x, "(min-width:960px) 30vw, 78vw")}</div>'
                 f'<figcaption><span class="ngk-nr">{i + 1:02d}</span><span>{E(x["alt"])}</span></figcaption></figure></li>' for i, x in enumerate(bilder))
    intro = (f'<li class="ngk-intro"><div><span class="etikett">{E(et)}</span><h2 id="ngk-h">{E(rub)}</h2></div>'
             f'<div class="ngk-ifot"><span class="ngk-dra">Dra för fler {PIL}</span>{s.textlank(s.T("proj_lank"), "projekt.html")}<small>{n} bilder · Illustrationsbilder</small></div></li>')
    return f'''<section class="sek {s.bg("galleri")}" aria-labelledby="ngk-h"><div class="wrap nv ngk">
  <ul class="ngk-rad" tabindex="0" aria-label="Bildgalleri, bläddra i sidled">{intro}{li}</ul></div></section>'''


# =====================================================================================================================
# Process
# =====================================================================================================================
@variant("process", "n-bildkort")
def process_bildkort(s):
    """Höga bildkort per steg: bilden fyller kortet och texten ligger i en vit ruta längst ned, med en stegmätare överst."""
    st = _steg(s)
    n = len(st)
    li = ""
    for i, x in enumerate(st):
        bild = s.bilder.ta(x.get("tagg"))
        matare = "".join(f'<i{" class=on" if j <= i else ""}></i>' for j in range(n))
        li += (f'<li class="npb-kort reveal">{s.bilder.fyll(bild, "(min-width:1100px) 25vw, (min-width:700px) 50vw, 85vw")}'
               f'<div class="npb-topp"><span class="npb-matare" aria-hidden="true">{matare}</span><span class="npb-nr">{i + 1:02d}</span></div>'
               f'<div class="npb-ruta"><small>Steg {i + 1} av {n}</small><h3>{E(x["titel"])}</h3><p>{_nb(x["text"])}</p></div></li>')
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="npb-h"><div class="wrap nv">
  {s.huvud(s.T("process_etikett"), _process_rubrik(s), "npb-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ol class="npb n{n}">{li}</ol><p class="npb-not">Illustrationsbilder</p></div></section>'''


@variant("process", "n-karusell")
def process_karusell(s):
    """Karusell med breda kort: stor bild till vänster och stegtexten i en färgpanel till höger, nästa steg sticker in från sidan."""
    st = _steg(s)
    n = len(st)
    li = ""
    for i, x in enumerate(st):
        bild = s.bilder.ta(x.get("tagg"))
        nasta = (f'<span class="npk-nasta"><small>Nästa</small>{E(st[i + 1]["titel"])}</span>' if i + 1 < n
                 else f'<span class="npk-nasta npk-sist">{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</span>')
        li += (f'<li class="npk-kort" id="npk-{i}"><div class="npk-bild">{s.bilder.fyll(bild, "(min-width:1000px) 36vw, 85vw")}'
               f'<span class="npk-stor" aria-hidden="true">{i + 1:02d}</span></div>'
               f'<div class="npk-panel"><span class="npk-steg">Steg {i + 1} / {n}</span><h3>{E(x["titel"])}</h3><p>{_nb(x["text"])}</p>{nasta}</div></li>')
    prickar = "".join(f'<a href="#npk-{i}" aria-label="Steg {i + 1}: {E(x["titel"])}"><b>{i + 1:02d}</b><span>{E(x["titel"])}</span></a>' for i, x in enumerate(st))
    return f'''<section class="sek {s.bg("process")}" aria-labelledby="npk-h"><div class="wrap nv">
  {s.huvud(s.T("process_etikett"), _process_rubrik(s), "npk-h", s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "kontur"))}
  <nav class="npk-flikar n{n}" aria-label="Stegen">{prickar}</nav></div>
  <div class="wrap nv npk-ram"><ol class="npk-rad" tabindex="0" aria-label="Processen steg för steg, bläddra i sidled">{li}</ol></div></section>'''


# =====================================================================================================================
# Omdömen
# =====================================================================================================================
@variant("omdomen", "n-bildkort")
def omdomen_bildkort(s):
    """Bildkort: en bild överst i varje kort, initialer i en rund porträttbricka över bildkanten, stjärnor, citatet och namnet."""
    om = (s.b.get("omdomen") or [])[:6]
    roller = [s.bt("om"), s.bt("panel"), s.bt("sida_om")]
    li = ""
    for i, x in enumerate(om):
        bild = s.bilder.ta(roller[i % 3])
        ort = f'<span>{E(x["ort"])}</span>' if x.get("ort") else ""
        li += (f'<li class="nob-kort reveal"><div class="nob-bild">{s.bilder.img(bild, "(min-width:1000px) 30vw, 90vw")}</div>'
               f'<span class="nob-av" aria-hidden="true">{_initial(x["namn"])}</span>'
               f'<figure><blockquote><p>”{_nb(x["text"])}”</p></blockquote><figcaption><span class="nob-vem"><b>{E(x["namn"])}</b>{ort}</span>{_stj("stjarnor nob-stj")}</figcaption></figure></li>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="nob-h"><div class="wrap nv">
  {s.huvud(s.T("omdomen_etikett"), s.T("omdomen_rubrik"), "nob-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ul class="nob n{len(om)}">{li}</ul><p class="nob-not">Illustrationsbilder</p></div></section>'''


@variant("omdomen", "n-bento")
def omdomen_bento(s):
    """Bento: en stor bildruta med rubriken i en färgruta, första omdömet stort i primärfärg, övriga i ljusa rutor och en kontaktruta."""
    om = (s.b.get("omdomen") or [])[:6]
    bild = s.bilder.ta(s.bt("om"))
    rutor = ""
    for i, x in enumerate(om):
        ort = f'<span>{E(x["ort"])}</span>' if x.get("ort") else ""
        rutor += (f'<figure class="non-c{" non-forst" if i == 0 else ""} reveal">{_stj("stjarnor non-stj")}<blockquote><p>”{_nb(x["text"])}”</p></blockquote>'
                  f'<figcaption><span class="non-av" aria-hidden="true">{_initial(x["namn"])}</span><span class="non-vem"><b>{E(x["namn"])}</b>{ort}</span></figcaption></figure>')
    return f'''<section class="sek {s.bg("omdomen")}" aria-labelledby="non-h"><div class="wrap nv">
  <div class="non n{len(om)}">
    <div class="non-bild">{s.bilder.fyll(bild, "(min-width:1000px) 40vw, 100vw", note=True)}<div class="non-rubrik"><span class="etikett">{E(s.T("omdomen_etikett"))}</span><h2 id="non-h">{E(s.T("omdomen_rubrik"))}</h2></div></div>
    {rutor}
    <a class="non-kontakt" href="om-oss.html#kontakt"><span>{E(s.T("kontakt_knapp"))}</span><span class="rundpil">{PIL}</span></a>
  </div></div></section>'''
