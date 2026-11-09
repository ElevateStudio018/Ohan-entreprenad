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


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nya = "--nya-paket" in sys.argv
    if "--galleri" not in sys.argv:
        for g in args or grupper_alla():
            bygg_grupp(g, nya)
    import galleri  # noqa: E402
    galleri.bygg()


if __name__ == "__main__":
    main()
