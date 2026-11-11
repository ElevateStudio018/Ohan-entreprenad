"""Exporterar en sajt ur biblioteket till en fristående mapp (eget repo): bilderna kopieras in, inga delade sökvägar.

Kör:  python3 koncern/exportera.py grupp/slug utmapp
Ger utmapp/ med alla sidor, assets/, img/ (bara de bilder sajten använder), README.md och .nojekyll.
"""
import json
import pathlib
import re
import shutil
import sys

ROT = pathlib.Path(__file__).resolve().parent
SITE = ROT.parent / "site"
BANK = SITE / "bildbank"
DELAD = "../../../bildbank/"


def kallor():
    f = ROT / "bildkallor.tsv"
    ut = {}
    if f.exists():
        rader = f.read_text(encoding="utf-8").splitlines()
        huvud = rader[0].split("\t")
        for r in rader[1:]:
            d = dict(zip(huvud, r.split("\t")))
            ut[d.get("id", "")] = d
    return ut


def exportera(nyckel, ut):
    g, slug = nyckel.split("/")
    src = SITE / "sajter" / g / slug
    b = json.loads((ROT / "nischer" / g / f"{slug}.json").read_text(encoding="utf-8"))
    ut = pathlib.Path(ut)
    if ut.exists():
        for x in ut.iterdir():
            if x.name != ".git":
                shutil.rmtree(x) if x.is_dir() else x.unlink()
    ut.mkdir(parents=True, exist_ok=True)
    bilder = set()
    for f in src.rglob("*"):
        if f.is_dir():
            continue
        rel = f.relative_to(src)
        mal = ut / rel
        mal.parent.mkdir(parents=True, exist_ok=True)
        if f.suffix in (".html", ".css", ".js"):
            t = f.read_text(encoding="utf-8")
            bilder |= set(re.findall(re.escape(DELAD) + r"([\w.-]+)", t))
            djup = len(rel.parts) - 1
            t = t.replace(DELAD, "../" * djup + "img/")
            mal.write_text(t, encoding="utf-8")
        else:
            shutil.copy2(f, mal)
    (ut / "img").mkdir(exist_ok=True)
    for namn in sorted(bilder):
        if (BANK / namn).exists():
            shutil.copy2(BANK / namn, ut / "img" / namn)
    k = kallor()
    ids = sorted({n.split("-")[0].split(".")[0] for n in bilder})
    rader = []
    for i in ids:
        d = k.get(i)
        if d:
            rader.append(f"- `{i}` – {d.get('källa', '')}: {d.get('sida', '')} ({d.get('licens', 'cc0').upper()})")
    (ut / ".nojekyll").write_text("", encoding="utf-8")
    (ut / "README.md").write_text(f"""# {b["namn"]} – exempelsajt från Elevate Studio

{b.get("tagline", "")} · {b.get("typ", "")}

Komplett statisk exempelsajt (HTML/CSS/JS, inga beroenden) byggd av Elevate Studio. **Företaget är påhittat** –
namn, siffror, personer och projekt är exempelinnehåll.

- Öppna `index.html` i en webbläsare, eller publicera mappen med GitHub Pages (Settings → Pages → branch `main`, mapp `/`).
- Bilderna i `img/` är fria illustrationsbilder (CC0) och ska bytas mot kundens egna med samma filnamn.
- `paket.json` beskriver det grafiska paketet (typsnitt, färger, former, sektionsvarianter).

## Bildkällor
{chr(10).join(rader) if rader else "Se koncern/bildkallor.tsv i Elevate Studios bibliotek."}
""", encoding="utf-8")
    return len(bilder)


if __name__ == "__main__":
    print(exportera(sys.argv[1], sys.argv[2]), "bilder")
