"""Bygger undersökningen som PDF: research/rapport/Koncernkansla-undersokning.pdf

Kör:  python3 research/rapport.py

Läser data/sammanstallning.json, skärmdumparna i data/shots och skärmdumpar av de 10 exempelsajterna
(research/rapport/exempel/*.jpg, skapas av koncern/skarmdump.py). Skriver rapport.html och gör PDF med Chromium.
"""
import html
import json
import pathlib
from collections import Counter, defaultdict

from PIL import Image
from playwright.sync_api import sync_playwright

ROT = pathlib.Path(__file__).resolve().parent
DATA = ROT / "data"
UT = ROT / "rapport"
BILD = UT / "bilder"
BILD.mkdir(parents=True, exist_ok=True)
E = html.escape
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

S = json.loads((DATA / "sammanstallning.json").read_text(encoding="utf-8"))
SAJ, TOT = S["sajter"], S["totalt"]
N = len(SAJ)
EX = json.loads((ROT.parent / "site/exempel/exempel.json").read_text(encoding="utf-8"))

ARK_NAMN = {
    "monument": "Monument", "ramad": "Ramad", "statement": "Statement", "finans": "Finans", "centrerad": "Centrerad",
    "split": "Split", "sökdriven": "Sökdriven", "industriell": "Industriell", "portal": "Portal",
}
ARK_BESKR = {
    "monument": "Helskärmsfilm eller -bild, stor rubrik nere till vänster, transparent header som blir vit när man scrollar. Kantiga bilder, pillerknappar. Skanska är skolexemplet.",
    "statement": "Rubriken är heron. Jättestor typografi på en lugn yta, bilden kommer under. Ofta serif eller ett udda typsnitt (Vasakronan, Alecta, Atrium Ljungberg).",
    "ramad": "Bilden ligger i en ram inne i sidan och ett vitt textkort överlappar den. Lugnt, ordnat, mycket luft (NCC, Tyréns, Skandia Fastigheter).",
    "finans": "Investeraren först: topprad med IR-länkar och aktiekurs, ibland nyckeltal direkt i heron (Sagax, Alm Equity, Logistea).",
    "centrerad": "Helskärmsbild eller film med centrerad rubrik. Elegant när typsnittet bär (Hufvudstaden, Corem, Humlegården).",
    "split": "Ett färgfält och en bild sida vid sida. Varmt och konsumentnära – vanligt hos bostadsutvecklare (Bonava, Veidekke).",
    "sökdriven": "Sökrutan för bostad eller lokal är huvudsaken i heron. Funktionellt men ger mer marknadsplats än koncern.",
    "industriell": "Smala versaler, mörka ytor, gul/orange signal. Råstyrka för infrastruktur och anläggning (Infranord, JSB, Svevia).",
    "portal": "Kundtjänstportal med ikoner och genvägar (allmännyttan). Fungerar för hyresgäster men ger ingen koncernkänsla.",
}

# --- Bilder ---------------------------------------------------------------------------------------------------------
def tumme(slug, typ="desk", w=640, crop=None):
    src = DATA / "shots" / f"{slug}-{typ}.jpg"
    dst = BILD / f"{slug}-{typ}-{w}.jpg"
    if not dst.exists() and src.exists():
        im = Image.open(src).convert("RGB")
        if crop:
            im = im.crop((0, 0, im.width, min(im.height, crop)))
        im.thumbnail((w, 10000))
        im.save(dst, quality=72, optimize=True)
    return f"bilder/{dst.name}"


def exbild(namn, w=900, crop=None):
    src = UT / "exempel" / namn
    dst = BILD / f"ex-{w}-{namn}"
    if not dst.exists() and src.exists():
        im = Image.open(src).convert("RGB")
        if crop:
            im = im.crop((0, 0, im.width, min(im.height, crop)))
        im.thumbnail((w, 20000))
        im.save(dst, quality=74, optimize=True)
    return f"bilder/{dst.name}"


# --- Diagram (enkel serie: horisontella staplar, en färg, värdet direkt vid stapeln) ---------------------------------
BLA, ORANGE = "#2a78d6", "#eb6834"


def staplar(rader, enhet="", maxv=None, bredd=520, etikett_b=190):
    maxv = maxv or max(v for _, v in rader) or 1
    h_rad, tj = 30, 18
    plot = bredd - etikett_b - 56
    svg = [f'<svg class="diagram" viewBox="0 0 {bredd} {len(rader) * h_rad + 6}" role="img">']
    for i, (namn, v) in enumerate(rader):
        y = i * h_rad + 6
        w = max(2, plot * v / maxv)
        r = min(4, w / 2)
        # Rundat bara i stapelns ände, rakt mot baslinjen
        svg.append(f'<text x="{etikett_b - 10}" y="{y + tj - 4}" text-anchor="end" class="d-et">{E(str(namn))}</text>')
        svg.append(f'<path d="M{etikett_b} {y} h{w - r} a{r} {r} 0 0 1 {r} {r} v{tj - 2 * r} a{r} {r} 0 0 1 -{r} {r} h-{w - r} z" fill="{BLA}"><title>{E(str(namn))}: {v}{enhet}</title></path>')
        svg.append(f'<text x="{etikett_b + w + 8}" y="{y + tj - 4}" class="d-v">{v}{enhet}</text>')
    svg.append(f'<line x1="{etikett_b}" y1="2" x2="{etikett_b}" y2="{len(rader) * h_rad + 4}" class="d-bas"/></svg>')
    return "".join(svg)


