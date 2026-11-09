"""Hämtar fria bilder (CC0/public domain) från Openverse till en granskningsmapp.

Kör:  python3 koncern/hamta_bilder.py hamta  <utmapp>     # söker och laddar ner kandidater (≈ 200 sökningar/dag tillåts)
      python3 koncern/hamta_bilder.py ark    <utmapp>     # gör kontaktark per tagg för granskning
      python3 koncern/hamta_bilder.py in     <utmapp> [--bort id,id,...]   # lägger godkända bilder i bildbanken

Bilderna kommer från källor där allt är CC0 eller public domain (StockSnap, rawpixel PD, WordPress Photo Directory),
så de får användas fritt, även kommersiellt. Alt-texten blir svensk utifrån sökordet.
"""
import hashlib
import io
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw

ROT = pathlib.Path(__file__).resolve().parent
BANK = ROT.parent / "site" / "bildbank"  # nya bilder ligger direkt i den publicerade bildbanken
TSV = ROT / "bildbank.tsv"
UA = {"User-Agent": "ElevateStudio-bildbank/1.0"}

# tagg: [(engelsk sökfras, svensk alt-text), ...]
SOK = {
    # Bröllopsfotografer
    "brollop": [("wedding ceremony", "Vigsel"), ("wedding couple", "Brudpar"), ("bride groom", "Brud och brudgum")],
    "brudpar": [("bride", "Brud på bröllopsdagen"), ("wedding portrait", "Porträtt av brudpar"), ("newlyweds", "Nygifta"),
                ("couple wedding outdoor", "Brudpar utomhus"), ("wedding kiss", "Brudpar kysser varandra")],
    "detalj": [("wedding rings", "Vigselringar"), ("wedding bouquet", "Brudbukett"), ("wedding details", "Detaljer från bröllopet")],
    "fest": [("wedding reception", "Bröllopsfest"), ("wedding party dance", "Dans på bröllopsfesten")],
    "kamera": [("photographer camera", "Fotograf med kamera")],
    # Arborister
    "arborist": [("tree pruning", "Arborist beskär träd"), ("chainsaw", "Motorsåg i arbete"), ("tree climbing", "Trädklättring"),
                 ("lumberjack", "Skogsarbetare"), ("logging", "Avverkning"), ("tree felling", "Trädfällning"), ("forestry worker", "Skogsarbete"),
                 ("cutting tree", "Trädfällning med motorsåg")],
    "trad": [("old oak tree", "Gammal ek"), ("tree trunk", "Trädstam"), ("park trees", "Träd i park")],
    "ved": [("firewood logs", "Ved och stockar"), ("tree stump", "Stubbe")],
    "tradgard": [("garden", "Trädgård"), ("hedge trimming", "Häckklippning")],
    # Djurfrisörer och djurstylister
    "hund": [("dog portrait", "Hund"), ("happy dog", "Glad hund"), ("dog walking", "Hundpromenad")],
    "trimning": [("dog grooming", "Hundtrimning"), ("dog bath", "Hund badas"), ("poodle", "Pudel"), ("dog groomer", "Hundfrisör"),
                 ("dog brushing", "Hund borstas"), ("dog haircut", "Klippning av hund"), ("pet salon", "Djursalong")],
    "valp": [("puppy", "Valp")],
    "katt": [("cat", "Katt"), ("kitten", "Kattunge")],
    "hundtraning": [("dog training", "Hundträning")],
    # Underskattade B2B-nischer
    "hiss": [("elevator", "Hiss"), ("escalator", "Rulltrappa")],
    "brand": [("fire extinguisher", "Brandsläckare"), ("firefighter", "Brandman"), ("fire sprinkler", "Sprinkler")],
    "ventilation": [("ventilation duct", "Ventilationskanal"), ("air conditioning unit", "Ventilationsaggregat")],
    "tak": [("roofer", "Takläggare"), ("roof tiles", "Takpannor"), ("metal roof", "Plåttak")],
    "skorsten": [("chimney", "Skorsten"), ("fireplace", "Eldstad")],
    "las": [("door lock", "Lås"), ("keys", "Nycklar")],
    "golv": [("wood floor", "Trägolv"), ("parquet floor", "Parkett")],
    "rivning": [("demolition", "Rivning"), ("demolition excavator", "Rivningsmaskin")],
    "mark": [("excavator", "Grävmaskin"), ("earthworks", "Markarbete")],
    "solel": [("solar panels", "Solceller"), ("solar panel roof", "Solceller på tak")],
    "vvs": [("plumber", "Rörmokare"), ("pipes plumbing", "Rör")],
    "maleri": [("house painter", "Målare"), ("painting wall", "Målning av vägg"), ("paint brush", "Pensel och färg")],
    "skadedjur": [("mouse", "Mus"), ("rat", "Råtta"), ("wasp nest", "Getingbo")],
    "stadning": [("cleaning", "Städning"), ("window cleaning", "Fönsterputs"), ("office interior clean", "Rent kontor")],
    "maskin": [("crane construction", "Lyftkran"), ("forklift", "Truck"), ("construction machine", "Entreprenadmaskin")],
    "begravning": [("funeral flowers", "Blommor vid begravning"), ("candle", "Tänt ljus"), ("cemetery", "Kyrkogård")],
    "korskola": [("driving car", "Bilkörning"), ("steering wheel", "Ratt"), ("road", "Väg")],
    "bat": [("boat", "Båt"), ("marina", "Småbåtshamn"), ("sailboat", "Segelbåt")],
    "svets": [("welding", "Svetsning"), ("blacksmith", "Smed"), ("metal workshop", "Verkstad")],
    "glas": [("glass window", "Fönster"), ("glass facade", "Glasfasad")],
    "sten": [("stone wall", "Stenmur"), ("granite", "Granit"), ("stone carving", "Stenhuggning")],
    "hast": [("horse", "Häst"), ("horseshoe", "Hästsko"), ("horse stable", "Stall")],
    # Tredje omgången: tunna taggar
    "ventilation": [("ventilation duct", "Ventilationskanal"), ("air conditioning unit", "Ventilationsaggregat"), ("air duct", "Luftkanal"),
                    ("hvac", "Ventilationsanläggning"), ("rooftop unit", "Aggregat på tak"), ("industrial fan", "Fläkt")],
    "maleri": [("house painter", "Målare"), ("painting wall", "Målning av vägg"), ("paint brush", "Pensel och färg"), ("paint roller", "Färgroller"),
               ("painting house exterior", "Fasadmålning"), ("painted wooden house", "Målat trähus"), ("interior painting", "Invändig målning")],
    "mark": [("excavator", "Grävmaskin"), ("earthworks", "Markarbete"), ("digger", "Grävare"), ("paving stones", "Markstenar"), ("gravel road", "Grusväg"), ("trench", "Schakt")],
    "hiss": [("elevator", "Hiss"), ("escalator", "Rulltrappa"), ("elevator doors", "Hissdörrar"), ("lift lobby", "Hisshall")],
    "hundtraning": [("dog training", "Hundträning"), ("dog agility", "Agility"), ("puppy training", "Valpkurs")],
    "natur": [("swedish forest", "Skog"), ("lake landscape", "Sjö och skog"), ("meadow", "Äng")],
    # Fler byggbilder till bygg och megakoncerner
    "bygg": [("construction worker", "Byggarbetare"), ("carpenter", "Snickare"), ("construction site", "Byggarbetsplats")],
    "interior": [("renovation", "Renovering"), ("kitchen interior", "Kök")],
    "kontor": [("office building", "Kontorshus"), ("skyscraper", "Höghus")],
    "people": [("business meeting", "Möte"), ("team office", "Team på kontor")],
    "stad": [("city skyline", "Stadssiluett")],
    "infra": [("bridge", "Bro"), ("railway", "Järnväg")],
}

