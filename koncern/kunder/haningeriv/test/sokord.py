"""Sökordstäckning: för varje sökning, vilken sida på sajten som bäst svarar och var orden finns (titel, h1, adress, beskrivning, text)."""
import re, html, sys, json, pathlib
SOK = [("rivning haninge", ["rivning"], ["haninge"]), ("rivningsfirma", ["rivningsfirma", "rivning"], []), ("stambytesrivning", ["stambytesrivning"], []),
       ("asbestsanering", ["asbestsanering", "asbest"], []), ("mögelsanering", ["mögelsanering", "mögel"], []), ("sanering vattenskada", ["sanering"], ["vattenskad"]),
       ("betonghåltagning haninge", ["betonghåltagning", "håltagning"], ["haninge"]), ("kärnborrning", ["kärnborrning"], []),
       ("friläggning av rör fuktskada", ["friläggning"], ["fukt"]), ("byggkonsult", ["byggkonsult", "konsult"], []), ("bemanning byggpersonal", ["bemanning"], ["byggpersonal"])]
def las(d):
    sidor = {}
    for f in sorted(pathlib.Path(d).glob("*.html")):
        t = f.read_text(encoding="utf-8", errors="ignore")
        if 'http-equiv="refresh"' in t or f.name == "404.html": continue
        g = lambda r: html.unescape(re.sub(r"<[^>]+>", " ", (re.search(r, t, re.S | re.I) or [None, ""])[1])).lower()
        body = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", t, flags=re.I)
        sidor[f.name] = {"titel": g(r"<title[^>]*>(.*?)</title>"), "h1": g(r"<h1[^>]*>(.*?)</h1>"),
                         "beskr": html.unescape((re.search(r'<meta name="description" content="([^"]*)"', t) or [None, ""])[1]).lower(),
                         "text": html.unescape(re.sub(r"<[^>]+>", " ", body)).lower(), "url": f.stem.lower()}
    return sidor
def poang(s, huvud, extra):
    har = lambda txt, ord_: any(o in txt for o in ord_)
    p = {"adress": har(s["url"].replace("-", ""), [h.replace(" ", "") for h in huvud[:1]]) or har(s["url"], huvud[:1]),
         "titel": har(s["titel"], huvud) and (not extra or har(s["titel"] + s["text"][:3000], extra)), "h1": har(s["h1"], huvud), "beskrivning": har(s["beskr"], huvud),
         "omnamnanden": sum(s["text"].count(h) for h in huvud[:1]) or sum(s["text"].count(h) for h in huvud)}
    return p, p["adress"] * 3 + p["titel"] * 3 + p["h1"] * 2 + p["beskrivning"] + min(p["omnamnanden"], 10) / 5
ut = {}
for namn, d in (("gammal", sys.argv[1]), ("ny", sys.argv[2])):
    sidor = las(d)
    for sok, huvud, extra in SOK:
        best = max(sidor.items(), key=lambda kv: poang(kv[1], huvud, extra)[1])
        p, sc = poang(best[1], huvud, extra)
        ut.setdefault(sok, {})[namn] = {"sida": best[0], "poang": round(sc, 1), **p}
print(f'{"Sökning":30} | {"Gamla sajten":42} | Nya sajten')
for sok, v in ut.items():
    f = lambda x: f'{x["sida"][:18]:18} {"A" if x["adress"] else "-"}{"T" if x["titel"] else "-"}{"H" if x["h1"] else "-"}{"B" if x["beskrivning"] else "-"} {x["omnamnanden"]:>3} ggr ({x["poang"]})'
    print(f'{sok:30} | {f(v["gammal"]):42} | {f(v["ny"])}')
json.dump(ut, open("sokord.json", "w"), ensure_ascii=False, indent=1)
