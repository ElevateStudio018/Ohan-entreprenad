"""SEO och teknik för HRS-sajten: tjänstesidor, titlar och beskrivningar, canonical, Open Graph, strukturerad data,
sajtkarta, robots.txt, 404-sida, omdirigeringar och serverrubriker. Används av bygg_hrs.py.

Läget styrs av två miljövariabler:
  HRS_SAJT  sajtens riktiga adress (standard https://www.haningeriv.se/), används i canonical, og:url och sajtkartan
  HRS_LAGE  "produktion" = sökbar sajt; annars förslag (noindex, robots.txt stänger, förslagsetiketten syns)
"""
import html
import json
import os
import re
from pathlib import Path

from PIL import Image

E = html.escape
SAJT = os.environ.get("HRS_SAJT", "https://www.haningeriv.se/").rstrip("/") + "/"
PRODUKTION = os.environ.get("HRS_LAGE") == "produktion"
TEL, TEL_E164, MAIL = "072-002 22 00", "+46720022200", "info@haningeriv.se"
NAMN = "Haninge Riv & Sanering AB"

# ---------- tjänstesidorna: en sida per tjänst, med HRS egna texter ----------
TJANSTER = [
 {"slug": "rivning", "namn": "Rivning", "tagg": "hrs-rivning", "tagg2": "hrs-hall", "typ": "Rivning",
  "titel": "Rivning och rivningsfirma i Haninge | HRS AB",
  "beskr": "Tung och lätt rivning: hela byggnader, lägenheter, väggar och stambytesrivning. Provtagning och miljöriktig sortering ingår. Svar inom 24 timmar.",
  "h1": "Rivning", "ingress": "Tunga och lätta rivningsarbeten – från enstaka väggar och rum till lägenheter och hela byggnader. Vi tar hand om allt som krävs för att rivningen ska ske smidigt och säkert.",
  "text": ["Vi jobbar med både tunga och lätta rivningsarbeten och tar hand om både små och stora byggnader, lägenheter och andra utrymmen. Åt stora byggföretag kör vi stambytesrivning, lägenhet för lägenhet.",
           "Innan vi börjar kontrollerar vårt team vilka material som finns i byggnaden och hur konstruktionen hänger ihop. Med hjälp av prover och ritningar planerar vi ett säkert och väl utfört rivningsarbete som du kan känna dig trygg med – enligt de regler och lagar som gäller.",
           "Sortering och hantering av avfallet på ett miljövänligt sätt ingår alltid. Vi tar hand om grovjobbet, och du får en planering som är smidig och smärtfri för dig."],
  "ingar": ["Hela byggnader", "Delar av byggnader", "Lägenheter", "Enstaka rum och väggar", "Stambytesrivning", "Sortering av avfall"]},
 {"slug": "sanering", "namn": "Sanering", "tagg": "hrs-sanering", "tagg2": "hrs-sanering2", "typ": "Sanering",
  "titel": "Sanering av mögel, asbest och vattenskador | HRS AB",
  "beskr": "Mögelsanering, asbestsanering, vattenskador, olja, lukt och klotter – i inplastade zoner så att inget sprids. Akuta ärenden tar vi så snart vi kan.",
  "h1": "Sanering", "ingress": "Bort med det som inte hör hemma och in med en fräschare miljö. Mögel, asbest, vattenskador, olja, lukt och klotter.",
  "text": ["Vid bygg, renovering och underhåll kan sanering komma bra till hands. Ibland stöter du på oönskade vattenskador, behöver avlägsna olja eller rensa ventilationen – då kan du räkna med oss.",
           "Vårt team har lång erfarenhet av saneringsarbeten, oavsett vilken typ av sanering det gäller: mögelsanering, asbestsanering, klottersanering och skadesanering. Vi avlägsnar farliga material, gammalt avfall, lukt och skadliga ämnen, och hjälper till med marksanering och rengöring av avlopp, rör och fasader.",
           "Skadliga ämnen saneras i inplastade zoner, så att damm och partiklar stannar där de ska. Har du ett akut ärende kan du alltid kontakta oss."],
  "ingar": ["Mögelsanering", "Asbestsanering", "Vattenskador", "Olja och lukt", "Klotter", "Marksanering", "Avlopp, rör och fasader"]},
 {"slug": "betonghaltagning", "namn": "Betonghåltagning", "tagg": "hrs-haltagning", "tagg2": "hrs-borrning", "typ": "Betonghåltagning",
  "titel": "Betonghåltagning och kärnborrning i Haninge | HRS AB",
  "beskr": "Kärnborrning, väggsågning och golvsågning i betong för rör, ventilation, dörrar, trappor och öppnare planlösningar. Begär offert – svar inom 24 timmar.",
  "h1": "Betonghåltagning", "ingress": "Kärnborrning, väggsågning och golvsågning i betong – för rör, ventilation, trappor, dörrar och öppnare planlösningar.",
  "text": ["Betonghåltagning används flitigt vid bygg och renovering: när nya vattenrör eller ventilationsrör ska installeras, när kök eller badrum renoveras, när trappor eller dörrar ska in eller när du vill ha en mer öppen planlösning.",
           "Vid en betonghåltagning gör vi hål i betongen efter gjutning och förbereder för olika typer av installationer samt kabel- och eldragningar.",
           "Som i alla våra uppdrag planeras arbetet noggrant för att undvika skador och ras. Vi tar alltid det säkra före det osäkra."],
  "ingar": ["Kärnborrning", "Väggsågning", "Golvsågning", "Dörr- och trapphål", "Hål för rör och ventilation"]},
 {"slug": "frilaggning-av-ror", "namn": "Friläggning av rör", "tagg": "hrs-ror", "tagg2": "hrs-stad", "typ": "Friläggning av rör vid fuktskada",
  "titel": "Friläggning av rör vid fuktskador | HRS AB",
  "beskr": "Har du fått en fuktskada? Vi öppnar golv och väggar och frilägger rör och golvbrunnar som blivit utsatta, så att de kan åtgärdas. Ring oss.",
  "h1": "Friläggning av rör vid fuktskador", "ingress": "Har du fått en fuktskada? Vi frilägger rören som blivit utsatta, så att de kan åtgärdas.",
  "text": ["Vid en fuktskada behöver de skadade rören friläggas innan de kan bytas eller lagas. Vårt team öppnar golv och väggar och frilägger rör och golvbrunnar där skadan finns.",
           "Arbetet planeras noggrant och rivningsmassorna sorteras för återvinning. Har du ett akut ärende kan du alltid kontakta oss."],
  "ingar": ["Golv", "Väggar", "Golvbrunnar", "Schakt vid rörbyte"]},
 {"slug": "byggkonsult", "namn": "Byggkonsult", "tagg": "hrs-konsult", "tagg2": "hrs-folk", "typ": "Konsult inom bygg",
  "titel": "Byggkonsult för små och stora projekt | HRS AB",
  "beskr": "Konsulter inom byggbranschen för små och stora företag. Rådgivning och planering kring bygg, rivning och renovering – kostnadsfri första konsultation.",
  "h1": "Konsult inom byggbranschen", "ingress": "Vi kan byggbranschen ut och innantill. Ta hjälp av våra konsulter i små projekt såväl som stora.",
  "text": ["Vi jobbar som konsulter inom byggbranschen och erbjuder tjänster till både små och stora företag. Du är alltid välkommen att ta hjälp av en av våra konsulter med frågor kring bygg och renovering.",
           "I stället för att försöka ge dig på allt själv kan du ta hjälp av ett kunnigt team. Du kan anlita en konsult för ett litet projekt såväl som ett stort.",
           "Hör av dig om du vill veta hur våra konsulttjänster fungerar. Du kan alltid kontakta oss utan att förbinda dig till något."],
  "ingar": ["Rådgivning", "Planering", "Små och stora projekt"]},
 {"slug": "bemanning", "namn": "Bemanning", "tagg": "hrs-bemanning", "tagg2": "hrs-lift", "typ": "Bemanning av byggpersonal",
  "titel": "Bemanning av byggpersonal | Haninge Riv & Sanering",
  "beskr": "Erfaren byggpersonal till rivning, renovering och annan typ av bygg – för korta och långa uppdrag. Hör av dig i god tid så hittar vi rätt personal.",
  "h1": "Bemanning av byggpersonal", "ingress": "Erfaren byggpersonal till rivning, renovering och annan typ av bygg – för korta och långa uppdrag.",
  "text": ["Behöver ditt företag erfaren personal till ett byggprojekt? Vi förser dig med professionella byggarbetare, både till korttidsprojekt och långtidsprojekt.",
           "I vissa fall kan vi hjälpa dig med bemanning med kort varsel. Många arbeten kräver dock planering långt i förväg, så det bästa är att kontakta oss i god tid inför ditt projekt."],
  "ingar": ["Korttidsuppdrag", "Långtidsuppdrag", "Rivningspersonal", "Personal till renovering"]},
]
OMR_TILL_TJANST = {0: "rivning", 1: "sanering", 2: "betonghaltagning", 3: "byggkonsult"}