def jamfor(rader, bredd=900, etikett_b=270):
    """Två serier per rad: topp (betyg 4–5) och svaga (betyg 1–2), med förklaring ovanför."""
    h_rad, tj, gap = 44, 14, 2
    plot = bredd - etikett_b - 60
    svg = [f'<svg class="diagram" viewBox="0 0 {bredd} {len(rader) * h_rad + 8}" role="img">']
    for i, (namn, (a, b)) in enumerate(rader):
        y = i * h_rad + 6
        svg.append(f'<text x="{etikett_b - 12}" y="{y + tj + 6}" text-anchor="end" class="d-et">{E(namn)}</text>')
        for j, (v, f) in enumerate(((a, BLA), (b, ORANGE))):
            yy = y + j * (tj + gap)
            w = max(2, plot * v / 100)
            r = min(4, w / 2)
            svg.append(f'<path d="M{etikett_b} {yy} h{w - r} a{r} {r} 0 0 1 {r} {r} v{tj - 2 * r} a{r} {r} 0 0 1 -{r} {r} h-{w - r} z" fill="{f}"/>')
            svg.append(f'<text x="{etikett_b + w + 6}" y="{yy + tj - 3}" class="d-v small">{v} %</text>')
    svg.append(f'<line x1="{etikett_b}" y1="2" x2="{etikett_b}" y2="{len(rader) * h_rad + 4}" class="d-bas"/></svg>')
    return "".join(svg)


def pct(pred, mangd=None):
    m = mangd if mangd is not None else SAJ
    return round(100 * sum(1 for s in m if pred(s)) / len(m))


def antal(key):
    return [(k, v) for k, v in Counter(s[key] for s in SAJ).most_common()]


# --- Sidor ----------------------------------------------------------------------------------------------------------
sidor = []


def sida(innehall, cls=""):
    sidor.append(f'<section class="sida {cls}">{innehall}<footer class="sidfot"><span>Koncernkänsla – undersökning av 100 svenska bygg- och fastighetskoncerners hemsidor</span><span class="nr"></span></footer></section>')


topp = [s for s in SAJ if s["betyg"] >= 4]
svag = [s for s in SAJ if s["betyg"] <= 2]
jfr = TOT["jamforelse"]["rader"]

# 1. Försättsblad
sk = next(s for s in SAJ if s["slug"] == "skanska")
sida(f'''<div class="omslag">
  <div class="omslag-text"><p class="kicker">Elevate Studio · November 2026</p>
  <h1>Koncernkänsla</h1><p class="omslag-under">En undersökning av hemsidorna hos 100 svenska bygg- och fastighetskoncerner – typografi, färg, form, layout och innehåll – och vad som skiljer de bästa från resten.</p>
  <ul class="omslag-fakta"><li><b>100</b> koncerner</li><li><b>112</b> sajter analyserade</li><li><b>2 400+</b> uppmätta värden</li><li><b>9</b> stilarketyper</li></ul></div>
  <div class="omslag-bild"><img src="{tumme("skanska", "desk", 1200)}" alt=""><span>Riktmärket: skanska.se</span></div></div>''', "forsta")

