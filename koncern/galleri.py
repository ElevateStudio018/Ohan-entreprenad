"""Galleri över alla nischsajter: site/sajter/index.html (en sektion per grupp, miniatyrer om de finns)."""
import html
import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parent
UT = ROT.parent / "site" / "sajter"
E = html.escape


def bygg():
    import bygg_nischer as bn
    sektioner, antal, nav = [], 0, []
    for g in bn.grupper_alla():
        filer = sorted((bn.BRIEFS / g).glob("*.json"))
        if not filer:
            continue
        rubrik, beskr, _ = bn.gruppinfo(g)
        kort = []
        for fil in filer:
            b = json.loads(fil.read_text(encoding="utf-8"))
            pfil = bn.BRIEFS / g / "paket" / fil.name
            if not (UT / g / b["slug"] / "index.html").exists() or not pfil.exists():
                continue
            p = json.loads(pfil.read_text(encoding="utf-8"))
            f = p["farger"]
            tumme = f'{g}/{b["slug"]}/tumme.jpg'
            bild = (f'<img src="{tumme}" alt="" loading="lazy">' if (UT / tumme).exists()
                    else f'<span class="ph" style="background:{f["primar"]};color:{f["primar_ink"]}">{E(b["kortnamn"])}</span>')
            kort.append(f'<li><a href="{g}/{b["slug"]}/index.html">{bild}<span class="m"><b>{E(b["namn"])}</b><span>{E(b["typ"])}</span>'
                        f'<span class="f"><i style="background:{f["primar"]}"></i><i style="background:{f["accent"]}"></i><i style="background:{f["ton"]}"></i> {E(p["hero"])}</span></span></a></li>')
        if not kort:
            continue
        antal += len(kort)
        nav.append(f'<a href="#{g}">{E(rubrik)} <small>{len(kort)}</small></a>')
        sektioner.append(f'<section id="{g}"><div class="sh"><h2>{E(rubrik)}</h2><p>{E(beskr)} · {len(kort)} sajter</p></div><ul class="g">{"".join(kort)}</ul></section>')
    doc = f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sajtbiblioteket – Elevate Studio</title><meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap">
<style>
:root{{--bg:#f4f3ef;--ink:#15161a;--mut:#62646b;--kort:#fff;--linje:#e2e0da}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:var(--bg);color:var(--ink);font:16px/1.5 "Plus Jakarta Sans",system-ui,sans-serif}}
a{{color:inherit}}header{{padding:56px 16px 28px;max-width:1360px;margin:auto}}h1{{font-size:clamp(32px,5vw,64px);line-height:1.05;letter-spacing:-.03em}}
header p{{margin-top:14px;color:var(--mut);max-width:46em}}nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-block:1px solid var(--linje);overflow-x:auto;white-space:nowrap}}
nav div{{max-width:1360px;margin:auto;padding:10px 16px;display:flex;gap:6px}}nav a{{text-decoration:none;font-size:14px;padding:7px 12px;border-radius:999px;background:var(--kort)}}nav small{{color:var(--mut)}}
section{{max-width:1360px;margin:auto;padding:48px 16px 8px}}.sh{{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:20px}}
h2{{font-size:clamp(24px,2.6vw,34px);letter-spacing:-.02em}}.sh p{{color:var(--mut)}}
.g{{list-style:none;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(260px,1fr))}}.g a{{display:block;text-decoration:none;background:var(--kort);border:1px solid var(--linje);overflow:hidden;transition:transform .2s}}
.g a:hover{{transform:translateY(-3px)}}.g img,.ph{{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top}}.ph{{display:grid;place-items:center;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}
.m{{display:grid;gap:3px;padding:14px 16px 16px}}.m b{{font-size:15.5px}}.m span{{font-size:13.5px;color:var(--mut)}}.f{{display:flex;align-items:center;gap:4px;margin-top:6px}}.f i{{width:14px;height:14px;border-radius:50%;border:1px solid rgba(0,0,0,.08)}}
footer{{max-width:1360px;margin:auto;padding:56px 16px;color:var(--mut);font-size:14px}}
</style></head><body>
<header><h1>Sajtbiblioteket</h1><p>{antal} kompletta exempelsajter i koncernstil – samma grafiska grund, olika paket, sektioner och innehåll per företag och nisch.
Företagen är påhittade och bilderna är fria illustrationsbilder (CC0).</p></header>
<nav aria-label="Grupper"><div>{"".join(nav)}</div></nav>
{"".join(sektioner)}
<footer>Elevate Studio · Varje sajt är statisk HTML/CSS/JS med 7–8 sidor.</footer>
</body></html>'''
    UT.mkdir(parents=True, exist_ok=True)
    (UT / "index.html").write_text(doc, encoding="utf-8")
    print("Galleri:", antal, "sajter ->", UT / "index.html")


if __name__ == "__main__":
    bygg()