# ---------- titlar och beskrivningar för de övriga sidorna ----------
SIDOR = {
 "index.html": ("Rivning, sanering & håltagning i Haninge | HRS AB",
                "Rivningsfirma i Österhaninge: rivning, stambytesrivning, asbest- och mögelsanering, betonghåltagning och kärnborrning. Svar inom 24 timmar."),
 "verksamhet.html": ("Tjänster: rivning, sanering och håltagning | HRS AB",
                     "Rivning, sanering, betonghåltagning, friläggning av rör vid fuktskador, byggkonsult och bemanning av byggpersonal – från Österhaninge."),
 "bolag.html": ("Våra bolag: HRS och Haninge Byggteam",
                "Haninge Riv & Sanering och Haninge Byggteam arbetar sida vid sida i Österhaninge: rivning och sanering i det ena bolaget, bygg och renovering i det andra."),
 "projekt.html": ("Projekt: rivning, sanering och håltagning | HRS AB",
                  "Bilder från våra arbetsplatser: stambytesrivning, sanering i inplastade zoner, kärnborrning och friläggning av rör i lokaler, lägenheter och hallar."),
 "hallbarhet.html": ("Hållbarhet: miljövänlig rivning och sanering | HRS",
                     "Provtagning före start, sorterat avfall till återvinning och säker hantering av farliga material. Så arbetar HRS med miljö och säkerhet."),
 "faq.html": ("Vanliga frågor om rivning och sanering | HRS AB",
              "Svar på vanliga frågor om rivning, sanering, provtagning, akuta ärenden, bemanning och offert. Vi svarar inom 24 timmar, även på helger."),
 "karriar.html": ("Jobba hos oss – rivning och sanering | HRS AB",
                  "Vill du arbeta med rivning, sanering och håltagning i ett lag som alltid får jobbet gjort? Skicka en intresseanmälan till Haninge Riv & Sanering."),
 "om-oss.html": ("Om oss och kontakt | Haninge Riv & Sanering AB",
                 "Haninge Riv & Sanering är ett framåtsträvande rivnings- och saneringsbolag i Österhaninge. Kontakt, öppettider och offertförfrågan."),
 "404.html": ("Sidan hittades inte | Haninge Riv & Sanering AB",
              "Sidan du letade efter finns inte längre. Gå till startsidan eller våra tjänster: rivning, sanering och betonghåltagning i Haninge."),
}
for t in TJANSTER:
    SIDOR[t["slug"] + ".html"] = (t["titel"], t["beskr"])
