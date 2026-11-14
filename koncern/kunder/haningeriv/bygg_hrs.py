"""Bygger Haninge Riv & Sanerings sajt med koncern-generatorn i Ohan-entreprenad, i samma stil som Haninge Byggteam.

Kör:  python3 bygg_hrs.py <Ohan-entreprenad> <utmapp> [<mapp med node_modules för purgecss/lightningcss>]

Innehållet ligger i brief.json, det grafiska paketet (Haninge Byggteams, med HRS färger) i paket.json och
företagets bilder i bilder/ (gör om dem med prep_bilder.py). Skriptet följer Haninge Byggteams bygge
(HB-AB/scripts/bygg_koncern.py) så att systerbolagens sajter ser likadana ut.
"""
import html
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROT = pathlib.Path(__file__).resolve().parent
OHAN = pathlib.Path(sys.argv[1]).resolve()
UT = pathlib.Path(sys.argv[2]).resolve()
NODE = pathlib.Path(sys.argv[3]).resolve() if len(sys.argv) > 3 else ROT

# Förhandsvisningen skickar förfrågningarna till Elevate Studio; byt till info@haningeriv.se vid lansering.
FORM_EMAIL = "elevate.studio018@gmail.com"
# Det gemensamma formuläret skickar till det bolag kunden väljer (båda vid "Båda / vet inte").
# Vid lansering: HRS -> info@haningeriv.se, Byggteam -> info@haningebyggteam.se.
FORM_TILL = {"hrs": FORM_EMAIL, "hb": FORM_EMAIL}
TEL = "072-002 22 00"
HB_URL = "https://www.haningebyggteam.se/"
TEL_KNAPP = ('<a class="head-tel" href="tel:+46720022200" aria-label="Ring oss: 072-002 22 00">'
             '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
             '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1z"/></svg><span>072-002 22 00</span></a>')

WORK_TYPES = ["Rivning", "Stambytesrivning", "Sanering", "Betonghåltagning", "Friläggning av rör vid fuktskada",
              "Konsult inom bygg", "Bemanning av byggpersonal"]
# Haninge Byggteams uppdragstyper (samma som i Byggteams eget formulär, HB-AB/scripts/bygg_koncern.py)
HB_TYPES = ["Totalrenovering", "Köksrenovering", "Badrumsrenovering", "Målning och ytskikt", "Golv, kakel och klinker",
            "Snickeri och inredning", "Dörrar, fönster och tak", "Om- och tillbyggnad, utomhus", "VVS och ledningsarbeten"]
BOLAG_VAL = [("hrs", "Rivning, sanering & håltagning", "Haninge Riv & Sanering"),
             ("hb", "Bygg & renovering", "Haninge Byggteam"),
             ("bada", "Båda / vet inte", "Vi fördelar förfrågan")]
START_OPTIONS = ["Så snart som möjligt", "Inom 1–3 månader", "Inom 3–6 månader", "Senare / vet inte"]

# Den gamla sajtens adresser pekar vidare.
REDIRECTS = {"tjanster.html": "verksamhet.html", "kontakt.html": "om-oss.html#kontakt", "offert.html": "om-oss.html#boka",
             "integritetspolicy.html": "om-oss.html#kontakt"}

KUNDER = [("phab", "Projekthjälpen AB (PHAB)", 56, "#0A6EB4"), ("jm-entreprenad", "J&M Entreprenad AB", 44, "#E3851F"),
          ("sara-bygger", "Sara Bygger AB", 24, "#55524D"), ("tumba-riv", "Tumba Riv & Sanering AB", 42, "#283D49"),
          ("nordhab", "Nordhab", 25, "#1C2140"), ("malardalens-rorinfodring", "Mälardalens Rörinfodring AB", 22, "#DB6E2D")]

