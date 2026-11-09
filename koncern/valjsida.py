"""Fristående väljarsida (för githack/Pages): site/sektioner/valj.html.

Rutnät med alla sektionsvarianter + helskärmsläge där man går igenom en i taget:
Mellanslag = Ja (och nästa), N / → = Nej, ← = tillbaka, M = dator/mobil, Esc = stäng.
Valen sparas i webbläsaren (localStorage) och kopieras/laddas ner som text att ge Claude.
Kör: python3 koncern/valjsida.py
"""
import json
import pathlib
import sys

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT / "mall"))
sys.path.insert(0, str(ROT))
import varianter  # noqa: E402
from katalog import NAMN  # noqa: E402
from rostsida import heroer  # noqa: E402

UT = ROT.parent / "site" / "sektioner" / "valj.html"


def kortlista():
    alla = varianter.alla()
    b = ROT.parent / "site" / "sektioner" / "bilder"
    kort = []
    for s, vs in alla.items():
        for v in vs:
            if (b / f"{s}-{v}.jpg").exists():
                kort.append({"id": f"{s}--{v}", "sek": s, "namn": NAMN.get(s, s), "v": v, "d": f"bilder/{s}-{v}.jpg",
                             "m": f"bilder/{s}-{v}-mobil.jpg", "sida": f"{s}-{v}.html"})
    for nyckel, etikett, t in heroer():
        rel = "../sajter/" + "/".join(t.parts[-3:-1])
        kort.append({"id": f"hero--{nyckel}", "sek": "hero", "namn": "Hero-layout", "v": nyckel, "info": etikett,
                     "d": rel + "/tumme.jpg", "m": rel + "/tumme.jpg", "sida": rel + "/index.html"})
    return kort