for fil, (ti, be) in SIDOR.items():  # Elevate Studios djupanalys: titel 25–60 tecken, beskrivning 70–160
    assert 25 <= len(ti) <= 60, (fil, len(ti), ti)
    assert 70 <= len(be) <= 160, (fil, len(be), be)

# Gamla WordPress-adresser (haningeriv.se) och förra förslagets adresser -> nya sidor, med 301 på servern
REDIRECTS_301 = {"/tjanster/": "/verksamhet.html", "/tjanster": "/verksamhet.html", "/om-oss/": "/om-oss.html", "/kontakt/": "/om-oss.html#kontakt",
                 "/kontakt": "/om-oss.html#kontakt", "/offertforfragan/": "/om-oss.html#boka", "/offertforfragan": "/om-oss.html#boka",
                 "/tjanster.html": "/verksamhet.html", "/kontakt.html": "/om-oss.html#kontakt", "/offert.html": "/om-oss.html#boka",
                 "/integritetspolicy.html": "/om-oss.html#kontakt", "/integritetspolicy/": "/om-oss.html#kontakt"}


def tjanstesidor(s):
    """Bygger tjänstesidorna med generatorns sidhuvud, sidfot och delar (anropas efter Sajt.bygg())."""
    from generera import PIL
    for t in TJANSTER:
        b1 = s.bilder.ta(t["tagg"])
        b2 = s.bilder.ta(t["tagg2"])
        stycken = "".join(f"<p>{E(x)}</p>" for x in t["text"])
        ingar = "".join(f"<li>{E(x)}</li>" for x in t["ingar"])
        andra = "".join(f'<li><a href="{x["slug"]}.html">{E(x["namn"])}{PIL}</a></li>' for x in TJANSTER if x is not t)
        innehall = f'''<section class="sek ts" aria-labelledby="ts-h"><div class="wrap ts-grid">
  <div class="ts-text"><span class="etikett">Tjänst</span><h2 id="ts-h">{E(t["namn"])} med Haninge Riv &amp; Sanering</h2>{stycken}
    <div class="knappar">{s.knapp("Begär offert", "#boka")}<a class="textlank" href="tel:{TEL_E164}"><span>Ring {TEL}</span>{PIL}</a></div></div>
  <div class="ts-sida"><div class="ts-bild">{s.bilder.img(b2, "(min-width:1000px) 40vw, 100vw")}</div>
    <div class="ts-ingar"><h3>Det här ingår</h3><ul>{ingar}</ul></div></div>
</div></section>
{s.s_process()}
<section class="sek ts-andra" aria-labelledby="ta-h"><div class="wrap"><div class="ts-huvud"><span class="etikett">Fler tjänster</span><h2 id="ta-h">Det här gör vi också</h2></div><ul class="ts-lista">{andra}</ul></div></section>
{s.s_boka()}'''
        s.undersida(t["slug"], t["namn"], t["h1"], t["ingress"], t["tagg"], innehall, t["beskr"])
        # rätt sida markerad i menyn: Tjänster
        f = s.ut / f'{t["slug"]}.html'
        f.write_text(f.read_text(encoding="utf-8").replace('<a href="verksamhet.html">', '<a href="verksamhet.html" aria-current=page>', 1), encoding="utf-8")


