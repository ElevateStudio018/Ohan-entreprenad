"""Builds docs/*.html for Ohan Entreprenad AB.

Run:  python3 scripts/build.py docs

All text, services and contact details live in this file. The service texts are based on ohanentreprenad.se;
the lists "Det kan ingå", the work process and the FAQ answers are suggestions that Ohan should confirm or edit.
"""
import hashlib
import html
import json
import pathlib
import sys
from urllib.parse import quote_plus

# Elevate Studio's credit under every footer: the mark and the name, the whole of it one link to elevatestudio.nu.
ELEVATE_CREDIT = '''<!-- elevate-credit -->
<style>.elevate-credit{max-width:1240px;margin:24px auto 0;padding:20px 16px 0;border-top:1px solid rgba(128,128,128,.25);display:flex;justify-content:center;box-sizing:border-box}.elevate-credit a{display:inline-flex;align-items:center;gap:10px;padding:8px 0;font:inherit;font-size:15px;line-height:1;color:inherit;opacity:.55;text-decoration:none;transition:opacity .2s}.elevate-credit a:hover,.elevate-credit a:focus-visible{opacity:1}.elevate-credit svg{width:20px;height:20px;flex:none;display:block}@media(min-width:1024px){.elevate-credit a{font-size:16px}}</style>
<div class="elevate-credit"><a href="https://elevatestudio.nu" target="_blank" rel="noopener"><svg viewBox="0 0 1884.3 1353.9" aria-hidden="true"><path d="M0.0 1353.9 L1218.7 0.0 L1218.7 329.1 L479.7 1136.4 L786.7 1132.4 L1215.5 687.4 L1884.3 1349.9 L1590.1 1349.9 L1218.6 994.7 L865.4 1349.9Z" fill="currentColor"/></svg>Byggd av Elevate Studio</a></div>
'''


OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "docs")


def ver(path):
    """A short hash of an asset, added as ?v= so browsers fetch the new file after every change."""
    return hashlib.md5((OUT / path).read_bytes()).hexdigest()[:8]

# --- Company details (ohanentreprenad.se) ---------------------------------------------------------------------------
NAME = "Ohan Entreprenad AB"
SHORT = "Ohan Entreprenad"
PHONE, TEL = "0720-49 82 90", "+46720498290"
EMAIL = "info@ohanentreprenad.se"
STREET, POSTAL, CITY = "Kungälvsvägen 66", "442 39", "Kungälv"
ADDR = f"{STREET}, {POSTAL} {CITY}"
ORG_NR = "559341-9335"
AREA = "Göteborg med omnejd"
MAPS_LINK = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(f"{NAME}, {ADDR}")
MAP_EMBED = "https://www.google.com/maps?q=" + quote_plus(ADDR) + "&z=13&hl=sv&output=embed"

# The quote form e-mails through FormSubmit. Elevate Studio receives the requests during the preview; at launch this
# becomes Ohan's own address. The first request to a new address only sends an activation e-mail.
FORM_EMAIL = "elevate.studio018@gmail.com"

SITE_URL = "https://elevatestudio018.github.io/Ohan-entreprenad/"

