"""Varianter L: tidslinje, investerare (ir), citat och frågor & svar (faq) – bildtunga syskon till användarens favoriter.

Prefix (alla börjar på l): .lv (gemensamma lokala färger), .ltb- (tidslinje/l-bildkort), .ltk- (tidslinje/l-karusell),
.lte- (tidslinje/l-epoker), .lir- (ir/l-rapporter), .lib- (ir/l-bento), .lik- (ir/l-kalender), .lcb- (citat/l-bildkort),
.lco- (citat/l-overlap), .lck- (citat/l-karusell), .lfb- (faq/l-bildkort), .lfe- (faq/l-bento).
"""
import re

from varianter import variant, E, ikon, PIL

MANAD = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
CIT = ('<svg class="{c}" viewBox="0 0 120 96" aria-hidden="true"><path fill="currentColor" d="M0 96V58C0 25 15 6 46 0l6 13C35 19 '
       '27 31 26 48h22v48zm68 0V58c0-33 15-52 46-58l6 13c-17 6-25 18-26 35h22v48z"/></svg>')


def _nb(text):
    """Escapar och håller ihop tal som "21 000" med hårt mellanslag."""
    return re.sub(r"(?<=\d) (?=\d|kr\b|%)", "&nbsp;", E(text))


def _tel(t):
    return t.replace(" ", "").replace("-", "")


def _ingress(text, kl="ingress"):
    return f'<p class="{kl}">{E(text)}</p>' if text else ""


def _initial(namn):
    d = [w for w in re.split(r"[\s.]+", namn or "") if w]
    return E("".join(w[0] for w in d[:2]).upper() or "?")