def sida_404(s):
    from generera import PIL
    rutor = "".join(f'<li><a href="{t["slug"]}.html">{E(t["namn"])}{PIL}</a></li>' for t in TJANSTER)
    innehall = f'''<section class="sek ts-andra" aria-labelledby="ta-h"><div class="wrap"><div class="ts-huvud"><span class="etikett">Hitta rätt</span><h2 id="ta-h">Våra tjänster</h2>
  <p class="ingress">Adressen kan ha ändrats när sajten byggdes om. Välj en tjänst nedan, gå till <a href="index.html">startsidan</a> eller ring oss på <a href="tel:{TEL_E164}">{TEL}</a>.</p></div><ul class="ts-lista">{rutor}</ul></div></section>'''
    s.undersida("404", "Sidan hittades inte", "Sidan hittades inte", "Sidan du letade efter finns inte, eller har flyttat.", "hrs-hall2", innehall, SIDOR["404.html"][1])


TS_CSS = """
/* Tjänstesidor */
.ts-grid { display: grid; gap: clamp(32px, 5vw, 72px); }
@media (min-width: 1000px) { .ts-grid { grid-template-columns: 1.25fr 1fr; align-items: start; } }
.ts-text h2 { margin: 10px 0 22px; }
.ts-text p { font-size: clamp(17px, 1.25vw, 19px); line-height: 1.7; margin: 0 0 18px; max-width: 40em; }
.ts-text .knappar { margin-top: 28px; }
.ts-bild { border-radius: var(--r-card); overflow: hidden; aspect-ratio: 4 / 3; }
.ts-bild img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ts-ingar { margin-top: 16px; padding: clamp(22px, 2.4vw, 32px); background: var(--c-yta); border-radius: var(--r-card); }
.ts-ingar h3 { font-size: 19px; margin: 0 0 14px; }
.ts-ingar ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 10px; }
.ts-ingar li { position: relative; padding-left: 30px; font-weight: 500; }
.ts-ingar li::before { content: ""; position: absolute; left: 0; top: .2em; width: 18px; height: 18px; border-radius: 50%; background: var(--c-a) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%230e1218' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12l5 5L20 7'/%3E%3C/svg%3E") center / 12px no-repeat; }
.ts-huvud { margin-bottom: 24px; }
.ts-huvud h2 { margin: 10px 0 0; }
.ts-huvud .ingress { margin-top: 14px; max-width: 40em; }
.ts-lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); }
.ts-lista a { display: flex; align-items: center; justify-content: space-between; gap: 12px; min-height: 72px; padding: 18px 22px; background: var(--c-yta); border-radius: var(--r-card); color: inherit; font-weight: 600; text-decoration: none; transition: background .2s, color .2s; }
.ts-lista a svg { width: 18px; height: 18px; flex: none; transition: transform .2s; }
.ts-lista a:hover { background: var(--c-p); color: #fff; }
.ts-lista a:hover svg { color: var(--c-a); transform: translateX(4px); }
/* Rubriker i menyn och sidfoten (inte rubriknivåer) */
.meny .meny-rub { font: 600 12.5px/1.3 var(--font-t); letter-spacing: .14em; text-transform: uppercase; opacity: .65; margin: 0 0 12px; }
.fot .fot-rub { font: 700 13px/1.3 var(--font-t); letter-spacing: .12em; text-transform: uppercase; margin: 0 0 14px; }
"""


# ---------- per sida: titel, beskrivning, canonical, Open Graph, strukturerad data ----------
def _abs(path):
    return SAJT if path in ("", "index.html") else SAJT + path


FORETAG = {
 "@type": "HomeAndConstructionBusiness", "@id": SAJT + "#foretag", "name": NAMN, "alternateName": "HRS AB", "url": SAJT,
 "logo": SAJT + "assets/logo.png", "image": SAJT + "img/og-hrs.jpg", "telephone": TEL_E164, "email": MAIL,
 "slogan": "Framåtsträvande inom rivning och sanering",
 "description": "Rivning, sanering, betonghåltagning, friläggning av rör vid fuktskador, byggkonsult och bemanning av byggpersonal.",
 "address": {"@type": "PostalAddress", "streetAddress": "Albybergsringen, lokal 35", "addressLocality": "Österhaninge", "addressRegion": "Stockholms län", "addressCountry": "SE"},
 "areaServed": [{"@type": "AdministrativeArea", "name": "Haninge kommun"}, {"@type": "AdministrativeArea", "name": "Stockholms län"}],
 "contactPoint": {"@type": "ContactPoint", "telephone": TEL_E164, "email": MAIL, "contactType": "customer service", "availableLanguage": "sv",
                  "hoursAvailable": [{"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "07:00", "closes": "16:00"},
                                     {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "10:00", "closes": "13:00"}]},
 "knowsAbout": ["Rivning", "Stambytesrivning", "Asbestsanering", "Mögelsanering", "Betonghåltagning", "Kärnborrning", "Friläggning av rör"],
 "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Tjänster", "itemListElement": [
     {"@type": "Offer", "itemOffered": {"@type": "Service", "name": t["namn"], "url": _abs(t["slug"] + ".html")}} for t in TJANSTER]},
 "parentOrganization": None,
}
FORETAG.pop("parentOrganization")
SYSTER = {"@type": "Organization", "name": "Haninge Byggteam AB", "url": "https://www.haningebyggteam.se/"}


