"""Register för sektionsvarianter (utöver de inbyggda i generera.py).

En variant är en funktion som tar Sajt-objektet och returnerar HTML för en hel <section>. Registrera med dekoratorn:

    from varianter import variant, E, ikon, PIL

    @variant("vagval", "kakel")
    def vagval_kakel(s):
        t = s.tjanster()           # listan med tjänster
        ...
        return f'<section class="sek {s.bg("vagval")}" aria-labelledby="vv-h"><div class="wrap">{s.huvud(...)}...</div></section>'

Varje fil varianter_<x>.py har en egen varianter_<x>.css som läggs till efter bas.css på alla sajter. Klassnamn i en
variant ska börja med ett eget prefix (t.ex. .vk- för vagval/kakel) så att de inte krockar med något annat.
"""
import html
import importlib
import pathlib
import sys

ROT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROT))
from ikoner import ikon  # noqa: E402

E = html.escape
PIL = ikon("pil", "pil")
REG = {}

# Inbyggda varianter i generera.py (sektion -> varianter). "standard" = sektionen har bara en form där.
INBYGGDA = {
    "vagval": ["rutor", "rader", "chips", "nummer", "cirklar", "bildrutor", "lankar", "register", "expertis"],
    "bolag": ["kort", "flikar", "lista", "tabell", "rund", "vagg"],
    "siffror": ["rad", "jatte", "band", "dashboard"],
    "nyheter": ["lista", "rad", "tidning"],
    "berattelser": ["tre", "stor", "rad", "band"],
    "projekt": ["karusell", "lista", "feature"],
    "hb": ["split", "helbild", "siffror", "kort"],
    "ir": ["kort", "tabell", "kompakt"],
    "panel": ["panel", "helbild", "jobb"],
    "snabb": ["rutor", "band"],
    "omdomen": ["kort", "stor"],
    "process": ["standard"], "citat": ["standard"], "service": ["standard"], "tidslinje": ["standard"], "kontor": ["standard"],
    "priser": ["standard"], "faq": ["standard"], "galleri": ["standard"], "boka": ["standard"], "certifikat": ["standard"],
    "logos": ["standard"],
}


def variant(sektion, namn):
    def dek(fn):
        REG[(sektion, namn)] = fn
        return fn
    return dek


def ladda():
    for p in sorted(ROT.glob("varianter_*.py")):
        importlib.import_module(p.stem)


def css():
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(ROT.glob("varianter_*.css")))


def alla():
    """Alla varianter per sektion (inbyggda + registrerade)."""
    ladda()
    ut = {k: list(v) for k, v in INBYGGDA.items()}
    for (sek, namn) in REG:
        ut.setdefault(sek, [])
        if namn not in ut[sek]:
            ut[sek].append(namn)
    return ut