# --- Services (the menu on ohanentreprenad.se) ----------------------------------------------------------------------
SERVICES = [
    dict(
        slug="va-arbeten", title="VA-arbeten", photo="va", pos="50% 50%",
        alt="Grå avloppsrör staplade på en byggarbetsplats",
        short="Nya, renoverade eller utbytta vatten- och avloppsledningar.",
        body=[
            "Vi utför alla typer av VA-arbeten. Det kan vara nyanläggning, renovering eller byte av vatten- och avloppsledningar – för villor, fastigheter och företag.",
            "Vi tar hand om hela kedjan, från schakt till rörläggning och återställning av marken, så att du har en kontakt genom hela jobbet.",
        ],
        items=["Nya vatten- och avloppsledningar", "Byte och renovering av befintliga ledningar", "Anslutning av VA till fastighet",
               "Schakt, rörläggning och återfyllning", "Återställning av mark och ytor"],
    ),
    dict(
        slug="draneringar", title="Dräneringar", photo="dranering", pos="50% 50%",
        alt="Gult rör monteras med hydraulverktyg",
        short="Dränering runt husgrunder, tomter, gårdar och parkeringar.",
        body=[
            "En fungerande dränering leder bort vattnet innan det gör skada. Vi dränerar runt husgrunder, gator, vägar och trädgårdar.",
            "Vi hjälper till med vattenavledning för trädgårdar, gårdar, parkeringsplatser och hela byggnader – och går igenom vad som behövs innan vi börjar gräva.",
        ],
        items=["Dränering runt husgrund", "Dränering av trädgård och tomt", "Gårdar och parkeringsplatser",
               "Dagvatten och avvattning", "Återfyllning och återställning"],
    ),
    dict(
        slug="husgrunder", title="Husgrunder", photo="husgrund", pos="50% 50%",
        alt="Betong gjuts i en grundgrop med armering bredvid",
        short="Platta på mark, källare eller krypgrund – för hus, garage och lokaler.",
        body=[
            "Vi gör grunder för hus, garage, industribyggnader, skolor och kontor, under olika markförhållanden.",
            "Valet mellan platta på mark, källare och krypgrund beror bland annat på vilken byggnad det gäller och hur marken ser ut. Vi hjälper dig att välja rätt lösning.",
        ],
        items=["Platta på mark", "Källargrund", "Krypgrund", "Schakt och markberedning", "Grunder för garage och lokaler"],
    ),
    dict(
        slug="parkeringsytor", title="Parkeringsytor", photo="parkering", pos="50% 55%",
        alt="Arbetare lägger marksten på en ny yta",
        short="Parkeringar och uppfarter med hållbar uppbyggnad.",
        body=[
            "Vi anlägger parkeringsytor och uppfarter för företag, föreningar och privatpersoner.",
            "En yta som håller börjar under ytan: rätt schakt, bärlager och avvattning. Därefter ytskiktet – grus, asfalt eller marksten.",
        ],
        items=["Nya parkeringsytor", "Uppfarter till villor", "Schakt och bärlager", "Avvattning och brunnar", "Grus, asfalt eller marksten"],
    ),
    dict(
        slug="sten-och-murarbeten", title="Sten- och murarbeten", photo="stenmur", pos="50% 50%",
        alt="Natursten staplad i en mur",
        short="Murar, stödmurar, trappor och stensättning.",
        body=[
            "Vi utför sten- och murarbeten för trädgårdar, tomter och fastigheter – både för att det ska fungera och för att det ska se bra ut.",
            "Berätta vad du vill göra, så hjälper vi dig med val av sten och utförande.",
        ],
        items=["Stödmurar", "Murar i natursten", "Trappor i sten", "Kantsten och stensättning", "Plattsättning"],
    ),
    dict(
        slug="schakt-och-transport", title="Schakt och transport", photo="schakt", pos="50% 50%",
        alt="Grävmaskin lastar massor på en dumper",
        short="Schaktning, massor och transporter till och från arbetsplatsen.",
        body=[
            "Vi schaktar för grunder, ledningar och anläggningar och sköter transporterna av massor till och från arbetsplatsen.",
            "Med egna maskiner kan vi planera schakt och transport tillsammans, så att jobbet flyter på.",
        ],
        items=["Schaktning och grävning", "Bortforsling av massor", "Leverans av grus, sand och makadam", "Återfyllning", "Markplanering"],
    ),
    dict(
        slug="infrastruktur", title="Infrastruktur och vägar", photo="infrastruktur", pos="50% 60%",
        alt="Väg under byggnation med nytt asfaltslager",
        short="Byggande och reparation av vägar – från uppfarter till större projekt.",
        body=[
            "Vi är experter inom mark och anläggning, och våra tjänster täcker hela infrastrukturområdet. Allt från mindre uppdrag som trädgårdsanläggning, konstruktioner och uppfarter till större projekt med ombyggnad och reparation av vägar, broar och tunnlar.",
            "Vi planerar varje projekt noggrant för att möta högt ställda krav och följer upp arbetet under hela byggtiden.",
        ],
        items=["Byggande av vägar", "Reparation och ombyggnad av vägar", "Uppfarter och tillfartsvägar", "Markarbeten för anläggningar",
               "Uppföljning under byggtiden"],
    ),
    dict(
        slug="uthyrning", title="Maskinuthyrning", photo="uthyrning", pos="50% 55%",
        alt="Gul grävmaskin på en grushög i skogen",
        short="Grävmaskiner, hjullastare och mer – med eller utan förare.",
        body=[
            "Vi hyr ut de flesta vanliga typer av entreprenadmaskiner, med eller utan förare.",
            "I maskinparken finns grävmaskiner, hjullastare, kompaktlastare, dumprar, lyftkranar med mera. Hyr på kort eller lång tid – hör av dig så berättar vi vad som är ledigt.",
        ],
        items=["Grävmaskiner", "Hjullastare", "Kompaktlastare", "Dumprar", "Lyftkranar", "Med eller utan förare"],
    ),
]
# The six ground works are shown as cards; the rest as buttons under "Vi utför också" (rental also has its own section).
CARD_SLUGS = ["va-arbeten", "draneringar", "husgrunder", "parkeringsytor", "schakt-och-transport", "infrastruktur"]
CARDS = [s for s in SERVICES if s["slug"] in CARD_SLUGS]
ALSO = [s for s in SERVICES if s["slug"] not in CARD_SLUGS]
WORK_TYPES = [s["title"] for s in SERVICES] + ["Annat"]
MACHINES = ["Grävmaskiner", "Hjullastare", "Kompaktlastare", "Dumprar", "Lyftkranar"]