GALLERI = [
 ("hero-kapning.jpg", "Håltagning", "Kapning i betonggolv"), ("riv-o-sanering.jpg", "Rivning", "Rivning av vägg från saxlift"),
 ("projekt-6.jpg", "Sanering", "Sluss in till saneringszon"), ("projekt/haninge-6.jpg", "Friläggning av rör", "Frilagda avloppsrör i golv"),
 ("rivning-tjanster.jpg", "Rivning", "Utriven dörrkarm och vägg"), ("haltagning.jpg", "Håltagning", "Kärnborrade hål i betongvägg"),
 ("projekt/haninge-11.jpg", "Håltagning", "Uppsågat hål i armerat golv"), ("sanering-zon.jpg", "Sanering", "Inplastad zon"),
 ("projekt/haninge-3.jpg", "Friläggning av rör", "Schakt i golv vid rörbyte"), ("hero-hall.jpg", "Rivning", "Rivning i lagerhall"),
 ("projekt/haninge-12.jpg", "Rivning", "Rivning av murad vägg"), ("projekt-5.jpg", "Håltagning", "Ny dörröppning sågad i vägg"),
 ("projekt/haninge-2.jpg", "Sanering", "Arbete innanför plastavskärmning"), ("grav-golv.jpg", "Friläggning av rör", "Friläggning av rör vid fuktskada"),
 ("projekt/haninge-20.jpg", "Håltagning", "Kärnborrning genom klinkergolv"), ("projekt/haninge-19.jpg", "Rivning", "Rivningsmassor lastade för bortforsling"),
 ("borrning.jpg", "Håltagning", "Borrning med vattenspolning"), ("projekt/haninge-4.jpg", "Rivning", "Uppbilat golv i badrum"),
 ("projekt/haninge-8.jpg", "Friläggning av rör", "Frilagd golvbrunn"), ("projekt-3.jpg", "Sanering", "Rengöring efter vattenskada"),
 ("vagg-oppnad.jpg", "Rivning", "Öppnad vägg inför ombyggnad"), ("projekt/haninge-5.jpg", "Friläggning av rör", "Schakt längs vägg"),
 ("projekt/haninge-16.jpg", "Håltagning", "Sågning vid väggfot"), ("sanering-inplastat.jpg", "Sanering", "Saneringszon"),
 ("projekt/haninge-18.jpg", "Rivning", "Rivning av bjälklag"), ("projekt/haninge-9.jpg", "Friläggning av rör", "Grävning vid rörskada"),
 ("projekt-1.jpg", "Håltagning", "Väggsågning"), ("hall-rivd.jpg", "Rivning", "Hall efter rivning"),
 ("projekt/haninge-7.jpg", "Friläggning av rör", "Frilagt stamrör i vägg"), ("projekt-4.jpg", "Håltagning", "Uppmärkning inför håltagning"),
 ("lift.jpg", "Rivning", "Rivning i butikslokal"), ("projekt/haninge-1.jpg", "Friläggning av rör", "Schakt vid grund"),
 ("rivning-haltagning.jpg", "Håltagning", "Väggsåg på skena"),
]
GALLERI_KALLA = ROT / "kalla"

E = html.escape


def prepare_bank():
    bank, tsv = OHAN / "koncern" / "bildbank", OHAN / "koncern" / "bildbank.tsv"
    rows = (ROT / "bilder" / "bilder.tsv").read_text(encoding="utf-8").splitlines()
    have = tsv.read_text(encoding="utf-8")
    for f in (ROT / "bilder").glob("*.jpg"):
        shutil.copy(f, bank / f.name)
    missing = [r for r in rows if r.strip() and r.split("\t")[0] + "\t" not in have]
    if missing:
        tsv.write_text(have.rstrip("\n") + "\n" + "\n".join(missing) + "\n", encoding="utf-8")


def load_generator():
    sys.path.insert(0, str(OHAN / "koncern"))
    import generera

    orig = generera.Bilder.ta

    def ta(self, tagg=None):
        # Bara några egna bilder per motiv: återanvänd dem hellre än att falla tillbaka på andra.
        if tagg and tagg.startswith("hrs-"):
            ids = {x["id"] for x in self.bank if x["tagg"] == tagg}
            if ids and ids <= self.anvanda:
                self.anvanda -= ids
        return orig(self, tagg)

    generera.Bilder.ta = ta
    orig_init = generera.Bilder.__init__

    def init(self, *a, **k):
        # Bara HRS egna bilder (och systerbolagets kortbild): inga stockbilder ur bildbanken.
        orig_init(self, *a, **k)
        egna = dict(r.split("\t")[:2] for r in (ROT / "bilder" / "bilder.tsv").read_text(encoding="utf-8").splitlines() if r.strip())
        self.bank = [dict(x, tagg=egna[x["id"]]) for x in self.bank if x["id"] in egna]
        self.reserv = ["hrs-folk", "hrs-rivning", "hrs-sanering", "hrs-haltagning", "hrs-hall", "hrs-borrning", "hrs-lift"]

    generera.Bilder.__init__ = init
    generera.varianter.REG[("hb-tjanster", None)] = tjanster_kort
    generera.varianter.REG[("vagval", "hb-t4")] = bolag_och_tjanster
    generera.varianter.REG[("siffror", "hb-r5")] = siffror_ringar
    generera.varianter.REG[("projekt", "hb-p57")] = projekt_lista
    generera.varianter.REG[("hrs-kunder", None)] = kunder
    generera.Sajt.sida_projekt = sida_projekt
    return generera


def tjanster_kort(self):
    """Startsidan: Våra tjänster som fyra stora bildkort, ett per affärsområde."""
    from generera import PIL
    kort = ""
    for i, a in enumerate(self.b["affarsomraden"]):
        bild = self.bilder.ta(a["tagg"])
        kort += (f'<li><a class="tk-kort" href="verksamhet.html#omr-{i}"><span class="tk-bild">{self.bilder.img(bild, "(min-width:1100px) 25vw, (min-width:640px) 50vw, 100vw")}</span>'
                 f'<span class="tk-text"><small>{i + 1:02d}</small><b>{E(a["titel"])}</b><span>{E(a["text"])}</span><i>Läs mer {PIL}</i></span></a></li>')
    return f'''<section class="sek tk" aria-labelledby="tk-h"><div class="wrap">
  <div class="tk-huvud"><div><span class="etikett">Vårt erbjudande</span><h2 id="tk-h">Våra tjänster</h2></div>
    <p>Från rivning av innerväggar till hela våningsbyggnader – vi tar hand om allt som krävs för att jobbet ska ske smidigt och säkert.</p>
    {self.knapp("Alla tjänster", "verksamhet.html")}</div>
  <ul class="tk-grid">{kort}</ul>
</div></section>'''


