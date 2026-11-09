"""Bygger röstsidan (artifact) där användaren kryssar i sektionsvarianter och hero-layouter hon/han gillar.

Kör:  python3 koncern/rostsida.py <utfil.html>
Bilderna bäddas in som data-URI (miniatyrer), rösterna sparas i artifactens db (samlingen "val").
"""
import base64
import html
import io
import json
import pathlib
import sys

from PIL import Image

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT / "mall"))
sys.path.insert(0, str(ROT))
import varianter  # noqa: E402
from katalog import NAMN  # noqa: E402

E = html.escape
BILDER = ROT.parent / "site" / "sektioner" / "bilder"


def tumme(path, w=560, maxh=700, q=52):
    im = Image.open(path).convert("RGB")
    if im.width > w:
        im = im.resize((w, int(im.height * w / im.width)))
    if im.height > maxh:
        im = im.crop((0, 0, im.width, maxh))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def heroer():
    """Ett exempel per hero-layout, från sajtbibliotekets miniatyrer."""
    ut, sedda = [], set()
    for p in sorted((ROT / "nischer").glob("*/paket/*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        ht = d.get("herotext", "standard")
        nyckel = ht if ht != "standard" else "standard-" + d["hero"]
        if nyckel in sedda:
            continue
        t = ROT.parent / "site" / "sajter" / p.parts[-3] / p.stem / "tumme.jpg"
        if t.exists():
            sedda.add(nyckel)
            ut.append((nyckel, f'{d["hero"]} · {d["typsnitt"]["rubrik"]}', t))
    return ut


def bygg(utfil):
    alla = varianter.alla()
    kort, nr = [], 0
    for sek, vs in alla.items():
        for v in vs:
            f = BILDER / f"{sek}-{v}.jpg"
            if not f.exists():
                continue
            nr += 1
            kort.append(dict(id=f"{sek}--{v}", nr=nr, grupp="sektion", sek=sek, sekNamn=NAMN.get(sek, sek), v=v, img=tumme(f)))
    for nyckel, etikett, t in heroer():
        kort.append(dict(id=f"hero--{nyckel}", nr=None, grupp="hero", sek="hero", sekNamn="Hero-layout", v=nyckel, info=etikett, img=tumme(t, 560, 350, 55)))
    data = json.dumps(kort, ensure_ascii=False)
    antal = sum(1 for k in kort if k["grupp"] == "sektion")
    sektioner = list(alla)
    doc = MALL.replace("__DATA__", data).replace("__ANTAL__", str(antal)).replace("__SEK__", json.dumps([[s, NAMN.get(s, s)] for s in sektioner], ensure_ascii=False))
    pathlib.Path(utfil).write_text(doc, encoding="utf-8")
    print(utfil, antal, "sektioner,", len(kort) - antal, "heroer,", round(len(doc) / 1e6, 1), "MB")


MALL = r'''<title>Sektionsväljaren</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Instrument+Sans:wght@400;500;600&display=swap">
<style>
/* Ett kontaktark: stora miniatyrer i rutnät, en tydlig "Gillar"-knapp per variant, filter överst */
:root{--bg:#f3f1ec;--yta:#fffefb;--ink:#1a1916;--mut:#6b675e;--linje:#dcd8ce;--gron:#1f7a4d;--gron-bg:#e2f2e8;--mark:#2a3a8f;
--disp:"Bricolage Grotesque",system-ui,sans-serif;--text:"Instrument Sans",system-ui,sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171613;--yta:#211f1b;--ink:#efece4;--mut:#a39e92;--linje:#38352e;--gron:#5fd08f;--gron-bg:#1d3527;--mark:#9fb0ff;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#171613;--yta:#211f1b;--ink:#efece4;--mut:#a39e92;--linje:#38352e;--gron:#5fd08f;--gron-bg:#1d3527;--mark:#9fb0ff;color-scheme:dark}
*{box-sizing:border-box}body{background:var(--bg);color:var(--ink);font:15px/1.5 var(--text);margin:0}
.ram{max-width:1500px;margin:auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{padding-block:40px 18px}h1{font:700 clamp(32px,5vw,58px)/1 var(--disp);letter-spacing:-.03em;margin:0;text-wrap:balance}
header p{color:var(--mut);max-width:62ch;margin:12px 0 0}
.status{margin-top:10px;font-size:13px;color:var(--mut)}.status b{color:var(--ink)}
.verktyg{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-block:1px solid var(--linje)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
.verktyg .ram{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding-block:10px}
.verktyg select,.verktyg button{font:500 14px var(--text);padding:8px 12px;border-radius:999px;border:1px solid var(--linje);background:var(--yta);color:var(--ink);cursor:pointer}
.verktyg button[aria-pressed="true"]{background:var(--ink);color:var(--bg);border-color:var(--ink)}
.verktyg .raknare{margin-left:auto;font:600 14px var(--text);font-variant-numeric:tabular-nums}
.verktyg button:focus-visible,.verktyg select:focus-visible,.gilla:focus-visible,textarea:focus-visible{outline:2px solid var(--mark);outline-offset:2px}
main{padding-block:24px 64px}
.rutnat{list-style:none;margin:0;padding:0;display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr))}
.kort{background:var(--yta);border:1px solid var(--linje);border-radius:6px;overflow:hidden;display:flex;flex-direction:column;min-width:0}
.kort.vald{border-color:var(--gron);box-shadow:0 0 0 2px var(--gron)}
.bild{display:block;width:100%;max-height:420px;overflow:hidden;background:var(--linje);cursor:zoom-in;border:0;padding:0}
.bild img{display:block;width:100%;height:auto}
.info{display:grid;gap:8px;padding:12px 14px 14px}
.rad{display:flex;align-items:center;gap:10px;justify-content:space-between}
.namn{min-width:0}.namn b{font:600 15px var(--text)}.namn span{display:block;font-size:12.5px;color:var(--mut)}
.nr{font:500 12px var(--text);color:var(--mut);font-variant-numeric:tabular-nums}
.gilla{flex:none;font:600 14px var(--text);padding:8px 14px;border-radius:999px;border:1.5px solid var(--linje);background:transparent;color:var(--ink);cursor:pointer}
.gilla[aria-pressed="true"]{background:var(--gron-bg);border-color:var(--gron);color:var(--gron)}
textarea{width:100%;font:14px/1.4 var(--text);padding:8px 10px;border:1px solid var(--linje);border-radius:6px;background:var(--bg);color:var(--ink);resize:vertical;min-height:38px}
h2{font:700 24px var(--disp);letter-spacing:-.02em;margin:34px 0 14px}
.tom{color:var(--mut);padding:40px 0}
dialog{border:0;padding:0;max-width:min(1200px,96vw);background:var(--yta)}dialog img{display:block;max-width:100%}
dialog::backdrop{background:rgba(0,0,0,.6)}dialog form{position:sticky;top:0;text-align:right;padding:8px;background:var(--yta)}
dialog button{font:600 14px var(--text);padding:8px 14px;border-radius:999px;border:1px solid var(--linje);background:var(--yta);color:var(--ink);cursor:pointer}
@media (prefers-reduced-motion:no-preference){.kort{transition:box-shadow .15s,border-color .15s}}
</style>
<header class="ram"><h1>Sektionsväljaren</h1>
<p>__ANTAL__ sektionsvarianter och alla hero-layouter från sajtbiblioteket. Tryck <b>Gillar</b> på dem du vill att agenten ska använda mer – skriv gärna en rad om varför. Allt sparas direkt och Claude läser dina val.</p>
<p class="status" id="status">Ansluter till lagringen …</p></header>
<div class="verktyg"><div class="ram">
<button type="button" id="f-alla" aria-pressed="true">Alla</button><button type="button" id="f-valda" aria-pressed="false">Mina val</button><button type="button" id="f-ovalda" aria-pressed="false">Inte valda</button>
<label for="f-sek" class="sr" style="position:absolute;left:-9999px">Sektion</label><select id="f-sek"><option value="">Alla sektioner</option><option value="hero">Hero-layouter</option></select>
<span class="raknare" id="raknare">0 valda</span></div></div>
<main class="ram" id="lista"></main>
<dialog id="zoom"><form method="dialog"><button>Stäng</button></form><img id="zoom-img" alt=""></dialog>
<script>
const KORT=__DATA__, SEK=__SEK__;
let val={}, db=null, filter="alla";
const $=s=>document.querySelector(s);
const sel=$("#f-sek"); SEK.forEach(([k,n])=>{const o=document.createElement("option");o.value=k;o.textContent=n;sel.append(o)});
function antalValda(){return Object.values(val).filter(x=>x&&x.gillar).length}
function rita(){
  const lista=$("#lista"); lista.textContent="";
  const synliga=KORT.filter(k=>(!sel.value||k.sek===sel.value)&&(filter==="alla"||(filter==="valda")===!!(val[k.id]&&val[k.id].gillar)));
  if(!synliga.length){const p=document.createElement("p");p.className="tom";p.textContent=filter==="valda"?"Du har inte valt något här ännu. Tryck Gillar på en variant så hamnar den här.":"Inga varianter matchar filtret.";lista.append(p)}
  let grupp=null, ul=null;
  for(const k of synliga){
    const g=k.grupp==="hero"?"Hero-layouter":k.sekNamn;
    if(g!==grupp){grupp=g;const h=document.createElement("h2");h.textContent=g;ul=document.createElement("ul");ul.className="rutnat";lista.append(h,ul)}
    const v=val[k.id]||{};
    const li=document.createElement("li");li.className="kort"+(v.gillar?" vald":"");
    const b=document.createElement("button");b.type="button";b.className="bild";b.setAttribute("aria-label","Förstora "+k.v);
    const img=document.createElement("img");img.src=k.img;img.alt=k.sekNamn+" – "+k.v;img.loading="lazy";b.append(img);
    b.onclick=()=>{$("#zoom-img").src=k.img;$("#zoom").showModal()};
    const info=document.createElement("div");info.className="info";
    const rad=document.createElement("div");rad.className="rad";
    const namn=document.createElement("div");namn.className="namn";
    const bb=document.createElement("b");bb.textContent=k.v;const sp=document.createElement("span");sp.textContent=(k.nr?"#"+k.nr+" · ":"")+(k.info||k.sekNamn);namn.append(bb,sp);
    const knapp=document.createElement("button");knapp.type="button";knapp.className="gilla";knapp.setAttribute("aria-pressed",v.gillar?"true":"false");knapp.textContent=v.gillar?"✓ Gillar":"Gillar";
    knapp.onclick=()=>spara(k.id,{gillar:!v.gillar});
    rad.append(namn,knapp);
    const ta=document.createElement("textarea");ta.id="not-"+k.id;ta.placeholder="Kommentar (valfritt)";ta.value=v.not||"";ta.rows=1;
    ta.onchange=()=>spara(k.id,{not:ta.value.trim()});
    info.append(rad,ta);li.append(b,info);ul.append(li);
  }
  $("#raknare").textContent=antalValda()+" valda";
}
async function spara(id,andring){
  val[id]=Object.assign({},val[id]||{},andring);rita();
  if(!db){$("#status").textContent="Valet syns här men kunde inte sparas: lagringen är inte ansluten (logga in på claude.ai och ladda om).";return}
  try{await db.doc("val/"+id).set(Object.assign({gillar:false,not:""},val[id],{tid:new Date().toISOString()}));$("#status").innerHTML="Sparat. <b>"+antalValda()+"</b> valda totalt.";}
  catch(e){$("#status").textContent="Kunde inte spara ("+(e&&e.code||"fel")+"). Försök igen om en stund.";}
}
["alla","valda","ovalda"].forEach(f=>$("#f-"+f).onclick=()=>{filter=f;["alla","valda","ovalda"].forEach(x=>$("#f-"+x).setAttribute("aria-pressed",x===f?"true":"false"));rita()});
sel.onchange=rita;
rita();
(async()=>{
  const timer=setTimeout(()=>{$("#status").textContent="Lagringen svarar inte – du kan titta, men val sparas inte just nu."},10000);
  try{
    db=window.claude?await window.claude.use("db"):null;
    if(!db){clearTimeout(timer);$("#status").textContent="Lagringen är inte tillgänglig i den här vyn (logga in på claude.ai). Du kan bläddra men inte spara.";return}
    db.collection("val").onSnapshot(snap=>{clearTimeout(timer);const ny={};(snap.docs||snap).forEach(d=>{const x=d.data?d.data():d;ny[d.id||x.id]=x});val=ny;if(document.activeElement&&document.activeElement.tagName==="TEXTAREA"){$("#raknare").textContent=antalValda()+" valda"}else{rita()}$("#status").innerHTML="Ansluten. <b>"+antalValda()+"</b> valda.";},err=>{clearTimeout(timer);$("#status").textContent="Kunde inte läsa sparade val ("+(err&&err.code||"fel")+").";});
  }catch(e){clearTimeout(timer);$("#status").textContent="Lagringen kunde inte startas.";}
})();
</script>
'''

if __name__ == "__main__":
    bygg(sys.argv[1])
