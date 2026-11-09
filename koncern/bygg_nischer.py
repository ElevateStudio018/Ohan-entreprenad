"""Bygger alla nischsajter: grafiskt paket per sajt (längst ifrån alla andra) + sajten i site/sajter/<grupp>/<slug>/.

Kör:  python3 koncern/bygg_nischer.py                 # bygger allt (befintliga paket återanvänds)
      python3 koncern/bygg_nischer.py foto bygg       # bara vissa grupper
      python3 koncern/bygg_nischer.py --nya-paket foto  # gör om paketen för gruppen
      python3 koncern/bygg_nischer.py --galleri       # bara galleriet site/sajter/index.html
"""
import json
import pathlib
import sys

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT))
import generera  # noqa: E402
import paket  # noqa: E402

BRIEFS = ROT / "nischer"
UT = ROT.parent / "site" / "sajter"
DELAD = (ROT.parent / "site" / "bildbank", "../../../bildbank/")
NREG = BRIEFS / "register.json"

GRUPPER = {
    "bygg": ("Byggföretag", "Vanliga byggföretag med koncernkänsla", "bygg"),
    "foto": ("Bröllopsfotografer", "Fotografer och studios", "foto"),
    "mega": ("Megakoncerner", "Stora noterade koncerner", "mega"),
    "arborist": ("Arborister", "Trädvård, fällning och beskärning", "arborist"),
    "djur": ("Djurfrisörer & djurstylister", "Hundtrim, kattvård och hundskola", "djur"),
}
# Underskattade B2B-nischer: företag med god ekonomi, svaga hemsidor och få som ringer dem
NISCHER = {
    "hiss": ("Hissföretag", "Service, besiktning och modernisering av hissar", "hiss", ["hiss", "kontor", "stad"]),
    "brand": ("Brandskydd", "Brandlarm, sprinkler, SBA och brandskyddskontroll", "brand", ["brand", "kontor", "people"]),
    "ventilation": ("Ventilation & OVK", "Ventilation, OVK och injustering", "ventilation", ["ventilation", "interior", "kontor", "bygg"]),
    "tak": ("Takläggare & plåtslagare", "Takbyten, takomläggning och plåtarbeten", "tak", ["tak", "bostad", "hem"]),
    "sotare": ("Sotare & skorstensfejare", "Sotning, brandskyddskontroll och skorstensrenovering", "skorsten", ["skorsten", "hem", "tak"]),
    "lassmed": ("Låssmeder", "Lås, passersystem och säkerhet", "las", ["las", "kontor", "hem"]),
    "golv": ("Golvföretag", "Golvslipning, parkett och mattläggning", "golv", ["golv", "interior", "hem"]),
    "rivning": ("Rivning & sanering", "Rivning, håltagning och asbestsanering", "rivning", ["rivning", "mark", "bygg"]),
    "mark": ("Mark & anläggning", "Schakt, grund, dränering och markarbeten", "mark", ["mark", "anlaggning", "bygg", "infra"]),
    "solel": ("Solcellsföretag", "Solceller, batterier och laddboxar", "solel", ["solel", "hem", "tak"]),
    "vvs": ("VVS & relining", "Rörarbeten, relining och badrum", "vvs", ["vvs", "interior", "hem"]),
    "maleri": ("Måleri & fasad", "Fasadmålning, tapetsering och fönsterrenovering", "maleri", ["maleri", "bostad", "interior"]),
    "skadedjur": ("Skadedjursbekämpning", "Sanering och förebyggande skadedjurskontroll", "skadedjur", ["skadedjur", "hem", "industri"]),
    "stad": ("Städ & fönsterputs", "Kontorsstäd, trappstäd och fönsterputs", "stadning", ["stadning", "kontor", "interior"]),
    "maskin": ("Maskinuthyrning", "Uthyrning av maskiner, liftar och kranar", "maskin", ["maskin", "mark", "bygg"]),
    "begravning": ("Begravningsbyråer", "Begravning, minnesstunder och juridik", "begravning", ["begravning", "natur"]),
    "trafikskola": ("Trafikskolor", "Körkort för bil, MC och tung trafik", "korskola", ["korskola", "stad", "people"]),
    "batvarv": ("Båtvarv & marinor", "Vinterförvaring, service och båtplatser", "bat", ["bat", "natur"]),
    "smide": ("Smide & svets", "Smide, räcken, trappor och svetsarbeten", "svets", ["svets", "industri", "bygg"]),
    "glas": ("Glasmästerier", "Glas, fönster, speglar och glasfasader", "glas", ["glas", "kontor", "interior"]),
    "sten": ("Stenhuggerier", "Bänkskivor, gravstenar och natursten", "sten", ["sten", "interior", "natur"]),
    "hovslagare": ("Hovslagare & hästservice", "Hovvård, skoning och stallservice", "hast", ["hast", "natur"]),
}
BILDTYNGD = {"foto": ["brollop", "brudpar", "detalj", "fest"], "arborist": ["arborist", "trad", "ved", "tradgard"],
             "djur": ["hund", "trimning", "valp", "katt", "hundtraning"], "bygg": ["bygg", "people", "bostad", "interior", "hem"],
             "mega": ["kontor", "stad", "infra", "bygg", "people"]}


