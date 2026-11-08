"""Skapar grafiska paket för koncernhemsidor – olika för varje sajt. Version 2.

Ett paket är en kombination av val längs ett antal axlar: typsnitt, palett, rundning, hero, header, vägvalsrutor,
färgpaneler, berättelsekort, knappar, projektvisning, nyheter, rytm (sektionsbakgrunder), sektionsordning och logga.
Axlarna kommer från undersökningen av 100 svenska bygg- och fastighetskoncerner (research/) och från genomgången av
hela sidorna hos de bästa (Granitor, Skanska, Hemsö, Castellum, Wallenstam).

Motorn utgår alltid från en arketyp (så att helheten hänger ihop), slumpar fram hundratals kandidater, mäter hur lika
de är alla paket som redan använts (koncern/register.json) och väljer den som skiljer sig mest.

Kör:
  python3 koncern/paket.py ny "Företagsnamn" [--bransch bygg|fastighet|bostad|infra|installation|konsult|tra|samhalle]
                                          [--farg "#hex"] [--stil <arketyp>] [--ut paket.json] [--registrera]
  python3 koncern/paket.py lista            # visar registret
  python3 koncern/paket.py arketyper        # visar arketyperna
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

# --- Typsnittspar (Google Fonts, så att sajterna fungerar utan licenser) ----------------------------------------------
TYPSNITT = [
    dict(id="manrope-inter", rubrik="Manrope", text="Inter", kat="geometrisk", vikt=600, sp="-0.03em"),
    dict(id="plusjakarta", rubrik="Plus Jakarta Sans", text="Plus Jakarta Sans", kat="geometrisk", vikt=600, sp="-0.025em"),
    dict(id="sora-inter", rubrik="Sora", text="Inter", kat="geometrisk", vikt=500, sp="-0.03em"),
    dict(id="outfit-dmsans", rubrik="Outfit", text="DM Sans", kat="geometrisk", vikt=500, sp="-0.015em"),
    dict(id="redhat", rubrik="Red Hat Display", text="Red Hat Text", kat="geometrisk", vikt=600, sp="-0.02em"),
    dict(id="figtree", rubrik="Figtree", text="Figtree", kat="geometrisk", vikt=600, sp="-0.025em"),
    dict(id="urbanist", rubrik="Urbanist", text="Urbanist", kat="geometrisk", vikt=600, sp="-0.02em"),
    dict(id="inter-tight", rubrik="Inter Tight", text="Inter", kat="grotesk", vikt=500, sp="-0.035em"),
    dict(id="instrument", rubrik="Instrument Sans", text="Instrument Sans", kat="grotesk", vikt=600, sp="-0.025em"),
    dict(id="archivo", rubrik="Archivo", text="Archivo", kat="grotesk", vikt=600, sp="-0.02em"),
    dict(id="ibm-plex", rubrik="IBM Plex Sans", text="IBM Plex Sans", kat="grotesk", vikt=500, sp="-0.02em"),
    dict(id="public-sans", rubrik="Public Sans", text="Public Sans", kat="grotesk", vikt=600, sp="-0.02em"),
    dict(id="hanken", rubrik="Hanken Grotesk", text="Hanken Grotesk", kat="grotesk", vikt=600, sp="-0.025em"),
    dict(id="source-sans", rubrik="Source Sans 3", text="Source Sans 3", kat="humanistisk", vikt=600, sp="-0.01em"),
    dict(id="mulish", rubrik="Mulish", text="Mulish", kat="humanistisk", vikt=700, sp="-0.02em"),
    dict(id="libre-franklin", rubrik="Libre Franklin", text="Libre Franklin", kat="humanistisk", vikt=600, sp="-0.02em"),
    dict(id="fraunces-inter", rubrik="Fraunces", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback="Georgia, serif"),
    dict(id="newsreader-inter", rubrik="Newsreader", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback="Georgia, serif"),
    dict(id="dmserif-dmsans", rubrik="DM Serif Display", text="DM Sans", kat="serif", vikt=400, sp="-0.01em", fallback="Georgia, serif", vikter="400"),
    dict(id="playfair-source", rubrik="Playfair Display", text="Source Sans 3", kat="serif", vikt=600, sp="-0.015em", fallback="Georgia, serif"),
    dict(id="plex-mono", rubrik="IBM Plex Mono", text="IBM Plex Sans", kat="mono", vikt=500, sp="-0.03em", fallback="ui-monospace, monospace"),
    dict(id="barlow-cond", rubrik="Barlow Condensed", text="Barlow", kat="smal", vikt=600, sp="0", versaler=True),
    dict(id="oswald-inter", rubrik="Oswald", text="Inter", kat="smal", vikt=500, sp="0.005em", versaler=True),
]

# --- Paletter: djup varumärkesfärg, accent, mörk ton och två ljusa toner till sektionsbakgrunder ---------------------
PALETTER = [
    dict(id="vinröd-lax", fam="rosa/vinröd", primar="#6b2d36", accent="#d4826f", mork="#3d1a20", ton="#f5ece8", ton2="#ecd8d1"),
    dict(id="marin-mint", fam="blå", primar="#12305f", accent="#5fd3a0", mork="#0b1d3a", ton="#ebf1f8", ton2="#d9f2e6"),
    dict(id="kobolt-is", fam="blå", primar="#1c3fd1", accent="#7fd6ff", mork="#0b1b5c", ton="#eef2fd", ton2="#dce5ff"),
    dict(id="havsblå-orange", fam="blå", primar="#0b4a7a", accent="#ff7a3d", mork="#072b47", ton="#ecf3f9", ton2="#ffe4d6"),
    dict(id="stål-himmel", fam="blå", primar="#2b3a4a", accent="#6fa8dc", mork="#18222c", ton="#eef2f5", ton2="#dbe8f4"),
    dict(id="skog-salvia", fam="grön", primar="#1f4d3a", accent="#b9d5a4", mork="#10291f", ton="#eef3ec", ton2="#dde9d6"),
    dict(id="oliv-guld", fam="grön", primar="#4b5a2a", accent="#d8b44a", mork="#262e15", ton="#f2f3ea", ton2="#efe5c3"),
    dict(id="petrol-sand", fam="turkos/petrol", primar="#0e5560", accent="#e3b26b", mork="#062e34", ton="#edf4f3", ton2="#f4e7d2"),
    dict(id="djupgrön-koppar", fam="turkos/petrol", primar="#13403a", accent="#d07a43", mork="#0a2622", ton="#eef4f1", ton2="#f3dccb"),
    dict(id="terrakotta-kräm", fam="orange/terrakotta", primar="#a9452b", accent="#f0b38f", mork="#2e1a14", ton="#f8efe7", ton2="#f1dccb"),
    dict(id="grafit-gul", fam="gul/guld", primar="#1f2328", accent="#f5b400", mork="#121417", ton="#f3f1ec", ton2="#fbecc0"),
    dict(id="plommon-rosa", fam="lila", primar="#4a2560", accent="#e7a3c2", mork="#22102e", ton="#f4eef7", ton2="#f6dde9"),
    dict(id="tegel-grå", fam="röd", primar="#b3261e", accent="#f2c2b8", mork="#1d1d1f", ton="#f5f3f2", ton2="#ece8e6"),
    dict(id="svart-lime", fam="monokrom", primar="#111111", accent="#c6f05c", mork="#0a0a0a", ton="#f2f2ef", ton2="#e9f6cc"),
]

AXLAR = {
    # vikt = hur vanligt greppet var bland de bästa sajterna (styr slumpen; avståndsmåttet styr mest)
    "hero": {"band": 3, "helskarm": 3, "split": 2, "statement": 2, "mosaik": 1, "centrerad": 2, "sok": 1, "kurs": 1},
    "header": {"ljus": 3, "mork": 1, "transparent": 2, "centrerad": 1, "pill": 1},
    "vagval": {"rutor": 3, "rader": 2, "chips": 1, "nummer": 1, "cirklar": 1, "bildrutor": 1, "lankar": 1, "register": 1, "expertis": 1},
    "bolagsblock": {"kort": 3, "flikar": 2, "lista": 2, "tabell": 1, "rund": 1},
    "siffrblock": {"rad": 3, "jatte": 2, "band": 1, "dashboard": 1},
    "motiv": {"inget": 3, "diagonal": 1, "kurva": 1, "mjuk": 1, "linjer": 1, "rutnat": 1},
    "meny": {"inline": 3, "burger": 1},
    "ruta": {"solid": 3, "mork": 2, "kontur": 1, "vanster": 2},
    "panel": {"primar": 3, "mork": 2, "ton": 2},
    "kort": {"overlay": 3, "under": 2},
    "knappstil": {"fylld": 4, "kontur": 1},
    "projekt": {"karusell": 3, "rutnat": 2},
    "nyheter": {"lista": 3, "kolumner": 2},
    "rytm": {"ton": 3, "mork": 2, "farg": 2, "ljus": 2},
    "ordning": {"a": 3, "b": 2, "c": 2},
    "sidhero": {"bild": 3, "ton": 1},
    "form": {"kantig": 3, "piller-kantig": 3, "lätt": 3, "rundad": 2, "mjuk": 1},
    "sidfot": {"primar": 3, "mork": 2},
    "logga": {"ingen": 4, "ring": 1, "kvadrat": 1, "tak": 1, "bage": 1, "staplar": 1, "blad": 1, "romb": 1, "punkt": 1, "streck": 1},
}
# Rundning per formfamilj: knapp, kort, bild (px)
FORMER = {"kantig": (2, 0, 0), "piller-kantig": (999, 0, 0), "lätt": (6, 6, 4), "rundad": (10, 14, 12), "mjuk": (999, 22, 20)}

ARKETYPER = {
    "monument": dict(beskr="Helskärmsbildspel, jättelik rubrik, transparent header, pillerknappar, kantiga bilder (Skanska-typ)",
                     hero="helskarm", header="transparent", form="piller-kantig", kort="overlay", typkat=["geometrisk", "grotesk"]),
    "koncernband": dict(beskr="Inramad hero med färgband i varumärkesfärgen, färgade vägvalsrutor, helfärgad sidfot (Granitor-typ)",
                        hero="band", header="ljus", form="lätt", ruta="solid", panel="primar", sidfot="primar", typkat=["geometrisk", "grotesk"]),
    "ramad": dict(beskr="Lugn delad hero, ramade kort, mycket luft och tonade ytor (NCC/Tyréns-typ)",
                  hero="split", header="ljus", form="kantig", ruta="kontur", kort="under", typkat=["grotesk", "humanistisk"]),
    "redaktionell": dict(beskr="Stor serif-rubrik som hero, nyheter i kolumner, varma toner (Vasakronan-typ)",
                         hero="statement", header="ljus", form="kantig", nyheter="kolumner", typkat=["serif"]),
    "varm-bostad": dict(beskr="Delad hero med färgfält, mjuka former, tonade ytor – konsumentnära bostadsutvecklare",
                        hero="split", header="ljus", form="mjuk", ruta="vanster", typkat=["geometrisk", "serif"]),
    "industriell": dict(beskr="Smala versaler, mörka band, kantigt, signalfärg – infrastruktur och anläggning",
                        hero="helskarm", header="mork", form="kantig", ruta="mork", rytm="mork", typkat=["smal"]),
    "finans": dict(beskr="Investeraren tidigt: nyckeltal och bolag först, kursband, sober palett",
                   hero="band", header="ljus", form="lätt", ordning="b", typkat=["grotesk", "humanistisk"]),
    "skandinavisk": dict(beskr="Mosaik av bilder, naturtoner, rundade hörn och mycket luft – trä och hållbarhet",
                         hero="mosaik", header="ljus", form="rundad", rytm="ljus", typkat=["geometrisk", "humanistisk"]),
    "urban": dict(beskr="Centrerat bildspel, stark färg i band, berättelser först – kommersiella fastigheter i storstad",
                  hero="centrerad", header="transparent", form="piller-kantig", rytm="farg", ordning="c", typkat=["grotesk", "geometrisk"]),
    "teknisk": dict(beskr="Typografisk hero i monospace eller stram sans, rundade former – konsult och teknik",
                    hero="statement", header="ljus", form="rundad", ruta="vanster", typkat=["mono", "grotesk"]),
}

BRANSCH_BILD = {"bygg": ["bygg", "people"], "fastighet": ["kontor", "stad"], "bostad": ["bostad", "hem"], "infra": ["infra", "anlaggning"],
                "installation": ["el", "industri", "people"], "konsult": ["people", "stad"], "tra": ["tra", "natur"], "samhalle": ["people", "kontor"]}


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


def blanda(a, b, t):
    ra, rb = rgb(a), rgb(b)
    return hexa(*(x + (y - x) * t for x, y in zip(ra, rb)))


def ink_for(bg):
    return "#ffffff" if kontrast(bg, "#ffffff") >= kontrast(bg, "#14171b") else "#14171b"


def text_safe(c, bg="#ffffff"):
    while kontrast(c, bg) < 4.5:
        c = justera(c, -0.04)
    return c


def hue(h):
    r, g, b = rgb(h)
    return colorsys.rgb_to_hls(r, g, b)[0] * 360


# --- Färgsättning ---------------------------------------------------------------------------------------------------
def bygg_farger(pal, v, rng):
    p, a, mork, ton, ton2 = pal["primar"], pal["accent"], pal["mork"], pal["ton"], pal["ton2"]
    varm = pal["fam"] in ("orange/terrakotta", "gul/guld", "grön", "rosa/vinröd")
    ink = "#1b1a18" if varm else "#14171b"
    f = dict(primar=p, primar2=justera(p, -0.06), primar_ink=ink_for(p), primar_text=text_safe(p), accent=a, accent_ink=ink_for(a),
             ton=ton, ton2=ton2, bg="#ffffff", yta=blanda(ton, "#ffffff", 0.35), ink=ink, rubrik=ink if v["typkat"] != "serif" else blanda(ink, p, 0.25),
             mut="#5d6168" if not varm else "#615c55", linje="#e3e4e6" if not varm else "#e7e2dc", mork=mork, mork_ink="#ffffff",
             etikett=text_safe(p), siffra=text_safe(p))
    # Knappar: primärfärgen, eller accenten när den bär (som Granitors laxrosa)
    if v.get("knapp_accent"):
        f.update(knapp=a, knapp2=justera(a, -0.06), knapp_ink=ink_for(a))
    # Vägvalsrutor
    if v["ruta"] == "mork":
        f.update(ruta=mork, ruta_ink="#ffffff", ruta_hover=justera(mork, 0.06))
    else:
        f.update(ruta=p, ruta_ink=f["primar_ink"], ruta_hover=blanda(p, a, 0.35) if kontrast(blanda(p, a, 0.35), f["primar_ink"]) >= 3 else justera(p, 0.08))
    # Panel
    f.update({"primar": dict(panel=p, panel_ink=f["primar_ink"]), "mork": dict(panel=mork, panel_ink="#ffffff"),
              "ton": dict(panel=ton, panel_ink=ink)}[v["panel"]])
    # Topprad, header, meny
    f.update(topp=ton if v["header"] != "mork" else mork, topp_ink=ink if v["header"] != "mork" else "#ffffff")
    if v["header"] == "mork":
        f.update(head=mork, head_ink="#ffffff", head_fast=mork, head_fast_ink="#ffffff")
    else:
        f.update(head="#ffffff", head_ink=ink, head_fast="#ffffff", head_fast_ink=ink)
    f.update(meny=p if kontrast(p, "#ffffff") > 4 else mork, meny_ink="#ffffff")
    # Sidfot: helfärgad
    fot = p if v["sidfot"] == "primar" else mork
    f.update(sidfot=fot, sidfot_ink=ink_for(fot), sidfot_knapp=a if kontrast(a, fot) >= 2 else "#ffffff",
             sidfot_knapp_ink=ink_for(a if kontrast(a, fot) >= 2 else "#ffffff"),
             sidfot_linje="rgba(255,255,255,.18)" if ink_for(fot) == "#ffffff" else "rgba(0,0,0,.14)")
    # Hero-färger
    split = rng.choice([p, mork, ton])
    f.update(split=split, split_ink=ink_for(split) if ink_for(split) == "#ffffff" else ink, statement=rng.choice(["#ffffff", ton]),
             band=blanda(p, "#ffffff", 0.35), band2=a)
    return f


def slumpa(rng, axel, tvang=None):
    if tvang:
        return tvang
    alt = AXLAR[axel]
    return rng.choices(list(alt), weights=list(alt.values()))[0]


def kandidat(rng, namn, bransch, farg=None, stil=None):
    if not stil or stil not in ARKETYPER:
        stil = rng.choice(list(ARKETYPER))
    ark = ARKETYPER[stil]
    typer = [t for t in TYPSNITT if t["kat"] in ark["typkat"]]
    ty = rng.choice(typer)
    if farg:
        pal = dict(id="egen", fam="egen", primar=farg, accent=blanda(farg, "#ffffff", 0.45), mork=justera(farg, -0.25, -0.1),
                   ton=blanda(farg, "#ffffff", 0.9), ton2=blanda(farg, "#ffffff", 0.78))
    else:
        pal = rng.choice(PALETTER)
    v = {ax: slumpa(rng, ax, ark.get(ax)) for ax in AXLAR}
    if v["header"] == "transparent" and v["hero"] not in ("helskarm", "centrerad", "kurs"):
        v["header"] = "ljus"
    if v["hero"] == "kurs" and bransch not in ("fastighet", "samhalle"):
        v["hero"] = "helskarm"
    if v["hero"] == "sok" and bransch not in ("bostad", "fastighet"):
        v["hero"] = "split"
    extra = rng.sample(["process", "citat"], rng.choice([0, 1, 1, 2]))
    if bransch == "bostad" and rng.random() < 0.5:
        extra.append("service")
    bas = ["vagval", "berattelser", "panel", "bolag", "siffror", "projekt", "hb", "ir", "nyheter", "snabb"]
    mitt = bas[1:-1] + [e for e in extra if e != "service"]
    rng.shuffle(mitt)
    ordning_lista = (["service"] if "service" in extra else []) + ["vagval"] + mitt + ["snabb"] if rng.random() < 0.6 else (["service"] if "service" in extra else []) + mitt[:2] + ["vagval"] + mitt[2:] + ["snabb"]
    v["typkat"] = ty["kat"]
    v["knapp_accent"] = stil == "koncernband" or rng.random() < 0.25
    knapp, kort, bild = FORMER[v["form"]]
    farger = bygg_farger(pal, v, rng)
    lg_farg = pal["primar"] if v["header"] != "mork" else pal["accent"]
    return {
        "version": 2, "id": hashlib.md5(f"{namn}-{rng.random()}".encode()).hexdigest()[:10], "for": namn, "arketyp": stil,
        "fro": hashlib.md5(namn.encode()).hexdigest()[:8],
        "typsnitt": {"id": ty["id"], "kategori": ty["kat"], "rubrik": ty["rubrik"], "text": ty["text"], "rubrik_vikt": ty["vikt"],
                     "spatiering": ty["sp"], "versaler": ty.get("versaler", False),
                     "skala": 0.88 if ty.get("versaler") else rng.choice([0.94, 1.0, 1.0, 1.06]),
                     "rubrik_fallback": ty.get("fallback", "system-ui, sans-serif"), "rubrik_vikter": ty.get("vikter", "400;500;600;700"),
                     "siffra_vikt": ty["vikt"], "logo_vikt": 800 if ty["kat"] not in ("serif", "mono") else 600,
                     "logo_versaler": ty.get("versaler", False) or rng.random() < 0.35, "logo_spatiering": rng.choice(["-0.03em", "-0.01em", "0.06em"]),
                     "nav_versaler": ty.get("versaler", False) or rng.random() < 0.5, "knapp_versaler": ty.get("versaler", False),
                     "logo_font": rng.choice(["rubrik", "rubrik", "text"])},
        "palett": pal["id"], "farger": farger,
        "form": {"namn": v["form"], "knapp": knapp, "kort": kort, "bild": bild, "hero": min(bild, 16)},
        **{ax: v[ax] for ax in ("hero", "header", "meny", "ruta", "panel", "kort", "knappstil", "projekt", "nyheter", "rytm", "ordning", "sidhero", "motiv")},
        "block": {"vagval": v["vagval"], "bolag": v["bolagsblock"], "siffror": v["siffrblock"], "nyheter": rng.choice(["lista", "lista", "tidning"])},
        "ordning_lista": ordning_lista,
        "panel_omvand": rng.random() < 0.5, "sidfot": v["sidfot"], "fot": rng.choice(["standard", "standard", "cta", "centrerad"]), "sidfot_stor_logga": rng.random() < 0.3,
        "logga": {"form": v["logga"], "farg": lg_farg, "ink": "#ffffff" if lum(lg_farg) < 0.4 else "#14171b",
                  "gemener": rng.random() < 0.35, "tagline": True},
        "bildtyngd": BRANSCH_BILD.get(bransch, ["kontor", "bygg"]), "maxbredd": rng.choice([1320, 1360, 1400]), "header_hojd": rng.choice([76, 80, 88]),
    }


def fran_val(namn, bransch, val, stil="fri"):
    """Bygger ett paket från uttryckliga val (de handplockade exemplen, eller när agenten vill styra ett fält)."""
    rng = random.Random(hashlib.md5(namn.encode()).hexdigest())
    p = kandidat(rng, namn, bransch, stil=stil if stil in ARKETYPER else None)
    p["arketyp"] = stil
    if "typsnitt" in val:
        ty = next(t for t in TYPSNITT if t["id"] == val["typsnitt"])
        p["typsnitt"].update(id=ty["id"], kategori=ty["kat"], rubrik=ty["rubrik"], text=ty["text"], rubrik_vikt=ty["vikt"], spatiering=ty["sp"],
                             versaler=ty.get("versaler", False), rubrik_fallback=ty.get("fallback", "system-ui, sans-serif"),
                             rubrik_vikter=ty.get("vikter", "400;500;600;700"), siffra_vikt=ty["vikt"], knapp_versaler=ty.get("versaler", False),
                             logo_vikt=800 if ty["kat"] not in ("serif", "mono") else 600)
        if ty.get("versaler"):
            p["typsnitt"].update(skala=0.88, nav_versaler=True, logo_versaler=True)
    for k in ("skala", "logo_versaler", "logo_spatiering", "nav_versaler", "logo_font", "rubrik_vikt", "siffra_vikt"):
        if k in val:
            p["typsnitt"][k] = val[k]
    for ax in ("hero", "header", "meny", "ruta", "panel", "kort", "knappstil", "projekt", "nyheter", "rytm", "ordning", "sidhero", "sidfot",
               "motiv", "ordning_lista", "bakgrund", "fot"):
        if ax in val:
            p[ax] = val[ax]
    if "block" in val:
        p["block"] = val["block"]
    form = val.get("form", p["form"]["namn"])
    knapp, kort, bild = FORMER[form]
    p["form"] = {"namn": form, "knapp": knapp, "kort": kort, "bild": bild, "hero": min(bild, 16)}
    pal = next(x for x in PALETTER if x["id"] == val["palett"]) if "palett" in val else None
    if pal:
        v = {k: p[k] for k in ("ruta", "panel", "header", "sidfot")}
        v["typkat"] = p["typsnitt"]["kategori"]
        v["knapp_accent"] = val.get("knapp_accent", False)
        p["palett"] = pal["id"]
        p["farger"] = bygg_farger(pal, v, rng)
        if "split" in val:
            s = pal[val["split"]]
            p["farger"].update(split=s, split_ink=ink_for(s) if ink_for(s) == "#ffffff" else p["farger"]["ink"])
        if "statement" in val:
            p["farger"]["statement"] = pal[val["statement"]] if val["statement"] in pal else val["statement"]
        lf = pal[val.get("logga_farg", "primar")]
        p["logga"].update(farg=lf, ink="#ffffff" if lum(lf) < 0.4 else "#14171b")
    for k in ("form_logga", "gemener"):
        pass
    if "logga" in val:
        p["logga"]["form"] = val["logga"]
    if "gemener" in val:
        p["logga"]["gemener"] = val["gemener"]
    for k in ("maxbredd", "header_hojd", "sidfot_stor_logga", "hero_tagg", "panel_omvand", "bildtyngd"):
        if k in val:
            p[k] = val[k]
    return p


# --- Avstånd --------------------------------------------------------------------------------------------------------
VIKTER = {"arketyp": 1.5, "hero": 3.0, "typsnitt": 2.5, "palett": 3.0, "form": 1.5, "ruta": 1.2, "panel": 1.0, "kort": 0.8, "header": 1.0,
          "rytm": 1.2, "ordning": 1.0, "projekt": 0.6, "nyheter": 0.6, "knappstil": 0.5, "sidfot": 0.5, "logga": 0.4, "meny": 0.4}


def avstand(a, b):
    if a.get("version") != 2 or b.get("version") != 2:
        return 99
    d = VIKTER["arketyp"] * (a["arketyp"] != b["arketyp"]) + VIKTER["hero"] * (a["hero"] != b["hero"])
    d += VIKTER["typsnitt"] * (0.5 * (a["typsnitt"]["id"] != b["typsnitt"]["id"]) + 0.5 * (a["typsnitt"]["kategori"] != b["typsnitt"]["kategori"]))
    hd = abs(hue(a["farger"]["primar"]) - hue(b["farger"]["primar"]))
    hd = min(hd, 360 - hd) / 180
    ld = abs(lum(a["farger"]["primar"]) - lum(b["farger"]["primar"]))
    d += VIKTER["palett"] * min(1, 1.2 * hd + 1.2 * ld + 0.3 * (a["palett"] != b["palett"]))
    d += VIKTER["form"] * (a["form"]["namn"] != b["form"]["namn"])
    for k in ("ruta", "panel", "kort", "header", "rytm", "ordning", "projekt", "nyheter", "knappstil", "sidfot", "meny"):
        d += VIKTER[k] * (a.get(k) != b.get(k))
    d += VIKTER["logga"] * (a["logga"]["form"] != b["logga"]["form"])
    ab, bb = a.get("block", {}), b.get("block", {})
    d += 1.6 * (ab.get("vagval") != bb.get("vagval")) + 1.4 * (ab.get("bolag") != bb.get("bolag")) + 1.0 * (ab.get("siffror") != bb.get("siffror"))
    d += 1.2 * (a.get("motiv", "inget") != b.get("motiv", "inget"))
    return d


def register():
    return json.loads(REGISTER.read_text(encoding="utf-8")) if REGISTER.exists() else []


def nytt(namn, bransch="bygg", farg=None, stil=None, antal=600):
    """Väljer den kandidat som ligger längst ifrån alla paket i registret (max-min-avstånd)."""
    rng = random.Random(hashlib.md5(namn.encode()).hexdigest())
    tidigare = [r for r in register() if r["for"] != namn]
    best, best_d = None, -1
    for _ in range(antal):
        k = kandidat(rng, namn, bransch, farg, stil)
        d = min((avstand(k, t) for t in tidigare), default=99) + rng.random() * 0.3
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
            print(f'{r["for"]:32} {r["arketyp"]:13} {r["hero"]:10} {r["typsnitt"]["rubrik"]:18} {r["palett"]:16} {r["form"]["namn"]}')
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
