"""Sammanställer research/data/resultat.json till nyckeltal per sajt och totalt.

Kör:  python3 research/sammanstall.py research/data

Skriver data/sammanstallning.json, som rapport.py och koncern-generatorn läser.
"""
import colorsys
import json
import math
import pathlib
import re
import statistics
import sys
from collections import Counter

DATA = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "research/data")

# --- Typsnitt -------------------------------------------------------------------------------------------------------
FONT_KIND = [
    ("serif", ["georgia", "times", "playfair", "merriweather", "lora", "baskerville", "source serif", "tiempos", "freight", "canela",
               "garamond", "fraunces", "recoleta", "dm serif", "serif display", "noto serif", "pt serif", "crimson", "cormorant", "domine",
               "spectral", "newsreader", "ivar", "gt sectra", "editorial", "minion", "caslon", "bodoni", "didot", "roslindale", "reckless"]),
    ("geometrisk", ["montserrat", "poppins", "futura", "gotham", "avenir", "circular", "proxima", "sofia", "outfit", "manrope", "dm sans",
                    "plus jakarta", "sora", "gilroy", "brandon", "museo", "raleway", "questrial", "nunito", "mulish", "urbanist", "lexend",
                    "red hat", "figtree", "jost", "kumbh", "quicksand", "comfortaa", "century gothic", "tt norms", "tt commons", "gordita",
                    "geomanist", "sharp grotesk", "cera", "campton", "axiforma", "eina", "visby", "hk grotesk", "satoshi", "general sans",
                    "space grotesk", "albert sans", "be vietnam", "hanken"]),
    ("humanistisk", ["open sans", "lato", "source sans", "frutiger", "myriad", "noto sans", "fira sans", "pt sans", "segoe", "calibri",
                     "gill sans", "verdana", "ubuntu", "trebuchet", "tahoma", "oxygen", "cabin", "catamaran", "asap", "hind", "karla",
                     "libre franklin", "franklin gothic", "vollkorn sans", "mukta", "titillium", "assistant", "heebo", "rubik", "overpass",
                     "nunito sans", "fs me", "ff meta", "meta", "scala sans", "sanuk", "colfax"]),
    ("grotesk", ["helvetica", "arial", "inter", "roboto", "haas", "aktiv", "graphik", "suisse", "untitled", "gt america", "akzidenz",
                 "work sans", "ibm plex", "barlow", "archivo", "public sans", "system-ui", "-apple-system", "blinkmacsystemfont", "sf pro",
                 "neue montreal", "pp neue", "gt walsheim", "maison", "favorit", "basis grotesque", "founders grotesk", "atlas grotesk",
                 "national", "unica", "univers", "din", "ff din", "roboto condensed", "oswald", "bebas", "barlow condensed", "instrument sans",
                 "schibsted", "hanken grotesk", "geist", "replica", "neue haas", "aeonik", "apercu", "grotesk", "grotesque", "sans-serif"]),
]
GOOGLE = {"inter", "roboto", "open sans", "lato", "montserrat", "poppins", "work sans", "ibm plex sans", "barlow", "archivo", "manrope",
          "dm sans", "plus jakarta sans", "sora", "outfit", "figtree", "nunito", "nunito sans", "source sans pro", "source sans 3",
          "raleway", "mulish", "rubik", "karla", "playfair display", "merriweather", "lora", "fraunces", "libre franklin", "red hat display",
          "space grotesk", "albert sans", "urbanist", "lexend", "jost", "public sans", "instrument sans", "noto sans", "fira sans", "pt sans",
          "oswald", "barlow condensed", "roboto condensed", "heebo", "hind", "asap", "cabin", "titillium web", "overpass", "quicksand"}
SYSTEM = {"arial", "helvetica", "helvetica neue", "times new roman", "georgia", "verdana", "segoe ui", "system-ui", "-apple-system",
          "sans-serif", "serif", "tahoma", "trebuchet ms", "calibri"}


def font_kind(name):
    n = (name or "").lower()
    for kind, keys in FONT_KIND:
        if any(k in n for k in keys):
            return kind
    return "eget/okänt"


def font_source(name):
    n = (name or "").lower().strip()
    if n in SYSTEM:
        return "systemtypsnitt"
    if n in GOOGLE:
        return "Google Fonts"
    return "licensierat/eget"


def clean_font(name):
    n = (name or "").strip()
    n = re.sub(r"(?i)[-_ ]?(regular|medium|bold|light|web|webfont|variable|vf|display|text|book|semibold|normal|\d+)$", "", n).strip(" -_")
    return n or name