SIDA = r'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sektionsväljaren</title><meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
:root{--bg:#f3f1ec;--yta:#fffefb;--ink:#1a1916;--mut:#6b675e;--linje:#dcd8ce;--ja:#1f7a4d;--ja-bg:#e2f2e8;--nej:#a3392b;--nej-bg:#f6e3df;--mark:#2a3a8f;
--disp:"Bricolage Grotesque",system-ui,sans-serif;--text:"Instrument Sans",system-ui,sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#171613;--yta:#211f1b;--ink:#efece4;--mut:#a39e92;--linje:#38352e;--ja:#5fd08f;--ja-bg:#1d3527;--nej:#ff8f7a;--nej-bg:#3a201b;--mark:#9fb0ff;color-scheme:dark}}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--text);margin:0}
.ram{max-width:1500px;margin:auto;padding-inline:max(16px,env(safe-area-inset-left,0px)) max(16px,env(safe-area-inset-right,0px))}
header{padding-block:40px 18px;display:grid;gap:14px}
h1{font:700 clamp(32px,5vw,58px)/1 var(--disp);letter-spacing:-.03em;margin:0}
header p{color:var(--mut);max-width:70ch;margin:0}
kbd{font:600 12px var(--text);padding:2px 7px;border:1px solid var(--linje);border-bottom-width:2px;border-radius:5px;background:var(--yta);color:var(--ink)}
.knappar{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
button,select{font:600 14px var(--text);padding:9px 15px;border-radius:999px;border:1px solid var(--linje);background:var(--yta);color:var(--ink);cursor:pointer}
button.huvud{background:var(--ink);color:var(--bg);border-color:var(--ink)}
button[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
button:focus-visible,select:focus-visible{outline:2px solid var(--mark);outline-offset:2px}
.stat{font-variant-numeric:tabular-nums;color:var(--mut)}.stat b{color:var(--ink)}
.verktyg{position:sticky;top:0;z-index:5;background:var(--bg);border-block:1px solid var(--linje)}
.verktyg .ram{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding-block:10px}
.verktyg .stat{margin-left:auto}
main{padding-block:20px 80px}
h2{font:700 24px var(--disp);letter-spacing:-.02em;margin:34px 0 14px}
.rutnat{list-style:none;margin:0;padding:0;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(min(100%,320px),1fr))}
.kort{background:var(--yta);border:1px solid var(--linje);border-radius:6px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.kort.ja{border-color:var(--ja);box-shadow:0 0 0 2px var(--ja)}.kort.nej{opacity:.55}
.kort .bild{display:block;border:0;padding:0;background:var(--linje);max-height:360px;overflow:hidden;cursor:zoom-in}
.kort img{display:block;width:100%;height:auto}
.kort .info{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px}
.kort b{font-weight:600}.kort small{display:block;color:var(--mut)}
.tagg{font:600 12px var(--text);padding:4px 10px;border-radius:999px;white-space:nowrap}
.tagg.ja{background:var(--ja-bg);color:var(--ja)}.tagg.nej{background:var(--nej-bg);color:var(--nej)}
/* Helskärmsläget */
#fs{position:fixed;inset:0;z-index:50;background:#0e0e0d;color:#f3f1ec;display:grid;grid-template-rows:auto 1fr auto}
#fs[hidden]{display:none}
#fs .topp{display:flex;align-items:center;gap:14px;padding:12px 18px;border-bottom:1px solid #2a2925;flex-wrap:wrap}
#fs .topp b{font:700 18px var(--disp)}#fs .topp .mut{color:#a39e92}
#fs .topp .hoger{margin-left:auto;display:flex;gap:8px;flex-wrap:wrap}
#fs button{background:#1e1d1a;color:#f3f1ec;border-color:#3a3833}
#fs .yta{overflow:auto;overscroll-behavior:contain;outline:none;display:flex;justify-content:center;align-items:flex-start;padding:18px}
#fs .yta img{display:block;max-width:min(100%,1440px);height:auto;box-shadow:0 10px 50px rgba(0,0,0,.5);background:#fff}
#fs .yta.mobil img{max-width:420px}
#fs .bott{display:flex;gap:10px;justify-content:center;align-items:center;padding:12px 18px;border-top:1px solid #2a2925;flex-wrap:wrap}
#fs .bott .ja{background:var(--ja);border-color:var(--ja);color:#06140c;font-size:16px;padding:12px 26px}
#fs .bott .nej{background:#3a201b;border-color:#5a2e26;color:#ffb3a5;font-size:16px;padding:12px 22px}
#fs .bott .hint{color:#a39e92;font-size:13px}
#fs .status{font:700 13px var(--text);padding:4px 10px;border-radius:999px}
#fs .status.ja{background:var(--ja);color:#06140c}#fs .status.nej{background:#5a2e26;color:#ffd2c8}
#flash{position:fixed;inset:0;z-index:60;pointer-events:none;display:grid;place-items:center;font:700 clamp(60px,12vw,160px) var(--disp);opacity:0;transition:opacity .25s}
#flash.visa{opacity:.9}
@media (prefers-reduced-motion:reduce){#flash{transition:none}}
dialog{border:0;border-radius:8px;padding:22px;max-width:min(680px,94vw);background:var(--yta);color:var(--ink)}
dialog textarea{width:100%;height:240px;font:13px/1.4 ui-monospace,monospace;background:var(--bg);color:var(--ink);border:1px solid var(--linje);border-radius:6px;padding:10px}
</style></head><body>
<header class="ram"><h1>Sektionsväljaren</h1>
<p>__ANTAL__ sektionsvarianter och __HEROER__ hero-layouter. Starta <b>helskärmsläget</b> och gå igenom dem en i taget: <kbd>Mellanslag</kbd> = Ja, <kbd>N</kbd> eller <kbd>→</kbd> = Nej, <kbd>←</kbd> = tillbaka, <kbd>M</kbd> = mobil/dator, <kbd>Esc</kbd> = stäng. Skrolla med mus, styrplatta eller <kbd>↑</kbd><kbd>↓</kbd>.</p>
<p>Valen sparas i den här webbläsaren. När du är klar: tryck <b>Kopiera mina val</b> och klistra in dem till Claude.</p>
<div class="knappar"><button class="huvud" id="startnya" type="button">Gå igenom bara de __NYA__ nya</button><button id="start" type="button">Starta helskärm från början</button><button id="fortsatt" type="button">Fortsätt där jag slutade</button><button id="exportera" type="button">Kopiera mina val</button><button id="rensa" type="button">Börja om</button></div>
</header>
<div class="verktyg"><div class="ram">
<button type="button" data-f="alla" aria-pressed="true">Alla</button><button type="button" data-f="ja" aria-pressed="false">Ja</button><button type="button" data-f="nej" aria-pressed="false">Nej</button><button type="button" data-f="ej" aria-pressed="false">Inte bedömda</button><button type="button" data-f="nya" aria-pressed="false">Nya varianter</button>
<select id="sek" aria-label="Sektion"><option value="">Alla sektioner</option></select>
<span class="stat" id="stat"></span></div></div>
<main class="ram" id="lista"></main>
<div id="fs" hidden role="dialog" aria-label="Helskärmsläge">
  <div class="topp"><b id="fs-titel"></b><span class="mut" id="fs-under"></span><span class="status" id="fs-status" hidden></span>
    <div class="hoger"><button type="button" id="fs-vy">Mobil (M)</button><a id="fs-sida" target="_blank" rel="noopener"><button type="button" tabindex="-1">Öppna sidan</button></a><button type="button" id="fs-stang">Stäng (Esc)</button></div></div>
  <div class="yta" id="fs-yta" tabindex="0"><img id="fs-img" alt=""></div>
  <div class="bott"><button type="button" id="fs-bak">← Tillbaka</button><button type="button" class="nej" id="fs-nej">Nej (N)</button><button type="button" class="ja" id="fs-ja">Ja (mellanslag)</button><span class="hint" id="fs-rakn"></span></div>
</div>
<div id="flash" aria-hidden="true"></div>
<dialog id="exp"><h2 style="margin-top:0">Dina val</h2><p>Texten är kopierad om webbläsaren tillät det – annars markera och kopiera den här. Klistra in den till Claude.</p><textarea id="exp-text" readonly></textarea><form method="dialog" style="margin-top:12px;text-align:right"><button>Stäng</button></form></dialog>
<script>
const KORT=__DATA__;
const NYCKEL="sektionsvaljaren-v1";
let val={};try{val=JSON.parse(localStorage.getItem(NYCKEL)||"{}")}catch(e){}
const spara=()=>{try{localStorage.setItem(NYCKEL,JSON.stringify(val))}catch(e){}};
const $=s=>document.querySelector(s);
let filter="alla", idx=0, mobil=false;
const sel=$("#sek");[...new Map(KORT.map(k=>[k.sek,k.namn]))].forEach(([k,n])=>{const o=document.createElement("option");o.value=k;o.textContent=n;sel.append(o)});
const arNy=k=>/^[klmn]-/.test(k.v);
let lista=KORT;
function synliga(){return KORT.filter(k=>(!sel.value||k.sek===sel.value)&&(filter==="alla"||(filter==="nya"?arNy(k):filter==="ej"?!val[k.id]:val[k.id]===filter)))}
function stat(){const ja=Object.values(val).filter(x=>x==="ja").length,nej=Object.values(val).filter(x=>x==="nej").length;$("#stat").innerHTML=`<b>${ja}</b> ja · <b>${nej}</b> nej · ${lista.length-ja-nej} kvar`}
function rita(){
  const L=$("#lista");L.textContent="";let g=null,ul=null;
  synliga().forEach(k=>{
    if(k.namn!==g){g=k.namn;const h=document.createElement("h2");h.textContent=g;ul=document.createElement("ul");ul.className="rutnat";L.append(h,ul)}
    const li=document.createElement("li");li.className="kort"+(val[k.id]?" "+val[k.id]:"");
    const b=document.createElement("button");b.type="button";b.className="bild";const im=document.createElement("img");im.src=k.d;im.alt=k.namn+" – "+k.v;im.loading="lazy";b.append(im);
    b.onclick=()=>oppna(KORT.indexOf(k),KORT);
    const i=document.createElement("div");i.className="info";const t=document.createElement("div");t.innerHTML="<b></b><small></small>";t.querySelector("b").textContent=k.v;t.querySelector("small").textContent=(k.info||k.namn);
    i.append(t);if(val[k.id]){const s=document.createElement("span");s.className="tagg "+val[k.id];s.textContent=val[k.id]==="ja"?"Ja":"Nej";i.append(s)}
    li.append(b,i);ul.append(li)});
  stat();
}
function visa(){
  const k=lista[idx];$("#fs-titel").textContent=k.v;$("#fs-under").textContent=(k.info||k.namn);
  const img=$("#fs-img");img.src=mobil&&k.m?k.m:k.d;img.alt=k.namn+" – "+k.v;
  $("#fs-yta").classList.toggle("mobil",mobil);$("#fs-yta").scrollTop=0;$("#fs-vy").textContent=mobil?"Dator (M)":"Mobil (M)";
  $("#fs-sida").href=k.sida;const st=$("#fs-status");if(val[k.id]){st.hidden=false;st.className="status "+val[k.id];st.textContent=val[k.id]==="ja"?"Ja":"Nej"}else st.hidden=true;
  $("#fs-rakn").textContent=`${idx+1} / ${lista.length}`;
  [idx+1,idx+2].forEach(j=>{if(lista[j]){const p=new Image();p.src=mobil?lista[j].m:lista[j].d}});
}
function oppna(i,urval){lista=urval||KORT;idx=Math.max(0,Math.min(lista.length-1,i));$("#fs").hidden=false;document.body.style.overflow="hidden";visa();$("#fs-yta").focus();const el=document.documentElement;if(el.requestFullscreen&&!document.fullscreenElement){el.requestFullscreen().catch(()=>{})}}
function stang(){$("#fs").hidden=true;document.body.style.overflow="";if(document.fullscreenElement&&document.exitFullscreen)document.exitFullscreen().catch(()=>{});rita()}
function flash(t,f){const e=$("#flash");e.textContent=t;e.style.color=f;e.classList.add("visa");clearTimeout(flash.t);flash.t=setTimeout(()=>e.classList.remove("visa"),350)}
function rosta(v){const k=lista[idx];val[k.id]=v;spara();flash(v==="ja"?"JA":"NEJ",v==="ja"?"var(--ja)":"var(--nej)");if(idx<lista.length-1){idx++;visa()}else{visa();stat()}}
$("#fs-ja").onclick=()=>rosta("ja");$("#fs-nej").onclick=()=>rosta("nej");$("#fs-bak").onclick=()=>{if(idx>0){idx--;visa()}};
$("#fs-stang").onclick=stang;$("#fs-vy").onclick=()=>{mobil=!mobil;visa()};
document.addEventListener("keydown",e=>{
  if($("#fs").hidden)return; if(e.target.tagName==="TEXTAREA")return;
  if(e.code==="Space"||e.key===" "){e.preventDefault();rosta("ja")}
  else if(e.key==="n"||e.key==="N"||e.key==="ArrowRight"){e.preventDefault();rosta("nej")}
  else if(e.key==="ArrowLeft"){e.preventDefault();if(idx>0){idx--;visa()}}
  else if(e.key==="m"||e.key==="M"){mobil=!mobil;visa()}
  else if(e.key==="Escape"){stang()}
  else if(e.key==="ArrowDown"||e.key==="ArrowUp"||e.key==="PageDown"||e.key==="PageUp"){/* skrolla bilden */ $("#fs-yta").focus()}
});
document.addEventListener("fullscreenchange",()=>{if(!document.fullscreenElement&&!$("#fs").hidden){/* användaren lämnade helskärm med Esc – låt läget vara öppet */}});
$("#start").onclick=()=>oppna(0,KORT);
$("#startnya").onclick=()=>oppna(0,KORT.filter(arNy));
$("#fortsatt").onclick=()=>{const i=KORT.findIndex(k=>!val[k.id]);oppna(i<0?0:i,KORT)};
$("#rensa").onclick=()=>{if($("#rensa").dataset.saker){val={};spara();rita();$("#rensa").textContent="Börja om";delete $("#rensa").dataset.saker}else{$("#rensa").dataset.saker=1;$("#rensa").textContent="Säker? Tryck igen";setTimeout(()=>{$("#rensa").textContent="Börja om";delete $("#rensa").dataset.saker},3000)}};
$("#exportera").onclick=()=>{
  const ja=KORT.filter(k=>val[k.id]==="ja").map(k=>k.id),nej=KORT.filter(k=>val[k.id]==="nej").map(k=>k.id);
  const txt="SEKTIONSVAL\nJA ("+ja.length+"): "+ja.join(", ")+"\nNEJ ("+nej.length+"): "+nej.join(", ");
  $("#exp-text").value=txt;$("#exp").showModal();$("#exp-text").select();
  if(navigator.clipboard)navigator.clipboard.writeText(txt).catch(()=>{});
};
document.querySelectorAll("[data-f]").forEach(b=>b.onclick=()=>{filter=b.dataset.f;document.querySelectorAll("[data-f]").forEach(x=>x.setAttribute("aria-pressed",x===b?"true":"false"));rita()});
sel.onchange=rita;rita();
</script></body></html>'''


def bygg():
    kort = kortlista()
    antal = sum(1 for k in kort if k["sek"] != "hero")
    doc = SIDA.replace("__DATA__", json.dumps(kort, ensure_ascii=False)).replace("__ANTAL__", str(antal)).replace("__HEROER__", str(len(kort) - antal)).replace("__NYA__", str(sum(1 for k in kort if k["v"][:2] in ("k-", "l-", "m-", "n-"))))
    UT.write_text(doc, encoding="utf-8")
    print(UT, antal, "sektioner", len(kort) - antal, "heroer")


if __name__ == "__main__":
    bygg()