def siffror_ringar(self):
    """Nyckeltalen i ringar över en mörk bild; ringarna fylls och talen räknar upp (hrs.js)."""
    b = self.b
    bild = self.bilder.ta("hrs-borrning")
    r, sw = 64, 12
    size, c = 2 * (r + sw), 2 * 3.14159 * r
    li = ""
    for x in b["nyckeltal"]:
        v = x["varde"]
        li += (f'<li><div class="r5-ring"><svg viewBox="0 0 {size} {size}" aria-hidden="true">'
               f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="rgba(255,255,255,.2)" stroke-width="{sw}"/>'
               f'<circle class="r5-fyll" cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="var(--c-a)" stroke-width="{sw}" stroke-linecap="round" '
               f'stroke-dasharray="{c:.1f}" stroke-dashoffset="{c:.1f}" transform="rotate(-90 {size/2} {size/2})"/></svg>'
               f'<b data-till="{v.replace(",", ".")}" data-dec="{1 if "," in v else 0}" data-slut="{E(v)}">{E(v)}</b></div><span>{E(x["etikett"])}</span></li>')
    return f'''<section class="r5 hb-anim" aria-labelledby="r5-h">{self.bilder.img(bild, "100vw")}<div class="wrap">
  <span class="etikett">HRS i siffror</span><h2 id="r5-h">{E(b["intro_rubrik"])}</h2><ul class="r5-lista">{li}</ul>
</div></section>'''


def projekt_lista(self):
    """Startsidan: mörk sektion med filter och stora bildkort; beskrivningen visas vid hover."""
    from generera import PIL
    pr = self.b["projekt"]
    typer = list(dict.fromkeys(p["typ"] for p in pr))
    chips = '<button type="button" data-typ="" aria-pressed="true">Alla</button>' + "".join(
        f'<button type="button" data-typ="{E(t)}" aria-pressed="false">{E(t)}</button>' for t in typer)
    kort = ""
    for i, p in enumerate(pr, 1):
        bild = self.bilder.ta(p.get("tagg"))
        meta = " · ".join(x for x in (f"{i:02d}", p["typ"], p.get("ort")) if x)
        kort += (f'<li data-typ="{E(p["typ"])}"><a href="projekt.html">{self.bilder.img(bild, "(min-width:1000px) 33vw, (min-width:640px) 50vw, 100vw")}'
                 f'<span class="pf-text"><small>{E(meta)}</small><b>{E(p["namn"])}</b><em>{E(p["text"])}</em></span>'
                 f'<i class="pf-pil">{PIL}</i></a></li>')
    return f'''<section class="sek pf" data-pf aria-labelledby="pf-h"><div class="wrap">
  <div class="pf-huvud"><div><span class="etikett">Projekt</span><h2 id="pf-h">Några av våra projekt</h2></div>{self.textlank("Alla projektbilder", "projekt.html")}</div>
  <div class="pf-chips" role="group" aria-label="Filtrera projekt">{chips}</div>
  <ul class="pf-lista">{kort}</ul>
</div></section>'''


def bolag_och_tjanster(self):
    """Våra bolag som två separata bildkort, sedan tjänsterna som ikonrutor."""
    from generera import ikon, PIL
    b = self.b
    bolag = ""
    for i, x in enumerate(self.bolagslista()):
        bild = self.bilder.ta(x.get("tagg"))
        bolag += (f'<a class="t4-bolag" href="bolag.html#bolag-{i}">{self.bilder.img(bild, "(min-width:900px) 50vw, 100vw")}'
                  f'<span class="t4-bt"><small>{E(x.get("segment", ""))}</small><b>{E(x["namn"])}</b><span>{E(x.get("rubrik", ""))}</span></span>'
                  f'<i class="t4-pil">{PIL}</i></a>')
    rutor = "".join(f'<li><a href="{t["href"]}">{ikon(t["ikon"])}<span>{E(t["titel"])}</span>{PIL}</a></li>'
                    for t in b["tjanster"] if "omr-" in t["href"])
    return f'''<section class="sek t4" aria-labelledby="t4-h"><div class="wrap">
  <div class="t4-huvud"><span class="etikett">Koncernen</span><h2 id="t4-h">Våra bolag</h2></div>
  <div class="t4-bolagen">{bolag}</div>
  <div class="t4-huvud t4-h2"><div><span class="etikett">Tjänster</span><h2>Vad kan vi hjälpa dig med?</h2></div>{self.textlank("Alla tjänster", "verksamhet.html")}</div>
  <ul class="t4-rutor">{rutor}</ul>
</div></section>'''


