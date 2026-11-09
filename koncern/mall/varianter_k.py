"""Varianter K: kontor, certifikat och kunder (logos) – bildtunga layouter med kort, bento, färgblock och scroll-snap-rader.

Prefix per variant (CSS i varianter_k.css):
  kontor/k-bildkort .kkb-   kontor/k-rulle .kkr-   kontor/k-bento .kkn-   kontor/k-overlapp .kko-
  certifikat/k-brickor .kcb-   certifikat/k-bento .kcn-   certifikat/k-bildsplit .kcs-
  logos/k-kundkort .klk-   logos/k-bento .kln-   logos/k-karusell .klc-
"""
from varianter import variant, E, ikon, PIL


def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _nb(t):
    """Escapad text där siffergrupper (2 400, 3 100) inte bryts."""
    import re
    return re.sub(r"(\d) (\d{3})", "\\1&nbsp;\\2", E(t or ""))


def _utan_alt(img):
    """Dekorativ bild (namnet står redan i texten bredvid)."""
    import re
    return re.sub(r'alt="[^"]*"', 'alt=""', img, count=1)


# --- Kontor -------------------------------------------------------------------------------------------------------------
def _ko(s):
    rader = []
    for n, a in s.b.get("kontor_lista") or []:
        ort, _, roll = n.partition(" – ")
        rader.append((ort.strip(), roll.strip(), a))
    return rader, s.T("kontor_etikett"), s.b.get("kontor_rubrik") or s.T("kontor_rubrik"), s.b.get("kontor_text", "")


def _ingress(text, cls):
    return f'<p class="ingress mut {cls}">{E(text)}</p>' if text else ""


def _roll(roll, i):
    return roll[:1].upper() + roll[1:] if roll else ("Huvudkontor" if i == 0 else "")


