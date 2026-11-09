"""Typsnittspar (Google Fonts) för sajtbiblioteket. Varje sajt får ett par – fördelat så att ingen i samma grupp delar par.

Fält: id, rubrik, text, kat, vikt (rubrikvikt), sp (spatiering), versaler, fallback, spec (Google-axlar för rubriken),
kursiv (rubriken har riktig kursiv), profiler (vilka grupper paret passar; tomt = alla utom foto/djur-specifika).
"""

S = "Georgia, 'Times New Roman', serif"
M = "ui-monospace, monospace"

PAR = [
    # Serif – elegant, redaktionellt
    dict(id="cormorant", rubrik="Cormorant Garamond", text="Montserrat", kat="serif", vikt=500, sp="-0.01em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400;1,500", kursiv=True, profiler="foto begravning sten mega"),
    dict(id="baskerville", rubrik="Libre Baskerville", text="Lato", kat="serif", vikt=400, sp="-0.02em", fallback=S, spec="ital,wght@0,400;0,700;1,400", kursiv=True, profiler="foto begravning bygg nisch"),
    dict(id="lora", rubrik="Lora", text="Nunito Sans", kat="serif", vikt=500, sp="-0.015em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400;1,500", kursiv=True, profiler="foto djur arborist nisch"),
    dict(id="spectral", rubrik="Spectral", text="Karla", kat="serif", vikt=500, sp="-0.02em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400", kursiv=True, profiler="foto mega nisch"),
    dict(id="garamond", rubrik="EB Garamond", text="Work Sans", kat="serif", vikt=500, sp="-0.015em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400;1,500", kursiv=True, profiler="foto begravning nisch"),
    dict(id="bodoni", rubrik="Bodoni Moda", text="Jost", kat="serif", vikt=500, sp="-0.02em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400", kursiv=True, profiler="foto mega"),
    dict(id="instrument-serif", rubrik="Instrument Serif", text="Inter", kat="serif", vikt=400, sp="-0.02em", fallback=S, spec="ital,wght@0,400;1,400", kursiv=True, profiler="foto bygg nisch mega"),
    dict(id="young-serif", rubrik="Young Serif", text="Inter", kat="serif", vikt=400, sp="-0.02em", fallback=S, spec="wght@400", profiler="foto djur arborist nisch bygg"),
    dict(id="dmserif", rubrik="DM Serif Display", text="DM Sans", kat="serif", vikt=400, sp="-0.01em", fallback=S, spec="ital,wght@0,400;1,400", kursiv=True, profiler="foto bygg nisch"),
    dict(id="playfair", rubrik="Playfair Display", text="Source Sans 3", kat="serif", vikt=600, sp="-0.015em", fallback=S, spec="ital,wght@0,400;0,600;0,700;1,400;1,600", kursiv=True, profiler="foto nisch mega"),
    dict(id="fraunces", rubrik="Fraunces", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400;1,500", kursiv=True, profiler="foto djur arborist nisch mega bygg"),
    dict(id="newsreader", rubrik="Newsreader", text="Inter", kat="serif", vikt=500, sp="-0.02em", fallback=S, spec="ital,wght@0,400;0,500;0,600;1,400", kursiv=True, profiler="foto mega nisch"),
    dict(id="zilla", rubrik="Zilla Slab", text="Source Sans 3", kat="slab", vikt=600, sp="-0.01em", fallback=S, spec="ital,wght@0,500;0,600;0,700;1,500", kursiv=True, profiler="bygg nisch arborist"),
    dict(id="robotoslab", rubrik="Roboto Slab", text="Roboto", kat="slab", vikt=600, sp="-0.02em", fallback=S, spec="wght@400;500;600;700", profiler="bygg nisch arborist mega"),
    # Smala / versaler – industri, hantverk
    dict(id="bebas", rubrik="Bebas Neue", text="Inter", kat="smal", vikt=400, sp="0.01em", versaler=True, spec="wght@400", profiler="bygg nisch arborist"),
    dict(id="anton", rubrik="Anton", text="Roboto", kat="smal", vikt=400, sp="0", versaler=True, spec="wght@400", profiler="bygg nisch"),
    dict(id="oswald", rubrik="Oswald", text="Inter", kat="smal", vikt=500, sp="0.005em", versaler=True, spec="wght@400;500;600;700", profiler="bygg nisch arborist"),
    dict(id="barlowcond", rubrik="Barlow Condensed", text="Barlow", kat="smal", vikt=600, sp="0", versaler=True, spec="wght@500;600;700", profiler="bygg nisch arborist mega"),
    dict(id="bigshoulders", rubrik="Big Shoulders Display", text="Barlow", kat="smal", vikt=700, sp="0", versaler=True, spec="wght@600;700;800", profiler="bygg nisch"),
    dict(id="archivoblack", rubrik="Archivo Black", text="Archivo", kat="tung", vikt=400, sp="-0.02em", spec="wght@400", profiler="bygg nisch mega"),
    dict(id="kanit", rubrik="Kanit", text="Inter", kat="tung", vikt=600, sp="-0.01em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="bygg nisch djur"),
    # Display
    dict(id="unbounded", rubrik="Unbounded", text="Inter", kat="display", vikt=600, sp="-0.03em", spec="wght@400;500;600;700", profiler="bygg nisch mega djur"),
    dict(id="syne", rubrik="Syne", text="Inter", kat="display", vikt=700, sp="-0.02em", spec="wght@500;600;700;800", profiler="foto mega nisch bygg"),
    dict(id="bricolage", rubrik="Bricolage Grotesque", text="Inter", kat="display", vikt=700, sp="-0.03em", spec="wght@500;600;700;800", profiler="djur bygg nisch mega arborist"),
    dict(id="spacemono", rubrik="Space Mono", text="Space Grotesk", kat="mono", vikt=700, sp="-0.03em", fallback=M, spec="ital,wght@0,400;0,700;1,400", kursiv=True, profiler="nisch mega bygg"),
    dict(id="plexmono", rubrik="IBM Plex Mono", text="IBM Plex Sans", kat="mono", vikt=500, sp="-0.03em", fallback=M, spec="ital,wght@0,400;0,500;0,600;1,400", kursiv=True, profiler="nisch mega"),
    # Vänliga / rundade
    dict(id="fredoka", rubrik="Fredoka", text="Nunito", kat="rund", vikt=600, sp="-0.01em", spec="wght@400;500;600;700", profiler="djur"),
    dict(id="quicksand", rubrik="Quicksand", text="Nunito Sans", kat="rund", vikt=700, sp="-0.01em", spec="wght@500;600;700", profiler="djur foto"),
    dict(id="nunito", rubrik="Nunito", text="Nunito", kat="rund", vikt=800, sp="-0.02em", spec="ital,wght@0,600;0,700;0,800;1,700", kursiv=True, profiler="djur arborist nisch"),
    dict(id="poppins", rubrik="Poppins", text="Poppins", kat="geometrisk", vikt=600, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="djur bygg nisch"),
    dict(id="rubik", rubrik="Rubik", text="Rubik", kat="geometrisk", vikt=600, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="djur bygg nisch arborist"),
    dict(id="lexend", rubrik="Lexend", text="Lexend", kat="geometrisk", vikt=600, sp="-0.03em", spec="wght@400;500;600;700", profiler="djur nisch mega"),
    dict(id="josefin", rubrik="Josefin Sans", text="Mulish", kat="geometrisk", vikt=600, sp="-0.01em", spec="ital,wght@0,400;0,600;0,700;1,400", kursiv=True, profiler="foto djur nisch"),
    dict(id="raleway", rubrik="Raleway", text="Raleway", kat="geometrisk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,500", kursiv=True, profiler="foto nisch bygg"),
    dict(id="montserrat", rubrik="Montserrat", text="Montserrat", kat="geometrisk", vikt=700, sp="-0.03em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="foto bygg nisch arborist"),
    dict(id="jost", rubrik="Jost", text="Jost", kat="geometrisk", vikt=500, sp="-0.02em", spec="ital,wght@0,400;0,500;0,600;1,400", kursiv=True, profiler="foto djur nisch mega"),
    # Groteskar – koncern
    dict(id="spacegrotesk", rubrik="Space Grotesk", text="Inter", kat="grotesk", vikt=600, sp="-0.03em", spec="wght@400;500;600;700", profiler="mega nisch bygg"),
    dict(id="intertight", rubrik="Inter Tight", text="Inter", kat="grotesk", vikt=600, sp="-0.035em", spec="ital,wght@0,500;0,600;0,700;1,500", kursiv=True, profiler="mega nisch bygg"),
    dict(id="manrope", rubrik="Manrope", text="Inter", kat="geometrisk", vikt=700, sp="-0.03em", spec="wght@500;600;700;800", profiler="mega nisch bygg arborist"),
    dict(id="sora", rubrik="Sora", text="Inter", kat="geometrisk", vikt=600, sp="-0.03em", spec="wght@400;500;600;700", profiler="mega nisch bygg djur"),
    dict(id="outfit", rubrik="Outfit", text="DM Sans", kat="geometrisk", vikt=600, sp="-0.02em", spec="wght@400;500;600;700", profiler="djur nisch bygg arborist"),
    dict(id="redhat", rubrik="Red Hat Display", text="Red Hat Text", kat="geometrisk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch bygg"),
    dict(id="figtree", rubrik="Figtree", text="Figtree", kat="geometrisk", vikt=700, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="djur foto nisch arborist"),
    dict(id="urbanist", rubrik="Urbanist", text="Urbanist", kat="geometrisk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="foto djur nisch"),
    dict(id="instrumentsans", rubrik="Instrument Sans", text="Instrument Sans", kat="grotesk", vikt=600, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;1,500", kursiv=True, profiler="mega nisch bygg"),
    dict(id="archivo", rubrik="Archivo", text="Archivo", kat="grotesk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;0,800;1,600", kursiv=True, profiler="mega nisch bygg arborist"),
    dict(id="plexsans", rubrik="IBM Plex Sans", text="IBM Plex Sans", kat="grotesk", vikt=600, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,500", kursiv=True, profiler="mega nisch"),
    dict(id="publicsans", rubrik="Public Sans", text="Public Sans", kat="grotesk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch bygg"),
    dict(id="hanken", rubrik="Hanken Grotesk", text="Hanken Grotesk", kat="grotesk", vikt=700, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch bygg arborist"),
    dict(id="albert", rubrik="Albert Sans", text="Albert Sans", kat="grotesk", vikt=700, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="foto mega nisch"),
    dict(id="chivo", rubrik="Chivo", text="Chivo", kat="grotesk", vikt=700, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;0,800;1,600", kursiv=True, profiler="mega nisch bygg"),
    dict(id="epilogue", rubrik="Epilogue", text="Epilogue", kat="grotesk", vikt=700, sp="-0.03em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="foto mega nisch"),
    dict(id="librefranklin", rubrik="Libre Franklin", text="Libre Franklin", kat="humanistisk", vikt=700, sp="-0.02em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch bygg"),
    dict(id="sourcesans", rubrik="Source Sans 3", text="Source Sans 3", kat="humanistisk", vikt=700, sp="-0.01em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch arborist"),
    dict(id="mulish", rubrik="Mulish", text="Mulish", kat="humanistisk", vikt=800, sp="-0.02em", spec="ital,wght@0,600;0,700;0,800;1,700", kursiv=True, profiler="djur nisch arborist"),
    dict(id="plusjakarta", rubrik="Plus Jakarta Sans", text="Plus Jakarta Sans", kat="geometrisk", vikt=700, sp="-0.025em", spec="ital,wght@0,500;0,600;0,700;1,600", kursiv=True, profiler="mega nisch bygg"),
]


def for_profil(profil, grupp):
    """Par som passar gruppen. Nischerna (B2B) räknas som 'nisch'; begravning/sten får även sina egna."""
    nyckel = profil if profil in ("foto", "djur", "arborist", "mega", "bygg") else "nisch"
    ut = [p for p in PAR if nyckel in p["profiler"].split() or grupp in p["profiler"].split()]
    if grupp in ("begravning", "sten"):
        ut = [p for p in ut if p["kat"] in ("serif", "geometrisk", "grotesk", "humanistisk")]
    return ut