def kunder(self):
    """Våra största kunder: vita loggkort på mörk botten; kundens färg och namn vid hover."""
    li = "".join(f'<li style="--k:{c}"><img src="img/kunder/{f}.png" alt="{E(n)}" style="--h:{h}px" loading="lazy"><span>{E(n)}</span></li>'
                 for f, n, h, c in KUNDER)
    return f'''<section class="sek ku pa-mork" aria-labelledby="ku-h"><div class="wrap">
  <div class="ku-huvud"><div><span class="etikett">Kunder</span><h2 id="ku-h">Våra största kunder</h2></div>
    <p>Vi kör stambytesrivning åt stora byggföretag, bland andra:</p></div>
  <ul class="ku-lista">{li}</ul>
</div></section>'''


def sida_projekt(self, slug, namn):
    """Projektsidan: alla bilder från arbetsplatserna, med filter och bildvisning i helskärm."""
    from generera import PIL
    typer = list(dict.fromkeys(t for _, t, _ in GALLERI))
    chips = '<button type="button" data-typ="" aria-pressed="true">Alla</button>' + "".join(
        f'<button type="button" data-typ="{E(t)}" aria-pressed="false">{E(t)}</button>' for t in typer)
    li = ""
    for f, t, alt in GALLERI:
        namn_ = "g-" + f.replace("/", "-")
        li += (f'<li data-typ="{E(t)}"><button type="button" aria-label="Visa större: {E(alt)}">'
               f'<img src="img/g/{namn_.replace(".jpg", "-s.jpg")}" data-full="img/g/{namn_}" alt="{E(alt)}" loading="lazy">'
               f'<span class="gl-text"><small>{E(t)}</small><b>{E(alt)}</b></span></button></li>')
    lb = (f'<div class="gl-lb" role="dialog" aria-modal="true" aria-label="Bildvisning" hidden><img src="data:," alt=""><p></p>'
          f'<button type="button" class="gl-stang" aria-label="Stäng">×</button><button type="button" class="gl-bak" aria-label="Föregående bild">{PIL}</button>'
          f'<button type="button" class="gl-fram" aria-label="Nästa bild">{PIL}</button></div>')
    innehall = f'''<section class="sek gl" data-galleri aria-label="Projektbilder"><div class="wrap">
  <div class="pf-chips" role="group" aria-label="Filtrera bilder">{chips}</div>
  <ul class="gl-lista">{li}</ul>
</div></section>{lb}''' + self.s_process()
    self.undersida(slug, namn, self.T("sida_projekt_titel"), self.T("sida_projekt_ingress"), "hrs-rivning2", innehall, f'{namn} – {self.b["namn"]}.')


def galleri_bilder(out):
    from PIL import Image
    mal = out / "img" / "g"
    mal.mkdir(parents=True, exist_ok=True)
    for f, _, _ in GALLERI:
        namn = "g-" + f.replace("/", "-")
        im = Image.open(GALLERI_KALLA / f).convert("RGB")
        stor = im.copy(); stor.thumbnail((1600, 1600), Image.LANCZOS)
        stor.save(mal / namn, quality=82, optimize=True, progressive=True)
        s = im.copy(); s.thumbnail((720, 720), Image.LANCZOS)
        s.save(mal / namn.replace(".jpg", "-s.jpg"), quality=76, optimize=True, progressive=True)
    k = out / "img" / "kunder"
    shutil.copytree(ROT / "kunder", k, dirs_exist_ok=True)