KALLOR = "stocksnap,rawpixel,wordpress"


def hamta_json(url):
    for forsok in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            print("  fel", e, file=sys.stderr)
            time.sleep(10 * (forsok + 1))
    return None


def hamta(ut):
    ut = pathlib.Path(ut)
    ut.mkdir(parents=True, exist_ok=True)
    manifest_p = ut / "manifest.json"
    manifest = json.loads(manifest_p.read_text()) if manifest_p.exists() else {}
    klara = {m["fras"] for m in manifest.values()}
    sedda = {m["kalla_url"] for m in manifest.values()}
    for tagg, fraser in SOK.items():
        for fras, alt in fraser:
            if fras in klara:
                continue
            q = urllib.parse.urlencode({"q": fras, "license": "cc0,pdm", "page_size": 20, "source": KALLOR, "mature": "false"})
            d = hamta_json(f"https://api.openverse.org/v1/images/?{q}")
            time.sleep(3.2)
            if not d:
                continue
            n = 0
            for r in d.get("results", []):
                url = r.get("url")
                if not url or url in sedda or (r.get("width") or 0) < 900:
                    continue
                if (r.get("width") or 1) / max(1, r.get("height") or 1) < 1.2:
                    continue  # bara liggande bilder
                id_ = "ov" + hashlib.md5(url.encode()).hexdigest()[:10]
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as resp:
                        im = Image.open(io.BytesIO(resp.read())).convert("RGB")
                except Exception as e:  # noqa: BLE001
                    print("  kunde inte ladda", url, e, file=sys.stderr)
                    continue
                if im.width < 900:
                    continue
                im.thumbnail((1600, 1600))
                im.save(ut / f"{id_}.jpg", quality=78, optimize=True, progressive=True)
                manifest[id_] = dict(tagg=tagg, fras=fras, alt=alt, kalla=r.get("source"), kalla_url=url, sida=r.get("foreign_landing_url"),
                                     titel=r.get("title"), licens=r.get("license"))
                sedda.add(url)
                n += 1
            if n == 0:  # markera frasen som sökt även om inget passade
                manifest[f"tom-{tagg}-{fras}"] = dict(tagg=tagg, fras=fras, tom=True, kalla_url=fras)
            print(f"{tagg:12} {fras:28} {n} bilder", flush=True)
            manifest_p.write_text(json.dumps(manifest, ensure_ascii=False, indent=1))