def grupper_alla():
    return list(GRUPPER) + list(NISCHER)


def gruppinfo(g):
    if g in GRUPPER:
        return GRUPPER[g][0], GRUPPER[g][1], GRUPPER[g][2]
    return NISCHER[g][0], NISCHER[g][1], "nisch"


def bildval(b, g):
    """Bildtyngd och reserv så att en fotografsajt aldrig får en byggkran."""
    if g in NISCHER:
        tyngd = NISCHER[g][3]
        roller = {r: NISCHER[g][2] for r in ("hb", "om", "sida_bolag", "sida_om", "sida_hb", "sida_faq", "sida_priser", "citat")}
        roller["panel"] = "people" if NISCHER[g][2] not in ("hast", "bat", "begravning") else NISCHER[g][2]
        roller["sida_karriar"] = roller["panel"]
        return tyngd, tyngd + ["people"], roller
    tyngd = BILDTYNGD[g]
    reserv = tyngd if g in ("foto", "arborist", "djur") else None
    return tyngd, reserv, {}


def register_alla():
    reg = paket.register()
    if NREG.exists():
        reg += json.loads(NREG.read_text(encoding="utf-8"))
    return reg


def bygg_grupp(g, nya_paket=False):
    filer = sorted((BRIEFS / g).glob("*.json"))
    if not filer:
        return []
    (BRIEFS / g / "paket").mkdir(exist_ok=True)
    nreg = json.loads(NREG.read_text(encoding="utf-8")) if NREG.exists() else []
    byggda = []
    for fil in filer:
        b = json.loads(fil.read_text(encoding="utf-8"))
        pfil = BRIEFS / g / "paket" / fil.name
        tyngd, reserv, roller = bildval(b, g)
        if roller:
            b["bild"] = {**roller, **b.get("bild", {})}
        if pfil.exists() and not nya_paket:
            p = json.loads(pfil.read_text(encoding="utf-8"))
        else:
            namn = f'{g}/{b["slug"]}'
            tidigare = [r for r in paket.register() if r.get("version") == 2] + [r for r in nreg if r["for"] != namn]
            p = paket.nytt(namn, "bygg", profil=b["profil"], nisch=b.get("nisch"), brief=b, tidigare=tidigare, antal=220)
            p["hero_tagg"] = b["affarsomraden"][0]["tagg"] if g not in BILDTYNGD or g in ("bygg", "mega") else tyngd[0]
            p["bildtyngd"] = tyngd
            if reserv:
                p["bildreserv"] = reserv
            pfil.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
            nreg = [r for r in nreg if r["for"] != namn] + [p]
            NREG.write_text(json.dumps(nreg, ensure_ascii=False), encoding="utf-8")
        ut = UT / g / b["slug"]
        generera.Sajt(b, p, ut, DELAD).bygg()
        byggda.append((g, b, p))
        print(f'  {g:12} {b["slug"]:24} hero {p["hero"]:9} {p["farger"]["primar"]}  {" ".join(p["ordning_lista"])}', flush=True)
    return byggda


# --- Differentiering: typsnitt, hero, rubrikstil, form och sektionsvarianter fördelas så jämnt som möjligt -------------
HEROTEXT = ["nere", "mitten", "uppe", "hoger", "jatte", "kort", "linje", "versal", "kursiv", "band", "stack", "kontur", "delad"]
RUBRIKSTIL = ["standard", "linje", "nummer", "pill", "stor", "understruken", "versal", "mitt", "kant"]
FORMER = {"kantig": (0, 0, 0), "piller-kantig": (999, 0, 0), "latt": (6, 6, 4), "rundad": (12, 14, 12), "mjuk": (999, 22, 20), "piller-rund": (999, 10, 10)}
HEROER = {"mega": ["helskarm", "band", "centrerad", "statement", "mosaik", "split", "kurs"],
          "standard": ["helskarm", "band", "centrerad", "statement", "mosaik", "split"]}
OVERLAY = {"helskarm", "band", "centrerad", "statement", "mosaik"}


def _minst(alt, raknare, glob, rng):
    alt = list(alt)
    rng.shuffle(alt)
    return min(alt, key=lambda x: (raknare[x], glob[x]))