def _ld(fil, h1, faq):
    graf = [dict(FORETAG, sameAs=[], subjectOf=None)]
    graf[0].pop("subjectOf"); graf[0].pop("sameAs")
    graf.append({"@type": "WebSite", "@id": SAJT + "#webbplats", "url": SAJT, "name": NAMN, "inLanguage": "sv-SE", "publisher": {"@id": SAJT + "#foretag"}})
    if fil != "index.html":
        graf.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Start", "item": SAJT},
            {"@type": "ListItem", "position": 2, "name": h1, "item": _abs(fil)}]})
    t = next((x for x in TJANSTER if x["slug"] + ".html" == fil), None)
    if t:
        graf.append({"@type": "Service", "name": t["h1"], "serviceType": t["typ"], "description": t["beskr"], "url": _abs(fil),
                     "provider": {"@id": SAJT + "#foretag"}, "areaServed": FORETAG["areaServed"]})
    if fil == "bolag.html":
        graf.append(SYSTER)
    if faq:
        graf.append({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graf}, ensure_ascii=False, separators=(",", ":")) + "</script>"


def sida(doc, fil, faq):
    ti, be = SIDOR.get(fil, (None, None))
    if ti is None:
        return doc
    doc = re.sub(r"<title>.*?</title>", f"<title>{E(ti)}</title>", doc, count=1, flags=re.S)
    doc = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{E(be)}">', doc, count=1)
    doc = re.sub(r'<meta property="og:[^>]*>', "", doc)
    h1 = re.sub(r"<[^>]+>", "", (re.search(r"<h1[^>]*>(.*?)</h1>", doc, re.S) or [None, ti])[1]).strip()
    url = _abs(fil)
    head = (f'<link rel="canonical" href="{url}">'
            f'<meta property="og:type" content="website"><meta property="og:locale" content="sv_SE"><meta property="og:site_name" content="{E(NAMN)}">'
            f'<meta property="og:title" content="{E(ti)}"><meta property="og:description" content="{E(be)}"><meta property="og:url" content="{url}">'
            f'<meta property="og:image" content="{SAJT}img/og-hrs.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:card" content="summary_large_image">'
            + (_ld(fil, html.unescape(h1), faq if fil == "faq.html" else None) if fil != "404.html" else ""))
    if fil == "404.html":
        head = head.replace(f'<link rel="canonical" href="{url}">', "") + '<meta name="robots" content="noindex">'
    doc = doc.replace("</head>", head + "\n</head>", 1)
    return doc


def lankar(doc):
    """Tjänsterna länkar till sina egna sidor; menyns och sidfotens rubriker blir rätt nivå."""
    for i, slug in OMR_TILL_TJANST.items():
        doc = doc.replace(f'href="verksamhet.html#omr-{i}"', f'href="{slug}.html"')
        doc = re.sub(r'(<section class="sek-tat" id="omr-%d">.*?)<a class="textlank" href="projekt.html"><span>[^<]*</span>' % i,
                     lambda m: m.group(1) + f'<a class="textlank" href="{slug}.html"><span>Mer om {next(t["namn"].lower() for t in TJANSTER if t["slug"] == slug)}</span>',
                     doc, count=1, flags=re.S)
    return doc


def rubriker(doc):
    # Menyns rubriker (före <main>) är etiketter, inte rubriker; sidfotens h4 blir h3 (efter sidfotens h2)
    i = doc.find("<main")
    if i > 0:
        doc = re.sub(r"<h4>(.*?)</h4>", r'<p class="meny-rub">\1</p>', doc[:i]) + doc[i:]
    j = doc.find("<footer")
    if j > 0:
        doc = doc[:j] + re.sub(r"<h4>(.*?)</h4>", r'<h3 class="fot-rub">\1</h3>', doc[j:])
    return doc


def bildmatt(out):
    """width och height på alla bilder (från filerna), så att sidan inte hoppar när de laddas."""
    cache = {}

    def matt(src, fil):
        p = (fil.parent / src.split("?")[0]).resolve()
        if p not in cache:
            try:
                with Image.open(p) as im:
                    cache[p] = im.size
            except Exception:
                cache[p] = None
        return cache[p]

    for fil in out.rglob("*.html"):
        doc = fil.read_text(encoding="utf-8")

        def fixa(m):
            tag = m.group(0)
            if re.search(r"\bwidth=", tag) and re.search(r"\bheight=", tag):
                return tag
            src = (re.search(r'data-src="([^"]+)"', tag) or re.search(r'\ssrc="([^"]+)"', tag))
            if not src or src.group(1).startswith("data:"):
                return tag
            wh = matt(src.group(1), fil)
            return tag.replace("<img ", f'<img width="{wh[0]}" height="{wh[1]}" ', 1) if wh else tag
        doc = re.sub(r"<img\b[^>]*>", fixa, doc)
        fil.write_text(doc, encoding="utf-8")


