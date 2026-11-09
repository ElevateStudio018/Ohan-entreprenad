"""Varianter G: hållbarhet, investerare, karriärpanel och servicerad i nya layouter.

Prefix per variant (CSS i varianter_g.css):
  hb:      g-kontur .gko-   g-diagonal .gdi-   g-bento .gbe-   g-manifest .gma-   g-tidning .gtd-
  ir:      g-ticker .gti-   g-kalender .gka-   g-tidslinje .gtl-   g-omslag .gom-
  panel:   g-kollage .gkl-  g-remsa .gre-      g-ord .gor-     g-valv .gva-       g-snitt .gsn-
  service: g-chips .gsc-    g-flik .gfl-
"""
import re

from varianter import variant, E, ikon, PIL

MANAD = ["jan", "feb", "mar", "apr", "maj", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]


def _lank_span(text):
    return f'<span class="textlank"><span>{E(text)}</span>{PIL}</span>'


def _datum(d):
    """'2026-10-23' -> ('23', 'okt', '2026'); annat format -> (d, '', '')."""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", (d or "").strip())
    if not m:
        return d or "", "", ""
    return str(int(m.group(3))), MANAD[int(m.group(2)) - 1], m.group(1)


def _kurs(inv):
    """(har_kurs, upp, pil-tecken)"""
    har = bool(inv.get("kurs"))
    upp = (inv.get("forandring") or "+").strip().startswith("+")
    return har, upp, ("&#9650;" if upp else "&#9660;")


def _jobb(s):
    return (s.b["karriar"].get("jobb") or [])[:4]


def _kultur(s):
    return s.b.get("kultur") or s.T("kultur")


SPARK = ('<svg class="{cls}" viewBox="0 0 300 90" preserveAspectRatio="none" aria-hidden="true">'
         '<path d="M0 70 L20 64 L40 68 L60 55 L80 59 L100 47 L120 52 L140 40 L160 45 L180 33 L200 38 L220 26 L240 30 L260 18 L280 22 L300 12 V90 H0Z" fill="currentColor" opacity=".14"/>'
         '<path d="M0 70 L20 64 L40 68 L60 55 L80 59 L100 47 L120 52 L140 40 L160 45 L180 33 L200 38 L220 26 L240 30 L260 18 L280 22 L300 12" fill="none" stroke="currentColor" stroke-width="2.5" vector-effect="non-scaling-stroke"/></svg>')


# =====================================================================================================================
# Hållbarhet
# =====================================================================================================================
@variant("hb", "g-kontur")
def hb_kontur(s):
    """Stora konturnummer i en liggande liggare: värdet som jätteram till vänster, beskrivningen till höger."""
    hb = s.b["hallbarhet"]
    rad = "".join(f'<li class="gko-rad reveal"><span class="gko-tal">{E(a)}</span><div class="gko-txt"><span class="gko-nr">{i + 1:02d}</span><p>{E(t)}</p></div></li>'
                  for i, (a, t) in enumerate(hb["mal"]))
    return (f'<section class="sek gko {s.bg("hb")}" aria-labelledby="gko-h"><div class="wrap">'
            f'<div class="gko-topp"><div><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="gko-h">{E(hb["rubrik"])}</h2></div>'
            f'<div class="gko-ingress"><p>{E(hb["text"])}</p>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div></div>'
            f'<ol class="gko-lista">{rad}</ol></div></section>')