FAQ = [
    ("Vilka jobb tar ni?",
     "Mark- och anläggningsarbeten: VA, dräneringar, husgrunder, parkeringsytor, sten- och murarbeten, schakt och transport samt vägar. Vi hyr också ut maskiner."),
    ("Kan jag få en offert?",
     f"Ja. Fyll i <a href=\"#offert\">formuläret</a>, ring <a href=\"tel:{TEL}\">{PHONE}</a> eller mejla <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Oftast tittar vi på platsen innan vi ger ett pris."),
    ("Var jobbar ni?",
     f"Vi utgår från {CITY} och jobbar i Göteborg med omnejd. Ligger jobbet längre bort, säg var, så svarar vi om vi kan ta det."),
    ("Kan jag hyra en maskin utan förare?",
     "Ja, vi hyr ut maskiner både med och utan förare, på kort eller lång tid."),
    ("Gäller ROT-avdrag?",
     "ROT-avdraget kan gälla arbetskostnaden för till exempel dränering och VA vid ditt hus. Vi går igenom vad som gäller för ditt jobb i offerten."),
]

STEPS = [
    ("Du hör av dig", "Berätta kort vad som ska göras och var."),
    ("Vi tittar på platsen", "Så att vi ser marken och förutsättningarna."),
    ("Du får en offert", "Med vad som ingår och vad det kostar."),
    ("Vi utför jobbet", "Med egna maskiner, och följer upp tills det är klart."),
]

# --- Markup helpers -------------------------------------------------------------------------------------------------
E = html.escape
PHONE_ICON = ('<svg class="pi" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
              '<path d="M21 16.5v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 1.1 3.8 2 2 0 0 1 3.1 1.6h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L7.1 9.5a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>'
              '<path d="M15 2.5a6.5 6.5 0 0 1 6.5 6.5M15 6a3 3 0 0 1 3 3"/></svg>')


def img(src, alt="", pos="50% 50%", sizes="100vw", lazy=True):
    return (f'<img src="img/{src}.jpg" srcset="img/{src}-s.jpg 800w, img/{src}.jpg 1800w" sizes="{sizes}" '
            f'alt="{E(alt)}"{" loading=\"lazy\"" if lazy else " fetchpriority=\"high\""} decoding="async" style="object-position:{pos}">')


def photo(src, alt, pos="50% 50%", sizes="(min-width: 960px) 50vw, 100vw"):
    """A rounded photo with the note that it is a stock photo, not from Ohan's own projects."""
    return f'<figure class="ph">{img(src, alt, pos, sizes)}<figcaption>Illustrationsbild</figcaption></figure>'