def og_bild(out, kalla):
    im = Image.open(kalla).convert("RGB")
    w, h = im.size
    mal = 1200 / 630
    if w / h > mal:
        nw = int(h * mal); im = im.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    else:
        nh = int(w / mal); im = im.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
    im.resize((1200, 630), Image.LANCZOS).save(out / "img" / "og-hrs.jpg", quality=82, optimize=True, progressive=True)


def filer(out, sidor):
    """Sajtkarta, robots.txt, omdirigeringar (301) och serverrubriker för Cloudflare Pages / Netlify."""
    if PRODUKTION:
        urls = "".join(f"<url><loc>{_abs(p)}</loc></url>" for p in sidor)
        (out / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
        (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SAJT}sitemap.xml\n", encoding="utf-8")
    else:
        (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "_redirects").write_text("".join(f"{a} {b} 301\n" for a, b in REDIRECTS_301.items()), encoding="utf-8")
    csp = ("default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; "
           "connect-src 'self' https://formsubmit.co; form-action 'self' https://formsubmit.co; frame-ancestors 'none'; base-uri 'self'; object-src 'none'; upgrade-insecure-requests")
    (out / "_headers").write_text(f"""/*
  Content-Security-Policy: {csp}
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: camera=(), microphone=(), geolocation=()
/assets/*
  Cache-Control: public, max-age=31536000, immutable
/img/*
  Cache-Control: public, max-age=31536000, immutable
/*.html
  Cache-Control: public, max-age=0, must-revalidate
""", encoding="utf-8")
    return csp


def typsnitt(out, fontsource):
    """Poppins från egen server i stället för Google Fonts: ingen extra anslutning och ingen blockerande stilfil."""
    mal = out / "assets" / "fonts"
    mal.mkdir(parents=True, exist_ok=True)
    css = ""
    for v in (400, 500, 600, 700):
        f = f"poppins-latin-{v}-normal.woff2"
        (mal / f).write_bytes((fontsource / "files" / f).read_bytes())
        css += f'@font-face{{font-family:"Poppins";font-style:normal;font-weight:{v};font-display:swap;src:url(fonts/{f}) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}}\n'
    bas = out / "assets" / "bas.css"
    bas.write_text(css + bas.read_text(encoding="utf-8"), encoding="utf-8")
    pre = "".join(f'<link rel="preload" href="assets/fonts/poppins-latin-{v}-normal.woff2" as="font" type="font/woff2" crossorigin>' for v in (700, 400, 600, 500))
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        doc = re.sub(r'<link rel="preconnect" href="https://fonts\.(googleapis|gstatic)\.com"[^>]*>', "", doc)
        doc = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', pre, doc)
        fil.write_text(doc, encoding="utf-8")


def inline_skript(out):
    """Inline-skript flyttas till egna filer (så att säkerhetspolicyn kan förbjuda inline-skript)."""
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        m = re.search(r"<script>\s*/\* Bildspelets bild 2 och 3.*?</script>", doc, re.S)
        if m:
            kod = re.sub(r"^<script>|</script>$", "", m.group(0).strip())
            (out / "assets" / "bildspel.js").write_text(kod.strip() + "\n", encoding="utf-8")
            doc = doc.replace(m.group(0), '<script src="assets/bildspel.js" defer></script>')
        fil.write_text(doc, encoding="utf-8")


def versionera(out):
    """?v=<innehållets hash> på filer i assets/ och img/, så att de kan cachas i ett år och ändå uppdateras direkt."""
    import hashlib
    cache = {}

    def v(rel):
        p = out / rel
        if rel not in cache:
            cache[rel] = hashlib.md5(p.read_bytes()).hexdigest()[:8] if p.is_file() else None
        return cache[rel]

    def fixa(m):
        rel = m.group(1)
        h = v(rel)
        return f"{rel}?v={h}" if h else rel
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        doc = re.sub(r"(?<![\w/?=])((?:assets|img)/[\w./-]+\.(?:js|css|png|svg|webp|jpg|woff2))(?![\w?])", fixa, doc)
        fil.write_text(doc, encoding="utf-8")


def responsiva(out):
    """Rätt bildstorlek för varje skärm: 480/800/1200 px-versioner i srcset med verkliga bredder, och src = 800-versionen."""
    cache = {}

    def varianter(rel):
        if rel in cache:
            return cache[rel]
        p = out / rel
        if not p.is_file():
            cache[rel] = None
            return None
        with Image.open(p) as im:
            im = im.convert("RGB")
            w, h = im.size
            lista = []
            for bredd in (480, 680, 760, 1100):  # 680/760 = kort och helbredd på mobil (412 px × 1,75)
                if bredd < w * 0.9:
                    n = p.with_name(f"{p.stem}-{bredd}.webp")
                    if not n.exists():
                        im.resize((bredd, round(h * bredd / w)), Image.LANCZOS).save(n, quality=64, method=6)
                    lista.append((str(n.relative_to(out)), bredd))
            if p.stat().st_size > 250 * 1024:  # för tung originalfil: komprimera hårdare
                im.save(p, quality=68, method=6)
            lista.append((rel, w))
        cache[rel] = lista
        return lista

    def fixa(m):
        tag = m.group(0)
        for attr in ("srcset", "data-srcset"):
            ss = re.search(r'\s' + attr + r'="([^"]+)"', tag)
            if not ss:
                continue
            filer_ = [x.strip().split(" ")[0] for x in ss.group(1).split(",")]
            stor = max(filer_, key=len) if not any(not f.endswith("-s.webp") for f in filer_) else next(f for f in filer_ if not f.endswith("-s.webp"))
            v = varianter(stor.split("?")[0])
            if not v:
                continue
            tag = tag.replace(ss.group(0), f' {attr}="' + ", ".join(f"{f} {b}w" for f, b in v) + '"')
            mitt = next((f for f, b in v if b == 760), v[-1][0])
            src_attr = "data-src" if attr == "data-srcset" else "src"
            tag = re.sub(r'(\s' + src_attr + r'=")[^"]+(")', lambda mm: mm.group(1) + mitt + mm.group(2), tag, count=1)
        # galleriets miniatyrer
        g = re.search(r'\ssrc="(img/g/[\w-]+-s\.webp)"', tag)
        if g and "srcset" not in tag:
            p = out / g.group(1)
            n = p.with_name(p.stem.replace("-s", "-400") + ".webp")
            with Image.open(p) as im:
                w, h = im.size
                if not n.exists():
                    im.convert("RGB").resize((400, round(h * 400 / w)), Image.LANCZOS).save(n, quality=64, method=6)
            rel = str(n.relative_to(out))
            tag = tag.replace(g.group(0), f' src="{rel}" srcset="{rel} 400w, {g.group(1)} {w}w" sizes="(min-width:1200px) 25vw, (min-width:900px) 33vw, 50vw"')
        return tag
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        doc = re.sub(r"<img\b[^>]*>", fixa, doc)
        # hjältebilden täcker hela skärmen: på stående skärm behövs bilden bredare än skärmen
        m = re.search(r'<div class="bildspel" data-bildspel>.*?</section>', doc, re.S)
        if m:
            doc = doc.replace(m.group(0), m.group(0).replace('sizes="100vw"', 'sizes="(orientation: portrait) 140vh, 100vw"'))
        fil.write_text(doc, encoding="utf-8")


def sidhjalte(out):
    """Undersidornas stora bild är sidans största innehåll: hämtas först (preload + fetchpriority), aldrig lat."""
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        m = re.search(r'<section class="sidhero"[^>]*>\s*<div class="bild-fyll">\s*(<img\b[^>]*>)', doc)
        if not m:
            m2 = re.search(r'<div class="bildspel" data-bildspel>.*?(<img\b[^>]*>)', doc, re.S)
            if m2 and 'rel="preload" as="image"' in doc:  # startsidan: uppdatera preload till de nya storlekarna
                tag = m2.group(1)
                ss, sz = re.search(r'srcset="([^"]+)"', tag), re.search(r'sizes="([^"]+)"', tag)
                if ss and sz:
                    doc = re.sub(r'<link rel="preload" as="image"[^>]*>', f'<link rel="preload" as="image" imagesrcset="{ss.group(1)}" imagesizes="{sz.group(1)}" fetchpriority="high">', doc, count=1)
            fil.write_text(doc, encoding="utf-8")
            continue
        tag = m.group(1)
        ny = re.sub(r'\sloading="lazy"', "", tag)
        if "fetchpriority" not in ny:
            ny = ny.replace("<img ", '<img fetchpriority="high" ', 1)
        doc = doc.replace(tag, ny, 1)
        ss, sz = re.search(r'srcset="([^"]+)"', ny), re.search(r'sizes="([^"]+)"', ny)
        if ss:
            doc = doc.replace("</title>", f'</title>\n<link rel="preload" as="image" imagesrcset="{ss.group(1)}" imagesizes="{sz.group(1) if sz else "100vw"}" fetchpriority="high">', 1)
        fil.write_text(doc, encoding="utf-8")


def loggor(out):
    """Loggan som WebP i de storlekar den visas i (srcset); den dolda varianten laddas inte i onödan."""
    a = out / "assets"
    for kalla, namn, bredder in (("logo.png", "logo", (180, 240)), ("logo-vit.png", "logo-vit", (180, 240, 300, 340))):
        with Image.open(a / kalla) as im:
            w, h = im.size
            for b in bredder:
                im.resize((b, round(h * b / w)), Image.LANCZOS).save(a / f"{namn}-{b}.webp", quality=72, method=6)
    huvud = 'srcset="assets/{n}-180.webp 180w, assets/{n}-240.webp 240w" sizes="(max-width:720px) 90px, 119px"'
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        har_hero = 'class="har-hero"' in doc
        doc = doc.replace('src="assets/logo.png" alt="" width="105" height="58">',
                          'src="assets/logo-180.webp" ' + huvud.format(n="logo") + ' alt="" width="105" height="58"' + (' loading="lazy">' if har_hero else ">"))
        if har_hero:
            doc = doc.replace('src="assets/logo-vit.png" alt="" width="105" height="58">', 'src="assets/logo-vit-180.webp" ' + huvud.format(n="logo-vit") + ' alt="" width="105" height="58">')
        else:  # undersidorna har vitt sidhuvud från start: den vita loggan visas aldrig
            doc = re.sub(r'<img class="logga-bild logga-vit" src="assets/logo-vit\.png"[^>]*>', "", doc)
        doc = doc.replace('src="assets/logo-vit.png" alt="Haninge Riv &amp; Sanering AB" width="170" height="94"',
                          'src="assets/logo-vit-300.webp" srcset="assets/logo-vit-300.webp 300w, assets/logo-vit-340.webp 340w" sizes="170px" alt="Haninge Riv &amp; Sanering AB" width="170" height="94" loading="lazy"')
        fil.write_text(doc, encoding="utf-8")


def inline_css(out, node_bin=None):
    """Stilarna direkt i sidan, rensade per sida: inga blockerande stilfiler och ingen oanvänd CSS."""
    import subprocess, tempfile
    a = out / "assets"
    css = (a / "tokens.css").read_text(encoding="utf-8") + "\n" + (a / "bas.css").read_text(encoding="utf-8")
    css = css.replace("url(fonts/", "url(assets/fonts/")
    full = Path(tempfile.mkdtemp()) / "alla.css"
    full.write_text(css, encoding="utf-8")
    for fil in out.glob("*.html"):
        doc = fil.read_text(encoding="utf-8")
        sid = css
        if node_bin and (node_bin / "purgecss").exists():
            ut = full.parent / (fil.stem + "-css")
            ut.mkdir(exist_ok=True)
            r = subprocess.run([str(node_bin / "purgecss"), "--css", str(full), "--content", str(fil), str(a / "*.js"),
                                "--safelist", "syns", "aktiv", "fast", "bak", "oppen", "menu-open", "visas", "--output", str(ut)], capture_output=True)
            if r.returncode == 0 and (ut / "alla.css").exists():
                m = subprocess.run([str(node_bin / "lightningcss"), "--minify", str(ut / "alla.css")], capture_output=True, text=True)
                sid = m.stdout if m.returncode == 0 and m.stdout.strip() else (ut / "alla.css").read_text(encoding="utf-8")
        doc = re.sub(r'<link rel="stylesheet" href="assets/tokens\.css[^"]*">\s*', "", doc)
        doc = re.sub(r'<link rel="stylesheet" href="assets/bas\.css[^"]*">', lambda m: "<style>" + sid + "</style>", doc)
        fil.write_text(doc, encoding="utf-8")


def hjalte_mobil(out, kalla):
    """Startsidans hjältebild: på stående skärm (mobil) en egen beskärning kring medarbetaren, mindre fil och bättre bild."""
    im = Image.open(kalla).convert("RGB")
    w, h = im.size
    bw = round(h * 0.6)
    x0 = max(0, min(w - bw, round(w * 0.30) - bw // 2))
    crop = im.crop((x0, 0, x0 + bw, h))
    filer_ = []
    for b in (600, 900):
        n = out / "img" / f"hrs-hero-staende-{b}.webp"
        crop.resize((b, round(crop.height * b / crop.width)), Image.LANCZOS).save(n, quality=56, method=6)
        filer_.append((f"img/hrs-hero-staende-{b}.webp", b))
    ss = ", ".join(f"{f} {b}w" for f, b in filer_)
    fil = out / "index.html"
    doc = fil.read_text(encoding="utf-8")
    m = re.search(r'<div class="bildspel" data-bildspel>.*?(<img\b[^>]*>)', doc, re.S)
    if m:
        tag = m.group(1)
        land = re.sub(r'sizes="[^"]*"', 'sizes="100vw"', tag)
        doc = doc.replace(tag, f'<picture><source media="(orientation: portrait)" srcset="{ss}" sizes="100vw">{land}</picture>', 1)
        lss = re.search(r'srcset="([^"]+)"', land).group(1)
        doc = re.sub(r'<link rel="preload" as="image"[^>]*>',
                     f'<link rel="preload" as="image" media="(orientation: portrait)" imagesrcset="{ss}" imagesizes="100vw" fetchpriority="high">'
                     f'<link rel="preload" as="image" media="(orientation: landscape)" imagesrcset="{lss}" imagesizes="100vw" fetchpriority="high">', doc, count=1)
    fil.write_text(doc, encoding="utf-8")


def stada(out):
    """Tar bort bildfiler som ingen sida använder (generatorns original-jpg, ersatta storlekar)."""
    text = "".join(f.read_text(encoding="utf-8", errors="ignore") for f in out.rglob("*") if f.suffix in (".html", ".css", ".js", ".xml"))
    borta = 0
    for f in list((out / "img").rglob("*")) + list((out / "assets").glob("*.png")):
        if f.is_file() and f.name != "og-hrs.jpg" and f.name not in text:
            f.unlink(); borta += 1
    return borta
