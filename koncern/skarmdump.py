"""Tar skärmdumpar av en byggd sajt så att man kan granska den: dator (hela sidan) och mobil (första skärmen + meny).

Kör:  python3 koncern/skarmdump.py <sajtmapp> <utmapp> [sida.html ...]

Startar en lokal webbserver för mappen, laddar sidorna i Chromium och sparar PNG/JPG. Skriver också ut om sidan
blir bredare än skärmen (horisontell scroll), vilket ska vara 0.
"""
import functools
import http.server
import pathlib
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    sajt, ut = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2])
    sidor = sys.argv[3:] or ["index.html"]
    ut.mkdir(parents=True, exist_ok=True)
    class Tyst(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Tyst, directory=str(sajt))
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as srv:
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        with sync_playwright() as p:
            kw = {"executable_path": CHROME} if pathlib.Path(CHROME).exists() else {}
            b = p.chromium.launch(**kw)
            for sida in sidor:
                namn = sida.replace(".html", "").replace("/", "-")
                for typ, w, h in (("dator", 1440, 900), ("mobil", 390, 844)):
                    pg = b.new_page(viewport={"width": w, "height": h})
                    pg.goto(f"http://127.0.0.1:{port}/{sida}", wait_until="networkidle")
                    pg.add_style_tag(content="html{scroll-behavior:auto!important}.reveal{opacity:1!important;transform:none!important}.hero-bild img{animation:none!important}")
                    for y in range(0, 12000, 700):
                        pg.evaluate(f"window.scrollTo(0,{y})")
                        pg.wait_for_timeout(180)
                    pg.evaluate("window.scrollTo(0,0)")
                    pg.wait_for_timeout(1500)
                    bredd = pg.evaluate("document.documentElement.scrollWidth")
                    if typ == "dator":
                        pg.screenshot(path=str(ut / f"{namn}-dator.jpg"), full_page=True, type="jpeg", quality=70)
                    else:
                        pg.screenshot(path=str(ut / f"{namn}-mobil.jpg"), type="jpeg", quality=70)
                        knapp = pg.query_selector("#menyKnapp")
                        if knapp:
                            knapp.click()
                            pg.wait_for_timeout(300)
                            pg.screenshot(path=str(ut / f"{namn}-mobil-meny.jpg"), type="jpeg", quality=70)
                    print(f"{sida} {typ}: sidbredd {bredd}px (skärm {w}px){'  <-- HORISONTELL SCROLL' if bredd > w else ''}")
                    pg.close()
            b.close()
        srv.shutdown()


if __name__ == "__main__":
    main()