def differentiera(nya=False, bara=None):
    """Går igenom alla paket grupp för grupp och ger varje sajt det typsnitt, den hero, rubrikstil, form och de
    sektionsvarianter som är minst använda i gruppen (och totalt). Resultatet sparas i paketen (nyckeln 'v7')."""
    import collections
    import random
    import typsnitt
    import varianter
    import preferenser
    alla_var = preferenser.godkanda(varianter.alla())
    glob = collections.defaultdict(collections.Counter)
    for g in grupper_alla():
        filer = sorted((BRIEFS / g).glob("*.json"))
        rak = collections.defaultdict(collections.Counter)
        nya_g = nya and (bara is None or g in bara)
        for fil in filer:
            pfil = BRIEFS / g / "paket" / fil.name
            if not pfil.exists():
                continue
            b = json.loads(fil.read_text(encoding="utf-8"))
            p = json.loads(pfil.read_text(encoding="utf-8"))
            rng = random.Random(f"v7-{g}-{b['slug']}")
            if p.get("v7") and not nya_g:
                for k in ("typ", "hero", "herotext", "rubrik", "form"):
                    rak[k][p["v7"][k]] += 1
                    glob[k][p["v7"][k]] += 1
                for sek, v in p["block"].items():
                    rak["b-" + sek][v] += 1
                    glob["b-" + sek][v] += 1
                continue
            profil = b["profil"]
            # typsnitt
            par = typsnitt.for_profil(profil, g)
            tyid = _minst([x["id"] for x in par], rak["typ"], glob["typ"], rng)
            ty = next(x for x in par if x["id"] == tyid)
            p["typsnitt"].update(id=ty["id"], kategori=ty["kat"], rubrik=ty["rubrik"], text=ty["text"], rubrik_vikt=ty["vikt"], spatiering=ty["sp"],
                                 versaler=ty.get("versaler", False), rubrik_fallback=ty.get("fallback", "system-ui, sans-serif"), rubrik_spec=ty["spec"],
                                 siffra_vikt=ty["vikt"], kursiv=ty.get("kursiv", False), knapp_versaler=ty.get("versaler", False),
                                 skala=0.9 if ty.get("versaler") else rng.choice([0.94, 1.0, 1.06]), logo_font="rubrik",
                                 logo_versaler=ty.get("versaler", False) or rng.random() < 0.5, logo_vikt=ty["vikt"] if ty["kat"] in ("serif", "smal", "tung") else 800,
                                 nav_versaler=rng.random() < 0.3, logo_spatiering=rng.choice(["-0.02em", "0.02em", "0.08em"]))
            # hero och herotext
            heroer = preferenser.heroer(profil)
            p["hero"] = _minst(heroer, rak["hero"], glob["hero"], rng)
            ht_alt = [h for h in preferenser.herotext() if h != "kursiv" or ty.get("kursiv")]
            if ty.get("versaler"):
                ht_alt = [h for h in ht_alt if h not in ("versal", "kursiv")]
            p["herotext"] = _minst(ht_alt, rak["herotext"], glob["herotext"], rng) if p["hero"] in OVERLAY else "standard"
            p["header"] = "transparent"
            p["rubrikstil"] = _minst(RUBRIKSTIL, rak["rubrik"], glob["rubrik"], rng)
            # form
            fnamn = _minst(list(FORMER), rak["form"], glob["form"], rng)
            k, c, i = FORMER[fnamn]
            p["form"] = {"namn": fnamn, "knapp": k, "kort": c, "bild": i, "hero": 0}
            # uppmaningssektion (cta) på ungefär hälften av sajterna, nära slutet
            if "cta" not in p["ordning_lista"] and rng.random() < 0.5:
                o = p["ordning_lista"]
                slut = len(o) - (1 if o and o[-1] in ("snabb", "boka") else 0)
                o.insert(max(1, slut - rng.choice([0, 1, 2])), "cta")
            # sektioner utan någon godkänd variant tas bort (användarens val)
            p["ordning_lista"] = [x for x in p["ordning_lista"] if x in alla_var or x in ("snabb",)]
            # sektionsvarianter
            for sek in p["ordning_lista"]:
                if sek in alla_var:
                    p["block"][sek] = _minst(alla_var[sek], rak["b-" + sek], glob["b-" + sek], rng)
            p["v7"] = {"typ": ty["id"], "hero": p["hero"], "herotext": p["herotext"], "rubrik": p["rubrikstil"], "form": fnamn}
            for kk in ("typ", "hero", "herotext", "rubrik", "form"):
                rak[kk][p["v7"][kk]] += 1
                glob[kk][p["v7"][kk]] += 1
            for sek in p["ordning_lista"]:
                if sek in p["block"]:
                    rak["b-" + sek][p["block"][sek]] += 1
                    glob["b-" + sek][p["block"][sek]] += 1
            pfil.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    return glob


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nya = "--nya-paket" in sys.argv
    if "--differentiera" in sys.argv or "--ny-stil" in sys.argv:
        g = differentiera("--ny-stil" in sys.argv, args or None)
        for k in ("typ", "hero", "herotext", "rubrik", "form"):
            print(k, len(g[k]), "olika")
    if "--galleri" not in sys.argv:
        for g in args or grupper_alla():
            bygg_grupp(g, nya)
    import galleri  # noqa: E402
    galleri.bygg()


if __name__ == "__main__":
    main()