@variant("hb", "g-diagonal")
def hb_diagonal(s):
    """Helbredd: bild som går ut i kanten med snett snitt, texten och målen i en lodrät stapel bredvid."""
    hb = s.b["hallbarhet"]
    bild = s.bilder.ta(s.bt("hb"))
    mal = "".join(f'<li><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
    return (f'<section class="gdi {s.bg("hb")}" aria-labelledby="gdi-h">'
            f'<div class="gdi-bild">{s.bilder.fyll(bild, "(min-width:960px) 55vw, 100vw", note=True)}</div>'
            f'<div class="gdi-text reveal"><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="gdi-h">{E(hb["rubrik"])}</h2>'
            f'<p class="gdi-ingress">{E(hb["text"])}</p><ul class="gdi-mal">{mal}</ul>'
            f'<div class="knappar">{s.knapp(s.T("hb_lank"), "hallbarhet.html", "kontur")}</div></div></section>')


@variant("hb", "g-bento")
def hb_bento(s):
    """Bento-rutnät: rubrikruta i färg, bildruta, textruta och målen som rutor i olika storlekar."""
    hb = s.b["hallbarhet"]
    bild = s.bilder.ta(s.bt("hb"))
    mal = "".join(f'<li class="gbe-ruta gbe-m gbe-m{i + 1}"><b>{E(a)}</b><span>{E(t)}</span></li>' for i, (a, t) in enumerate(hb["mal"]))
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="gbe-h"><div class="wrap"><ul class="gbe">'
            f'<li class="gbe-ruta gbe-rub"><span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="gbe-h">{E(hb["rubrik"])}</h2></li>'
            f'<li class="gbe-ruta gbe-bild">{s.bilder.fyll(bild, "(min-width:960px) 50vw, 100vw", note=True)}</li>'
            f'<li class="gbe-ruta gbe-txt"><p>{E(hb["text"])}</p>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</li>'
            f'{mal}</ul></div></section>')


@variant("hb", "g-manifest")
def hb_manifest(s):
    """Centrerad ordbild: målen skrivs ut som ett löpande manifest i stor stil, siffrorna som färgade märken."""
    hb = s.b["hallbarhet"]
    rader = "".join(f'<span class="gma-del"><span class="gma-tal">{E(a)}</span> {E(t.rstrip("."))}.</span> ' for a, t in hb["mal"])
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="gma-h"><div class="wrap gma">'
            f'<span class="etikett">{E(s.T("hb_etikett"))}</span><h2 id="gma-h">{E(hb["rubrik"])}</h2>'
            f'<p class="gma-manifest reveal">{rader}</p>'
            f'<div class="gma-fot"><p class="mut">{E(hb["text"])}</p>{s.knapp(s.T("hb_lank"), "hallbarhet.html")}</div></div></section>')


@variant("hb", "g-tidning")
def hb_tidning(s):
    """Tidningsuppslag: tjock linje och spaltrubrik, brödtext i två spalter med anfang, bild och faktaruta i sidospalt."""
    hb = s.b["hallbarhet"]
    bild = s.bilder.ta(s.bt("hb"))
    fakta = "".join(f'<li><b>{E(a)}</b><span>{E(t)}</span></li>' for a, t in hb["mal"])
    return (f'<section class="sek {s.bg("hb")}" aria-labelledby="gtd-h"><div class="wrap">'
            f'<div class="gtd-list"><span>{E(s.T("hb_etikett"))}</span>{s.textlank(s.T("hb_lank"), "hallbarhet.html")}</div>'
            f'<div class="gtd">'
            f'<article class="gtd-huvud"><h2 id="gtd-h">{E(hb["rubrik"])}</h2><p class="gtd-spalt">{E(hb["text"])}</p></article>'
            f'<aside class="gtd-sida"><figure class="gtd-fig"><div class="gtd-foto">{s.bilder.img(bild, "(min-width:960px) 30vw, 100vw")}</div>'
            f'<figcaption>Illustrationsbild</figcaption></figure>'
            f'<div class="gtd-fakta"><h3>Fakta</h3><ul>{fakta}</ul></div></aside></div></div></section>')


