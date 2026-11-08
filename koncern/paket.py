"""Skapar grafiska paket för koncernhemsidor – olika för varje sajt.

Ett paket är en kombination av val längs ett antal axlar (typsnitt, färg, rundning, header, hero, kort, knappar,
rytm, signatur, logga). Axlarna och alternativen kommer från undersökningen av 100 svenska bygg- och
fastighetskoncerner (research/). Motorn slumpar fram hundratals kandidater, mäter hur lika de är alla paket som
redan använts (koncern/register.json) och väljer den som skiljer sig mest – så blir ingen sajt lik en annan.

Kör:
  python3 koncern/paket.py ny "Företagsnamn" [--bransch bygg|fastighet|bostad|infra|installation|konsult|tra]
                                          [--farg "#hex"] [--stil <arketyp>] [--ut paket.json] [--registrera]
  python3 koncern/paket.py lista            # visar registret
  python3 koncern/paket.py arketyper        # visar arketyperna från undersökningen
"""
import argparse
import colorsys
import hashlib
import json
import pathlib
import random
import sys

ROT = pathlib.Path(__file__).resolve().parent
REGISTER = ROT / "register.json"

# --- Typsnittspar (alla från Google Fonts så att sajterna fungerar utan licenser) -------------------------------------
# kategori följer undersökningen: geometrisk, grotesk, humanistisk, serif, smal (condensed)
TYPSNITT = [
    dict(id="manrope-inter", rubrik="Manrope", text="Inter", kat="geometrisk", vikt=600, sp="-0.035em"),
    dict(id="plusjakarta", rubrik="Plus Jakarta Sans", text="Plus Jakarta Sans", kat="geometrisk", vikt=700, sp="-0.03em"),
    dict(id="sora-inter", rubrik="Sora", text="Inter", kat="geometrisk", vikt=600, sp="-0.035em"),
    dict(id="outfit-dmsans", rubrik="Outfit", text="DM Sans", kat="geometrisk", vikt=500, sp="-0.02em"),
    dict(id="redhat", rubrik="Red Hat Display", text="Red Hat Text", kat="geometrisk", vikt=700, sp="-0.025em"),
    dict(id="figtree", rubrik="Figtree", text="Figtree", kat="geometrisk", vikt=700, sp="-0.03em"),
    dict(id="inter-tight", rubrik="Inter Tight", text="Inter", kat="grotesk", vikt=600, sp="-0.04em"),
    dict(id="instrument", rubrik="Instrument Sans", text="Instrument Sans", kat="grotesk", vikt=600, sp="-0.03em"),
    dict(id="archivo", rubrik="Archivo", text="Archivo", kat="grotesk", vikt=700, sp="-0.02em"),
    dict(id="ibm-plex", rubrik="IBM Plex Sans", text="IBM Plex Sans", kat="grotesk", vikt=600, sp="-0.02em"),
    dict(id="public-sans", rubrik="Public Sans", text="Public Sans", kat="grotesk", vikt=700, sp="-0.025em"),
    dict(id="source-sans", rubrik="Source Sans 3", text="Source Sans 3", kat="humanistisk", vikt=700, sp="-0.015em"),
    dict(id="mulish", rubrik="Mulish", text="Mulish", kat="humanistisk", vikt=800, sp="-0.02em"),
    dict(id="libre-franklin", rubrik="Libre Franklin", text="Libre Franklin", kat="humanistisk", vikt=700, sp="-0.02em"),
    dict(id="fraunces-inter", rubrik="Fraunces", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback="Georgia, serif"),
    dict(id="newsreader-inter", rubrik="Newsreader", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback="Georgia, serif"),
    dict(id="dmserif-dmsans", rubrik="DM Serif Display", text="DM Sans", kat="serif", vikt=400, sp="-0.01em", fallback="Georgia, serif", vikter="400"),
    dict(id="playfair-source", rubrik="Playfair Display", text="Source Sans 3", kat="serif", vikt=600, sp="-0.015em", fallback="Georgia, serif"),
    dict(id="plex-mono", rubrik="IBM Plex Mono", text="IBM Plex Sans", kat="mono", vikt=500, sp="-0.03em", fallback="ui-monospace, monospace"),
    dict(id="barlow-cond", rubrik="Barlow Condensed", text="Barlow", kat="smal", vikt=600, sp="0", versaler=True),
    dict(id="oswald-inter", rubrik="Oswald", text="Inter", kat="smal", vikt=500, sp="0.005em", versaler=True),
]

