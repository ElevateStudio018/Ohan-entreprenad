"""Herokatalogen: renderar varje hero-textlayout som en helskärmshero och tar bilder (dator + mobil).

Kör:  python3 koncern/herokatalog.py            # alla layouter
      python3 koncern/herokatalog.py t-glas ...  # bara vissa
Ger site/sektioner/hero-<layout>.html och site/sektioner/bilder/hero-<layout>.jpg / -mobil.jpg.
Väljarsidan (valjsida.py) visar dem under "Hero-text".
"""
import functools
import http.server
import pathlib
import sys
import threading

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT))
import generera  # noqa: E402
import katalog  # noqa: E402

UT = katalog.UT

# (nyckel, kort beskrivning). Omgång 1 (redan bedömda) först, sedan de nya t-layouterna.
GAMLA = [("nere", "Stor rubrik nere till vänster"), ("stack", "Ett ord per rad"), ("kort", "Vitt kort på bilden"),
         ("hoger", "Högerställd text"), ("linje", "Accentlinje vid rubriken"), ("uppe", "Texten uppe"), ("delad", "Rubrik uppe, ingress nere"),
         ("mitten", "Allt centrerat"), ("jatte", "Jätterubrik i versaler"), ("kursiv", "Kursiv rubrik"), ("band", "Färgband längst ner"),
         ("kontur", "Konturrubrik"), ("versal", "Spärrade versaler")]
NYA = [("t-markering", "Rubriken på accentmarkering"), ("t-understruken", "Tjock accentunderstrykning"), ("t-forsta", "Första raden i accentfärg"),
       ("t-tunntjock", "Tunn rubrik, fet första rad"), ("t-spoke", "Namnet jättestort i bakgrunden"), ("t-glas", "Frostad glaspanel"),
       ("t-morkkort", "Mörk panel nere till vänster"), ("t-fargkort", "Färgkort nere till höger"), ("t-accentkort", "Accentkort uppe till vänster"),
       ("t-hogerkort", "Vitt kort till höger"), ("t-diagonal", "Färgpanel med sned kant"), ("t-ram", "Tunn ram runt heron"),
       ("t-kolumner", "Rubrik vänster, ingress höger"), ("t-lodrat", "Lodrät etikett"), ("t-nummer", "Stort nummer ovanför"),
       ("t-pil", "Rubrik som slutar med pil"), ("t-citat", "Citattecken framför rubriken"), ("t-streck", "Accentstreck vid etiketten"),
       ("t-pill", "Etikett som piller med prick"), ("t-gradient", "Rubrik som tonar till accent"), ("t-skugga", "Ljus bild, skuggad text"),
       ("t-mittvanster", "Vertikalt centrerad, vänster"), ("t-smal", "Smal kolumn, stor ingress"), ("t-storingress", "Ingress med accentkant"),
       ("t-kant", "Hög accentkant vid hela texten"), ("t-horn", "Rubrik uppe, knappar nere till höger"), ("t-rad", "Allt på en rad längst ner"),
       ("t-tvafarg", "Etikett och ingress i accentfärg"), ("t-ruta", "Rubriken i en vit ruta"),
       ("t-bildkort", "Bild: två överlappande bildkort"), ("t-bildtrio", "Bild: tre stående bilder"), ("t-bildremsa", "Bild: remsa med småbilder"),
       ("t-bildram", "Bild: färgyta och inramad bild"), ("t-bildcirkel", "Bild: rund bild med ring")]
ALLA = GAMLA + NYA


def bygg(val=None):
    b = katalog.brief()
    p = katalog.paket(b)
    p.update(header="transparent", mosaik_taggar=["people", "kontor"])
    s = generera.Sajt(b, p, UT, katalog.DELAD)
    s.bilder = generera.Bilder("herokatalog", UT, ["bygg", "kontor", "people"], katalog.DELAD)
    s.hero_bild = s.bilder.ta("bygg")
    s.assets()
    lista = []
    for nyckel, namn in ALLA:
        if val and nyckel not in val:
            continue
        p["herotext"] = nyckel
        p["hero"] = "statement"
        s.bilder.anvanda = {s.hero_bild["id"]}
        fil = f"hero-{nyckel}.html"
        s.sida(fil, f"Hero – {namn}", "Hero-layout", s.hero(), aktiv="index", har_hero=True)
        lista.append((nyckel, fil))
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
        br = pw.chromium.launch(executable_path=katalog.CHROME)
        dator = br.new_page(viewport={"width": 1440, "height": 900})
        mobil = br.new_page(viewport={"width": 390, "height": 844})
        for nyckel, fil in lista:
            for sida, suf, w in ((dator, "", 1440), (mobil, "-mobil", 390)):
                sida.goto(f"http://127.0.0.1:{port}/sektioner/{fil}", wait_until="networkidle")
                sida.evaluate("document.querySelector('.demo-rad')?.remove();document.querySelector('.foto-not')?.remove()")
                sida.wait_for_timeout(500)
                if sida.evaluate("document.documentElement.scrollWidth") > w:
                    print(f"  SIDLED-SCROLL {nyckel} ({w}px)")
                sida.screenshot(path=str(UT / "bilder" / f"hero-{nyckel}{suf}.jpg"), type="jpeg", quality=74)
            print(nyckel, flush=True)
        br.close()
    srv.shutdown()


if __name__ == "__main__":
    val = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    lista = bygg(val)
    if "--utan-bilder" not in sys.argv:
        bilder(lista)