# 2. Sammanfattning
sida(f'''<h2>Sammanfattning</h2>
<div class="tva"><div>
<p class="ingress">"Koncernkänsla" går att mäta. De sajter vi bedömde som bäst (betyg 4–5, {len(topp)} st) delar ett litet antal grepp som de svaga ({len(svag)} st) saknar.</p>
<ol class="fynd">
<li><b>Storleken avgör.</b> Rubrikerna är stora: median {int(TOT["h1_topp_median"])} px hos de bästa mot {int(TOT["h1_svag_median"])} px hos de svaga. {jfr["Rubrik ≥ 56 px"][0]} % av de bästa har rubriker på minst 56 px, mot {jfr["Rubrik ≥ 56 px"][1]} %.</li>
<li><b>Bilden tar hela skärmen.</b> {jfr["Helskärms- eller stor bildhero"][0]} % av de bästa har helskärmsbild eller film i heron (svaga: {jfr["Helskärms- eller stor bildhero"][1]} %). {pct(lambda s: s["hero_type"] == "video")} % av alla använder film.</li>
<li><b>Headern försvinner.</b> {jfr["Transparent header över hero"][0]} % av de bästa låter headern ligga transparent över bilden (svaga: {jfr["Transparent header över hero"][1]} %).</li>
<li><b>Runda knappar, raka bilder.</b> Kombinationen pillerknapp + kantig bild är signaturen för svensk koncerndesign: {pct(lambda s: s["btn_shape"] == "piller")} % har pillerknappar och {pct(lambda s: s["img_shape"] == "kantig (0 px)")} % helt kantiga bilder.</li>
<li><b>Eget typsnitt är toppens kännetecken.</b> {pct(lambda s: s["font_own"])} % har ett eget varumärkestypsnitt (Skanska, JM, Bonava, Vasakronan, Sweco …) – bland de bästa {jfr["Eget varumärkestypsnitt"][0]} %. {pct(lambda s: s["font_source"] != "Google Fonts" and s["font_source"] != "systemtypsnitt")} % använder licensierade typsnitt, bara {pct(lambda s: s["font_source"] == "Google Fonts")} % Google Fonts.</li>
<li><b>Blått dominerar – men inte i toppen.</b> {pct(lambda s: s["brand_family"] == "blå")} % har blått som varumärkesfärg. Bland de mest minnesvärda finns svart/orange (Infranord), neongult (JSB) och monokromt (Atrium Ljungberg).</li>
<li><b>Koncernens fyra dörrar.</b> Menyerna har nästan alltid Hållbarhet ({TOT["pct"]["hallbarhet"]} %), Karriär ({TOT["pct"]["karriar"]} %), Press ({TOT["pct"]["press"]} %) och Investerare ({TOT["pct"]["investor"]} %). Det är innehållet – inte bara formen – som säger "koncern".</li>
<li><b>Portalen dödar känslan.</b> Sajter som börjar med ikoner, sökrutor och kundtjänst (allmännyttan) hamnar i botten oavsett hur välgjorda de är.</li>
</ol></div>
<div class="recept"><h3>Receptet</h3>
<p>En koncernsajt i toppklass har nästan alltid:</p>
<ul><li>Helskärmsbild/film med <b>en enda stor rubrik</b> (60–100 px)</li><li>Transparent header som blir solid vid scroll</li><li>Ett distinkt typsnitt – eget eller ovanligt</li><li>En stark färg, sparsamt använd mot mycket vitt</li><li>Pillerknappar men kantiga bilder</li><li>Nyckeltal i stor siffra tidigt på sidan</li><li>Affärsområden, projekt, hållbarhet, investerare, karriär</li><li>Mörk eller färgad sidfot med tydlig struktur</li></ul>
<p class="liten">Men: alla som följer receptet blir lika varandra. Därför bygger våra 10 sajter på <b>olika arketyper</b> (sid. 13–14) och agenten mäter avståndet till alla tidigare paket.</p></div></div>''')

# 3. Metod
uteslutna = ", ".join(f'{u["namn"]} ({u["skal"].lower()})' for u in S["uteslutna"])
misslyckade = ", ".join(u["namn"] for u in S["misslyckade"])
sida(f'''<h2>Metod</h2>
<div class="tre">
<div><h3>Urval</h3><p>116 svenska koncerner inom bygg, bostadsutveckling, kommersiella fastigheter, samhälls- och bostadsfastigheter, infrastruktur, installation och teknikkonsult – de största efter omsättning och fastighetsvärde, plus allmännyttans största bolag.</p>
<p>112 sajter gick att ladda ({misslyckade} gick inte). Efter manuell granskning togs 12 bort: {E(uteslutna)}. Kvar: <b>exakt 100</b>.</p>
<h3>Fördelning</h3>{staplar([(k, v) for k, v in TOT["kategorier"][:10]], bredd=360, etikett_b=190)}</div>
<div><h3>Automatisk mätning</h3><p>Varje sajt öppnades i Chromium (1440×900 och 390×844), cookie-rutan klickades bort och ett skript mätte i den färdiga sidan:</p>
<ul class="lista"><li>typsnitt, storlek, vikt och versaler för rubriker och brödtext</li><li>rundning, färg och stil på knappar, bilder och kort</li><li>headerns läge (transparent/solid, sticky), höjd och menyord</li><li>heron: höjd, film, bild, text ovanpå bild</li><li>färger viktade efter yta, länk- och knappfärger</li><li>koncernsignaler: investerare, hållbarhet, karriär, press, engelska</li></ul>
<p>Totalt drygt 2 400 värden. Skärmdumpar sparades av varje sajt.</p></div>
<div><h3>Manuell bedömning</h3><p>Alla 100 skärmdumpar granskades för hand. Varje sajt fick en <b>arketyp</b> (vilken stil den representerar), ett <b>betyg 1–5</b> för koncernkänsla – hur stor, självsäker och genomarbetad den känns – och en kommentar. Rubriktypsnittet klassades för hand (geometrisk, grotesk, humanistisk, serif, smal, mono) och om det är bolagets eget.</p>
<h3>Begränsningar</h3><p class="liten">Ögonblicksbild från november 2026. Några filmer laddade inte i den automatiska webbläsaren (grå hero på t.ex. NREP, Fortinova, Genova) och några cookie-rutor gick inte att stänga. Varumärkesfärgen räknades ut från knappar, länkar och ytor och kan i enstaka fall träffa en sekundärfärg. Betygen är en designbedömning, inte en mätning.</p></div></div>''')