# --- Färgpaletter: primär (varumärke), accent, mörk ton och ytfärg ---------------------------------------------------
# Familjerna följer undersökningens fördelning (blått vanligast, sedan orange/terrakotta, monokromt, guld, grönt ...)
PALETTER = [
    dict(id="marin-grön", fam="blå", primar="#143275", accent="#3ece7b", mork="#0b1a3d", yta="#f2f4f7"),
    dict(id="koboltblå", fam="blå", primar="#0606cc", accent="#0606cc", mork="#05052e", yta="#f5f5f7"),
    dict(id="djupblå-sand", fam="blå", primar="#0f3557", accent="#d9a441", mork="#0a2238", yta="#f5f1ea"),
    dict(id="himmelsblå", fam="blå", primar="#0067b1", accent="#00a3e0", mork="#00243f", yta="#eef5fa"),
    dict(id="terrakotta", fam="orange/terrakotta", primar="#b4532a", accent="#e8a27c", mork="#2b1a14", yta="#f6efe8"),
    dict(id="signalorange", fam="orange/terrakotta", primar="#e85a1b", accent="#e85a1b", mork="#1c1c1c", yta="#f4f2ef"),
    dict(id="monokrom", fam="monokrom", primar="#111111", accent="#111111", mork="#111111", yta="#f2f2f0"),
    dict(id="grafit-gul", fam="gul/guld", primar="#1f2328", accent="#f5b400", mork="#16191d", yta="#f3f2ee"),
    dict(id="mässing", fam="gul/guld", primar="#8a6a2f", accent="#c9a45c", mork="#1d1a15", yta="#f4f0e6"),
    dict(id="skogsgrön", fam="grön", primar="#1f4d3a", accent="#9cc5a1", mork="#11291f", yta="#eef2ec"),
    dict(id="mossgrön", fam="grön", primar="#3d6b2e", accent="#c8d96f", mork="#1b2a16", yta="#f1f3e9"),
    dict(id="petrol", fam="turkos/petrol", primar="#00606b", accent="#5ec7c0", mork="#002b31", yta="#eaf3f2"),
    dict(id="vinröd", fam="rosa/vinröd", primar="#7a1f3d", accent="#e7b3c1", mork="#2a0f18", yta="#f6eff1"),
    dict(id="tegelröd", fam="röd", primar="#c8102e", accent="#c8102e", mork="#1a1a1a", yta="#f5f3f2"),
    dict(id="plommon", fam="lila", primar="#4b2a6b", accent="#b9a2e0", mork="#1e1030", yta="#f3f0f7"),
    dict(id="skiffer-koppar", fam="grå", primar="#2e3a46", accent="#c06d3b", mork="#1a222b", yta="#eff1f3"),
]

AXLAR = {
    # vikt = hur vanligt det var i undersökningen (styr slumpen, men avståndsmåttet styr mest)
    "hero": {"helskarm": 3, "ruta": 2, "split": 2, "statement": 2, "mosaik": 1, "centrerad": 1},
    "header": {"transparent": 3, "ljus": 3, "mork": 1, "topbar": 1},
    "meny": {"inline": 3, "burger": 2},
    "kort": {"platt": 3, "ram": 1, "skugga": 1, "overlay": 2, "lista": 1},
    "knappstil": {"fylld": 3, "kontur": 1, "pil": 1},
    "rytm": {"ljus": 2, "alternerande": 3, "morka-band": 2, "primar-band": 1},
    "signatur": {"nyckeltal-rad": 3, "stora-siffror": 2, "citat": 1},
    "sidhero": {"bild": 3, "ljus": 1},
    "form": {"kantig": 4, "piller-kantig": 4, "lätt": 2, "rundad": 1, "mjuk": 1},
    "sidfot": {"mork": 3, "primar": 2, "ljus": 1},
    "logga": {"ring": 1, "kvadrat": 1, "tak": 1, "bage": 1, "staplar": 1, "blad": 1, "romb": 1, "vag": 1, "punkt": 1, "ingen": 2},
}
# Rundning per formfamilj: knapp, kort, bild (px). Undersökningen: piller-knappar + kantiga bilder dominerar.
FORMER = {"kantig": (0, 0, 0), "piller-kantig": (999, 0, 0), "lätt": (4, 4, 4), "rundad": (10, 14, 12), "mjuk": (999, 24, 24)}

