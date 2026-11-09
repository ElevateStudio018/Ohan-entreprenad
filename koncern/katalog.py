"""Sektionsbiblioteket: renderar varje sektionsvariant för sig och tar bilder av dem.

Kör:  python3 koncern/katalog.py                    # bygger alla varianter till site/sektioner/ + bilder + index.html
      python3 koncern/katalog.py vagval/kakel ...    # bara vissa (snabb kontroll när man skriver en variant)
      --utan-bilder   hoppa över skärmdumpar

Varje variant blir site/sektioner/<sektion>-<variant>.html (en sida med bara den sektionen) och bilden
site/sektioner/bilder/<sektion>-<variant>.jpg. Sidan index.html visar alla med bild, namn och antal.
"""
import functools
import html
import http.server
import json
import pathlib
import sys
import threading

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT))
import generera  # noqa: E402
import varianter  # noqa: E402

UT = ROT.parent / "site" / "sektioner"
DELAD = (ROT.parent / "site" / "bildbank", "../bildbank/")
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
E = html.escape

NAMN = {"vagval": "Vägval / tjänster", "bolag": "Bolag / team", "siffror": "Nyckeltal", "nyheter": "Nyheter", "berattelser": "Berättelser",
        "projekt": "Projekt / referenser", "hb": "Hållbarhet / löften", "ir": "Investerare", "panel": "Karriär / panel", "snabb": "Genvägar",
        "omdomen": "Omdömen", "process": "Process", "citat": "Citat", "service": "Servicerad", "tidslinje": "Tidslinje", "kontor": "Kontor",
        "priser": "Priser", "faq": "Frågor & svar", "galleri": "Galleri", "boka": "Bokning / kontakt", "certifikat": "Certifikat",
        "logos": "Kunder", "cta": "Uppmaning (CTA)"}


def brief():
    """En brief med innehåll för alla sektioner (megakoncern + nischfält)."""
    b = json.loads((ROT / "nischer/mega/aldervik.json").read_text(encoding="utf-8"))
    n = json.loads((ROT / "nischer/brand/brandlinjen.json").read_text(encoding="utf-8"))
    f = json.loads((ROT / "nischer/foto/ljung-hav.json").read_text(encoding="utf-8"))
    for k in ("omdomen", "faq", "certifikat", "kunder", "process"):
        b[k] = n.get(k) or b.get(k)
    b["priser"], b["prislista"], b["galleri_taggar"] = n.get("priser") or f["priser"], f["prislista"], ["bygg", "kontor", "people", "stad"]
    b["profil"] = "mega"
    b.pop("demo", None)
    return b


def paket(b):
    import paket as pk
    p = pk.nytt("katalog-sektioner", "bygg", farg="#1f3d5a", accent="#f2b84b", antal=1, profil="mega", brief=b, tidigare=[])
    p.update(hero="statement", header="ljus", herotext="standard", rubrikstil="standard", bildtyngd=["bygg", "kontor", "people"])
    p["bakgrund"] = {}
    return p


def bygg(val=None):
    b = brief()
    p = paket(b)
    UT.mkdir(parents=True, exist_ok=True)
    s = generera.Sajt(b, p, UT, DELAD)
    s.bilder = generera.Bilder("katalog", UT, ["bygg", "kontor", "people"], DELAD)
    s.hero_bild = s.bilder.ta("bygg")
    s.assets()
    s.index_delar = None
    # samma delar-tabell som index()
    s._delar = {"vagval": s.s_vagval, "berattelser": s.s_berattelser, "panel": lambda: s.s_panel(False), "bolag": s.s_bolag, "siffror": s.s_siffror,
                "projekt": s.s_projekt, "hb": s.s_hb, "ir": s.s_ir, "nyheter": s.s_nyheter, "snabb": s.s_snabb, "process": s.s_process,
                "citat": s.s_citat, "service": s.s_service, "tidslinje": s.s_tidslinje, "kontor": s.s_kontor, "priser": s.s_priser,
                "omdomen": s.s_omdomen, "faq": s.s_faq, "galleri": s.s_galleri, "boka": s.s_boka, "certifikat": s.s_certifikat, "logos": s.s_logos}
    alla = varianter.alla()
    lista = []
    for sek, vs in alla.items():
        for v in vs:
            nyckel = f"{sek}/{v}"
            if val and nyckel not in val:
                continue
            p.setdefault("block", {})[sek] = v
            try:
                html_ = s.sektion(sek, v) if (sek, v) in varianter.REG else s._delar[sek]()
            except Exception as e:  # noqa: BLE001
                html_ = f'<section class="sek"><div class="wrap"><h2>FEL i {nyckel}: {E(repr(e))}</h2></div></section>'
                print("FEL", nyckel, repr(e))
            fil = f"{sek}-{v}.html"
            s.sida(fil, f"{NAMN.get(sek, sek)} – {v}", "Sektionsvariant", f'<div class="katalog-del" data-namn="{nyckel}">{html_}</div>', har_hero=False)
            lista.append((sek, v, fil))
    return lista