def quote_form():
    """Ett offertformulär för båda bolagen: kunden väljer vad det gäller och förfrågan går till rätt bolag."""
    val = "".join(f'<label class="bv-val"><input type="radio" name="bolag" value="{k}"{" checked" if k == "hrs" else ""}>'
                  f'<span><b>{E(t)}</b><small>{E(u)}</small></span></label>' for k, t, u in BOLAG_VAL)
    types = (f'<optgroup label="Haninge Riv &amp; Sanering" data-bolag="hrs">{"".join(f"<option>{E(t)}</option>" for t in WORK_TYPES)}</optgroup>'
             f'<optgroup label="Haninge Byggteam" data-bolag="hb">{"".join(f"<option>{E(t)}</option>" for t in HB_TYPES)}</optgroup>'
             '<option>Annat</option>')
    start = "".join(f"<option>{E(t)}</option>" for t in START_OPTIONS)
    return f'''<form class="boka-form" id="qform" novalidate data-endpoint-hrs="https://formsubmit.co/ajax/{FORM_TILL["hrs"]}" data-endpoint-hb="https://formsubmit.co/ajax/{FORM_TILL["hb"]}">
<fieldset class="hel bv"><legend>Vad gäller förfrågan?</legend><div class="bv-lista">{val}</div></fieldset>
<label><span>Namn *</span><input id="f-namn" name="namn" autocomplete="name" required><small class="fel" id="e-namn" hidden>Ange ditt namn.</small></label>
<label><span>Telefon *</span><input id="f-tel" name="tel" type="tel" autocomplete="tel"><small class="fel" id="e-tel" hidden>Ange telefon eller e-post.</small></label>
<label><span>E-post</span><input id="f-epost" name="epost" type="email" autocomplete="email"><small class="fel" id="e-epost" hidden>Kontrollera e-postadressen.</small></label>
<label><span>Adress eller ort för uppdraget</span><input id="f-adress" name="adress" autocomplete="street-address"></label>
<label><span>Typ av uppdrag</span><select id="f-typ" name="typ"><option value="">Välj</option>{types}</select></label>
<label><span>Önskad start</span><select id="f-start" name="start"><option value="">Välj</option>{start}</select></label>
<label class="hel"><span>Beskriv jobbet</span><textarea id="f-besk" name="besk" rows="4"></textarea></label>
<div class="hp" aria-hidden="true"><label>Lämna tomt<input id="f-web" name="web" tabindex="-1" autocomplete="off"></label></div>
<button class="knapp knapp-primar" type="submit"><span>Skicka offertförfrågan</span></button>
<p class="hel boka-fin">Förfrågan går bara till det bolag du väljer, eller till båda. Uppgifterna används endast för att besvara den.</p>
<p class="hel fel" id="send-err" role="alert" hidden>Förfrågan kunde inte skickas. Försök igen eller ring {TEL}.</p>
</form>
<div class="boka-form boka-klar" id="qdone" tabindex="-1" hidden><h3>Tack för din förfrågan</h3><p id="qdone-txt">Vi hör av oss så snart vi kan.</p>
<button class="knapp" type="button" id="qagain"><span>Skicka en ny förfrågan</span></button></div>'''


# Haninge Byggteams tillägg till generatorns CSS (HB-AB/scripts/bygg_koncern.py), med HRS svart i stället för marinblått.
HB_CSS = (pathlib.Path(__file__).parent / "hb_extra.css")