# Arketyper från undersökningen (research/rapport) – var och en en igenkännbar "koncernstil"
ARKETYPER = {
    "monument": dict(beskr="Helskärmsfilm/bild, jättelik rubrik, transparent header, piller-knappar, kantiga bilder (Skanska-typ)",
                     hero="helskarm", header="transparent", form="piller-kantig", kort="platt", rytm="alternerande", typkat=["geometrisk", "grotesk"]),
    "ramad": dict(beskr="Inramad hero-bild med överlappande vitt kort, lugn grotesk, mycket luft (NCC-typ)",
                  hero="ruta", header="ljus", form="kantig", kort="platt", rytm="ljus", typkat=["grotesk", "humanistisk"]),
    "redaktionell": dict(beskr="Stor serif-rubrik, typografisk hero, listor i stället för kort, varm ytfärg (tidskriftskänsla)",
                         hero="statement", header="ljus", form="kantig", kort="lista", rytm="ljus", typkat=["serif"]),
    "varm-bostad": dict(beskr="Delad hero med färgfält, rundade former, skuggade kort – konsumentnära bostadsutvecklare",
                        hero="split", header="ljus", form="mjuk", kort="skugga", rytm="alternerande", typkat=["geometrisk", "serif"]),
    "industriell": dict(beskr="Smal versal rubrik, mörka band, kantigt, gul/orange signal – infrastruktur och anläggning",
                        hero="helskarm", header="mork", form="kantig", kort="overlay", rytm="morka-band", typkat=["smal"]),
    "finans": dict(beskr="Investerarfokus: topprad med IR-länkar, aktieruta, ramade kort, sober blå/grå",
                   hero="ruta", header="topbar", form="lätt", kort="ram", rytm="alternerande", typkat=["grotesk", "humanistisk"]),
    "skandinavisk": dict(beskr="Mosaik av bilder, naturtoner, mjuka hörn och mycket vitt – trä och hållbarhet",
                         hero="mosaik", header="ljus", form="rundad", kort="platt", rytm="ljus", typkat=["geometrisk", "humanistisk"]),
    "urban": dict(beskr="Centrerad helskärm, stark enfärgad accent, overlay-kort – kommersiella fastigheter i storstad",
                  hero="centrerad", header="transparent", form="piller-kantig", kort="overlay", rytm="primar-band", typkat=["grotesk", "geometrisk"]),
    "kontrast": dict(beskr="Delad hero med mörkt fält, topprad, kantigt, en stark signalfärg i band – installation och service",
                     hero="split", header="topbar", form="kantig", kort="ram", rytm="primar-band", typkat=["grotesk"]),
    "teknisk": dict(beskr="Typografisk hero i monospace eller stram sans, rundade former, overlay-kort – konsult och teknik",
                    hero="statement", header="ljus", form="rundad", kort="overlay", rytm="alternerande", typkat=["mono", "grotesk"]),
}

BRANSCH_BILD = {"bygg": ["bygg", "people"], "fastighet": ["kontor", "stad"], "bostad": ["bostad", "tra"], "infra": ["infra", "anlaggning"],
                "installation": ["people", "kontor"], "konsult": ["people", "stad"], "tra": ["tra", "bostad"], "samhalle": ["kontor", "people"]}


# --- Färghjälp ------------------------------------------------------------------------------------------------------
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hexa(r, g, b):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(x * 255))) for x in (r, g, b))