@variant("kontor", "k-bildkort")
def kontor_bildkort(s):
    """Bildkort per ort: huvudkontoret som stor 2×2-ruta, övriga orter som kort med bild, nummerbricka och adress; sista raden fylls ut med breda kort."""
    rader, et, rub, text = _ko(s)
    if not rader:
        return ""
    r = len(rader) - 1
    spann = []
    if r == 1:
        spann = ["s4"]
    elif r == 2:
        spann = ["s2", "s2"]
    elif r == 3:
        spann = ["", "", "s2"]
    elif r >= 4:
        spann = [""] * 4
        rest = r - 4
        rad = [""] * rest
        rem = rest % 4
        if rem == 1:
            rad[-1] = "s4"
        elif rem == 2:
            rad[-2:] = ["s2", "s2"]
        elif rem == 3:
            rad[-1] = "s2"
        spann += rad
    li = ""
    for i, (ort, roll, a) in enumerate(rader):
        kl = "kkb-hq" if i == 0 else (f"kkb-{spann[i - 1]}" if spann[i - 1] else "")
        stor = i == 0 or spann[i - 1] in ("s2", "s4")
        bild = s.bilder.ta(s.bt("sida_bolag") if i == 0 else None)
        sz = "(min-width:1000px) 50vw, 100vw" if stor else "(min-width:1000px) 25vw, (min-width:600px) 50vw, 40vw"
        rl = _roll(roll, i)
        li += (f'<li class="kkb-kort {kl}"><div class="kkb-bild">{_utan_alt(s.bilder.img(bild, sz, lazy=i > 1))}<span class="kkb-nr">{i + 1:02d}</span></div>'
               f'<div class="kkb-text">{f"""<span class="kkb-roll">{E(rl)}</span>""" if rl else ""}<h3>{E(ort)}</h3><p>{_nb(a)}</p>'
               f'{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt") if i == 0 else ""}</div></li>')
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="kkb-h"><div class="wrap">
  {s.huvud(et, rub, "kkb-h", _ingress(text, "kkb-ingress"))}
  <ul class="kkb n{len(rader)}">{li}</ul><p class="kkb-not mut">Illustrationsbilder</p></div></section>'''


@variant("kontor", "k-rulle")
def kontor_rulle(s):
    """Scroll-snap-rad ut till skärmkanten: först ett färgblock med antal orter och kontaktvägar, sedan höga bildkort per ort i trappsteg."""
    rader, et, rub, text = _ko(s)
    if not rader:
        return ""
    k = s.b["kontakt"]
    forsta = (f'<li class="kkr-farg"><div class="kkr-farg-topp"><b>{len(rader)}</b><span>orter</span></div>'
              f'{f"""<p>{E(text)}</p>""" if text else ""}<div class="kkr-farg-fot"><a class="kkr-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>'
              f'{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></li>')
    kort = ""
    for i, (ort, roll, a) in enumerate(rader):
        bild = s.bilder.ta(s.bt("sida_bolag") if i == 0 else None)
        rl = _roll(roll, i)
        kort += (f'<li class="kkr-kort"><article>{_utan_alt(s.bilder.fyll(bild, "(min-width:1100px) 24vw, (min-width:700px) 40vw, 74vw", lazy=i > 2))}'
                 f'<div class="kkr-topp"><span>{i + 1:02d} / {len(rader):02d}</span>{f"""<em>{E(rl)}</em>""" if rl else ""}</div>'
                 f'<div class="kkr-text"><h3>{E(ort)}</h3><p>{_nb(a)}</p></div></article></li>')
    return f'''<section class="sek {s.bg("kontor")} kkr-sek" aria-labelledby="kkr-h"><div class="wrap">
  {s.huvud(et, rub, "kkr-h")}</div>
  <div class="kkr-ram"><ul class="kkr" tabindex="0" aria-label="{E(rub)}">{forsta}{kort}</ul></div></section>'''


@variant("kontor", "k-bento")
def kontor_bento(s):
    """Bento-rutnät: rubrik i färgblock, huvudkontoret som stor bild, övriga orter som bild- och tonrutor i blandade storlekar och en kontaktruta som fyller sista raden."""
    rader, et, rub, text = _ko(s)
    if not rader:
        return ""
    k = s.b["kontakt"]
    hq, ovr = rader[0], rader[1:]
    # Fördela rutor rad för rad i ett rutnät med fyra kolumner (andra raden har två lediga platser bredvid huvudkontoret).
    monster4 = [[2, 1, 1], [1, 1, 2], [1, 2, 1], [1, 1, 1, 1]]
    storlek, kvar, cap, mi = [], len(ovr), 2, 0
    while kvar > 0:
        mon = [1, 1] if cap == 2 else monster4[mi % 4]
        if cap == 4:
            mi += 1
        if len(mon) > kvar:
            mon = [1] * kvar
        storlek += mon
        kvar -= len(mon)
        sista_fyllt = sum(mon)
        if kvar == 0:
            cta = cap - sista_fyllt
            break
        cap = 4
    else:
        cta = 2
    if cta == 0:
        cta = 4
    ettor = [i for i, z in enumerate(storlek) if z == 1]
    m2 = ettor[-1] if len(ettor) % 2 else -1
    rutor = (f'<div class="kkn-ruta kkn-huvud"><span class="etikett">{E(et)}</span><h2 id="kkn-h">{E(rub)}</h2>'
             f'{f"""<p>{E(text)}</p>""" if text else ""}</div>')
    bild = s.bilder.ta(s.bt("sida_bolag"))
    rutor += (f'<div class="kkn-ruta kkn-bildruta kkn-hq">{_utan_alt(s.bilder.fyll(bild, "(min-width:1000px) 50vw, 100vw"))}'
              f'<div class="kkn-text"><span class="kkn-chip">01 · {E(_roll(hq[1], 0))}</span><h3>{E(hq[0])}</h3><p>{_nb(hq[2])}</p></div></div>')
    tonnr = 0
    for j, ((ort, roll, a), z) in enumerate(zip(ovr, storlek)):
        nr = f"{j + 2:02d}"
        ext = " kkn-m2" if j == m2 else ""
        rl = f' · {E(roll)}' if roll else ""
        if z == 1:
            tonnr += 1
        if z == 1 and tonnr % 3 == 2:
            rutor += (f'<div class="kkn-ruta kkn-ton{ext}"><span class="kkn-nr">{nr}{rl}</span>{ikon("karta")}<div><h3>{E(ort)}</h3><p>{_nb(a)}</p></div></div>')
        else:
            b = s.bilder.ta()
            sz = "(min-width:1000px) 50vw, 100vw" if z == 2 else "(min-width:1000px) 25vw, 50vw"
            rutor += (f'<div class="kkn-ruta kkn-bildruta{" kkn-bred" if z == 2 else ""}{ext}">{_utan_alt(s.bilder.fyll(b, sz))}'
                      f'<div class="kkn-text"><span class="kkn-chip">{nr}{rl}</span><h3>{E(ort)}</h3>{f"""<p>{_nb(a)}</p>""" if z == 2 else ""}</div></div>')
    rutor += (f'<div class="kkn-ruta kkn-cta kkn-c{cta}"><div class="kkn-cta-topp"><b>{len(rader)}</b><span>orter</span></div>'
              f'<div class="kkn-cta-fot"><a class="kkn-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>'
              f'{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}</div></div>')
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="kkn-h"><div class="wrap"><div class="kkn">{rutor}</div></div></section>'''