HRS_CSS = """
/* ---- Haninge Riv & Sanering ---- */
/* Loggan: vit över heron, mörk när sidhuvudet är vitt */
.logga-bild { height: 66px; }
@media (max-width: 720px) { .logga-bild { height: 50px; } }
.logga .logga-vit { display: none; }
body[data-header="transparent"].har-hero .head:not(.fast) .logga .logga-vit { display: block; }
body[data-header="transparent"].har-hero .head:not(.fast) .logga .logga-mork { display: none; }
.fot-namn .fot-logga { width: 170px; }

/* Herorubriken är längre än Byggteams: lite mindre grad */
body[data-herotext="nere"] .hero .hero-txt h1, body[data-herotext="nere"] .hero .hero-txt h2 { font-size: calc(clamp(44px, 6.6vw, 112px) * var(--skala-r)); max-width: 11em; }

/* Telefonknappen i sidhuvudet: orange med numret, rund ikon på smal mobil */
.head-tel { display: inline-flex; align-items: center; gap: 8px; min-height: 40px; padding: 9px 18px 9px 14px; border-radius: 999px; background: var(--c-a); color: var(--c-a-ink); font: 600 14px/1 var(--font-t); white-space: nowrap; text-decoration: none; transition: background .2s, transform .2s; }
.head-tel svg { width: 18px; height: 18px; flex: none; }
.head-tel:hover { background: #e57a3a; transform: translateY(-1px); }
@media (max-width: 479px) { .head-tel { width: 42px; height: 42px; padding: 0; justify-content: center; } .head-tel span { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); } }
@media (min-width: 1180px) and (max-width: 1379px) { .head-kontakt { display: none !important; } .nav { gap: 20px; } }

/* Sex tjänsterutor: tre eller sex i bredd */
@media (min-width: 760px) { .t4-rutor { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1200px) { .t4-rutor { grid-template-columns: repeat(6, 1fr); } }

/* Processen: fyra pilar */
.hpp-lista, .hpp-steg { --n: 4; }

/* Våra största kunder: vita loggkort; kundens färg som list och namn vid hover */
.ku h2 { color: #fff; margin: 10px 0 0; }
.ku .etikett { color: var(--c-a); }
.ku-huvud { display: grid; gap: 14px; margin-bottom: clamp(28px, 4vw, 44px); align-items: end; }
@media (min-width: 1000px) { .ku-huvud { grid-template-columns: 1fr 1fr; gap: 48px; } }
.ku-huvud p { margin: 0; color: rgba(255,255,255,.75); max-width: 36em; }
.ku-lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 14px; grid-template-columns: repeat(2, 1fr); }
@media (min-width: 900px) { .ku-lista { grid-template-columns: repeat(3, 1fr); } }
.ku-lista li { position: relative; display: grid; place-items: center; gap: 12px; min-height: 150px; padding: 30px 20px 22px; background: #fff; border-radius: var(--r-card); overflow: hidden; transition: transform .25s ease, box-shadow .25s ease; }
.ku-lista li::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 5px; background: var(--k); transform: scaleX(0); transform-origin: left; transition: transform .3s ease; }
.ku-lista img { height: var(--h); max-height: 56px; max-width: 80%; width: auto; object-fit: contain; }
.ku-lista span { font-size: 13px; font-weight: 600; color: var(--c-mut); text-align: center; transition: color .25s; }
.ku-lista li:hover { transform: translateY(-4px); box-shadow: 0 20px 44px rgba(0,0,0,.35); }
.ku-lista li:hover::before { transform: none; }
.ku-lista li:hover span { color: var(--k); }
@media (max-width: 599px) { .ku-lista li { min-height: 120px; padding: 24px 12px 16px; } .ku-lista img { max-height: 40px; } }

/* Offertformuläret: val av bolag */
.bv { border: 0; margin: 0; padding: 0; min-width: 0; }
.bv legend { font-size: 14px; font-weight: 600; margin-bottom: 8px; padding: 0; }
.bv-lista { display: grid; gap: 10px; grid-template-columns: repeat(3, minmax(0, 1fr)); }
.bv-val { position: relative; display: block; cursor: pointer; }
.bv-val input { position: absolute; opacity: 0; width: 1px; height: 1px; }
.bv-val span { display: grid; gap: 3px; height: 100%; padding: 13px 14px 13px 40px; border: 1px solid var(--c-line); border-radius: min(var(--r-card), 10px); background: var(--c-yta); transition: border-color .2s, background .2s; }
.bv-val span::before { content: ""; position: absolute; left: 14px; top: 16px; width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--c-mut); background: #fff; }
.bv-val b { font-size: 14.5px; line-height: 1.25; }
.bv-val small { font-size: 12.5px; font-weight: 500; color: var(--c-mut); }
.bv-val:hover span { border-color: var(--c-ink); }
.bv-val input:checked + span { border-color: var(--c-a); background: #fff; box-shadow: inset 0 0 0 1px var(--c-a); }
.bv-val input:checked + span::before { border-color: var(--c-a); background: radial-gradient(circle, var(--c-a) 0 4px, #fff 5px); }
.bv-val input:focus-visible + span { outline: 2px solid var(--c-ink); outline-offset: 2px; }
@media (max-width: 759px) { .bv-lista { grid-template-columns: 1fr; } }

/* Projektsidan: bildgalleri med filter */
.gl .pf-chips button { color: var(--c-ink); border-color: var(--c-line); }
.gl .pf-chips button:hover { border-color: var(--c-ink); }
.gl .pf-chips button[aria-pressed="true"] { background: var(--c-a); color: var(--c-a-ink); border-color: var(--c-a); }
.gl-lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 14px; grid-template-columns: repeat(2, 1fr); }
@media (min-width: 900px) { .gl-lista { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 1200px) { .gl-lista { grid-template-columns: repeat(4, 1fr); } }
.gl-lista li[hidden] { display: none; }
.gl-lista button { position: relative; display: block; width: 100%; aspect-ratio: 4 / 3; padding: 0; border: 0; border-radius: var(--r-card); overflow: hidden; cursor: zoom-in; background: var(--c-yta); isolation: isolate; text-align: left; }
.gl-lista img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; z-index: -2; transition: transform .6s ease; }
.gl-lista button::after { content: ""; position: absolute; inset: 0; z-index: -1; background: linear-gradient(0deg, rgba(14,18,24,.85) 0%, rgba(14,18,24,0) 55%); }
.gl-text { position: absolute; left: 0; right: 0; bottom: 0; display: grid; gap: 4px; padding: 16px 18px; color: #fff; }
.gl-text small { font-size: 11.5px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--c-a); }
.gl-text b { font: 600 15px/1.3 var(--font-t); }
.gl-lista button:hover img { transform: scale(1.05); }
.gl-lista button:focus-visible { outline: 3px solid var(--c-a); outline-offset: 3px; }
@media (max-width: 599px) { .gl-text { padding: 12px; } .gl-text b { font-size: 13px; } }
.gl-lb { position: fixed; inset: 0; z-index: 200; display: grid; place-items: center; padding: 64px 16px; background: rgba(14,18,24,.94); }
.gl-lb[hidden] { display: none; }
.gl-lb img { max-width: min(1400px, 100%); max-height: calc(100vh - 160px); width: auto; height: auto; border-radius: var(--r-img); }
.gl-lb p { position: absolute; left: 0; right: 0; bottom: 20px; margin: 0; text-align: center; color: #fff; font-weight: 600; }
.gl-lb button { position: absolute; width: 48px; height: 48px; border-radius: 50%; border: 0; display: grid; place-items: center; cursor: pointer; background: #fff; color: var(--c-ink); font-size: 26px; line-height: 1; }
.gl-lb button svg { width: 20px; height: 20px; }
.gl-stang { top: 16px; right: 16px; }
.gl-bak { left: 16px; top: 50%; transform: translateY(-50%) rotate(180deg); }
.gl-fram { right: 16px; top: 50%; transform: translateY(-50%); }
.gl-lb button:hover { background: var(--c-a); }
"""