# Wordmark: a yellow mark and the name in the site font (so it renders the same everywhere without a font in an SVG).
# Replace with Ohan's own logo when there is one.
MARK = ('<svg class="logo-mark" viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="9" fill="#f5b400"/>'
        '<circle cx="20" cy="20" r="10" fill="none" stroke="#1d1d1d" stroke-width="5.5"/>'
        '<path d="M27 27h7v7h-7z" fill="#1d1d1d"/></svg>')


def logo():
    return f'{MARK}<span class="logo-txt"><b>OHAN</b><small>ENTREPRENAD</small></span>'


def call_btn(label=None, cls=""):
    return f'<a class="pill pill-accent {cls}" href="tel:{TEL}">{PHONE_ICON}<span>{label or "Ring " + PHONE}</span></a>'


NAV = [("tjanster", "Tjänster"), ("uthyrning", "Uthyrning"), ("om-oss", "Om oss"), ("fragor", "Frågor"), ("kontakt", "Kontakt")]


def header(home):
    pre = "" if home else "index.html"
    links = "".join(f'<a href="{pre}#{a}">{t}</a>' for a, t in NAV)
    rows = "".join(f'<li><a href="{pre}#{a}">{t}</a></li>' for a, t in NAV)
    svc = "".join(f'<li><a href="tjanst-{s["slug"]}.html">{s["title"]}</a></li>' for s in SERVICES)
    return f'''<a class="skip" href="#main">Hoppa till innehållet</a>
<header class="head">
  <div class="wrap bar">
    <a class="logo" href="{'#top' if home else 'index.html'}" aria-label="{NAME}, till startsidan">{logo()}</a>
    <nav class="nav" aria-label="Huvudmeny">{links}</nav>
    <a class="pill pill-accent head-call" href="tel:{TEL}">{PHONE_ICON}<span>{PHONE}</span></a>
    <a class="round round-accent head-round" href="tel:{TEL}" aria-label="Ring {PHONE}">{PHONE_ICON}</a>
    <button class="burger" id="menuBtn" type="button" aria-expanded="false" aria-controls="menu" aria-label="Meny"><span></span><span></span></button>
  </div>
  <nav class="menu" id="menu" aria-label="Meny" hidden>
    <div class="wrap">
      <ul class="menu-main">{rows}</ul>
      <p class="menu-h">Tjänster</p><ul class="menu-svc">{svc}</ul>
      {call_btn()}
    </div>
  </nav>
</header>'''


def footer(home):
    pre = "" if home else "index.html"
    svc = "".join(f'<li><a href="tjanst-{s["slug"]}.html">{s["title"]}</a></li>' for s in SERVICES)
    return f'''<footer class="foot">
  <div class="wrap">
    <a class="logo" href="{pre or '#top'}" aria-label="{NAME}, till startsidan">{logo()}</a>
    <div class="foot-grid">
      <div>
        <p class="foot-h">{NAME}</p>
        <p><b>{AREA}</b></p>
        <p>c/o {STREET},<br>{POSTAL} {CITY}</p>
        <p><a href="tel:{TEL}">{PHONE}</a></p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
        <p>Org.nr {ORG_NR}</p>
      </div>
      <div><p class="foot-h">Tjänster</p><ul>{svc}</ul></div>
      <div><p class="foot-h">{SHORT}</p><ul>{"".join(f'<li><a href="{pre}#{a}">{t}</a></li>' for a, t in NAV)}<li><a href="{pre}#offert">Begär offert</a></li></ul></div>
    </div>
    <div class="foot-end">
      <span>© <span data-year>2026</span> {NAME} · Bilderna är stockfoton från Pexels</span>
    </div>
  </div>
{ELEVATE_CREDIT}</footer>
<script src="assets/site.js?v={ver("assets/site.js")}" defer></script>
</body>
</html>
'''