# =====================================================================================================================
# Investerare
# =====================================================================================================================
@variant("ir", "g-ticker")
def ir_ticker(s):
    """Mörk premiumpanel: kursen stort med kurva, rapporterna som rader och kalendern som ett band i botten."""
    inv = s.b["investerare"]
    har, upp, tecken = _kurs(inv)
    if har:
        kurs = (f'<div class="gti-kurs"><b>{E(inv["kurs"])}</b><span class="gti-sek">SEK</span></div>'
                f'<span class="gti-chip {"upp" if upp else "ned"}"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))} idag</span>'
                f'{SPARK.format(cls="gti-kurva")}<small class="gti-not">Fördröjd kurs · exempeldata</small>')
    else:
        kurs = f'<div class="gti-kurs gti-utan"><b>{E(inv["aktie"])}</b></div><small class="gti-not">{E(inv["lista"])}</small>'
    rap = "".join(f'<li><a href="investerare.html#rapporter"><time>{E(d)}</time><span>{E(t)}</span>{PIL}</a></li>' for t, d in inv["rapporter"][:4])
    kal = "".join(f'<li><time>{E(d)}</time><span>{E(t)}</span></li>' for t, d in (inv.get("kalender") or [])[:4])
    kal_html = f'<div class="gti-kal"><h3>Kalender</h3><ul>{kal}</ul></div>' if kal else ""
    return (f'<section class="sek {s.bg("ir")}" aria-labelledby="gti-h"><div class="wrap"><div class="gti">'
            f'<div class="gti-vanster"><span class="etikett">Investerare</span><h2 id="gti-h">{E(inv["aktie"])} <span>· {E(inv["lista"])}</span></h2>{kurs}</div>'
            f'<div class="gti-hoger"><h3>Rapporter</h3><ul class="gti-rap">{rap}</ul>{s.textlank("Till investerarsidan", "investerare.html")}</div>'
            f'{kal_html}</div></div></section>')


@variant("ir", "g-kalender")
def ir_kalender(s):
    """Finansiell kalender som kalenderblad (dag, månad, år) bredvid en smal spalt med aktien och senaste rapporter."""
    inv = s.b["investerare"]
    har, upp, tecken = _kurs(inv)
    kal = inv.get("kalender") or []
    rubrik = "Finansiell kalender"
    blad_data = kal[:4]
    if not blad_data:
        blad_data, rubrik = inv["rapporter"][:4], "Senaste rapporterna"
    blad = ""
    for t, d in blad_data:
        dag, man, ar = _datum(d)
        topp = f'<span class="gka-man">{E(man)} {E(ar)}</span>' if man else '<span class="gka-man">&nbsp;</span>'
        blad += f'<li class="gka-blad reveal">{topp}<b class="gka-dag">{E(dag)}</b><span class="gka-t">{E(t)}</span></li>'
    if har:
        aktie = (f'<div class="gka-aktie"><span class="gka-namn">{E(inv["aktie"])}</span><b>{E(inv["kurs"])} <small>SEK</small></b>'
                 f'<span class="gka-for {"upp" if upp else "ned"}"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))}</span><small class="mut">{E(inv["lista"])} · exempeldata</small></div>')
    else:
        aktie = f'<div class="gka-aktie"><span class="gka-namn">Ägande</span><b>{E(inv["aktie"])}</b><small class="mut">{E(inv["lista"])}</small></div>'
    rap = "".join(f'<li><a href="investerare.html#rapporter"><span class="gka-pdf">PDF</span><span>{E(t)}</span></a></li>' for t, _ in inv["rapporter"][:3])
    return (f'<section class="sek {s.bg("ir")}" aria-labelledby="gka-h"><div class="wrap">'
            f'{s.huvud("Investerare", rubrik, "gka-h", s.textlank("Till investerarsidan", "investerare.html"))}'
            f'<div class="gka"><aside class="gka-sida">{aktie}<ul class="gka-rap">{rap}</ul>{s.knapp("Finansiell information", "investerare.html", "kontur")}</aside>'
            f'<ol class="gka-blad-lista gka-n{len(blad_data)}">{blad}</ol></div></div></section>')