@variant("kontor", "k-overlapp")
def kontor_overlapp(s):
    """Stor bild med rubriken i en färgruta, och vita ortkort med bildminiatyr som lägger sig över bildens nederkant."""
    rader, et, rub, text = _ko(s)
    if not rader:
        return ""
    bild = s.bilder.ta(s.bt("sida_bolag"))
    kol = 4 if len(rader) in (4, 7, 8) or len(rader) >= 11 else 3
    li = ""
    for i, (ort, roll, a) in enumerate(rader):
        b = s.bilder.ta()
        rl = _roll(roll, i)
        li += (f'<li class="kko-kort"><a href="om-oss.html#kontakt"><span class="kko-tumme">{_utan_alt(s.bilder.img(b, "96px"))}<i>{i + 1}</i></span>'
               f'<span class="kko-txt"><b>{E(ort)}</b>{f"""<em>{E(rl)}</em>""" if rl else ""}<span>{_nb(a)}</span></span><span class="kko-pil">{PIL}</span></a></li>')
    return f'''<section class="sek {s.bg("kontor")}" aria-labelledby="kko-h"><div class="wrap">
  <div class="kko-topp"><div class="kko-bild">{s.bilder.fyll(bild, "(min-width:1000px) 90vw, 100vw", note=True)}</div>
  <div class="kko-ruta"><span class="etikett">{E(et)}</span><h2 id="kko-h">{E(rub)}</h2>{f"""<p>{E(text)}</p>""" if text else ""}
  <span class="kko-antal"><b>{len(rader)}</b> orter</span></div></div>
  <ul class="kko k{kol}{' n-udda' if len(rader) % 2 else ''}">{li}</ul></div></section>'''


# --- Certifikat ---------------------------------------------------------------------------------------------------------
def _cert(s):
    return (s.b.get("certifikat") or [], s.T("certifikat_etikett"), s.b.get("certifikat_rubrik") or s.T("certifikat_rubrik"))


@variant("certifikat", "k-brickor")
def certifikat_brickor(s):
    """Bildbrickor: varje certifikat som ett kort med foto, en ikonbricka i färg som bryter bildkanten, nummer, titel och text."""
    c, et, rub = _cert(s)
    li = ""
    for i, x in enumerate(c):
        b = s.bilder.ta()
        li += (f'<li class="kcb-kort"><div class="kcb-bild">{_utan_alt(s.bilder.img(b, "(min-width:1000px) 25vw, (min-width:640px) 50vw, 100vw"))}<span class="kcb-nr">{i + 1:02d}</span></div>'
               f'<span class="kcb-ik">{ikon(x.get("ikon", "skold"))}</span><div class="kcb-text"><h3>{E(x["titel"])}</h3>{f"""<p>{E(x["text"])}</p>""" if x.get("text") else ""}</div></li>')
    return f'''<section class="sek {s.bg("certifikat")}" aria-labelledby="kcb-h"><div class="wrap">
  {s.huvud(et, rub, "kcb-h", s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt"))}
  <ul class="kcb n{len(c)}">{li}</ul></div></section>'''


@variant("certifikat", "k-bento")
def certifikat_bento(s):
    """Bento: stor bild med rubriken i en färgruta, certifikaten som färgblock i olika toner med ikon och nummer, bildrutor fyller tomma platser."""
    c, et, rub = _cert(s)
    huvud = (f'<div class="kcn-ruta kcn-stor">{s.bilder.fyll(s.bilder.ta(s.bt("om")), "(min-width:1000px) 50vw, 100vw", note=True)}'
             f'<div class="kcn-rubrik"><span class="etikett">{E(et)}</span><h2 id="kcn-h">{E(rub)}</h2></div></div>')
    toner = ["kcn-p", "kcn-a", "kcn-t", "kcn-d"]

    def cert(i, x):
        return (f'<div class="kcn-ruta kcn-cert {toner[i % 4]}"><div class="kcn-topp">{ikon(x.get("ikon", "skold"))}<span>{i + 1:02d}</span></div>'
                f'<div><h3>{E(x["titel"])}</h3>{f"""<p>{E(x["text"])}</p>""" if x.get("text") else ""}</div></div>')

    def bild(bred=False):
        return f'<div class="kcn-ruta kcn-bild{" kcn-bred" if bred else ""}">{_utan_alt(s.bilder.fyll(s.bilder.ta(), "(min-width:1000px) 25vw, 50vw"))}</div>'
    rutor = huvud
    forsta = c[:4]
    for i, x in enumerate(forsta):
        rutor += cert(i, x)
    for _ in range(4 - len(forsta)):
        rutor += bild()
    rest = c[4:]
    for i, x in enumerate(rest, start=4):
        rutor += cert(i, x)
    if rest:
        fyll = (4 - len(rest) % 4) % 4
        if fyll == 1:
            rutor += bild()
        elif fyll == 2:
            rutor += bild(True)
        elif fyll == 3:
            rutor += bild() + bild(True)
    return f'''<section class="sek {s.bg("certifikat")}" aria-labelledby="kcn-h"><div class="wrap"><div class="kcn n{len(c)}">{rutor}</div></div></section>'''