def ark(ut):
    ut = pathlib.Path(ut)
    manifest = json.loads((ut / "manifest.json").read_text())
    per = {}
    for id_, m in manifest.items():
        if not m.get("tom"):
            per.setdefault(m["tagg"], []).append(id_)
    (ut / "ark").mkdir(exist_ok=True)
    for tagg, ids in per.items():
        cols, tw, th = 6, 300, 200
        rows = (len(ids) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), "white")
        d = ImageDraw.Draw(sheet)
        for i, id_ in enumerate(ids):
            im = Image.open(ut / f"{id_}.jpg")
            im.thumbnail((tw - 4, th - 4))
            x, y = (i % cols) * tw, (i // cols) * (th + 18)
            sheet.paste(im, (x + 2, y + 2))
            d.text((x + 4, y + th), f"{i}:{id_}", fill="black")
        sheet.save(ut / "ark" / f"{tagg}.jpg", quality=70)
        print(tagg, len(ids))


def in_(ut, bort):
    ut = pathlib.Path(ut)
    manifest = json.loads((ut / "manifest.json").read_text())
    befintliga = {line.split("\t")[0] for line in TSV.read_text(encoding="utf-8").splitlines() if line.strip()}
    rader, kallor = [], []
    for id_, m in manifest.items():
        if m.get("tom") or id_ in bort or id_ in befintliga:
            continue
        im = Image.open(ut / f"{id_}.jpg")
        im.save(BANK / f"{id_}.jpg", quality=76, optimize=True, progressive=True)
        s = im.copy()
        s.thumbnail((700, 700))
        s.save(BANK / f"{id_}-s.jpg", quality=74, optimize=True, progressive=True)
        rader.append(f"{id_}\t{m['tagg']}\t{m['alt']}")
        kallor.append(f"{id_}\t{m['kalla']}\t{m['licens']}\t{m['sida']}")
    with TSV.open("a", encoding="utf-8") as f:
        f.write("\n".join(rader) + "\n")
    with (ROT / "bildkallor.tsv").open("a", encoding="utf-8") as f:
        f.write("\n".join(kallor) + "\n")
    print("lade till", len(rader))


if __name__ == "__main__":
    kmd, mapp = sys.argv[1], sys.argv[2]
    if kmd == "hamta":
        hamta(mapp)
    elif kmd == "ark":
        ark(mapp)
    else:
        b = set(sys.argv[4].split(",")) if len(sys.argv) > 4 and sys.argv[3] == "--bort" else set()
        in_(mapp, b)