def jsonld():
    data = {
        "@context": "https://schema.org", "@type": "GeneralContractor", "name": NAME, "url": SITE_URL,
        "telephone": TEL, "email": EMAIL, "image": SITE_URL + "img/hero-grav.jpg", "taxID": ORG_NR,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "postalCode": POSTAL.replace(" ", ""),
                    "addressLocality": CITY, "addressCountry": "SE"},
        "areaServed": [{"@type": "City", "name": "Göteborg"}, {"@type": "City", "name": "Kungälv"}],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def page(name, title, desc, main, home=False, image="hero-grav"):
    url = SITE_URL + ("" if name == "index.html" else name)
    doc = f'''<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="sv_SE">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:image" content="{SITE_URL}img/{image}.jpg">
<meta name="theme-color" content="#1d1d1d">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/site.css?v={ver("assets/site.css")}">
<link rel="icon" href="img/favicon.svg" type="image/svg+xml">
{jsonld() if home else ''}
</head>
<body>
{header(home)}
<main id="main">
{main}
</main>
{footer(home)}'''
    (OUT / name).write_text(doc, encoding="utf-8")


def card(s):
    return (f'<li class="card"><a href="tjanst-{s["slug"]}.html">{photo(s["photo"], s["alt"], s["pos"], "(min-width: 960px) 33vw, 100vw")}'
            f'<h3>{s["title"]}</h3><p>{s["short"]}</p><span class="more">Läs mer</span></a></li>')


def also_pills(skip=None):
    return "".join(f'<a class="pill pill-dark" href="tjanst-{s["slug"]}.html">{s["title"]}</a>' for s in ALSO if s["slug"] != skip)


def quote_form():
    opts = "".join(f"<option>{E(t)}</option>" for t in WORK_TYPES)
    req = '<span class="req" aria-hidden="true">*</span>'
    return f'''<form class="form" id="qform" novalidate data-endpoint="https://formsubmit.co/ajax/{FORM_EMAIL}">
  <p class="field"><label for="f-typ">Typ av jobb</label><select id="f-typ" name="Typ av jobb"><option value="">– Välj ett alternativ –</option>{opts}</select></p>
  <p class="field"><label for="f-namn">För- och efternamn{req}</label><input id="f-namn" name="Namn" autocomplete="name" required><span class="err" id="e-namn" hidden>Skriv ditt namn.</span></p>
  <p class="field"><label for="f-tel">Telefonnummer{req}</label><input id="f-tel" name="Telefon" type="tel" autocomplete="tel"><span class="err" id="e-tel" hidden>Skriv telefonnummer eller e-post.</span></p>
  <p class="field"><label for="f-epost">E-post</label><input id="f-epost" name="E-post" type="email" autocomplete="email"><span class="err" id="e-epost" hidden>Kontrollera e-postadressen.</span></p>
  <p class="field"><label for="f-besk">Beskriv jobbet</label><textarea id="f-besk" name="Beskrivning" rows="5" placeholder="Vad ska göras, var och när?"></textarea></p>
  <p class="hp" aria-hidden="true"><label for="f-web">Lämna tomt</label><input id="f-web" name="_honey" tabindex="-1" autocomplete="off"></p>
  <p class="small">{req} Telefonnummer eller e-post räcker. Uppgifterna används bara för att svara dig.</p>
  <p><button class="pill pill-dark" type="submit">Skicka förfrågan</button></p>
  <p class="send-err" id="send-err" role="alert" hidden>Det gick inte att skicka just nu. Försök igen, eller ring <a href="tel:{TEL}">{PHONE}</a>.</p>
</form>
<div class="done" id="qdone" tabindex="-1" hidden>
  <p class="done-h">Tack! Vi har fått din förfrågan.</p>
  <p>Vi hör av oss så snart vi kan. Brådskar det, ring <a href="tel:{TEL}">{PHONE}</a>.</p>
  <p><button class="link" type="button" id="qagain">Skicka en ny förfrågan</button></p>
</div>'''