@variant("certifikat", "k-bildsplit")
def certifikat_bildsplit(s):
    """Delad layout: hög bild med rubrik och antal i en färgruta till vänster, till höger staplade kort med bildminiatyr, ikonbricka, titel och text."""
    c, et, rub = _cert(s)
    li = ""
    for i, x in enumerate(c):
        b = s.bilder.ta()
        li += (f'<li class="kcs-kort"><div class="kcs-tumme">{_utan_alt(s.bilder.img(b, "(min-width:700px) 180px, 34vw"))}<span class="kcs-ik">{ikon(x.get("ikon", "skold"))}</span></div>'
               f'<div class="kcs-text"><span class="kcs-nr">{i + 1:02d}</span><h3>{E(x["titel"])}</h3>{f"""<p>{E(x["text"])}</p>""" if x.get("text") else ""}</div></li>')
    bild = s.bilder.ta(s.bt("om"))
    return f'''<section class="sek {s.bg("certifikat")}" aria-labelledby="kcs-h"><div class="wrap kcs">
  <div class="kcs-vanster">{s.bilder.fyll(bild, "(min-width:1000px) 45vw, 100vw", note=True)}
  <div class="kcs-ruta"><span class="etikett">{E(et)}</span><h2 id="kcs-h">{E(rub)}</h2><div class="kcs-fot">{s.textlank(s.T("kontakt_knapp"), "om-oss.html#kontakt")}</div></div></div>
  <ul class="kcs-lista">{li}</ul></div></section>'''


# --- Kunder (logos) -----------------------------------------------------------------------------------------------------
def _kunder(s):
    return s.b.get("kunder") or [], s.T("logos_etikett"), s.b.get("kunder_rubrik") or s.T("logos_rubrik")


_KATEGORI = [
    (("brf ", "bostadsrätt"), "Bostadsrättsförening"),
    (("kommun", "region ", "regionen", "landsting", "trafikverket", "staten"), "Offentlig sektor"),
    (("skol", "förskol", "utbildning"), "Skolfastigheter"),
    (("omsorg", "vård", "sjukhus"), "Vård och omsorg"),
    (("logistik", "lager", "hamn"), "Logistik"),
    (("handel", "köpcent", "butik"), "Handel"),
    (("kraft", "energi", "värme", "el ", "vatten"), "Energi"),
    (("bostäder", "bostad", "hyres"), "Bostadsbolag"),
    (("fastighet", "företagspark", "park", "förvaltning"), "Fastighetsägare"),
    (("industri", "bruk", "verk"), "Industri"),
]


def _kategori(namn, standard):
    n = namn.lower() + " "
    for nycklar, kat in _KATEGORI:
        if any(k in n for k in nycklar):
            return kat
    return standard


@variant("logos", "k-kundkort")
def logos_kundkort(s):
    """Kundkort: stående bildkort per uppdragsgivare med en vit namnplatta som ligger över bildens nederkant, kategori och pil; rutnätet fylls jämnt."""
    ls, et, rub = _kunder(s)
    n = len(ls)
    kol = 3 if n in (3, 5, 6, 9) else 4
    extra = (kol - n % kol) % kol
    m_extra = n % 2
    li = ""
    for i, namn in enumerate(ls):
        b = s.bilder.ta()
        kl = (" klk-s2" if i < extra else "") + (" klk-m2" if i < m_extra else "")
        li += (f'<li class="klk-kort{kl}"><a href="projekt.html"><div class="klk-bild">{_utan_alt(s.bilder.img(b, "(min-width:1000px) 30vw, 50vw"))}</div>'
               f'<div class="klk-platta"><span>{E(_kategori(namn, et))}</span><h3>{E(namn)}</h3><span class="klk-pil">{PIL}</span></div></a></li>')
    return f'''<section class="sek {s.bg("logos")}" aria-labelledby="klk-h"><div class="wrap">
  {s.huvud(et, rub, "klk-h", s.textlank(s.T("proj_lank"), "projekt.html"))}
  <ul class="klk k{kol}">{li}</ul><p class="klk-not mut">Illustrationsbilder</p></div></section>'''