# --- Färger ---------------------------------------------------------------------------------------------------------
def parse_color(s):
    """CSS-färg från getComputedStyle -> (r, g, b, a) 0-255 eller None."""
    if not s:
        return None
    m = re.match(r"rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)", s)
    if m:
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        a = float(m.group(4)) if m.group(4) else 1.0
        return r, g, b, a
    m = re.match(r"oklab\(([-\d.e]+)\s+([-\d.e]+)\s+([-\d.e]+)(?:\s*/\s*([\d.]+))?\)", s)
    if m:
        L, A, B = (float(m.group(i)) for i in (1, 2, 3))
        a = float(m.group(4)) if m.group(4) else 1.0
        l_ = (L + 0.3963377774 * A + 0.2158037573 * B) ** 3
        m_ = (L - 0.1055613458 * A - 0.0638541728 * B) ** 3
        s_ = (L - 0.0894841775 * A - 1.2914855480 * B) ** 3
        lin = [4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
               -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
               -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_]
        out = []
        for c in lin:
            c = max(0.0, min(1.0, c))
            out.append(255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055))
        return out[0], out[1], out[2], a
    return None


def hexc(c):
    return "#%02x%02x%02x" % tuple(int(round(x)) for x in c[:3])


def lum(c):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c[:3]
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def hsl(c):
    h, l, s = colorsys.rgb_to_hls(*(x / 255 for x in c[:3]))
    return h * 360, s, l


def is_chromatic(c):
    h, s, l = hsl(c)
    return c[3] > 0.5 and s > 0.28 and 0.12 < l < 0.85


def hue_family(c):
    h, s, l = hsl(c)
    if not is_chromatic(c):
        if l < 0.2:
            return "svart/antracit"
        if l > 0.9:
            return "vit"
        return "grå"
    if h < 15 or h >= 345:
        return "röd"
    if h < 40:
        return "orange/terrakotta"
    if h < 65:
        return "gul/guld"
    if h < 165:
        return "grön"
    if h < 195:
        return "turkos/petrol"
    if h < 250:
        return "blå"
    if h < 290:
        return "lila"
    return "rosa/vinröd"


def brand_color(r):
    """Den mest använda mättade färgen bland knappar, länkar och bakgrunder."""
    score = Counter()
    for b in r.get("btn_samples") or []:
        for key, w in (("bg", 40), ("fg", 12)):
            c = parse_color(b.get(key))
            if c and is_chromatic(c):
                score[hexc(c)] += w
    for col, n in r.get("link_colors") or []:
        c = parse_color(col)
        if c and is_chromatic(c):
            score[hexc(c)] += 6 * n
    for col, area in r.get("bg_colors") or []:
        c = parse_color(col)
        if c and is_chromatic(c):
            score[hexc(c)] += area / 4000
    for col, n in r.get("text_colors") or []:
        c = parse_color(col)
        if c and is_chromatic(c):
            score[hexc(c)] += 2 * n
    if not score:
        # Monokrom sajt: ta den mörkaste stora textfärgen
        return None
    return score.most_common(1)[0][0]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (1,)


# --- Grupper --------------------------------------------------------------------------------------------------------
def radius_bucket(v, h=None):
    if v is None:
        return None
    if h and v >= h / 2 - 1 and v > 10:
        return "piller"
    if v <= 1:
        return "kantig (0 px)"
    if v <= 6:
        return "lätt rundad (2–6 px)"
    if v <= 16:
        return "rundad (8–16 px)"
    return "kraftigt rundad (>16 px)"


def mode(values):
    vals = [v for v in values if v is not None]
    return Counter(vals).most_common(1)[0][0] if vals else None