# 4. Skanska
sida(f'''<h2>Riktmärket: Skanska</h2>
<div class="sk"><div class="sk-bild"><img src="{tumme("skanska", "long", 900)}" alt="skanska.se"></div>
<div><p class="ingress">Skanska gör få saker – men gör dem stort.</p>
<ul class="anteckningar">
<li><b>Film i helskärm</b> som första intryck, med rubriken "Vi skapar platserna som formar samhället" nere till vänster och en kort ingress till höger.</li>
<li><b>Eget typsnitt</b> (Shape Sans Display) i {sk["h1_size"]} px och lätt vikt. Storleken, inte tjockleken, ger auktoriteten.</li>
<li><b>Transparent header</b> med marinblå logga, sju menyord, sök och språk – och en liten pillerformad Kontakt-knapp som enda knapp.</li>
<li><b>Två färger:</b> marinblått ({sk["brand"] or "#143275"}) och grönt som accent – resten är vitt.</li>
<li><b>Kantiga bilder</b> rakt igenom; inga skuggor, inga ramar.</li>
<li><b>Genvägar som bildkort:</b> "Vad kan vi hjälpa till med?" följs av fyra bilder med gröna pilknappar – kundens vanligaste ärenden direkt efter heron.</li>
<li><b>Stora marinblå rubriker</b> även längre ned och en bred bildsektion för studentprogrammet – samma skala hela vägen.</li>
<li><b>Innehållet säger koncern:</b> Bygg & infrastruktur, Produkter & tjänster, Fastigheter, Köpa bostad, Jobba hos oss, Om oss.</li>
</ul>
<p class="liten">Samma grepp går igen hos Ramboll, Norconsult, Hemsö, Pandox, Instalco och Ikano Bostad – de vanligaste toppbetygen finns i arketypen <b>Monument</b>.</p></div></div>''')

# 5. Typografi
kinds = [(k, v) for k, v in TOT["font_kind"]]
egna = [s for s in SAJ if s["font_own"]]
h1_buckets = Counter()
for s in SAJ:
    h = s["h1_size"] or 0
    b = "< 40 px" if h < 40 else "40–55 px" if h < 56 else "56–71 px" if h < 72 else "72–95 px" if h < 96 else "≥ 96 px"
    h1_buckets[b] += 1
ordning = ["< 40 px", "40–55 px", "56–71 px", "72–95 px", "≥ 96 px"]
sida(f'''<h2>Typografi</h2>
<div class="tre">
<div><h3>Rubriktypsnittets karaktär</h3>{staplar(kinds, bredd=360, etikett_b=120)}
<p class="liten">Geometriska (Avenir, Futura, Circular, Brown) och groteska (Graphik, Suisse, Neue Montreal) dominerar. Serif ({pct(lambda s: s["font_kind"] == "serif")} %) används oftare i fastighet än i bygg – för att signalera kvalitet och långsiktighet.</p></div>
<div><h3>Rubrikstorlek på startsidan</h3>{staplar([(b, h1_buckets[b]) for b in ordning], bredd=360, etikett_b=120)}
<p class="liten">Median {int(TOT["h1_median"])} px. De bästa: {int(TOT["h1_topp_median"])} px, de svaga: {int(TOT["h1_svag_median"])} px. Versala rubriker är sällsynta ({TOT["pct"]["h1_upper"]} %) och används nästan bara av infrastruktur.</p></div>
<div><h3>Var typsnitten kommer ifrån</h3>{staplar([(k, v) for k, v in TOT["font_source"]], bredd=360, etikett_b=130)}
<h3 style="margin-top:14px">Egna varumärkestypsnitt ({len(egna)} st)</h3><p class="typlista">{" · ".join(E(s["namn"]) + " <i>" + E(s["font_display"]) + "</i>" for s in egna)}</p></div></div>
<div class="rad-bilder">{"".join(f'<figure><img src="{tumme(s, "desk", 420)}" alt=""><figcaption>{E(n)}</figcaption></figure>' for s, n in [("vasakronan", "Vasakronan: eget serif-typsnitt"), ("atrium-ljungberg", "Atrium Ljungberg: monospace"), ("jsb", "JSB: smala versaler"), ("hufvudstaden", "Hufvudstaden: lätt Garamond")])}</div>''')

