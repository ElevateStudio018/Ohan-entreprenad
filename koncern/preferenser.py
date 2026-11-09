"""Användarens smak, från Sektionsväljaren (koncern/preferenser.json).

Generatorn (bygg_nischer.differentiera) och koncern-agenten (paket.nytt) väljer bara bland varianter användaren
har sagt ja till. Varianter som skrivits efter valet, i användarens smak (prefix k-, l-, m-, n-), räknas som ja
tills användaren har bedömt dem. Sektioner utan någon godkänd variant tas bort ur sektionsordningen.
"""
import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parent
FIL = ROT / "preferenser.json"
SMAKPREFIX = ("k-", "l-", "m-", "n-")
OVERLAY = ["helskarm", "band", "centrerad", "statement", "mosaik"]


def _data():
    return json.loads(FIL.read_text(encoding="utf-8")) if FIL.exists() else {"ja": {}, "nej": {}, "hero_ja": [], "hero_nej": []}


def godkanda(alla_varianter):
    """sektion -> lista av varianter som får användas."""
    d = _data()
    ut = {}
    for sek, vs in alla_varianter.items():
        ja = [v for v in vs if v in d["ja"].get(sek, []) or (v.startswith(SMAKPREFIX) and v not in d["nej"].get(sek, []))]
        if ja:
            ut[sek] = ja
    return ut


def herotext():
    d = _data()
    return [h for h in d["hero_ja"] if not h.startswith("standard")] or ["nere"]


def heroer(profil):
    d = _data()
    ut = [h for h in OVERLAY if f"standard-{h}" not in d["hero_nej"]]
    if profil == "mega" and "standard-kurs" in d["hero_ja"]:
        ut.append("kurs")
    return ut