def site(r):
    out = {k: r.get(k) for k in ("namn", "kategori", "url", "slug", "final_url", "title", "h1_text")}
    fd = clean_font(r.get("font_h1") or r.get("font_h2") or r.get("font_body"))
    fb = clean_font(r.get("font_body"))
    out["font_display"], out["font_body"] = fd, fb
    out["font_kind"] = font_kind(fd)
    out["font_source"] = font_source(fd)
    out["two_fonts"] = bool(fd and fb and fd.lower() != fb.lower())
    out["h1_size"] = round(r["h1_size"]) if r.get("h1_size") else None
    out["h1_weight"] = int(float(r["h1_weight"])) if r.get("h1_weight") else None
    out["h1_upper"] = r.get("h1_transform") == "uppercase"
    # Knappar
    btns = [b for b in r.get("btn_samples") or [] if b.get("text")]
    br = [radius_bucket(b["r"], b["h"]) for b in btns]
    out["btn_shape"] = mode(br) or "inga tydliga knappar"
    out["btn_radius_px"] = statistics.median([b["r"] for b in btns]) if btns else None
    out["btn_outline"] = bool(btns) and sum("rgba(0, 0, 0, 0)" in b["bg"] for b in btns) > len(btns) / 2
    out["btn_upper"] = bool(btns) and sum(b["upper"] for b in btns) > len(btns) / 2
    # Bilder och kort
    ir = [x for x in r.get("img_radius") or []]
    out["img_shape"] = radius_bucket(statistics.median(ir)) if ir else "få bilder"
    out["img_radius_px"] = statistics.median(ir) if ir else None
    cr = r.get("card_radius") or []
    out["card_radius_px"] = statistics.median(cr) if cr else None
    out["card_shadow"] = (r.get("card_shadow") or 0) > 0
    # Header
    hb = parse_color(r.get("header_bg"))
    if hb is None or hb[3] < 0.3:
        out["header_type"] = "transparent över hero"
    elif lum(hb) < 0.18:
        out["header_type"] = "mörk/färgad"
    else:
        out["header_type"] = "ljus solid"
    out["header_sticky"] = bool(r.get("header_sticky"))
    out["header_h"] = r.get("header_h")
    out["nav_count"] = r.get("nav_count")
    out["nav_texts"] = r.get("nav_texts") or []
    out["nav_upper"] = bool(r.get("nav_upper"))
    out["burger_desktop"] = bool(r.get("has_burger_desktop"))
    out["search"] = bool(r.get("has_search"))
    # Hero
    hv = r.get("hero_h_vh") or 0
    if r.get("hero_video"):
        out["hero_type"] = "video"
    elif r.get("hero_image") and r.get("hero_overlay") and hv >= 0.8:
        out["hero_type"] = "helskärmsbild med text"
    elif r.get("hero_image") and r.get("hero_overlay"):
        out["hero_type"] = "bild med text ovanpå"
    elif r.get("hero_image"):
        out["hero_type"] = "text bredvid/ovanför bild"
    else:
        out["hero_type"] = "typografisk/ingen bild"
    out["hero_vh"] = hv
    # Färger
    bc = brand_color(r)
    out["brand"] = bc
    out["brand_family"] = hue_family(hex2rgb(bc)) if bc else "monokrom"
    fb_ = parse_color(r.get("footer_bg"))
    out["footer_dark"] = bool(fb_ and fb_[3] > 0.5 and lum(fb_) < 0.2)
    out["footer_color"] = hexc(fb_) if fb_ and fb_[3] > 0.5 else None
    bgs = []
    for col, area in r.get("bg_colors") or []:
        c = parse_color(col)
        if c and c[3] > 0.5:
            bgs.append((hexc(c), area))
    out["palette"] = [h for h, _ in bgs[:6]]
    tc = parse_color((r.get("text_colors") or [[None]])[0][0])
    out["text_color"] = hexc(tc) if tc else None
    out["text_pure_black"] = bool(tc and max(tc[:3]) < 20)
    # Koncernsignaler
    for k in ("sig_investor", "sig_hallbarhet", "sig_karriar", "sig_press", "sig_english"):
        out[k] = bool(r.get(k))
    out["max_width"] = r.get("max_width")
    out["page_h"] = r.get("page_h")
    return out


def pct(sites, pred):
    return round(100 * sum(1 for s in sites if pred(s)) / len(sites))


def dist(sites, key):
    c = Counter(s[key] for s in sites if s.get(key) is not None)
    return [[k, v] for k, v in c.most_common()]