# 6. Form
sida(f'''<h2>Form: rundning på knappar och bilder</h2>
<div class="tre">
<div><h3>Knappar</h3>{staplar([(k, v) for k, v in TOT["btn_shape"]], bredd=360, etikett_b=170)}</div>
<div><h3>Bilder</h3>{staplar([(k, v) for k, v in TOT["img_shape"]], bredd=360, etikett_b=170)}</div>
<div><h3>Det typiska svenska greppet</h3><p class="ingress" style="font-size:15px">Runda knappar – raka bilder.</p>
<p>{pct(lambda s: s["btn_shape"] == "piller" and s["img_shape"] == "kantig (0 px)")} av 100 kombinerar pillerknappar med helt kantiga bilder. Det ger ett vänligt gränssnitt utan att arkitekturen i bilderna mjukas upp.</p>
<p>Rundade bilder och kort (8 px och mer) hittar vi framför allt hos bostadsbolag och konsumentnära sajter – de ger värme men mindre auktoritet.</p>
<p>Skuggor på kort är nästan borta ({TOT["pct"]["card_shadow"]} %). Konturknappar används av {TOT["pct"]["btn_outline"]} %.</p></div></div>
<div class="rad-bilder">{"".join(f'<figure><img src="{tumme(s, "desk", 420)}" alt=""><figcaption>{E(n)}</figcaption></figure>' for s, n in [("skanska", "Skanska: piller + kantigt"), ("tyrens", "Tyréns: svarta piller"), ("bonava", "Bonava: mjukt"), ("infranord", "Infranord: helt kantigt")])}</div>''')

# 7. Färg
fam_ordning = ["blå", "turkos/petrol", "grön", "gul/guld", "orange/terrakotta", "röd", "rosa/vinröd", "lila", "monokrom"]
per_fam = defaultdict(list)
for s in SAJ:
    per_fam[s["brand_family"]].append(s)
rutor = ""
for fam in fam_ordning:
    for s in per_fam.get(fam, []):
        c = s["brand"] or "#111111"
        rutor += f'<div class="ruta"><span style="background:{c}"></span><small>{E(s["namn"])}</small></div>'
sida(f'''<h2>Färg</h2>
<div class="tva-ett"><div><h3>Varumärkesfärg per sajt, sorterad efter färgfamilj</h3><div class="rutor">{rutor}</div></div>
<div><h3>Färgfamiljer</h3>{staplar([(k, v) for k, v in TOT["brand_family"]], bredd=330, etikett_b=130)}
<p class="liten">Blått är tryggt men gör att sajterna smälter ihop. Petrol och grönt kopplas till hållbarhet. Monokromt (svart/vitt) används av de mest designdrivna (Atrium Ljungberg, Klövern, White).</p>
<p class="liten">{TOT["pct"]["footer_dark"]} % har mörk sidfot. {TOT["pct"]["pure_black"]} % använder helt svart text – resten en mjukare mörkgrå eller mörkblå.</p></div></div>''')

# 8. Header, hero, navigation
sig = [("Karriär/jobb", TOT["pct"]["karriar"]), ("Hållbarhet", TOT["pct"]["hallbarhet"]), ("Press/nyheter", TOT["pct"]["press"]),
       ("Investerare", TOT["pct"]["investor"]), ("Sök", TOT["pct"]["search"]), ("Engelsk version", TOT["pct"]["english"])]
ord_ = [(k.capitalize(), v) for k, v in TOT["nav_words"][:12]]
sida(f'''<h2>Header, hero och navigation</h2>
<div class="tre">
<div><h3>Header</h3>{staplar([(k, v) for k, v in TOT["header_type"]], bredd=360, etikett_b=170)}
<p class="liten">{TOT["pct"]["sticky"]} % har en header som följer med vid scroll. {TOT["pct"]["burger"]} % visar hamburgermeny även på dator – oftast tillsammans med några synliga länkar.</p>
<h3>Hero</h3>{staplar([(k, v) for k, v in TOT["hero_type"]], bredd=360, etikett_b=170)}</div>
<div><h3>Koncernsignaler i menyn (andel sajter, %)</h3>{staplar(sig, "%", 100, bredd=360, etikett_b=130)}
<p class="liten">Investerare, hållbarhet, karriär och press är koncernens "fyra dörrar". De finns på nästan alla stora sajter, ofta i en egen topprad.</p></div>
<div><h3>Vanligaste menyorden</h3>{staplar(ord_, bredd=360, etikett_b=130)}</div></div>''')

# 9. Topp mot botten
rader = [(k, (v[0], v[1])) for k, v in jfr.items()]
sida(f'''<h2>Vad skiljer de bästa från de svaga?</h2>
<p class="legend"><span><i style="background:{BLA}"></i>Betyg 4–5 ({len(topp)} sajter)</span><span><i style="background:{ORANGE}"></i>Betyg 1–2 ({len(svag)} sajter)</span></p>
<div class="tva-ett"><div>{jamfor(rader)}</div>
<div><h3>Tolkning</h3><p>De största skillnaderna gäller <b>skala och självförtroende</b>: stor rubrik, stor bild, transparent header. Detaljer som mörk sidfot eller hamburgermeny skiljer inte alls.</p>
<p>Eget typsnitt och serif-rubriker är dubbelt så vanligt i toppen – ett distinkt typsnitt är det snabbaste sättet att inte se ut som alla andra.</p>
<p>Hållbarhet och investerare är vanligare hos de bästa: innehållet i menyn bidrar lika mycket som formen.</p></div></div>''')