def postprocess(out):
    for f in out.rglob("*.html"):
        doc = f.read_text(encoding="utf-8")
        doc = re.sub(r'<form class="boka-form".*?</form>', lambda m: quote_form(), doc, flags=re.S)
        doc = re.sub(r'<nav aria-label="Juridiskt">.*?</nav>', "", doc, flags=re.S)
        doc = defer_slides(doc)
        doc = re.sub(r'<div class="topprad">.*?</div></div>', "", doc, count=1, flags=re.S)
        # Systerbolaget Haninge Byggteam har en egen webbplats: dess bolagslänkar går dit.
        doc = doc.replace('href="bolag.html#bolag-1"', f'href="{HB_URL}" target="_blank" rel="noopener"')
        doc = re.sub(r'(<section class="sek-tat" id="bolag-1">.*?<div class="knappar">)<a class="textlank" href="[^"]*"><span>[^<]*</span>',
                     lambda m: m.group(1) + f'<a class="textlank" href="{HB_URL}" target="_blank" rel="noopener"><span>Till haningebyggteam.se</span>', doc, flags=re.S)
        doc = re.sub(r'(<section class="sek-tat" id="bolag-0">.*?<div class="knappar">)<a class="textlank" href="[^"]*">',
                     lambda m: m.group(1) + '<a class="textlank" href="om-oss.html#kontakt">', doc, flags=re.S)
        # Loggan: vit över heron, mörk på vitt sidhuvud
        doc = re.sub(r'<span class="ord">Haninge Riv &amp; Sanering</span>(<span class="tag">[^<]*</span>)?',
                     '<img class="logga-bild logga-mork" src="assets/logo.png" alt="" width="105" height="58">'
                     '<img class="logga-bild logga-vit" src="assets/logo-vit.png" alt="" width="105" height="58">', doc)
        doc = re.sub(r'(<a class="logga"[^>]*>)<svg.*?</svg>', r"\1", doc, flags=re.S)
        doc = doc.replace('<p class="fot-namn">Haninge Riv &amp; Sanering</p>',
                          '<p class="fot-namn"><img class="fot-logga" src="assets/logo-vit.png" alt="Haninge Riv &amp; Sanering AB" width="170" height="94"></p>')
        # Bilderna är HRS egna foton från arbetsplatserna, inte illustrationer: ingen "Illustrationsbild"-märkning.
        doc = re.sub(r'<span class="(?:foto-not|figtext)">Illustrationsbild</span>', "", doc)
        # Telefonnumret syns alltid: orange knapp i sidhuvudet, som på HRS gamla sajt
        doc = doc.replace('<div class="head-verktyg">', '<div class="head-verktyg">' + TEL_KNAPP, 1)
        # Ingen sökfunktion på sajten: ta bort sökknappen. Generatorns "Kvalitet & miljö" heter Hållbarhet här.
        doc = re.sub(r'<a class="sok" href="#".*?</a>', "", doc, flags=re.S)
        doc = doc.replace("Kvalitet &amp; miljö", "Hållbarhet").replace("Kvalitet & miljö", "Hållbarhet")
        doc = doc.replace('<ul class="jobb"><li><a href="#">', '<ul class="jobb"><li><a href="mailto:info@haningeriv.se?subject=Intresseanm%C3%A4lan">')
        # Hållbarhetsblocket: den skarpa bilden (sorterat avfall) stort, den mindre upplösta i den lilla rutan
        def byt(m):
            s = m.group(0)
            a, c = "hrs-miljo", "hrs-projekt-haninge-19"
            if s.find(c) < s.find(a) and c in s:
                s = s.replace(a, "\0").replace(c, a).replace("\0", c)
            return s
        doc = re.sub(r'<section[^>]*aria-labelledby="mhn-h".*?</section>', byt, doc, flags=re.S)
        if f.name == "om-oss.html":  # generatorn upprepar första om-stycket tre gånger på Om oss
            om0 = E(json.loads((ROT / "brief.json").read_text(encoding="utf-8"))["om"][0])
            delar = doc.split(om0)
            if len(delar) == 4:
                doc = (delar[0] + "Ett rivnings- och saneringsbolag i Österhaninge, söder om Stockholm – systerbolag till Haninge Byggteam." + delar[1] + om0 + delar[2]
                       + "Vi svarar på offertförfrågningar inom 24 timmar, även på helger, och har telefontid sex dagar i veckan." + delar[3])
        doc = doc.replace("family=Poppins:wght@400;500;600;700;800", "family=Poppins:wght@400;500;600;700")
        if ("hb-anim" in doc or "data-pf" in doc or "data-galleri" in doc) and "hrs.js" not in doc:
            doc = doc.replace("</body>", '<script src="assets/hrs.js" defer></script>\n</body>')
        if 'id="qform"' in doc and "offert.js" not in doc:
            doc = doc.replace("</body>", '<script src="assets/offert.js" defer></script>\n</body>')
        f.write_text(doc, encoding="utf-8")
    hb = HB_CSS.read_text(encoding="utf-8")
    hb = hb.replace("rgba(10,31,54,", "rgba(14,18,24,").replace("rgba(6,18,32,", "rgba(14,18,24,").replace("rgba(14,42,71,", "rgba(14,18,24,")
    with open(out / "assets" / "bas.css", "a", encoding="utf-8") as fh:
        fh.write(hb + HRS_CSS)
    shutil.copy(ROT / "offert.js", out / "assets" / "offert.js")
    shutil.copy(ROT / "hrs.js", out / "assets" / "hrs.js")
    shutil.copy(ROT / "logo" / "hrs-logo.png", out / "assets" / "logo.png")
    shutil.copy(ROT / "logo" / "hrs-logo-vit.png", out / "assets" / "logo-vit.png")