# --- Start page -----------------------------------------------------------------------------------------------------
def index():
    cards = "".join(card(s) for s in CARDS)
    steps = "".join(f"<li><b>{t}</b> {d}</li>" for t, d in STEPS)
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    machines = "".join(f"<li>{m}</li>" for m in MACHINES)
    intro_links = " ".join(f'<a class="pill pill-dark" href="tjanst-{s["slug"]}.html">{s["title"]}</a>' for s in CARDS[:3])

    main = f'''<section class="hero" id="top" aria-labelledby="hero-h">
  <div class="hero-ph">{img("hero-grav", "Grävmaskin på en arbetsplats", "60% 50%", lazy=False)}</div>
  <div class="wrap hero-in">
    <h1 id="hero-h">Mark och anläggning i Göteborg med omnejd</h1>
    <p>{SHORT} är din pålitliga samarbetspartner för maskintjänster – för både företag och privatpersoner.</p>
    <div class="btns">{call_btn()}<a class="pill pill-dark" href="#offert">Begär offert</a></div>
  </div>
  <span class="hero-note">Illustrationsbild</span>
</section>

<section class="sec tint" aria-labelledby="intro-h">
  <div class="wrap split">
    {photo("intro", "Grävmaskin på en byggarbetsplats i stan")}
    <div>
      <h2 id="intro-h">VA, dränering och husgrunder i Göteborg</h2>
      <p class="lead">Vi utför VA-arbeten, dräneringar, husgrunder, parkeringsytor, sten- och murarbeten, schakt och transport samt byggande och reparation av vägar. Med egna maskiner tar vi jobbet hela vägen.</p>
      <div class="btns">{intro_links}</div>
    </div>
  </div>
</section>

<section class="sec" id="tjanster" aria-labelledby="tj-h">
  <div class="wrap">
    <h2 id="tj-h">Våra tjänster</h2>
    <ul class="cards">{cards}</ul>
    <h3 class="also-h">Vi utför också</h3>
    <div class="btns">{also_pills()}</div>
  </div>
</section>

<section class="sec tint" id="uthyrning" aria-labelledby="ut-h">
  <div class="wrap narrow center">
    <h2 id="ut-h">Maskinuthyrning – med eller utan förare</h2>
    <p class="lead">Vi hyr ut de flesta vanliga typer av entreprenadmaskiner, på kort eller lång tid.</p>
    <ul class="machines">{machines}<li>Med mera</li></ul>
    <div class="btns">{call_btn()}<a class="pill pill-dark" href="tjanst-uthyrning.html">Läs mer om uthyrning</a></div>
  </div>
</section>

<section class="sec" id="om-oss" aria-labelledby="om-h">
  <div class="wrap split">
    {photo("om-oss", "Grävmaskin i snö framför granskog")}
    <div>
      <h2 id="om-h">Ett lokalt markföretag från Kungälv</h2>
      <p class="lead">{NAME} är ett mark- och anläggningsföretag som tar uppdrag i Göteborg med omnejd, för både företag och privatpersoner. Vi planerar noggrant, kör med egna maskiner och följer upp arbetet tills det är klart.</p>
      <h3>Så går det till</h3>
      <ol class="steps">{steps}</ol>
      <div class="btns">{call_btn()}</div>
    </div>
  </div>
</section>

<section class="sec tint" id="kontakt" aria-labelledby="kt-h">
  <div class="wrap narrow">
    <h2 id="kt-h">Bli kontaktad av {SHORT}</h2>
    <p class="lead">Fyll i formuläret så hör vi av oss. Vill du hellre ringa eller mejla går det lika bra: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
    <div class="btns">{call_btn()}</div>
    <div id="offert">{quote_form()}</div>
  </div>
</section>

<section class="sec" id="fragor" aria-labelledby="fq-h">
  <div class="wrap narrow">
    <h2 id="fq-h">Vanliga frågor</h2>
    <div class="faq">{faq}</div>
  </div>
</section>

<section class="sec tint seo" aria-labelledby="seo-h">
  <div class="wrap narrow">
    <h2 id="seo-h">Markentreprenör i Göteborg och Kungälv</h2>
    <p>{SHORT} är en markentreprenör med bas i Kungälv som jobbar i hela Göteborgsregionen. Vi gör <a href="tjanst-va-arbeten.html">VA-arbeten</a> och <a href="tjanst-draneringar.html">dräneringar</a> för villor och fastigheter, och bygger <a href="tjanst-husgrunder.html">husgrunder</a> för hus, garage och lokaler.</p>
    <p>Vi anlägger också <a href="tjanst-parkeringsytor.html">parkeringsytor</a>, utför <a href="tjanst-sten-och-murarbeten.html">sten- och murarbeten</a>, sköter <a href="tjanst-schakt-och-transport.html">schakt och transport</a> och bygger och reparerar <a href="tjanst-infrastruktur.html">vägar</a>. Behöver du bara en maskin finns <a href="tjanst-uthyrning.html">maskinuthyrning</a> med eller utan förare. Ring {PHONE} eller <a href="#offert">begär en offert</a>.</p>
    <h3>Hitta hit</h3>
    <p>{NAME}, c/o {ADDR}.</p>
    <div class="btns"><a class="pill pill-accent" href="{MAPS_LINK}" target="_blank" rel="noopener">Öppna i Google Maps</a></div>
  </div>
</section>

<section class="map" aria-label="Karta">
  <iframe src="{MAP_EMBED}" title="Karta: {ADDR}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</section>'''
    page("index.html", "Markentreprenad i Göteborg – VA, dränering, grunder, maskinuthyrning | Ohan Entreprenad AB",
         f"Ohan Entreprenad AB utför VA-arbeten, dräneringar, husgrunder, parkeringsytor och vägar i Göteborg med omnejd och hyr ut maskiner. Ring {PHONE}.",
         main, home=True)