def lum(h):
    def ch(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def kontrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def justera(h, dl=0.0, ds=0.0):
    r, g, b = rgb(h)
    hh, l, s = colorsys.rgb_to_hls(r, g, b)
    return hexa(*colorsys.hls_to_rgb(hh, max(0, min(1, l + dl)), max(0, min(1, s + ds))))


def ink_for(bg):
    return "#ffffff" if kontrast(bg, "#ffffff") >= kontrast(bg, "#111111") else "#111111"


def text_safe(c, bg="#ffffff"):
    """Mörka ner en färg tills den klarar 4.5:1 som text på bg."""
    while kontrast(c, bg) < 4.5:
        c = justera(c, -0.04)
    return c


def hue(h):
    r, g, b = rgb(h)
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


# --- Paket ----------------------------------------------------------------------------------------------------------
def bygg_farger(pal, sidfot, header, rng, varm):
    p, a, mork = pal["primar"], pal["accent"], pal["mork"]
    bg = "#ffffff" if not varm else rng.choice(["#ffffff", "#fcfbf8", "#faf8f4"])
    yta = pal["yta"]
    f = dict(primar=p, primar2=justera(p, -0.07), primar_ink=ink_for(p), primar_text=text_safe(p), accent=a,
             accent_mork=a if kontrast(a, mork) >= 3 else justera(a, 0.25), bg=bg, yta=yta, ink="#14171c" if not varm else "#1d1a17",
             mut="#5b616b" if not varm else "#5f5a52", linje="#e1e3e6" if not varm else "#e6e1d8", mork=mork, mork_ink="#ffffff",
             etikett=text_safe(p), siffra=text_safe(p))
    if sidfot == "mork":
        f.update(sidfot=mork, sidfot_ink="#ffffff")
    elif sidfot == "primar":
        f.update(sidfot=p, sidfot_ink=ink_for(p), sidfot_mut="rgba(255,255,255,.7)" if ink_for(p) == "#ffffff" else "rgba(0,0,0,.6)",
                 sidfot_linje="rgba(255,255,255,.18)" if ink_for(p) == "#ffffff" else "rgba(0,0,0,.14)")
    else:
        f.update(sidfot=yta, sidfot_ink="#14171c", sidfot_mut="#5b616b", sidfot_linje="#d9dbde")
    if header == "mork":
        f.update(header=mork, header_ink="#ffffff")
    elif header == "topbar":
        f.update(header="#ffffff", header_ink="#14171c")
    split = rng.choice([p, mork, yta])
    f.update(split=split, split_ink=ink_for(split))
    if f["split_ink"] == "#111111":
        f["split_ink"] = f["ink"]
    return f


def slumpa(rng, axel, tvang=None):
    if tvang:
        return tvang
    alt = AXLAR[axel]
    return rng.choices(list(alt), weights=list(alt.values()))[0]


def kandidat(rng, namn, bransch, farg=None, stil=None):
    # Varje paket utgår från en arketyp ur undersökningen, så att helheten hänger ihop. Arketypen låser de bärande
    # axlarna (hero, header, form, kort, rytm, typsnittskategori); resten varieras fritt.
    if not stil or stil not in ARKETYPER:
        stil = rng.choice(list(ARKETYPER))
    ark = ARKETYPER[stil]
    typkat = ark.get("typkat")
    typer = [t for t in TYPSNITT if not typkat or t["kat"] in typkat]
    ty = rng.choice(typer)
    if farg:
        pal = dict(id="egen", fam="egen", primar=farg, accent=farg, mork=justera(farg, -0.32, -0.1), yta=justera(farg, 0.46, -0.3))
        if lum(pal["yta"]) < 0.85:
            pal["yta"] = "#f3f4f5"
    else:
        pal = rng.choice(PALETTER)
    v = {ax: slumpa(rng, ax, ark.get(ax)) for ax in AXLAR}
    if ty["kat"] == "smal" and v["knappstil"] == "pil":
        v["knappstil"] = "fylld"
    if v["hero"] in ("statement", "mosaik", "ruta") and v["header"] == "transparent":
        v["header"] = "ljus"
    knapp, kort, bild = FORMER[v["form"]]
    varm = pal["fam"] in ("orange/terrakotta", "gul/guld", "grön", "rosa/vinröd") or ty["kat"] == "serif"
    farger = bygg_farger(pal, v["sidfot"], v["header"], rng, varm)
    lg_farg = pal["accent"] if v["header"] in ("mork",) or rng.random() < 0.4 else pal["primar"]
    paket = {
        "id": hashlib.md5(f"{namn}-{rng.random()}".encode()).hexdigest()[:10],
        "for": namn, "arketyp": stil or "fri", "fro": hashlib.md5(namn.encode()).hexdigest()[:8],
        "typsnitt": {"id": ty["id"], "kategori": ty["kat"], "rubrik": ty["rubrik"], "text": ty["text"], "rubrik_vikt": ty["vikt"],
                     "spatiering": ty["sp"], "versaler": ty.get("versaler", False), "skala": 0.86 if ty.get("versaler") else rng.choice([0.92, 1.0, 1.0, 1.08]),
                     "rubrik_fallback": ty.get("fallback", "system-ui, sans-serif"), "rubrik_vikter": ty.get("vikter", "400;500;600;700"),
                     "siffra_vikt": ty["vikt"], "logo_vikt": 800 if ty["kat"] != "serif" else 600, "logo_versaler": rng.random() < 0.45,
                     "logo_spatiering": "0.06em" if rng.random() < 0.5 else "-0.02em", "nav_versaler": ty.get("versaler", False) or rng.random() < 0.12,
                     "knapp_versaler": ty.get("versaler", False)},
        "palett": pal["id"], "farger": farger,
        "form": {"namn": v["form"], "knapp": knapp, "kort": kort, "bild": bild, "hero": bild * 2, "cta": kort},
        "hero": v["hero"], "header": v["header"], "meny": v["meny"], "kort": v["kort"], "knappstil": v["knappstil"], "rytm": v["rytm"],
        "signatur": v["signatur"], "sidhero": v["sidhero"], "sidfot_stor_logga": rng.random() < 0.35,
        "logga": {"form": v["logga"], "farg": lg_farg, "ink": "#ffffff" if lum(lg_farg) < 0.4 else "#111111"},
        "bildtyngd": BRANSCH_BILD.get(bransch, ["kontor", "bygg"]),
        "maxbredd": rng.choice([1240, 1320, 1400]), "header_hojd": rng.choice([76, 84, 92]),
    }
    return paket


def fran_val(namn, bransch, val, stil="fri"):
    """Bygger ett paket från uttryckliga val (används för de handplockade exemplen och när agenten vill styra)."""
    rng = random.Random(hashlib.md5(namn.encode()).hexdigest())
    p = kandidat(rng, namn, bransch, stil=stil if stil in ARKETYPER else None)
    ty = next(t for t in TYPSNITT if t["id"] == val["typsnitt"])
    pal = next(x for x in PALETTER if x["id"] == val["palett"])
    p["arketyp"] = stil
    p["typsnitt"].update(id=ty["id"], kategori=ty["kat"], rubrik=ty["rubrik"], text=ty["text"], rubrik_vikt=ty["vikt"], spatiering=ty["sp"],
                         versaler=ty.get("versaler", False), rubrik_fallback=ty.get("fallback", "system-ui, sans-serif"),
                         rubrik_vikter=ty.get("vikter", "400;500;600;700"), siffra_vikt=ty["vikt"], knapp_versaler=ty.get("versaler", False))
    if ty.get("versaler"):
        p["typsnitt"]["skala"] = 0.86
    for k in ("skala", "logo_versaler", "logo_spatiering", "nav_versaler"):
        if k in val:
            p["typsnitt"][k] = val[k]
    for ax in ("hero", "header", "meny", "kort", "knappstil", "rytm", "signatur", "sidhero"):
        if ax in val:
            p[ax] = val[ax]
    form = val.get("form", p["form"]["namn"])
    knapp, kort, bild = FORMER[form]
    p["form"] = {"namn": form, "knapp": knapp, "kort": kort, "bild": bild, "hero": bild * 2, "cta": kort}
    sidfot = val.get("sidfot", "mork")
    varm = pal["fam"] in ("orange/terrakotta", "gul/guld", "grön", "rosa/vinröd") or ty["kat"] == "serif"
    p["palett"] = pal["id"]
    p["farger"] = bygg_farger(pal, sidfot, p["header"], rng, varm)
    if "split" in val:
        s = {"primar": pal["primar"], "mork": pal["mork"], "yta": pal["yta"]}[val["split"]]
        p["farger"].update(split=s, split_ink=ink_for(s) if ink_for(s) == "#ffffff" else p["farger"]["ink"])
    lf = pal[val.get("logga_farg", "primar")]
    p["logga"] = {"form": val.get("logga", p["logga"]["form"]), "farg": lf, "ink": "#ffffff" if lum(lf) < 0.4 else "#111111"}
    for k in ("maxbredd", "header_hojd", "sidfot_stor_logga", "hero_tagg", "om_tagg", "hero_cta"):
        if k in val:
            p[k] = val[k]
    return p


# Avstånd: hur olika två paket är (0 = identiska). Vikter efter hur mycket axeln syns.
VIKTER = {"arketyp": 1.5, "hero": 3.0, "typsnitt": 2.5, "palett": 2.5, "form": 2.0, "kort": 1.5, "header": 1.2, "rytm": 1.2, "knappstil": 0.8,
          "signatur": 0.6, "sidfot": 0.6, "logga": 0.4, "meny": 0.4}


def avstand(a, b):
    d = 0.0
    d += VIKTER["arketyp"] * (a.get("arketyp") != b.get("arketyp"))
    d += VIKTER["hero"] * (a["hero"] != b["hero"])
    d += VIKTER["typsnitt"] * (0.5 * (a["typsnitt"]["id"] != b["typsnitt"]["id"]) + 0.5 * (a["typsnitt"]["kategori"] != b["typsnitt"]["kategori"]))
    hd = abs(hue(a["farger"]["primar"]) - hue(b["farger"]["primar"]))
    hd = min(hd, 360 - hd) / 180
    ld = abs(lum(a["farger"]["primar"]) - lum(b["farger"]["primar"]))
    d += VIKTER["palett"] * min(1, 0.6 * hd * 2 + 0.4 * ld * 3 + 0.3 * (a["palett"] != b["palett"]))
    d += VIKTER["form"] * (a["form"]["namn"] != b["form"]["namn"])
    for k in ("kort", "header", "rytm", "knappstil", "signatur", "meny"):
        d += VIKTER[k] * (a[k] != b[k])
    d += VIKTER["sidfot"] * (a["farger"]["sidfot"] != b["farger"]["sidfot"])
    d += VIKTER["logga"] * (a["logga"]["form"] != b["logga"]["form"])
    return d


def register():
    return json.loads(REGISTER.read_text(encoding="utf-8")) if REGISTER.exists() else []


def nytt(namn, bransch="bygg", farg=None, stil=None, antal=600):
    """Väljer den kandidat som ligger längst ifrån alla paket i registret (max-min-avstånd)."""
    rng = random.Random(hashlib.md5(namn.encode()).hexdigest())
    tidigare = register()
    best, best_d = None, -1
    for _ in range(antal):
        k = kandidat(rng, namn, bransch, farg, stil)
        d = min((avstand(k, t) for t in tidigare), default=99)
        d += rng.random() * 0.3  # lite slump bland nästan lika bra
        if d > best_d:
            best, best_d = k, d
    best["min_avstand"] = round(best_d, 2)
    return best


def registrera(p):
    reg = [r for r in register() if r["for"] != p["for"]]
    reg.append(p)
    REGISTER.write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kommando", choices=["ny", "lista", "arketyper"])
    ap.add_argument("namn", nargs="?")
    ap.add_argument("--bransch", default="bygg")
    ap.add_argument("--farg")
    ap.add_argument("--stil", choices=list(ARKETYPER))
    ap.add_argument("--ut")
    ap.add_argument("--registrera", action="store_true")
    a = ap.parse_args()
    if a.kommando == "arketyper":
        for k, v in ARKETYPER.items():
            print(f"{k:14} {v['beskr']}")
        return
    if a.kommando == "lista":
        for r in register():
            print(f'{r["for"]:32} {r["arketyp"]:13} {r["hero"]:10} {r["typsnitt"]["rubrik"]:18} {r["palett"]:14} {r["form"]["namn"]}')
        return
    if not a.namn:
        sys.exit("Ange företagsnamn")
    p = nytt(a.namn, a.bransch, a.farg, a.stil)
    txt = json.dumps(p, ensure_ascii=False, indent=1)
    if a.ut:
        pathlib.Path(a.ut).write_text(txt, encoding="utf-8")
    else:
        print(txt)
    if a.registrera:
        registrera(p)
    print(f'# {a.namn}: arketyp {p["arketyp"]}, hero {p["hero"]}, typsnitt {p["typsnitt"]["rubrik"]}/{p["typsnitt"]["text"]}, '
          f'palett {p["palett"]}, form {p["form"]["namn"]}, minsta avstånd till tidigare paket {p["min_avstand"]}', file=sys.stderr)


if __name__ == "__main__":
    main()