@variant("ir", "g-tidslinje")
def ir_tidslinje(s):
    """Rapporter och kalender på en gemensam tidslinje med en Idag-markör mellan det publicerade och det kommande."""
    inv = s.b["investerare"]
    har, upp, tecken = _kurs(inv)
    forut = [(d, t, False) for t, d in inv["rapporter"][:4]]
    fram = [(d, t, True) for t, d in (inv.get("kalender") or [])[:4]]
    iso = all(re.match(r"^\d{4}-\d{2}-\d{2}$", d or "") for d, _, _ in forut + fram)
    forut = sorted(forut) if iso else list(reversed(forut))
    fram = sorted(fram) if iso else fram
    def punkt(d, t, kommande):
        return (f'<li class="gtl-p{" gtl-fram" if kommande else ""}"><time>{E(d)}</time><span class="gtl-prick" aria-hidden="true"></span>'
                f'<span class="gtl-typ">{"Kommande" if kommande else "Publicerad"}</span><span class="gtl-t">{E(t)}</span></li>')
    li = "".join(punkt(*x) for x in forut)
    if fram:
        li += '<li class="gtl-idag" aria-hidden="true"><span>Idag</span></li>' + "".join(punkt(*x) for x in fram)
    if har:
        rad = (f'<div class="gtl-aktie"><span class="gtl-namn">{E(inv["aktie"])}</span><b>{E(inv["kurs"])} SEK</b>'
               f'<span class="gtl-for"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))}</span><small class="mut">{E(inv["lista"])} · fördröjd kurs, exempeldata</small>'
               f'{s.knapp("Finansiell information", "investerare.html", "kontur")}</div>')
    else:
        rad = f'<div class="gtl-aktie"><span class="gtl-namn">{E(inv["aktie"])}</span><small class="mut">{E(inv["lista"])}</small>{s.knapp("Finansiell information", "investerare.html", "kontur")}</div>'
    return (f'<section class="sek {s.bg("ir")}" aria-labelledby="gtl-h"><div class="wrap">'
            f'{s.huvud("Investerare", "Rapporter och kalender", "gtl-h", s.textlank("Till investerarsidan", "investerare.html"))}'
            f'<div class="gtl-ram" tabindex="0" aria-label="Tidslinje med rapporter och kalender"><ol class="gtl">{li}</ol></div>{rad}</div></section>')


@variant("ir", "g-omslag")
def ir_omslag(s):
    """Senaste rapporten som ett tecknat rapportomslag i färg, med övriga rapporter, nästa händelse och aktien bredvid."""
    inv = s.b["investerare"]
    har, upp, tecken = _kurs(inv)
    t0, d0 = inv["rapporter"][0]
    ar = re.findall(r"(?:19|20)\d{2}", t0) or re.findall(r"(?:19|20)\d{2}", d0) or [""]
    ovr = "".join(f'<li><a href="investerare.html#rapporter"><span>{E(t)}</span><time>{E(d)}</time>{PIL}</a></li>' for t, d in inv["rapporter"][1:4])
    kal = inv.get("kalender") or []
    nasta = (f'<p class="gom-nasta"><span class="gom-nasta-et">Nästa</span><b>{E(kal[0][0])}</b><time>{E(kal[0][1])}</time></p>' if kal else "")
    aktie = (f'<p class="gom-aktie"><b>{E(inv["aktie"])}</b> {E(inv["kurs"])} SEK <span class="gom-for"><span aria-hidden="true">{tecken}</span> {E(inv.get("forandring", ""))}</span> <small class="mut">· {E(inv["lista"])} · exempeldata</small></p>'
             if har else f'<p class="gom-aktie"><b>{E(inv["aktie"])}</b> <small class="mut">· {E(inv["lista"])}</small></p>')
    return (f'<section class="sek {s.bg("ir")}" aria-labelledby="gom-h"><div class="wrap gom">'
            f'<a class="gom-omslag reveal" href="investerare.html#rapporter" aria-label="{E(t0)}, öppna rapporten">'
            f'<span class="gom-bolag">{E(s.b["kortnamn"])}</span><span class="gom-ar" aria-hidden="true">{E(ar[-1])}</span>'
            f'<span class="gom-titel">{E(t0)}</span><span class="gom-pdf">PDF</span></a>'
            f'<div class="gom-text"><span class="etikett">Investerare</span><h2 id="gom-h">{E(t0)}</h2><p class="gom-datum mut">Publicerad {E(d0)}</p>'
            f'<div class="knappar">{s.knapp("Läs rapporten", "investerare.html#rapporter")}{s.textlank("Finansiell information", "investerare.html")}</div>'
            f'{nasta}<ul class="gom-ovr">{ovr}</ul>{aktie}</div></div></section>')