def main():
    raw = json.loads((DATA / "resultat.json").read_text(encoding="utf-8"))
    manuell = json.loads((DATA / "manuell.json").read_text(encoding="utf-8"))
    ns = {}
    exec((pathlib.Path(__file__).parent / "typsnitt_manuell.py").read_text(encoding="utf-8"), ns)
    typ = ns["T"]
    ok = [r for r in raw if r.get("ok") and manuell.get(r["slug"], {}).get("med")]
    sites = []
    for r in ok:
        s = site(r)
        m = manuell[r["slug"]]
        s.update(arketyp=m["arketyp"], betyg=m["betyg"], kommentar=m["kommentar"])
        t = typ[r["slug"]]
        s.update(font_display=t[0], font_kind=t[1], font_own=t[2])
        sites.append(s)
    h1 = [s["h1_size"] for s in sites if s["h1_size"]]
    total = {
        "antal": len(sites),
        "font_kind": dist(sites, "font_kind"),
        "font_source": dist(sites, "font_source"),
        "fonts": [[k, v] for k, v in Counter(s["font_display"] for s in sites if s["font_display"]).most_common(25)],
        "btn_shape": dist(sites, "btn_shape"),
        "img_shape": dist(sites, "img_shape"),
        "header_type": dist(sites, "header_type"),
        "hero_type": dist(sites, "hero_type"),
        "brand_family": dist(sites, "brand_family"),
        "h1_median": statistics.median(h1) if h1 else None,
        "h1_quartiles": statistics.quantiles(h1, n=4) if len(h1) > 4 else None,
        "pct": {
            "sticky": pct(sites, lambda s: s["header_sticky"]),
            "investor": pct(sites, lambda s: s["sig_investor"]),
            "hallbarhet": pct(sites, lambda s: s["sig_hallbarhet"]),
            "karriar": pct(sites, lambda s: s["sig_karriar"]),
            "press": pct(sites, lambda s: s["sig_press"]),
            "english": pct(sites, lambda s: s["sig_english"]),
            "search": pct(sites, lambda s: s["search"]),
            "burger": pct(sites, lambda s: s["burger_desktop"]),
            "footer_dark": pct(sites, lambda s: s["footer_dark"]),
            "two_fonts": pct(sites, lambda s: s["two_fonts"]),
            "h1_upper": pct(sites, lambda s: s["h1_upper"]),
            "nav_upper": pct(sites, lambda s: s["nav_upper"]),
            "btn_outline": pct(sites, lambda s: s["btn_outline"]),
            "card_shadow": pct(sites, lambda s: s["card_shadow"]),
            "pure_black": pct(sites, lambda s: s["text_pure_black"]),
        },
        "nav_words": [[k, v] for k, v in Counter(t.lower() for s in sites for t in s["nav_texts"]).most_common(40)],
    }
    by_cat = {}
    for s in sites:
        by_cat.setdefault(s["kategori"], []).append(s)
    total["kategorier"] = [[k, len(v)] for k, v in sorted(by_cat.items(), key=lambda kv: -len(kv[1]))]
    total["arketyp"] = dist(sites, "arketyp")
    total["betyg"] = dist(sites, "betyg")
    total["pct"]["eget_typsnitt"] = pct(sites, lambda s: s["font_own"])
    # Vad skiljer de bästa (betyg 4–5) från de svaga (1–2)?
    topp = [s for s in sites if s["betyg"] >= 4]
    svag = [s for s in sites if s["betyg"] <= 2]
    jfr = {}
    for namn, pred in [
        ("Helskärms- eller stor bildhero", lambda s: s["hero_vh"] >= 0.8 or s["hero_type"] in ("video", "helskärmsbild med text")),
        ("Film i heron", lambda s: s["hero_type"] == "video"),
        ("Transparent header över hero", lambda s: s["header_type"] == "transparent över hero"),
        ("Eget varumärkestypsnitt", lambda s: s["font_own"]),
        ("Serif i rubriker", lambda s: s["font_kind"] == "serif"),
        ("Pillerformade knappar", lambda s: s["btn_shape"] == "piller"),
        ("Kantiga bilder (0 px)", lambda s: s["img_shape"] == "kantig (0 px)"),
        ("Rubrik ≥ 56 px", lambda s: (s["h1_size"] or 0) >= 56),
        ("Investerarlänk", lambda s: s["sig_investor"]),
        ("Hållbarhetslänk", lambda s: s["sig_hallbarhet"]),
        ("Engelsk version", lambda s: s["sig_english"]),
        ("Mörk sidfot", lambda s: s["footer_dark"]),
        ("Hamburgermeny på dator", lambda s: s["burger_desktop"]),
    ]:
        jfr[namn] = [pct(topp, pred) if topp else 0, pct(svag, pred) if svag else 0, pct(sites, pred)]
    total["jamforelse"] = {"n_topp": len(topp), "n_svag": len(svag), "rader": jfr}
    total["h1_topp_median"] = statistics.median([s["h1_size"] for s in topp if s["h1_size"]])
    total["h1_svag_median"] = statistics.median([s["h1_size"] for s in svag if s["h1_size"]])
    out = {"sajter": sites, "totalt": total, "misslyckade": [{"namn": r["namn"], "fel": r.get("error")} for r in raw if not r.get("ok")],
           "uteslutna": [{"namn": v["namn"], "skal": v["skal"]} for v in manuell.values() if not v["med"]]}
    (DATA / "sammanstallning.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(sites), "sajter")
    for k in ("font_kind", "font_source", "btn_shape", "img_shape", "header_type", "hero_type", "brand_family"):
        print(k, total[k])
    print("fonts", total["fonts"][:15])
    print("h1", total["h1_median"], total["h1_quartiles"])
    print(total["pct"])
    print(total["nav_words"][:25])
    print(total["arketyp"], total["jamforelse"], total["h1_topp_median"], total["h1_svag_median"])


if __name__ == "__main__":
    main()