def _datum(d):
    """'2027-02-05' -> ('5', 'feb', '2027'); annat format -> (hela texten, '', '')."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", d or "")
    if m:
        return str(int(m.group(3))), MANAD[int(m.group(2)) - 1], m.group(1)
    return d or "", "", ""


def _kurs(inv):
    har = bool(inv.get("kurs"))
    upp = (inv.get("forandring") or "+").strip().startswith("+")
    return har, upp, "▲" if upp else "▼"


def _delar(n, k):
    """Delar n poster i k sammanhängande grupper (de första blir störst)."""
    k = max(1, min(k, n))
    bas, rest = divmod(n, k)
    ut, i = [], 0
    for j in range(k):
        st = bas + (1 if j < rest else 0)
        ut.append((i, i + st))
        i += st
    return ut


def _meningar(text):
    """Delar ett citat i 2–3 delar (meningar, annars kolon/tankstreck/komma)."""
    delar = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]
    if len(delar) < 2:
        m = re.search(r"(?<=[:–,])\s+", text)
        if m and 18 <= m.start() <= len(text) - 12:
            delar = [text[:m.start()], text[m.end():]]
    if len(delar) == 2 and len(delar[1]) > 90:
        m = re.search(r"(?<=[:–])\s+", delar[1])
        if m and 20 <= m.start() <= len(delar[1]) - 20:
            delar = [delar[0], delar[1][:m.start()], delar[1][m.end():]]
    if len(delar) > 3:
        delar = delar[:2] + [" ".join(delar[2:])]
    return delar or [text]


# =====================================================================================================================
# Tidslinje
# =====================================================================================================================
def _tl(s):
    tl = s.b.get("tidslinje") or []
    return tl, s.T("tidslinje_etikett"), s.b.get("tidslinje_rubrik") or s.T("tidslinje_rubrik"), s.b.get("tidslinje_text", "")


def _tl_bild(s, i):
    """Bild till händelse i: växlar mellan om-sidans motiv, sajtens tyngd och om-bilden."""
    return s.bilder.ta([s.bt("sida_om"), None, s.bt("om")][i % 3])


@variant("tidslinje", "l-bildkort")
def tidslinje_bildkort(s):
    """Bildkort i ett rutnät där en sammanhängande linje löper genom årtalen mellan bild och text."""
    tl, et, rub, text = _tl(s)
    li = ""
    for i, (a, t) in enumerate(tl):
        bild = _tl_bild(s, i)
        li += (f'<li class="ltb-steg reveal"><div class="ltb-foto">{s.bilder.img(bild, "(min-width:1100px) 25vw, (min-width:700px) 45vw, 90vw")}</div>'
               f'<div class="ltb-linje"><span class="ltb-prick" aria-hidden="true"></span><b class="ltb-ar">{E(a)}</b></div><p>{_nb(t)}</p></li>')
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="ltb-h"><div class="wrap lv">
  {s.huvud(et, rub, "ltb-h", _ingress(text, "ingress ltb-ingress"))}
  <ol class="ltb n{len(tl)}">{li}</ol><span class="figtext ltb-not">Illustrationsbilder</span></div></section>'''


@variant("tidslinje", "l-karusell")
def tidslinje_karusell(s):
    """Stora bildslides i en horisontell scroll-snap-rad, årtalet i en färgruta på bilden och en årsnavigering ovanför."""
    tl, et, rub, text = _tl(s)
    n = len(tl)
    nav = "".join(f'<a href="#ltk-{i}">{E(a)}</a>' for i, (a, _) in enumerate(tl))
    li = ""
    for i, (a, t) in enumerate(tl):
        bild = _tl_bild(s, i)
        li += (f'<li class="ltk-slide" id="ltk-{i}">{s.bilder.fyll(bild, "(min-width:900px) 60vw, 86vw")}<span class="ltk-nr">{i + 1:02d} / {n:02d}</span>'
               f'<div class="ltk-ruta"><b class="ltk-ar">{E(a)}</b><p>{_nb(t)}</p></div></li>')
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="ltk-h"><div class="wrap lv">
  {s.huvud(et, rub, "ltk-h", _ingress(text, "ingress ltk-ingress"))}
  <nav class="ltk-nav" aria-label="Hoppa till år">{nav}</nav></div>
  <div class="lv ltk-ram" tabindex="0" aria-label="{E(rub)} – bläddra i sidled"><ol class="ltk-rad">{li}</ol></div></section>'''


@variant("tidslinje", "l-epoker")
def tidslinje_epoker(s):
    """Historien delad i tre epoker som ett bento: bildrutor med epokens år och färgrutor med händelserna."""
    tl, et, rub, text = _tl(s)
    grupper = _delar(len(tl), 3) if tl else []
    rutor = []
    for j, (a, b) in enumerate(grupper):
        del_ = tl[a:b]
        spann = E(del_[0][0]) + (f"–{E(del_[-1][0])}" if len(del_) > 1 else "")
        bild = _tl_bild(s, j)
        rader = "".join(f'<li><b>{E(ar)}</b><span>{_nb(t)}</span></li>' for ar, t in del_)
        rutor.append(f'<div class="lte-bild lte-b{j + 1} reveal">{s.bilder.fyll(bild, "(min-width:1000px) 50vw, 100vw")}<span class="lte-spann"><small>Epok {j + 1}</small>{spann}</span></div>')
        rutor.append(f'<div class="lte-text lte-t{j + 1} reveal"><span class="lte-etikett">{spann}</span><ul>{rader}</ul></div>')
    slut = (f'<div class="lte-slut reveal"><p>{E(s.T("fot_cta"))}</p>{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "kontur")}</div>')
    return f'''<section class="sek {s.bg("tidslinje")}" aria-labelledby="lte-h"><div class="wrap lv">
  {s.huvud(et, rub, "lte-h", _ingress(text, "ingress lte-ingress"))}
  <div class="lte e{len(grupper)}">{"".join(rutor)}{slut}</div></div></section>'''


# =====================================================================================================================
# Investerare
# =====================================================================================================================
def _kurs_chip(inv, kl):
    har, upp, tecken = _kurs(inv)
    if har:
        return (f'<p class="{kl}"><b>{E(inv["aktie"])}</b><span>{E(inv["kurs"])}&nbsp;SEK</span>'
                f'<span class="{kl}-for {"upp" if upp else "ned"}"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))}</span><small>{E(inv["lista"])} · exempeldata</small></p>')
    return f'<p class="{kl}"><b>{E(inv["aktie"])}</b><small>{E(inv["lista"])}</small></p>'


@variant("ir", "l-rapporter")
def ir_rapporter(s):
    """Rapporterna som fotoomslag i en rad: bild med PDF-märke och en färgad fotdel med titel och datum."""
    inv = s.b["investerare"]
    rap = inv["rapporter"][:4]
    kort = ""
    for i, (t, d) in enumerate(rap):
        bild = s.bilder.ta(s.bt("sida_inv"))
        dag, man, ar = _datum(d)
        datum = f"{dag} {man} {ar}" if man else d
        kort += (f'<li class="lir-kort{" lir-forsta" if i == 0 else ""} reveal"><a href="investerare.html#rapporter">'
                 f'<div class="lir-foto">{s.bilder.img(bild, "(min-width:1100px) 25vw, 78vw")}<span class="lir-pdf">PDF</span>'
                 f'{"<span class=lir-ny>Senaste</span>" if i == 0 else ""}<span class="lir-namn">{E(s.b["kortnamn"])}</span></div>'
                 f'<div class="lir-fot"><h3>{E(t)}</h3><span class="lir-rad"><time>{E(datum)}</time><span class="rundpil">{PIL}</span></span></div></a></li>')
    return f'''<section class="sek {s.bg("ir")}" aria-labelledby="lir-h"><div class="wrap lv">
  {s.huvud("Investerare", "Rapporter och presentationer", "lir-h", _kurs_chip(inv, "lir-kurs"))}
  <ul class="lir n{len(rap)}">{kort}</ul>
  <div class="lir-fot-rad">{s.textlank("Till investerarsidan", "investerare.html")}<span class="figtext lir-not">Illustrationsbilder</span></div></div></section>'''


@variant("ir", "l-bento")
def ir_bento(s):
    """Bento: kursen i en stor färgruta, två bildrutor, nästa händelse som datumruta, senaste rapporten och övriga rapporter."""
    inv = s.b["investerare"]
    har, upp, tecken = _kurs(inv)
    if har:
        kurs = (f'<div class="lib-k reveal"><span class="lib-et">{E(inv["aktie"])}</span><b class="lib-kurs">{E(inv["kurs"])}<small>SEK</small></b>'
                f'<span class="lib-for {"upp" if upp else "ned"}"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))} idag</span>'
                f'<small class="lib-lista">{E(inv["lista"])} · fördröjd kurs, exempeldata</small>{s.textlank("Aktien", "investerare.html")}</div>')
    else:
        kurs = (f'<div class="lib-k reveal"><span class="lib-et">Ägande</span><b class="lib-kurs lib-utan">{E(inv["aktie"])}</b>'
                f'<small class="lib-lista">{E(inv["lista"])}</small>{s.textlank("Finansiell information", "investerare.html")}</div>')
    rap = inv["rapporter"]
    kal = inv.get("kalender") or []
    if kal:
        nt, nd = kal[0]
        n_et = "Nästa händelse"
        senaste, ovr = rap[0], rap[1:4]
    else:
        nt, nd = rap[0]
        n_et = "Senast publicerad"
        senaste, ovr = (rap[1] if len(rap) > 1 else rap[0]), rap[2:5]
    dag, man, ar = _datum(nd)
    nasta = (f'<div class="lib-n reveal"><span class="lib-et">{n_et}</span><b class="lib-dag">{E(dag)}</b>'
             f'{f"<span class=lib-man>{E(man)} {E(ar)}</span>" if man else ""}<span class="lib-nt">{E(nt)}</span></div>')
    rt, rd = senaste
    rapport = (f'<a class="lib-r reveal" href="investerare.html#rapporter"><span class="lib-pdf">PDF</span><span class="lib-et">Senaste rapport</span>'
               f'<b>{E(rt)}</b><span class="lib-rad"><time>{E(rd)}</time><span class="rundpil">{PIL}</span></span></a>')
    lista = "".join(f'<li><a href="investerare.html#rapporter"><span>{E(t)}</span><time>{E(d)}</time>{PIL}</a></li>' for t, d in ovr)
    lista_html = f'<div class="lib-l reveal"><span class="lib-et">Fler rapporter</span><ul>{lista}</ul></div>' if lista else ""
    b1, b2 = s.bilder.ta(s.bt("sida_inv")), s.bilder.ta(s.bt("hb"))
    return f'''<section class="sek {s.bg("ir")}" aria-labelledby="lib-h"><div class="wrap lv">
  {s.huvud("Investerare", "Finansiell information", "lib-h", s.textlank("Till investerarsidan", "investerare.html"))}
  <div class="lib{"" if lista else " utan-lista"}">{kurs}<div class="lib-i reveal">{s.bilder.fyll(b1, "(min-width:1000px) 50vw, 100vw", note=True)}</div>{nasta}{rapport}
  <div class="lib-j reveal">{s.bilder.fyll(b2, "(min-width:1000px) 50vw, 100vw")}</div>{lista_html}</div></div></section>'''


@variant("ir", "l-kalender")
def ir_kalender(s):
    """Kalenderkort med foto: varje händelse får en bild med ett kalenderblad som sticker ut, nästa händelse i färg; kursband under."""
    inv = s.b["investerare"]
    kal = (inv.get("kalender") or [])[:4]
    rubrik, typ = "Kommande händelser", "Kommande"
    if not kal:
        kal, rubrik, typ = inv["rapporter"][:4], "Senaste rapporterna", "Publicerad"
    kort = ""
    for i, (t, d) in enumerate(kal):
        bild = s.bilder.ta(s.bt("sida_inv") if i % 2 == 0 else s.bt("om"))
        dag, man, ar = _datum(d)
        blad = (f'<span class="lik-blad"><span class="lik-man">{E(man)}</span><b>{E(dag)}</b><span class="lik-ar">{E(ar)}</span></span>' if man
                else f'<span class="lik-blad lik-fri"><b>{E(dag)}</b></span>')
        et = "Nästa" if i == 0 and typ == "Kommande" else typ
        kort += (f'<li class="lik-kort{" lik-forsta" if i == 0 else ""} reveal"><div class="lik-foto">{s.bilder.img(bild, "(min-width:1100px) 25vw, 80vw")}</div>{blad}'
                 f'<div class="lik-text"><span class="lik-typ">{et}</span><h3>{E(t)}</h3></div></li>')
    rap = "".join(f'<li><a href="investerare.html#rapporter"><span class="lik-pdf">PDF</span><span>{E(t)}</span></a></li>' for t, _ in inv["rapporter"][:3])
    return f'''<section class="sek {s.bg("ir")}" aria-labelledby="lik-h"><div class="wrap lv">
  {s.huvud("Investerare", rubrik, "lik-h", s.textlank("Finansiell kalender", "investerare.html"))}
  <ol class="lik n{len(kal)}">{kort}</ol>
  <div class="lik-band reveal">{_kurs_chip(inv, "lik-kurs")}<ul class="lik-rap">{rap}</ul>{s.knapp("Finansiell information", "investerare.html", "ljus")}</div></div></section>'''


# =====================================================================================================================
# Citat
# =====================================================================================================================
def _citat(s):
    return s.b.get("citat") or {"text": s.b["om"][1], "namn": "Vd", "roll": s.b["namn"]}


@variant("citat", "l-bildkort")
def citat_bildkort(s):
    """Bento av bildkort: porträttbild med namnruta, citatet i en stor tonad ruta, en andra bild och en färgruta med länk."""
    c = _citat(s)
    b1 = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    b2 = s.bilder.ta(s.bt("om"))
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap lv"><figure class="lcb">
  <div class="lcb-portratt reveal">{s.bilder.fyll(b1, "(min-width:1000px) 40vw, 100vw", note=True)}<figcaption class="lcb-namn"><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></div>
  <blockquote class="lcb-citat reveal">{CIT.format(c="lcb-tecken")}<p>{_nb(c["text"])}</p></blockquote>
  <div class="lcb-bild reveal">{s.bilder.fyll(b2, "(min-width:1000px) 25vw, 50vw")}</div>
  <a class="lcb-lank reveal" href="om-oss.html"><span class="lcb-av" aria-hidden="true">{_initial(c["namn"])}</span><span class="lcb-lt">{E(s.T("sida_om_titel"))}</span><span class="rundpil">{PIL}</span></a>
</figure></div></section>'''


@variant("citat", "l-overlap")
def citat_overlap(s):
    """Panoramabild över hela bredden med en färgad citatpanel och ett litet porträtt som båda överlappar bildens nederkant."""
    c = _citat(s)
    b1 = s.bilder.ta(s.bt("om"))
    b2 = s.bilder.ta(c.get("tagg") or s.bt("citat"))
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><div class="wrap lv"><figure class="lco">
  <div class="lco-pano">{s.bilder.fyll(b1, "100vw", note=True)}</div>
  <div class="lco-portratt reveal">{s.bilder.img(b2, "(min-width:1000px) 22vw, 40vw")}</div>
  <div class="lco-panel reveal">{CIT.format(c="lco-tecken")}<blockquote><p>{_nb(c["text"])}</p></blockquote>
    <figcaption><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></figcaption></div>
</figure></div></section>'''


@variant("citat", "l-karusell")
def citat_karusell(s):
    """Citatet berättat i en horisontell rad: ett färgkort med vem som talar, sedan bildkort med citatet mening för mening."""
    c = _citat(s)
    delar = _meningar(c["text"])
    n = len(delar)
    kort = ""
    for i, d in enumerate(delar):
        bild = s.bilder.ta(c.get("tagg") or s.bt("citat") if i == 0 else s.bt("om") if i == 1 else None)
        oppna = "”" if i == 0 else ""
        stang = "”" if i == n - 1 else ""
        kort += (f'<li class="lck-kort"><div class="lck-foto">{s.bilder.img(bild, "(min-width:1000px) 30vw, 80vw")}<span class="lck-nr">{i + 1}/{n}</span></div>'
                 f'<p class="lck-del">{oppna}{_nb(d)}{stang}</p></li>')
    forsta = (f'<li class="lck-kort lck-start">{CIT.format(c="lck-tecken")}<span class="lck-et">Citat</span>'
              f'<p class="lck-vem"><b>{E(c["namn"])}</b><span>{E(c["roll"])}</span></p><span class="lck-av" aria-hidden="true">{_initial(c["namn"])}</span></li>')
    return f'''<section class="sek {s.bg("citat")}" aria-label="Citat"><figure class="lv lck-ram" tabindex="0" aria-label="Citat från {E(c["namn"])} – bläddra i sidled">
  <blockquote class="lv-sr"><p>”{_nb(c["text"])}”</p></blockquote><figcaption class="lv-sr">{E(c["namn"])}, {E(c["roll"])}</figcaption>
  <ol class="lck-rad" aria-hidden="true">{forsta}{kort}</ol></figure>
  <div class="wrap"><p class="figtext lck-not">Illustrationsbilder</p></div></section>'''


# =====================================================================================================================
# Frågor och svar
# =====================================================================================================================
def _fq(s, n=6):
    return ((s.b.get("faq") or [])[:n], s.T("faq_etikett"), s.T("faq_rubrik"), s.b.get("faq_text", "Hittar du inte svaret? Ring eller mejla oss."))


def _faq_lank(s):
    return s.textlank("Alla frågor", "faq.html") if "faq" in s.slugs else ""


@variant("faq", "l-bildkort")
def faq_bildkort(s):
    """Stort bildkort med rubriken i en färgruta (står kvar vid scroll) bredvid frågorna som fristående kort."""
    fq, et, rub, text = _fq(s)
    k = s.b["kontakt"]
    bild = s.bilder.ta(s.bt("sida_faq"))
    kort = "".join(f'<details class="lfb-kort"{" open" if i == 0 else ""}><summary><span class="lfb-nr">{i + 1:02d}</span><span class="lfb-q">{E(q)}</span>'
                   f'<span class="lfb-plus" aria-hidden="true"></span></summary><p>{_nb(a)}</p></details>' for i, (q, a) in enumerate(fq))
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="lfb-h"><div class="wrap lv lfb">
  <div class="lfb-sida"><div class="lfb-bild">{s.bilder.fyll(bild, "(min-width:1000px) 42vw, 100vw", note=True)}
    <div class="lfb-ruta"><span class="etikett">{E(et)}</span><h2 id="lfb-h">{E(rub)}</h2><p>{E(text)}</p>
    <div class="lfb-knappar">{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}<a class="lfb-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a></div></div></div></div>
  <div class="lfb-lista">{kort}<div class="lfb-fot">{_faq_lank(s)}</div></div></div></section>'''


@variant("faq", "l-bento")
def faq_bento(s):
    """Bento där frågekort med synliga svar varvas med två bildrutor och en färgad kontaktruta."""
    fq, et, rub, text = _fq(s, 5)
    k = s.b["kontakt"]
    b1, b2 = s.bilder.ta(s.bt("sida_faq")), s.bilder.ta(s.bt("om"))
    q = [f'<li class="lfe-q lfe-q{i + 1} reveal"><span class="lfe-nr">Fråga {i + 1:02d}</span><h3>{E(fq_)}</h3><p>{_nb(a)}</p></li>' for i, (fq_, a) in enumerate(fq)]
    bild1 = f'<li class="lfe-bild lfe-b1 reveal">{s.bilder.fyll(b1, "(min-width:1000px) 33vw, 100vw", note=True)}</li>'
    bild2 = f'<li class="lfe-bild lfe-b2 reveal">{s.bilder.fyll(b2, "(min-width:1000px) 33vw, 100vw")}</li>'
    kontakt = (f'<li class="lfe-kontakt reveal"><p>{E(text)}</p><a class="lfe-tel" href="tel:{_tel(k["telefon"])}">{ikon("telefon")}<span>{E(k["telefon"])}</span></a>'
               f'{s.knapp(s.T("kontakt_knapp"), "om-oss.html#kontakt", "ljus")}</li>')
    # Ordning: bild, F1, F2, F3, kontakt, F4, bild, F5 (rutnätet placerar dem som ett schackbräde på dator)
    delar = [bild1] + q[:3] + [kontakt] + q[3:4] + [bild2] + q[4:5]
    return f'''<section class="sek {s.bg("faq")}" aria-labelledby="lfe-h"><div class="wrap lv">
  {s.huvud(et, rub, "lfe-h", _faq_lank(s))}
  <ul class="lfe n{len(fq)}">{"".join(delar)}</ul></div></section>'''