# 10–11. Arketyper
ark = defaultdict(list)
for s in SAJ:
    ark[s["arketyp"]].append(s)
ark_ordning = sorted(ark, key=lambda a: -sum(x["betyg"] for x in ark[a]) / len(ark[a]))
def ark_block(a):
    xs = sorted(ark[a], key=lambda s: -s["betyg"])
    snitt = sum(x["betyg"] for x in xs) / len(xs)
    bilder = "".join(f'<figure><img src="{tumme(x["slug"], "desk", 420)}" alt=""><figcaption>{E(x["namn"])} · {x["betyg"]}/5</figcaption></figure>' for x in xs[:3])
    return f'''<div class="ark"><div class="ark-head"><h3>{ARK_NAMN[a]}</h3><span>{len(xs)} sajter · snittbetyg {snitt:.1f}</span></div><p>{E(ARK_BESKR[a])}</p><div class="ark-bilder">{bilder}</div></div>'''
sida(f'<h2>Nio arketyper</h2><div class="ark-grid">{"".join(ark_block(a) for a in ark_ordning[:5])}</div>', "tat")
sida(f'<h2>Nio arketyper (forts.)</h2><div class="ark-grid">{"".join(ark_block(a) for a in ark_ordning[5:])}</div>', "tat")

# 12. Från undersökning till 10 sajter
TYP_KAT = {"geometrisk": "geometrisk", "grotesk": "grotesk", "humanistisk": "humanistisk", "serif": "serif", "smal": "smal", "mono": "mono"}
rad_ex = ""
for e in EX:
    p = e["paket"]
    f = p["farger"]
    rad_ex += (f'<tr><td><b>{E(e["kortnamn"])}</b><br><small>{E(e["typ"])}</small></td><td>{E(p["arketyp"].capitalize())}</td><td>{E(p["hero"])}</td>'
               f'<td>{E(p["typsnitt"]["rubrik"])}<br><small>{E(p["typsnitt"]["kategori"])}</small></td>'
               f'<td><span class="sw" style="background:{f["primar"]}"></span><span class="sw" style="background:{f["accent"]}"></span><span class="sw" style="background:{f["mork"]}"></span><span class="sw" style="background:{f["yta"]}"></span></td>'
               f'<td>{E(p["form"]["namn"])}<br><small>knapp {p["form"]["knapp"] if p["form"]["knapp"] < 999 else "piller"} · bild {p["form"]["bild"]} px</small></td><td>{E(p["header"])}</td><td>{E(p["kort"])}</td><td>{E(p["rytm"])}</td></tr>')
sida(f'''<h2>Från undersökning till 10 olika koncernsajter</h2>
<p class="ingress" style="font-size:14px;max-width:none">Varje sajt bygger på en arketyp från undersökningen men kombinerar typsnitt, färg, form och layout på sitt eget sätt. Paketmotorn mäter hur olika paketen är (0 = identiska); det minsta avståndet mellan två av de tio är {min(e["paket"]["min_avstand"] for e in EX)}.</p>
<table class="tabell"><thead><tr><th>Koncern (fiktiv)</th><th>Arketyp</th><th>Hero</th><th>Rubriktypsnitt</th><th>Färger</th><th>Form</th><th>Header</th><th>Kort</th><th>Rytm</th></tr></thead><tbody>{rad_ex}</tbody></table>
<p class="liten">Alla tio är fiktiva koncerner. Sajterna har sidorna Start, Verksamhet, Projekt, Hållbarhet, Investerare, Karriär och Om oss, och bilderna är stockfoton från Pexels.</p>''')

# 13–14. De tio sajterna
def ex_kort(e):
    return f'<figure class="ex"><div class="ex-ram"><img src="{exbild("exempel-" + e["slug"] + "-index-dator.jpg", 560, 2900)}" alt=""></div><figcaption><b>{E(e["kortnamn"])}</b> · {E(e["paket"]["arketyp"])}</figcaption></figure>'
sida(f'<h2>De tio sajterna</h2><div class="ex-grid">{"".join(ex_kort(e) for e in EX[:5])}</div>', "tat")
sida(f'<h2>De tio sajterna (forts.)</h2><div class="ex-grid">{"".join(ex_kort(e) for e in EX[5:])}</div>', "tat")