# =====================================================================================================================
# Karriärpanel
# =====================================================================================================================
@variant("panel", "g-kollage")
def panel_kollage(s):
    """Polaroidkollage: tre lutade fotoramar (med orterna som bildtext) bredvid texten och jobben som etiketter."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    orter = list(dict.fromkeys(o for _, o in jobb if o))
    bilder = [s.bilder.ta(s.bt("panel")) for _ in range(3)]
    ramar = "".join(f'<figure class="gkl-ram gkl-r{i + 1}"><div class="gkl-foto">{s.bilder.img(b, "(min-width:960px) 24vw, 60vw")}</div>'
                    f'<figcaption>{E(orter[i]) if i < len(orter) else "&nbsp;"}</figcaption></figure>' for i, b in enumerate(bilder))
    etik = ""
    if jobb:
        etik = '<ul class="gkl-jobb">' + "".join(f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span></a></li>' for t, o in jobb) + "</ul>"
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="gkl-h"><div class="wrap gkl">'
            f'<div class="gkl-kollage" aria-hidden="false">{ramar}<span class="gkl-not">Illustrationsbilder</span></div>'
            f'<div class="gkl-text"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="gkl-h">{E(k["rubrik"])}</h2>'
            f'<p class="ingress">{E(k["text"])}</p><p class="gkl-kultur">{E(_kultur(s))}</p>{etik}'
            f'<div class="knappar">{s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div></div></div></section>')


@variant("panel", "g-remsa")
def panel_remsa(s):
    """Jobben som höga biljettkort i en horisontell scroll-snap-rad, inledd av ett bildkort och avslutad av ett färgkort."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    bild = s.bilder.ta(s.bt("panel"))
    kort = (f'<li class="gre-kort gre-bild">{s.bilder.fyll(bild, "(min-width:960px) 30vw, 80vw", note=True)}'
            f'<p class="gre-kultur">{E(_kultur(s))}</p></li>')
    kort += "".join(f'<li class="gre-kort gre-jobb"><a href="karriar.html"><span class="gre-topp"><span class="gre-nr">{i + 1:02d}</span><span class="gre-ort">{E(o)}</span></span>'
                    f'<b>{E(t)}</b>{_lank_span("Läs mer och ansök")}</a></li>' for i, (t, o) in enumerate(jobb))
    sista = (f'<b class="gre-antal">{len(jobb)}</b><span>{"ledig tjänst" if len(jobb) == 1 else "lediga tjänster"} just nu</span>' if jobb
             else f'<b class="gre-stor">{E(s.T("panel_knapp"))}</b>')
    kort += f'<li class="gre-kort gre-cta"><a href="karriar.html">{sista}<span class="rundpil">{PIL}</span></a></li>'
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="gre-h"><div class="wrap">'
            f'<div class="gre-huvud"><div><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="gre-h">{E(k["rubrik"])}</h2></div>'
            f'<p class="ingress">{E(k["text"])}</p></div>'
            f'<ul class="gre" tabindex="0" aria-label="{E(s.T("panel_etikett"))}, bläddra i sidled">{kort}</ul>'
            f'<div class="gre-fot"><span class="mut gre-dra" aria-hidden="true">Dra för fler {PIL}</span>{s.textlank(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div></div></section>')


