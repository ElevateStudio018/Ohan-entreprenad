"""Bygger de 10 exempelsajterna i site/exempel/ från innehållet i koncern/exempel/*.json.

Kör:  python3 koncern/exempel/bygg_exempel.py

Varje sajt får ett handplockat grafiskt paket som bygger på en arketyp från undersökningen (research/). Paketen
registreras i koncern/register.json, så att koncern-agenten aldrig gör en ny sajt som liknar någon av dem.
"""
import json
import pathlib
import sys

ROT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROT / "koncern"))
import generera  # noqa: E402
import paket  # noqa: E402

EX = ROT / "koncern/exempel"
UT = ROT / "site/exempel"

# Sjöstaden är låst: den byggs inte om, så att ändringar i mallen inte påverkar den.
FRYSTA = {"sjostaden"}

VAL = {
    # slug: (bransch, arketyp, val). Varje sajt har ett eget koncept med egna block (block, motiv, ordning_lista, bakgrund),
    # inte bara egna färger och typsnitt.
    "norrvik": ("bygg", "monument", dict(fot="standard", typsnitt="inter-tight", palett="marin-mint", hero="helskarm", header="transparent", meny="inline",
                ruta="solid", panel="primar", kort="overlay", form="piller-kantig", sidfot="mork", logga="ring", logga_farg="accent",
                hero_tagg="bygg", skala=1.06, gemener=False, sidfot_stor_logga=True, motiv="inget",
                block=dict(vagval="rader", bolag="flikar", siffror="jatte", nyheter="lista"),
                ordning_lista=["vagval", "bolag", "siffror", "berattelser", "projekt", "hb", "panel", "nyheter", "ir", "snabb"],
                bakgrund=dict(vagval="", bolag="pa-ton", siffror="", berattelser="pa-mork", projekt="", hb="pa-ton", panel="", nyheter="", ir="pa-yta"))),
    "ekbacka": ("bostad", "varm-bostad", dict(fot="cta", typsnitt="fraunces-inter", palett="terrakotta-kräm", hero="sok", header="pill", meny="inline",
                ruta="vanster", panel="ton", kort="under", form="mjuk", sidfot="primar", logga="tak", hero_tagg="bostad", motiv="mjuk",
                block=dict(vagval="chips", bolag="kort", siffror="rad", nyheter="lista"), projekt="rutnat",
                ordning_lista=["vagval", "projekt", "citat", "bolag", "berattelser", "siffror", "hb", "panel", "nyheter"],
                bakgrund=dict(vagval="pa-ton", projekt="", citat="pa-farg", bolag="", berattelser="pa-ton", siffror="", hb="pa-ton", panel="", nyheter=""))),
    "tornberg": ("infra", "industriell", dict(fot="cta", typsnitt="barlow-cond", palett="grafit-gul", hero="helskarm", header="mork", meny="inline", ruta="mork",
                 panel="mork", kort="overlay", form="kantig", sidfot="mork", logga="staplar", logga_farg="accent", knapp_accent=True,
                 hero_tagg="anlaggning", motiv="diagonal", block=dict(vagval="nummer", bolag="kort", siffror="band", nyheter="tidning"),
                 ordning_lista=["siffror", "vagval", "berattelser", "bolag", "projekt", "panel", "hb", "nyheter", "snabb"],
                 bakgrund=dict(siffror="pa-accent", vagval="", berattelser="pa-mork", bolag="", projekt="pa-yta", panel="", hb="pa-mork", nyheter=""))),
    "lindhem": ("bostad", "grannskap", dict(fot="cta", typsnitt="public-sans", palett="havsblå-orange", hero="split", split="primar", header="ljus", meny="inline",
                ruta="kontur", panel="primar", kort="under", projekt="rutnat", form="rundad", sidfot="primar", logga="punkt", hero_tagg="bostad",
                motiv="kurva", block=dict(vagval="cirklar", bolag="rund", siffror="rad", nyheter="lista"),
                ordning_lista=["service", "vagval", "citat", "bolag", "siffror", "berattelser", "projekt", "hb", "nyheter"],
                bakgrund=dict(vagval="", citat="pa-ton", bolag="", siffror="pa-farg", berattelser="", projekt="pa-ton", hb="", nyheter="pa-yta"))),
    "arcus": ("samhalle", "redaktionell", dict(fot="centrerad", typsnitt="newsreader-inter", palett="skog-salvia", hero="statement", statement="ton", header="centrerad",
              meny="inline", ruta="solid", panel="ton", kort="under", form="kantig", sidfot="mork", sidhero="ton", logga="bage", hero_tagg="people",
              sidfot_stor_logga=True, motiv="linjer", block=dict(vagval="register", bolag="lista", siffror="rad", nyheter="tidning"),
              ordning_lista=["vagval", "bolag", "berattelser", "siffror", "hb", "projekt", "nyheter", "ir"],
              bakgrund=dict(vagval="", bolag="", berattelser="", siffror="", hb="pa-ton", projekt="", nyheter="", ir=""))),
    "vardtra": ("tra", "skandinavisk", dict(fot="centrerad", typsnitt="outfit-dmsans", palett="oliv-guld", hero="mosaik", header="pill", meny="burger", ruta="vanster",
                panel="primar", kort="overlay", projekt="rutnat", form="rundad", sidfot="primar", logga="blad", hero_tagg="tra", gemener=True,
                motiv="inget", block=dict(vagval="bildrutor", bolag="kort", siffror="rad", nyheter="lista"), nyheter="kolumner",
                ordning_lista=["process", "vagval", "berattelser", "siffror", "bolag", "projekt", "hb", "panel", "nyheter"],
                bakgrund=dict(process="pa-ton", vagval="", berattelser="", siffror="pa-farg", bolag="", projekt="pa-yta", hb="", panel="", nyheter=""))),
    "kvarter": ("fastighet", "finans", dict(fot="cta", sidfot_stor_logga=False, typsnitt="libre-franklin", palett="stål-himmel", hero="kurs", header="transparent", meny="inline", ruta="mork",
                panel="mork", kort="overlay", form="lätt", sidfot="mork", logga="kvadrat", logo_versaler=True, logo_spatiering="0.1em",
                hero_tagg="kontor", motiv="inget", block=dict(vagval="lankar", bolag="tabell", siffror="dashboard", nyheter="lista"),
                ordning_lista=["siffror", "vagval", "ir", "bolag", "projekt", "hb", "berattelser", "nyheter", "snabb"],
                bakgrund=dict(siffror="pa-ton", vagval="", ir="", bolag="pa-yta", projekt="", hb="pa-mork", berattelser="", nyheter="pa-yta"))),
    "stenhamra": ("installation", "koncernband", dict(fot="standard", sidfot_stor_logga=False, typsnitt="manrope-inter", palett="djupgrön-koppar", hero="band", header="ljus", meny="inline",
                  ruta="solid", panel="primar", kort="overlay", rytm="ton", form="lätt", sidfot="primar", logga="ingen", gemener=True,
                  knapp_accent=True, nav_versaler=True, hero_tagg="el", bildtyngd=["el", "industri", "people"], motiv="inget",
                  block=dict(vagval="rutor", bolag="vagg", siffror="rad", nyheter="lista"),
                  ordning_lista=["vagval", "berattelser", "panel", "bolag", "siffror", "projekt", "hb", "ir", "nyheter", "snabb"])),
    "brofors": ("konsult", "teknisk", dict(fot="standard", typsnitt="plex-mono", palett="petrol-sand", hero="split", split="mork", header="ljus", meny="burger",
                ruta="vanster", panel="mork", kort="under", nyheter="kolumner", form="rundad", sidfot="mork", logga="romb", hero_tagg="infra",
                sidfot_stor_logga=True, motiv="rutnat", block=dict(vagval="expertis", bolag="kort", siffror="rad", nyheter="lista"),
                ordning_lista=["vagval", "projekt", "bolag", "siffror", "berattelser", "hb", "ir", "nyheter"],
                bakgrund=dict(vagval="pa-mork", projekt="", bolag="pa-ton", siffror="pa-farg", berattelser="", hb="pa-ton", nyheter="", ir=""))),
}