# 15–19. Galleri
gal = sorted(SAJ, key=lambda s: (-s["betyg"], s["namn"]))
for i in range(0, N, 20):
    g = gal[i:i + 20]
    kort = "".join(f'''<figure class="g"><img src="{tumme(s["slug"], "desk", 420)}" alt=""><figcaption><b>{E(s["namn"])}</b> <span class="betyg">{s["betyg"]}/5</span><br>
      <span class="sw" style="background:{s["brand"] or "#111"}"></span>{E(ARK_NAMN[s["arketyp"]])} · {E(s["font_display"])}</figcaption></figure>''' for s in g)
    sida(f'<h2>Galleri {i // 20 + 1}/5 <small>sorterat efter betyg</small></h2><div class="galleri">{kort}</div>', "tat")

# 20–22. Tabell
rader_t = sorted(SAJ, key=lambda s: s["namn"].lower())
for i in range(0, N, 34):
    tr = "".join(f'''<tr><td><b>{E(s["namn"])}</b></td><td>{E(s["kategori"])}</td><td>{E(s["font_display"])}{" *" if s["font_own"] else ""}</td><td>{E(s["font_kind"])}</td><td>{s["h1_size"] or "–"}</td>
      <td>{E(s["btn_shape"])}</td><td>{E(s["img_shape"])}</td><td>{E(s["header_type"])}</td><td>{E(s["hero_type"])}</td><td><span class="sw" style="background:{s["brand"] or "#111"}"></span>{E(s["brand_family"])}</td><td>{E(ARK_NAMN[s["arketyp"]])}</td><td>{s["betyg"]}</td></tr>''' for s in rader_t[i:i + 34])
    sida(f'''<h2>Bilaga: alla 100 {i // 34 + 1}/3</h2><table class="tabell mini"><thead><tr><th>Koncern</th><th>Kategori</th><th>Rubriktypsnitt</th><th>Typ</th><th>H1 px</th><th>Knappar</th><th>Bilder</th><th>Header</th><th>Hero</th><th>Färg</th><th>Arketyp</th><th>Betyg</th></tr></thead><tbody>{tr}</tbody></table>
    <p class="liten">* eget varumärkestypsnitt</p>''', "tat")