def bilder(lista):
    from playwright.sync_api import sync_playwright
    (UT / "bilder").mkdir(exist_ok=True)

    class Tyst(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Tyst, directory=str(UT.parent)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME)
        pg = br.new_page(viewport={"width": 1440, "height": 900})
        mob = br.new_page(viewport={"width": 390, "height": 844})
        for sek, v, fil in lista:
            for sida, namn, w in ((pg, f"{sek}-{v}.jpg", 1440), (mob, f"{sek}-{v}-mobil.jpg", 390)):
                sida.goto(f"http://127.0.0.1:{port}/sektioner/{fil}", wait_until="networkidle")
                sida.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('syns'));document.querySelector('.demo-rad')?.remove()")
                sida.wait_for_timeout(500)
                el = sida.query_selector(".katalog-del")
                bredd = sida.evaluate("document.documentElement.scrollWidth")
                el.screenshot(path=str(UT / "bilder" / namn), type="jpeg", quality=72)
                if bredd > w:
                    print(f"  SIDLED-SCROLL {sek}/{v} ({w}px: {bredd})")
            print(f"{sek}/{v}", flush=True)
        br.close()
    srv.shutdown()


def index(lista):
    alla = varianter.alla()
    antal = sum(len(v) for v in alla.values())
    sek_html = []
    for sek, vs in alla.items():
        kort = "".join(f'<li><a href="{sek}-{v}.html"><img src="bilder/{sek}-{v}.jpg" alt="{E(sek)} – {E(v)}" loading="lazy"><span><b>{E(v)}</b> · {E(sek)}</span></a></li>' for v in vs)
        sek_html.append(f'<section id="{sek}"><h2>{E(NAMN.get(sek, sek))} <small>{len(vs)} varianter</small></h2><ul>{kort}</ul></section>')
    doc = f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sektionsbiblioteket – Elevate Studio</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap">
<style>:root{{--bg:#f4f3ef;--ink:#15161a;--mut:#62646b}}*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--ink);font:16px/1.5 "Plus Jakarta Sans",system-ui,sans-serif}}
header,section{{max-width:1400px;margin:auto;padding:40px 16px 8px}}h1{{font-size:clamp(32px,5vw,60px);letter-spacing:-.03em}}header p{{color:var(--mut);margin-top:10px;max-width:50em}}
h2{{font-size:26px;letter-spacing:-.02em;margin-bottom:16px}}h2 small{{font-size:14px;color:var(--mut);font-weight:400}}
ul{{list-style:none;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(320px,1fr))}}a{{display:block;text-decoration:none;color:inherit;background:#fff;border:1px solid #e2e0da}}
img{{display:block;width:100%;height:260px;object-fit:cover;object-position:top}}a span{{display:block;padding:10px 14px;font-size:14px;color:var(--mut)}}a b{{color:var(--ink)}}</style></head><body>
<header><h1>Sektionsbiblioteket</h1><p>{antal} sektionsvarianter fördelade på {len(alla)} sektionstyper. Varje sajt i biblioteket får sina egna varianter – inga två sajter i samma grupp har samma kombination.</p></header>
{"".join(sek_html)}</body></html>'''
    (UT / "index.html").write_text(doc, encoding="utf-8")
    print("Sektionsbiblioteket:", antal, "varianter")


if __name__ == "__main__":
    val = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    lista = bygg(val)
    if "--utan-bilder" not in sys.argv:
        bilder(lista)
    if not val:
        index(lista)
