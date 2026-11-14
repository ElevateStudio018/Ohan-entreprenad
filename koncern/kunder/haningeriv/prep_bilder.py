"""Gör HRS bilder till generatorns format (id.jpg max 1600 px + id-s.jpg 700 px) och loggorna."""
import pathlib, shutil
from PIL import Image
SRC = pathlib.Path(__file__).parent / "kalla"
UT = pathlib.Path(__file__).parent / "bilder"
UT.mkdir(exist_ok=True)
BILDER = [  # fil, tagg, alt
 ("hero-kapning", "hrs-hero", "HRS-medarbetare kapar ett betonggolv"),
 ("vagg-oppnad", "hrs-rivning", "Vägg öppnad inför ombyggnad"),
 ("rivning-tjanster", "hrs-rivning", "Utriven dörrkarm och vägg"),
 ("riv-o-sanering", "hrs-rivning2", "Rivning av vägg från saxlift"),
 ("hero-hall", "hrs-hall", "Rivning i lagerhall"),
 ("hall-rivd", "hrs-hall2", "Lagerhall efter rivning"),
 ("sanering-inplastat", "hrs-sanering", "Inplastad saneringszon"),
 ("sanering-zon", "hrs-sanering2", "Sanering innanför inplastad zon"),
 ("projekt-6", "hrs-sluss", "Sluss in till en inplastad saneringszon"),
 ("haltagning", "hrs-haltagning", "Kärnborrade hål i betongvägg"),
 ("borrning", "hrs-borrning", "HRS-medarbetare borrar i betongvägg"),
 ("rivning-haltagning", "hrs-sag", "Väggsåg monterad på skena"),
 ("projekt-5", "hrs-dorr", "Ny dörröppning sågad i vägg"),
 ("projekt-1", "hrs-vaggsag", "Väggsågning"),
 ("grav-golv", "hrs-ror", "Rör frilagda i uppgrävt golv efter fuktskada"),
 ("tekniker", "hrs-folk", "HRS-medarbetare i varselkläder"),
 ("lift", "hrs-lift", "HRS-medarbetare på lift i butikslokal"),
 ("bemanning", "hrs-bemanning", "HRS-medarbetare i korridor"),
 ("bil-bred", "hrs-bil", "HRS servicebil"),
 ("bil-staende", "hrs-bil2", "HRS servicebil"),
 ("miljo", "hrs-miljo", "Rivningsavfall sorterat i säckar"),
 ("projekt/haninge-19", "hrs-miljo", "Rivningsmassor lastade för bortforsling"),
 ("projekt-3", "hrs-stad", "Städning efter rivning"),
 ("projekt-4", "hrs-konsult", "Uppmärkning på vägg inför håltagning"),
]
rows = []
for f, tagg, alt in BILDER:
    im = Image.open(SRC / f"{f}.jpg").convert("RGB")
    f = f.replace("/", "-")
    big = im.copy(); big.thumbnail((1600, 1600), Image.LANCZOS)
    big.save(UT / f"hrs-{f}.jpg", quality=84, optimize=True, progressive=True)
    s = im.copy(); s.thumbnail((700, 700), Image.LANCZOS)
    s.save(UT / f"hrs-{f}-s.jpg", quality=78, optimize=True, progressive=True)
    rows.append(f"hrs-{f}\t{tagg}\t{alt}")
# Systerbolagets kort: Haninge Byggteams villabild
im = Image.open(SRC / "hb-villa.jpg").convert("RGB")
im.save(UT / "hb-villa.jpg", quality=84, optimize=True, progressive=True)
im.thumbnail((700, 700), Image.LANCZOS); im.save(UT / "hb-villa-s.jpg", quality=78, optimize=True, progressive=True)
rows.append("hb-villa\thrs-hb\tVit villa med pool och trädäck i kvällsljus")
(UT / "bilder.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")

# Loggan: vit version (original) och mörk version (vitt -> HRS svart, orange behålls)
L = pathlib.Path(__file__).parent / "logo"
vit = Image.open(SRC / "logo-vit.png").convert("RGBA")
vit.save(L / "hrs-logo-vit.png", optimize=True)
px = vit.load(); mork = vit.copy(); pm = mork.load()
for y in range(vit.height):
    for x in range(vit.width):
        r, g, b, a = px[x, y]
        if a and min(r, g, b) > 150 and max(r, g, b) - min(r, g, b) < 40:  # vitt/grått -> svart
            pm[x, y] = (14, 18, 24, a)
mork.save(L / "hrs-logo.png", optimize=True)
print(len(rows), "bilder")