@variant("panel", "g-ord")
def panel_ord(s):
    """Ordbild: jätterubrik över hela bredden, en låg panoramabild och tre spalter med text, kultur och jobb."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    bild = s.bilder.ta(s.bt("panel"))
    if jobb:
        tredje = ('<ol class="gor-jobb">' + "".join(f'<li><a href="karriar.html"><span class="gor-nr">{i + 1:02d}</span><b>{E(t)}</b><span class="mut">{E(o)}</span></a></li>'
                                                  for i, (t, o) in enumerate(jobb)) + "</ol>")
    else:
        tredje = f'<div class="knappar" style="margin-top:0">{s.knapp(s.T("panel_knapp"), "karriar.html")}</div>'
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="gor-h"><div class="wrap">'
            f'<span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="gor-h" class="gor-rubrik">{E(k["rubrik"])}</h2>'
            f'<div class="gor-bild reveal">{s.bilder.fyll(bild, "(min-width:1360px) 1300px, 100vw", note=True)}</div>'
            f'<div class="gor-spalter"><p class="ingress">{E(k["text"])}</p><div><p class="gor-kultur">{E(_kultur(s))}</p>'
            f'{s.textlank(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div>{tredje}</div></div></section>')


@variant("panel", "g-valv")
def panel_valv(s):
    """Valvformad bild med ett runt märke för antalet lediga jobb, texten och jobben i ett tvåspaltigt rutnät bredvid."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    bild = s.bilder.ta(s.bt("panel"))
    marke = (f'<span class="gva-marke"><b>{len(jobb)}</b><span>{"ledig tjänst" if len(jobb) == 1 else "lediga tjänster"}</span></span>' if jobb else "")
    lista = ""
    if jobb:
        lista = '<ul class="gva-jobb">' + "".join(f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span>{PIL}</a></li>' for t, o in jobb) + "</ul>"
    return (f'<section class="sek {s.bg("panel")}" aria-labelledby="gva-h"><div class="wrap gva">'
            f'<div class="gva-figur reveal"><div class="gva-bild">{s.bilder.fyll(bild, "(min-width:960px) 40vw, 90vw", note=True)}</div>{marke}</div>'
            f'<div class="gva-text"><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="gva-h">{E(k["rubrik"])}</h2>'
            f'<p class="ingress">{E(k["text"])}</p><blockquote class="gva-kultur"><p>{E(_kultur(s))}</p></blockquote>{lista}'
            f'<div class="knappar">{s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html")}</div></div></div></section>')


@variant("panel", "g-snitt")
def panel_snitt(s):
    """Bildband i helbredd med snett snitt nedtill, och en färgpanel som skjuter upp över bilden och går ut i högerkanten."""
    k = s.b["karriar"]
    jobb = _jobb(s)
    bild = s.bilder.ta(s.bt("panel"))
    if jobb:
        hoger = ('<ul class="gsn-jobb">' + "".join(f'<li><a href="karriar.html"><b>{E(t)}</b><span>{E(o)}</span>{PIL}</a></li>' for t, o in jobb) + "</ul>")
    else:
        hoger = f'<p class="gsn-kultur">{E(_kultur(s))}</p>'
    return (f'<section class="gsn" aria-labelledby="gsn-h"><div class="gsn-bild">{s.bilder.fyll(bild, note=True)}</div>'
            f'<div class="gsn-panel reveal"><div class="gsn-inner">'
            f'<div><span class="etikett">{E(s.T("panel_etikett"))}</span><h2 id="gsn-h">{E(k["rubrik"])}</h2><p class="gsn-text">{E(k["text"])}</p>'
            f'{f"""<p class="gsn-kultur gsn-k2">{E(_kultur(s))}</p>""" if jobb else ""}</div>'
            f'<div>{hoger}<div class="knappar">{s.knapp(s.T("panel_alla" if jobb else "panel_knapp"), "karriar.html", "ljus")}</div></div>'
            f'</div></div></section>')


# =====================================================================================================================
# Servicerad
# =====================================================================================================================
def _service(s):
    return s.b.get("service") or [("Lediga lägenheter", "hus", "projekt.html"), ("Felanmälan", "kugge", "om-oss.html#kontakt"),
                                  ("Bostadskö", "dokument", "om-oss.html#kontakt"), ("Mina sidor", "nyckel", "#")]


@variant("service", "g-chips")
def service_chips(s):
    """Smalt tonat band med en rubrik till vänster och genvägarna som rundade piller med ikon."""
    a = "".join(f'<a href="{E(h)}">{ikon(i, "ik")}<span>{E(t)}</span></a>' for t, i, h in _service(s))
    return (f'<div class="gsc"><div class="wrap gsc-in"><span class="gsc-rubrik">Genvägar</span>'
            f'<nav class="gsc-nav" aria-label="Snabbtjänster">{a}</nav></div></div>')


@variant("service", "g-flik")
def service_flik(s):
    """Mörk flikrad i helbredd: genvägarna som jämnbreda kolumner med ikon i ring, accentlinje upptill vid hovring."""
    r = _service(s)
    a = "".join(f'<a href="{E(h)}"><span class="gfl-ik">{ikon(i, "ik")}</span><span class="gfl-t">{E(t)}</span>{PIL}</a>' for t, i, h in r)
    return (f'<div class="gfl"><div class="wrap"><nav class="gfl-nav" style="--n:{len(r)}" aria-label="Snabbtjänster">{a}</nav></div></div>')