# --- Service pages --------------------------------------------------------------------------------------------------
def service_page(s):
    items = "".join(f"<li>{i}</li>" for i in s["items"])
    body = "".join(f"<p>{p}</p>" for p in s["body"])
    others = "".join(card(o) for o in [o for o in CARDS if o["slug"] != s["slug"]][:3])
    offer = f'index.html?typ={quote_plus(s["title"])}#offert'
    main = f'''<section class="hero hero-small" aria-labelledby="ph-h">
  <div class="hero-ph">{img(s["photo"], s["alt"], s["pos"], lazy=False)}</div>
  <div class="wrap hero-in">
    <nav class="crumbs" aria-label="Brödsmulor"><a href="index.html">Start</a> / <a href="index.html#tjanster">Tjänster</a> / <span aria-current="page">{s["title"]}</span></nav>
    <h1 id="ph-h">{s["title"]} i Göteborg</h1>
    <p>{s["short"]}</p>
    <div class="btns">{call_btn()}<a class="pill pill-dark" href="{offer}">Begär offert</a></div>
  </div>
  <span class="hero-note">Illustrationsbild</span>
</section>
<section class="sec">
  <div class="wrap narrow prose">
    <h2>{s["title"]} med {SHORT}</h2>
    {body}
    <h3>Det kan ingå</h3>
    <ul class="list">{items}</ul>
    <div class="btns">{call_btn()}<a class="pill pill-dark" href="{offer}">Begär offert</a></div>
  </div>
</section>
<section class="sec tint">
  <div class="wrap">
    <h2>Fler tjänster</h2>
    <ul class="cards">{others}</ul>
    <h3 class="also-h">Vi utför också</h3>
    <div class="btns">{also_pills(skip=s["slug"])}</div>
  </div>
</section>'''
    desc = f'{s["title"]} i Göteborg med omnejd. {s["short"]} {NAME}, telefon {PHONE}.'
    page(f'tjanst-{s["slug"]}.html', f'{s["title"]} i Göteborg | {NAME}', desc, main, image=s["photo"])


def not_found():
    main = f'<section class="sec"><div class="wrap narrow"><h1>Sidan finns inte</h1><div class="btns"><a class="pill pill-dark" href="index.html">Till startsidan</a>{call_btn()}</div></div></section>'
    page("404.html", f"Sidan finns inte | {NAME}", "Sidan kunde inte hittas.", main)


def seo_files():
    urls = ["index.html"] + [f'tjanst-{s["slug"]}.html' for s in SERVICES]
    locs = "".join(f"<url><loc>{SITE_URL}{'' if u == 'index.html' else u}</loc></url>" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>\n', encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    index()
    for s in SERVICES:
        service_page(s)
    not_found()
    seo_files()
    print("Byggde", len(list(OUT.glob("*.html"))), "sidor i", OUT)
