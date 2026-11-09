"""Skärmdumpar av nischsajter (serverar site/ så att den delade bildbanken fungerar).

Kör:  python3 koncern/skarmdump_nisch.py <utmapp> grupp/slug [grupp/slug ...]   # eller "grupp" för hela gruppen
      --tumme   sparar också site/sajter/<grupp>/<slug>/tumme.jpg (miniatyr till galleriet)
      --bara-tumme  bara miniatyrer
Skriver ut sidbredd och varnar för horisontell scroll.
"""
import functools
import http.server
import pathlib
import sys
import threading

from playwright.sync_api import sync_playwright

ROT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROT / "site"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ut = pathlib.Path(args[0])
    ut.mkdir(parents=True, exist_ok=True)
    mal = []
    for a in args[1:]:
        if "/" in a:
            mal.append(a)
        else:
            mal += [f"{a}/{p.name}" for p in sorted((SITE / "sajter" / a).iterdir()) if (p / "index.html").exists()]
    tumme = "--tumme" in sys.argv or "--bara-tumme" in sys.argv
    bara = "--bara-tumme" in sys.argv

    class Tyst(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Tyst, directory=str(SITE)))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        for m in mal:
            url = f"http://127.0.0.1:{port}/sajter/{m}/index.html"
            namn = m.replace("/", "-")
            for typ, w, h in (("dator", 1440, 900), ("mobil", 390, 844)):
                if bara and typ == "mobil":
                    continue
                pg = b.new_page(viewport={"width": w, "height": h})
                pg.goto(url, wait_until="networkidle")
                if not bara:
                    for y in range(0, 14000, 800):
                        pg.evaluate(f"window.scrollTo(0,{y})")
                        pg.wait_for_timeout(120)
                    pg.evaluate("window.scrollTo(0,0)")
                    pg.evaluate("document.querySelectorAll('.reveal').forEach(e=>e.classList.add('syns'))")
                pg.wait_for_timeout(900)
                bredd = pg.evaluate("document.documentElement.scrollWidth")
                if typ == "dator":
                    if tumme:
                        pg.screenshot(path=str(SITE / "sajter" / m / "tumme.jpg"), type="jpeg", quality=62, clip={"x": 0, "y": 0, "width": 1440, "height": 900})
                        from PIL import Image
                        im = Image.open(SITE / "sajter" / m / "tumme.jpg")
                        im.thumbnail((640, 400))
                        im.save(SITE / "sajter" / m / "tumme.jpg", quality=70, optimize=True)
                    if not bara:
                        pg.screenshot(path=str(ut / f"{namn}-dator.jpg"), full_page=True, type="jpeg", quality=60)
                else:
                    pg.screenshot(path=str(ut / f"{namn}-mobil.jpg"), full_page=True, type="jpeg", quality=60)
                print(f"{m} {typ}: {bredd}px{'  <-- HORISONTELL SCROLL' if bredd > w else ''}", flush=True)
                pg.close()
        b.close()
    srv.shutdown()


if __name__ == "__main__":
    main()