# Gemensam stil: alla exempel har Sjöstadens typsnitt, knappar, former, logga och header. De skiljer sig i färg
# (egen palett) och i sektionerna (hero, block, ordning, bakgrunder, sidfot).
def sjostaden_stil(val):
    v = dict(val)
    v.update(typsnitt="plusjakarta", skala=1.0, logo_versaler=True, logo_spatiering="0.08em", nav_versaler=False, logo_font="text",
             form="piller-kantig", knappstil="fylld", kort="overlay", panel="mork", sidhero="bild", sidfot="primar", meny="inline",
             logga="ingen", gemener=False, knapp_accent=False, motiv="inget", sidfot_stor_logga=False, maxbredd=1360, header_hojd=80,
             header="transparent" if val.get("hero") in ("helskarm", "centrerad", "kurs") else "ljus")
    if v.get("ruta") not in (None, "vanster"):
        v["ruta"] = "vanster"
    v.pop("statement", None)
    return v


def main():
    UT.mkdir(parents=True, exist_ok=True)
    namn_alla = {json.loads((EX / f"{s}.json").read_text())["namn"] for s in list(VAL) + list(FRYSTA)}
    reg = [r for r in paket.register() if r["for"] not in namn_alla]
    alla = []
    for slug in FRYSTA:
        b = json.loads((EX / f"{slug}.json").read_text(encoding="utf-8"))
        p = json.loads((UT / slug / "paket.json").read_text(encoding="utf-8"))
        p["fryst"] = True
        alla.append((b, p))
    for slug, (bransch, stil, val) in VAL.items():
        b = json.loads((EX / f"{slug}.json").read_text(encoding="utf-8"))
        p = paket.fran_val(b["namn"], bransch, sjostaden_stil(val), stil)
        p["exempel"] = True
        alla.append((b, p))
    # Kontroll: hur olika är exemplen inbördes?
    for b, p in alla:
        andra = [q for c, q in alla if q is not p]
        p["min_avstand"] = round(min(paket.avstand(p, q) for q in andra), 2)
    ordning = ["norrvik", "sjostaden", "ekbacka", "tornberg", "lindhem", "arcus", "vardtra", "kvarter", "stenhamra", "brofors"]
    alla.sort(key=lambda bp: ordning.index(bp[0]["slug"]) if bp[0]["slug"] in ordning else 99)
    for b, p in alla:
        if not p.get("fryst"):
            generera.Sajt(b, p, UT / b["slug"], delad=(ROT / "site/bildbank", "../../bildbank/")).bygg()
        reg.append(p)
        print(f'{b["kortnamn"]:10} {p["arketyp"]:13} {p["hero"]:10} {p["typsnitt"]["rubrik"]:18} {p["palett"]:14} {p["form"]["namn"]:13} minsta avstånd {p["min_avstand"]}')
    paket.REGISTER.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    (UT / "exempel.json").write_text(json.dumps([{"slug": b["slug"], "namn": b["namn"], "kortnamn": b["kortnamn"], "typ": b["typ"],
        "slogan": b["slogan"], "paket": p} for b, p in alla], ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()


def startsida():
    """site/index.html: översikt över de tio sajterna och länk till undersökningen."""
    from PIL import Image
    ex = json.loads((UT / "exempel.json").read_text(encoding="utf-8"))
    fv = ROT / "site/forhandsvisning"
    fv.mkdir(parents=True, exist_ok=True)
    kort = ""
    for e in ex:
        src = ROT / f'research/rapport/exempel/exempel-{e["slug"]}-index-dator.jpg'
        if src.exists():
            im = Image.open(src).convert("RGB")
            im = im.crop((0, 0, im.width, min(im.height, 1800)))
            im.thumbnail((720, 2000))
            im.save(fv / f'{e["slug"]}.jpg', quality=78, optimize=True)
        p, f = e["paket"], e["paket"]["farger"]
        sw = "".join(f'<i style="background:{c}"></i>' for c in (f["primar"], f["accent"], f["mork"], f["yta"]))
        kort += f'''<li><a href="exempel/{e["slug"]}/index.html"><div class="bild"><img src="forhandsvisning/{e["slug"]}.jpg" alt="Förhandsvisning av {generera.E(e["namn"])}" loading="lazy"></div>
<div class="txt"><span class="ark">{generera.E(p["arketyp"].capitalize())}</span><h2>{generera.E(e["kortnamn"])}</h2><p>{generera.E(e["typ"])}</p>
<p class="meta"><span class="sw">{sw}</span>{generera.E(p["typsnitt"]["rubrik"])} · {generera.E(p["hero"])} · {generera.E(p["form"]["namn"])}</p></div></a></li>'''
    html_ = f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Koncernsajter – 10 exempel och undersökning</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@600;700&display=swap">
<style>
*{{box-sizing:border-box}}body{{margin:0;background:#f4f4f2;color:#16181b;font:400 17px/1.6 Inter,system-ui,sans-serif}}
.wrap{{max-width:1320px;margin:0 auto;padding:0 20px}}@media(min-width:760px){{.wrap{{padding:0 40px}}}}
header{{padding:72px 0 40px}}h1{{font:700 clamp(40px,7vw,92px)/0.98 "Inter Tight",sans-serif;letter-spacing:-.04em;margin:0;max-width:12em}}
.ingress{{font-size:clamp(18px,1.6vw,22px);max-width:40em;margin:24px 0 0;color:#3b3f45}}
.knapp{{display:inline-flex;align-items:center;gap:10px;margin-top:28px;padding:14px 24px;border-radius:999px;background:#16181b;color:#fff;text-decoration:none;font-weight:600}}
.knapp:hover{{background:#000}}
ul{{list-style:none;margin:0;padding:0 0 80px;display:grid;gap:28px}}@media(min-width:700px){{ul{{grid-template-columns:repeat(2,1fr)}}}}@media(min-width:1100px){{ul{{grid-template-columns:repeat(3,1fr)}}}}
li a{{display:block;height:100%;background:#fff;border-radius:6px;overflow:hidden;text-decoration:none;color:inherit;box-shadow:0 1px 2px rgba(0,0,0,.05);transition:transform .25s,box-shadow .25s}}
li a:hover{{transform:translateY(-4px);box-shadow:0 18px 40px rgba(0,0,0,.1)}}
.bild{{aspect-ratio:4/3;overflow:hidden;border-bottom:1px solid #e6e6e3}}.bild img{{width:100%;display:block}}
.txt{{padding:20px 22px 24px}}.ark{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:600;color:#6a6f76}}
h2{{font:700 26px/1.1 "Inter Tight",sans-serif;letter-spacing:-.02em;margin:6px 0 4px}}.txt p{{margin:0;color:#4b5057}}
.meta{{margin-top:12px!important;font-size:14px}}.sw{{display:inline-flex;gap:3px;margin-right:10px;vertical-align:-3px}}.sw i{{display:block;width:16px;height:16px;border-radius:3px;border:1px solid rgba(0,0,0,.08)}}
footer{{padding:0 0 40px;color:#6a6f76;font-size:14px}}
</style></head><body>
<header class="wrap"><h1>Tio koncernsajter – ingen lik den andra</h1>
<p class="ingress">Byggda på en undersökning av 100 svenska bygg- och fastighetskoncerners hemsidor. Varje sajt bygger på en arketyp från undersökningen och har ett eget grafiskt paket. Alla tio koncerner är fiktiva.</p>
<a class="knapp" href="rapport/Koncernkansla-undersokning.pdf">Läs undersökningen (PDF) →</a></header>
<main class="wrap"><ul>{kort}</ul></main>
<footer class="wrap">Bilderna på sajterna är stockfoton från Pexels.</footer>
{generera.ELEVATE_CREDIT}</body></html>'''
    (ROT / "site/index.html").write_text(html_, encoding="utf-8")
    rap = ROT / "research/rapport/Koncernkansla-undersokning.pdf"
    if rap.exists():
        (ROT / "site/rapport").mkdir(exist_ok=True)
        import shutil
        shutil.copy(rap, ROT / "site/rapport" / rap.name)
    (ROT / "site/.nojekyll").write_text("", encoding="utf-8")


if __name__ == "__main__":
    startsida()