CSS = f'''
@page {{ size: A4 landscape; margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font: 11px/1.5 "Inter", system-ui, sans-serif; color: #17191c; counter-reset: sida; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
.sida {{ position: relative; width: 297mm; height: 210mm; padding: 14mm 16mm 16mm; page-break-after: always; overflow: hidden; counter-increment: sida; background: #fff; }}
.sidfot {{ position: absolute; left: 16mm; right: 16mm; bottom: 8mm; display: flex; justify-content: space-between; font-size: 8.5px; color: #8a8f96; border-top: 1px solid #e3e5e8; padding-top: 4px; }}
.sidfot .nr::after {{ content: counter(sida); }}
h1 {{ font: 700 84px/0.95 "Inter Tight", "Inter", sans-serif; letter-spacing: -0.045em; margin: 0; }}
h2 {{ font: 650 26px/1.1 "Inter Tight", "Inter", sans-serif; letter-spacing: -0.025em; margin: 0 0 14px; }}
h2 small {{ font-size: 13px; font-weight: 500; color: #8a8f96; letter-spacing: 0; margin-left: 8px; }}
h3 {{ font: 650 13px/1.3 "Inter", sans-serif; margin: 0 0 8px; }}
p {{ margin: 0 0 8px; }}
.ingress {{ font-size: 16px; line-height: 1.45; font-weight: 500; max-width: 40em; }}
.liten {{ font-size: 9.5px; color: #5d636b; }}
.kicker {{ font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: #5d636b; font-weight: 600; margin-bottom: 18px; }}
.tva {{ display: grid; grid-template-columns: 1.6fr 1fr; gap: 28px; }}
.tre {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 26px; }}
.tva-ett {{ display: grid; grid-template-columns: 2fr 1fr; gap: 28px; }}
.forsta {{ padding: 0; }}
.omslag {{ display: grid; grid-template-columns: 1fr 1.25fr; height: 100%; }}
.omslag-text {{ padding: 22mm 14mm 20mm 18mm; display: flex; flex-direction: column; justify-content: center; }}
.omslag-under {{ font-size: 16px; line-height: 1.45; margin-top: 18px; color: #3a3f45; max-width: 26em; }}
.omslag-fakta {{ list-style: none; padding: 0; margin: 28px 0 0; display: grid; grid-template-columns: repeat(2, auto); gap: 10px 26px; font-size: 12px; color: #5d636b; }}
.omslag-fakta b {{ display: block; font: 700 30px/1 "Inter Tight", sans-serif; color: #17191c; letter-spacing: -0.03em; }}
.omslag-bild {{ position: relative; background: #0b1a3d; overflow: hidden; }}
.omslag-bild img {{ width: 100%; height: 100%; object-fit: cover; object-position: left top; }}
.omslag-bild span {{ position: absolute; left: 14px; bottom: 12px; color: #fff; font-size: 10px; background: rgba(0,0,0,.45); padding: 3px 8px; border-radius: 99px; }}
.forsta .sidfot {{ display: none; }}
.fynd {{ padding-left: 18px; margin: 10px 0 0; }}
.fynd li {{ margin-bottom: 9px; font-size: 12.4px; line-height: 1.5; }}
.recept {{ background: #f3f4f6; border-radius: 6px; padding: 16px 18px; }}
.recept ul {{ padding-left: 16px; margin: 0 0 10px; }}
.recept li {{ margin-bottom: 6px; font-size: 12px; }}
.lista {{ padding-left: 16px; margin: 0 0 8px; }}
.diagram {{ width: 100%; height: auto; display: block; margin: 4px 0 10px; }}
.d-et {{ font-size: 10.5px; fill: #3a3f45; }}
.d-v {{ font-size: 10.5px; fill: #17191c; font-weight: 600; }}
.d-v.small {{ font-size: 9.5px; }}
.d-bas {{ stroke: #c9ccd1; stroke-width: 1; }}
.legend {{ display: flex; gap: 22px; font-size: 11px; margin: -4px 0 8px; }}
.legend i {{ display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin-right: 6px; vertical-align: -2px; }}
.typlista {{ font-size: 10px; line-height: 1.7; }}
.typlista i {{ color: #5d636b; }}
.sk {{ display: grid; grid-template-columns: 1.15fr 1fr; gap: 26px; height: 150mm; }}
.sk-bild {{ overflow: hidden; border: 1px solid #e3e5e8; }}
.sk-bild img {{ width: 100%; display: block; }}
.anteckningar {{ padding-left: 16px; }}
.anteckningar li {{ margin-bottom: 8px; font-size: 11.5px; }}
.rad-bilder {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 8px; }}
figure {{ margin: 0; }}
.rad-bilder img, .ark-bilder img, .galleri img {{ width: 100%; aspect-ratio: 16 / 10; object-fit: cover; object-position: top; display: block; border: 1px solid #e3e5e8; }}
figcaption {{ font-size: 9px; color: #3a3f45; margin-top: 3px; }}
.rutor {{ display: grid; grid-template-columns: repeat(10, 1fr); gap: 6px 6px; }}
.ruta span {{ display: block; height: 24px; border-radius: 3px; border: 1px solid rgba(0,0,0,.08); }}
.ruta small {{ display: block; font-size: 6.6px; line-height: 1.15; margin-top: 2px; color: #3a3f45; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }}
.ark-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px 24px; }}
.ark {{ border-top: 2px solid #17191c; padding-top: 6px; }}
.ark-head {{ display: flex; justify-content: space-between; align-items: baseline; }}
.ark-head span {{ font-size: 9.5px; color: #5d636b; }}
.ark p {{ font-size: 10px; margin-bottom: 6px; }}
.ark-bilder {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }}
.tat h2 {{ margin-bottom: 10px; }}
.galleri {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 9px 10px; }}
.galleri figcaption {{ font-size: 8.4px; line-height: 1.35; }}
.betyg {{ float: right; font-weight: 700; }}
.sw {{ display: inline-block; width: 9px; height: 9px; border-radius: 2px; margin-right: 4px; vertical-align: -1px; border: 1px solid rgba(0,0,0,.1); }}
td .sw {{ width: 14px; height: 14px; margin-right: 3px; vertical-align: -3px; }}
.tabell {{ width: 100%; border-collapse: collapse; font-size: 10px; margin-top: 8px; }}
.tabell th {{ text-align: left; font-weight: 650; border-bottom: 1.5px solid #17191c; padding: 5px 6px; }}
.tabell td {{ border-bottom: 1px solid #e3e5e8; padding: 5px 6px; vertical-align: top; }}
.tabell small {{ color: #5d636b; }}
.tabell.mini {{ font-size: 7.6px; }}
.tabell.mini td, .tabell.mini th {{ padding: 2.4px 4px; }}
.tabell.mini td .sw {{ width: 9px; height: 9px; }}
.ex-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
.ex-ram {{ height: 150mm; overflow: hidden; border: 1px solid #e3e5e8; }}
.ex-ram img {{ width: 100%; height: auto; display: block; }}
'''

doc = f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><title>Koncernkänsla – undersökning</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;650;700&family=Inter+Tight:wght@600;650;700&display=swap">
<style>{CSS}</style></head><body>{"".join(sidor)}</body></html>'''
(UT / "rapport.html").write_text(doc, encoding="utf-8")

with sync_playwright() as p:
    kw = {"executable_path": CHROME} if pathlib.Path(CHROME).exists() else {}
    b = p.chromium.launch(**kw)
    pg = b.new_page()
    pg.goto((UT / "rapport.html").as_uri(), wait_until="networkidle")
    pg.wait_for_timeout(800)
    pg.pdf(path=str(UT / "Koncernkansla-undersokning.pdf"), format="A4", landscape=True, print_background=True,
           margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    b.close()
print("Skrev", UT / "Koncernkansla-undersokning.pdf", len(sidor), "sidor")