@variant("logos", "k-bento")
def logos_bento(s):
    """Bento: rubrik och antal i ett färgblock, en stor bildruta för första kunden, därefter bildrutor och tonade namnrutor i blandade bredder."""
    ls, et, rub = _kunder(s)
    if not ls:
        return ""
    n = len(ls)
    extra = (4 - (5 + n) % 4) % 4
    typ = []  # för kund 1..n-1: "bild" eller "ord"
    for i in range(1, n):
        typ.append("ord" if i % 2 == 1 else "bild")
    bred = set()
    for j, t in enumerate(typ):
        if len(bred) < extra and t == "bild":
            bred.add(j)
    j = len(typ) - 1
    while len(bred) < extra and j >= 0:
        bred.add(j)
        j -= 1
    ettor = [j for j in range(len(typ)) if j not in bred]
    m2 = ettor[-1] if len(ettor) % 2 else -1
    rutor = (f'<div class="kln-ruta kln-huvud"><span class="etikett">{E(et)}</span><h2 id="kln-h">{E(rub)}</h2>'
             f'<div class="kln-fot">{s.textlank(s.T("proj_lank"), "projekt.html")}</div></div>')
    b0 = s.bilder.ta()
    rutor += (f'<a class="kln-ruta kln-bildruta kln-stor" href="projekt.html">{_utan_alt(s.bilder.fyll(b0, "(min-width:1000px) 50vw, 100vw"))}'
              f'<span class="kln-kat">{E(_kategori(ls[0], et))}</span><h3>{E(ls[0])}</h3></a>')
    ordnr = 0
    for j, (namn, t) in enumerate(zip(ls[1:], typ)):
        kl = (" kln-bred" if j in bred else "") + (" kln-m2" if j == m2 else "")
        if t == "ord":
            ordnr += 1
            kl += " kln-accent" if ordnr % 3 == 2 else ""
            rutor += (f'<a class="kln-ruta kln-ord{kl}" href="projekt.html"><span class="kln-kat">{E(_kategori(namn, et))}</span><h3>{E(namn)}</h3><span class="kln-pil">{PIL}</span></a>')
        else:
            b = s.bilder.ta()
            rutor += (f'<a class="kln-ruta kln-bildruta{kl}" href="projekt.html">{_utan_alt(s.bilder.fyll(b, "(min-width:1000px) 25vw, 50vw"))}'
                      f'<span class="kln-kat">{E(_kategori(namn, et))}</span><h3>{E(namn)}</h3></a>')
    return f'''<section class="sek {s.bg("logos")}" aria-labelledby="kln-h"><div class="wrap"><div class="kln">{rutor}</div></div></section>'''


@variant("logos", "k-karusell")
def logos_karusell(s):
    """Karusell med kundcase: breda kort i en scroll-snap-rad, bild till vänster och färgpanel med nummer, kategori, kundnamn och länk till höger."""
    ls, et, rub = _kunder(s)
    if not ls:
        return ""
    kort = ""
    for i, namn in enumerate(ls):
        b = s.bilder.ta()
        kort += (f'<li class="klc-kort klc-t{i % 3}"><a href="projekt.html"><div class="klc-bild">{_utan_alt(s.bilder.img(b, "(min-width:1100px) 36vw, 86vw", lazy=i > 1))}</div>'
                 f'<div class="klc-panel"><span class="klc-nr">{i + 1:02d} / {len(ls):02d}</span><div><span class="klc-kat">{E(_kategori(namn, et))}</span><h3>{E(namn)}</h3></div>'
                 f'<span class="klc-lank"><span>{E(s.T("proj_lank"))}</span>{PIL}</span></div></a></li>')
    hoger = f'<span class="klc-hint mut">{len(ls)} uppdragsgivare<span aria-hidden="true"> · dra i sidled</span></span>'
    return f'''<section class="sek {s.bg("logos")} klc-sek" aria-labelledby="klc-h"><div class="wrap">{s.huvud(et, rub, "klc-h", hoger)}</div>
  <div class="klc-ram"><ul class="klc" tabindex="0" aria-label="{E(rub)}">{kort}</ul></div></section>'''