LAZY_SLIDES = """<script>
/* Bildspelets bild 2 och 3 laddas först när sidan har visats, så att första bilden och texten kommer fram snabbare. */
addEventListener("load", function () { setTimeout(function () {
  document.querySelectorAll("img[data-src]").forEach(function (i) {
    if (i.dataset.srcset) i.srcset = i.dataset.srcset;
    i.src = i.dataset.src; i.removeAttribute("data-src"); i.removeAttribute("data-srcset");
  });
}, 300); });
</script>"""


def defer_slides(doc):
    m = re.search(r'<div class="bildspel" data-bildspel>.*?</section>', doc, flags=re.S)
    if not m:
        return doc
    slides = m.group(0).split('<div class="bild-slide')
    for i in range(2, len(slides)):
        slides[i] = re.sub(r'<img src="([^"]+)" srcset="([^"]+)"', r'<img src="data:image/gif;base64,R0lGODlhAQABAAAAACw=" data-src="\1" data-srcset="\2"', slides[i], count=1)
    first = re.search(r'<img src="([^"]+)" srcset="([^"]+)" sizes="([^"]+)"', slides[1]) if len(slides) > 1 else None
    doc = doc.replace(m.group(0), '<div class="bild-slide'.join(slides))
    if len(slides) > 2:
        doc = doc.replace("</body>", LAZY_SLIDES + "\n</body>", 1)
    if first:
        pre = f'<link rel="preload" as="image" href="{first.group(1)}" imagesrcset="{first.group(2)}" imagesizes="{first.group(3)}">'
        doc = doc.replace("</title>", "</title>\n" + pre, 1)
    return doc


def to_webp(out):
    from PIL import Image
    for f in list((out / "img").glob("*.jpg")) + list((out / "img" / "g").glob("*.jpg")):
        Image.open(f).save(f.with_suffix(".webp"), quality=74, method=6)
    for f in out.rglob("*.html"):
        doc = f.read_text(encoding="utf-8")
        doc = re.sub(r'(?<!content=")((?:\.\./)*img/(?:g/)?[\w-]+)\.jpg', r"\1.webp", doc)
        f.write_text(doc, encoding="utf-8")


def optimize_css(out):
    bin_ = NODE / "node_modules" / ".bin"
    css = out / "assets" / "bas.css"
    if not (bin_ / "purgecss").exists():
        print("OBS: purgecss saknas – CSS:en rensas inte.")
        return
    tmp = out / "assets" / "_purge"
    tmp.mkdir(exist_ok=True)
    subprocess.run([str(bin_ / "purgecss"), "--css", str(css), "--content", str(out / "**" / "*.html"), str(out / "assets" / "*.js"),
                    "--safelist", "syns", "aktiv", "fast", "bak", "--output", str(tmp)], check=True)
    subprocess.run([str(bin_ / "lightningcss"), "--minify", str(tmp / "bas.css"), "-o", str(css)], check=True)
    shutil.rmtree(tmp)


def redirects(out):
    for old, new in REDIRECTS.items():
        (out / old).write_text(f'<!doctype html><meta charset="utf-8"><title>Haninge Riv &amp; Sanering AB</title><meta name="robots" content="noindex">'
                               f'<meta http-equiv="refresh" content="0; url={new}"><link rel="canonical" href="{new}">'
                               f'<p>Sidan har flyttat: <a href="{new}">{new}</a></p>\n', encoding="utf-8")


def meta(out):
    # Förslag, inte bolagets officiella sajt: inga sökmotorer.
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
    (out / "paket.json").unlink(missing_ok=True)


def main():
    prepare_bank()
    generera = load_generator()
    brief = json.loads((ROT / "brief.json").read_text(encoding="utf-8"))
    paket = json.loads((ROT / "paket.json").read_text(encoding="utf-8"))
    generera.Sajt(brief, paket, UT).bygg()
    galleri_bilder(UT)
    postprocess(UT)
    redirects(UT)
    meta(UT)
    optimize_css(UT)
    to_webp(UT)
    print(f"Byggde {brief['namn']} -> {UT}")


if __name__ == "__main__":
    main()
