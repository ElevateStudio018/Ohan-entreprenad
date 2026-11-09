"""Kontrollerar briefs för nischsajterna. Kör: python3 koncern/validera.py <fil.json eller mapp> [...]"""
import json
import pathlib
import re
import sys

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT / "mall"))
from ikoner import NAMN as IKONER  # noqa: E402

TAGGAR = set("""bygg people kontor bostad hem stad natur tra infra interior industri el anlaggning brollop brudpar detalj fest kamera
arborist trad ved tradgard hund trimning valp katt hundtraning hiss brand ventilation tak skorsten las golv rivning mark solel vvs
maleri skadedjur stadning maskin begravning korskola bat svets glas sten hast""".split())
PROFILER = {"bygg", "foto", "mega", "arborist", "djur", "nisch"}
KLYSCHOR = ["brinner för", "lorem", "ipsum", "kvalitet i fokus", "din partner", "i framkant", "skräddarsydda lösningar", "vi sätter kunden i centrum"]


def fel_i(b, fil):
    f = []
    def krav(cond, msg):
        if not cond:
            f.append(msg)
    krav(b.get("profil") in PROFILER, "profil saknas/okänd")
    for k in ("namn", "kortnamn", "slug", "typ", "tagline", "slogan", "hero_rubrik", "hero_text", "intro_rubrik", "vagval_rubrik", "demo", "fot_cta"):
        krav(isinstance(b.get(k), str) and b[k].strip(), f"{k} saknas")
    if f:
        return f
    krav(re.fullmatch(r"[a-z0-9-]+", b["slug"]) is not None, "slug får bara ha a–z, 0–9, -")
    krav(b["slug"] == pathlib.Path(fil).stem, "slug ska vara samma som filnamnet")
    krav(len(b["hero_rubrik"]) <= 48, f"hero_rubrik för lång ({len(b['hero_rubrik'])} tecken)")
    krav(len(b["hero_text"]) <= 220, "hero_text för lång")
    krav(len(b["tagline"].split()) <= 4, "tagline max 4 ord")
    krav(len(b["kortnamn"]) <= 18, "kortnamn för långt (max 18 tecken)")
    krav(isinstance(b.get("om"), list) and len(b["om"]) == 2, "om ska vara 2 stycken")
    t = b.get("tjanster", [])
    krav(len(t) == 8, "tjanster ska vara exakt 8")
    for x in t:
        krav(x.get("ikon") in IKONER, f"okänd ikon: {x.get('ikon')}")
        krav(len(x.get("titel", "")) <= 26, f"tjänstetitel för lång: {x.get('titel')}")
    krav(len(b.get("affarsomraden", [])) == 4, "affarsomraden ska vara 4")
    krav(3 <= len(b.get("bolag", [])) <= 4, "bolag ska vara 3–4")
    krav(len(b.get("berattelser", [])) == 3, "berattelser ska vara 3")
    krav(len(b.get("nyckeltal", [])) == 4, "nyckeltal ska vara 4")
    for n in b.get("nyckeltal", []):
        krav(set(n) >= {"varde", "enhet", "etikett"}, "nyckeltal behöver varde, enhet, etikett")
        krav(len(str(n.get("varde", ""))) <= 9, f"nyckeltalets värde för långt: {n.get('varde')}")
    krav(len(b.get("projekt", [])) == 6, "projekt ska vara 6")
    for x in b.get("projekt", []):
        krav(set(x) >= {"namn", "ort", "typ", "ar", "text", "tagg"}, "projekt behöver namn, ort, typ, ar, text, tagg")
    krav(len(b.get("process", [])) == 4, "process ska vara 4 steg")
    hb = b.get("hallbarhet", {})
    krav(hb.get("rubrik") and hb.get("text") and len(hb.get("mal", [])) == 3, "hallbarhet behöver rubrik, text och 3 mål")
    k = b.get("karriar", {})
    krav(k.get("rubrik") and k.get("text") and isinstance(k.get("jobb"), list), "karriar behöver rubrik, text, jobb")
    krav(isinstance(b.get("citat"), dict) and b["citat"].get("text"), "citat saknas")
    krav(len(b.get("omdomen", [])) == 3, "omdomen ska vara 3")
    krav(6 <= len(b.get("faq", [])) <= 8, "faq ska vara 6–8")
    if b["profil"] in ("foto", "djur", "arborist"):
        krav(len(b.get("priser", [])) == 3, "priser ska vara 3")
    if b.get("priser"):
        krav(sum(1 for x in b["priser"] if x.get("utvald")) == 1, "exakt ett pris ska vara utvalt")
        for x in b["priser"]:
            krav(len(x.get("punkter", [])) >= 3, "varje pris behöver minst 3 punkter")
    if b["profil"] in ("bygg", "arborist", "nisch"):
        krav(len(b.get("certifikat", [])) >= 3, "certifikat ska vara 3–6")
    for c in b.get("certifikat", []):
        krav(c.get("ikon", "skold") in IKONER, f"okänd ikon i certifikat: {c.get('ikon')}")
    if b["profil"] in ("foto", "djur"):
        krav(len(b.get("galleri_taggar", [])) >= 2, "galleri_taggar behövs")
    if b["profil"] == "mega":
        inv = b.get("investerare", {})
        krav(inv.get("aktie") and inv.get("rapporter"), "investerare behövs för mega")
        krav(len(b.get("kontor_lista", [])) >= 5, "kontor_lista behövs för mega")
    if b["profil"] == "nisch":
        krav(b.get("nisch"), "nisch saknas")
    krav(3 <= len(b.get("nyheter", [])) <= 4, "nyheter ska vara 3–4")
    kt = b.get("kontakt", {})
    krav(all(kt.get(x) for x in ("adress", "postnr", "ort", "telefon")), "kontakt ofullständig")
    krav(re.fullmatch(r"070-174 06 \d\d", kt.get("telefon", "")) is not None, "telefon ska vara 070-174 06 05–99")
    # Taggar
    def taggar(o):
        if isinstance(o, dict):
            for kk, vv in o.items():
                if kk == "tagg" and isinstance(vv, str):
                    yield vv
                else:
                    yield from taggar(vv)
        elif isinstance(o, list):
            for vv in o:
                yield from taggar(vv)
    for tg in list(taggar(b)) + list(b.get("galleri_taggar", [])) + [r[3] for r in b.get("nyheter", []) if len(r) > 3] + list(b.get("bild", {}).values()):
        krav(tg in TAGGAR, f"okänd bildtagg: {tg}")
    txt = json.dumps(b, ensure_ascii=False).lower()
    for kl in KLYSCHOR:
        krav(kl not in txt, f"klyscha: {kl}")
    return f


def main():
    filer = []
    for a in sys.argv[1:]:
        p = pathlib.Path(a)
        filer += sorted(p.rglob("*.json")) if p.is_dir() else [p]
    ok = True
    slugs = {}
    for fil in filer:
        try:
            b = json.loads(fil.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(f"{fil}: OGILTIG JSON – {e}")
            ok = False
            continue
        f = fel_i(b, fil)
        key = (fil.parent.name, b.get("slug"))
        if key in slugs:
            f.append(f"slug används redan av {slugs[key]}")
        slugs[key] = fil.name
        if f:
            ok = False
            print(f"{fil}:")
            for x in f:
                print("   -", x)
        else:
            print(f"{fil}: OK")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
