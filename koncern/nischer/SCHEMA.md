# Brief för nischsajter (exempelsajter med koncernstil)

Varje sajt är en JSON-fil: `koncern/nischer/<grupp>/<slug>.json`. Grupper: `bygg`, `foto`, `mega`, `arborist`, `djur` och
en grupp per B2B-nisch (`hiss`, `brand`, …, se NISCHER i `koncern/bygg_nischer.py`).

Företagen är **påhittade**. Hitta på trovärdiga namn som inte tillhör ett känt, verkligt företag (undvik t.ex. Peab, NCC,
Skanska, Byggmax och liknande, och undvik namn som är exakt lika riktiga företag du känner till). Siffror, kunder och projekt är
påhittade men ska vara **realistiska för företagets storlek** (en bröllopsfotograf har inte 400 anställda, en sotare inte 2 miljarder i omsättning).

## Ton
Svenska, sakligt och konkret, i koncernton: stora påståenden i rubrikerna, konkreta detaljer i texten (orter, material,
metoder, tider, garantier). Inga klyschor ("vi brinner för", "kvalitet i fokus", "din partner"). Ingen lorem ipsum.
Varje sajt i en grupp ska kännas som ett eget företag: egen ort/region, egen inriktning, egen personlighet (familjeföretag
sedan 1962, nystartad specialist, regional marknadsledare, premium, prisvärd, miljöprofil …), egna rubriker och formuleringar.
Skriv aldrig samma mening på två sajter.

## Fält

```jsonc
{
  "profil": "bygg | foto | mega | arborist | djur | nisch",
  "nisch": "hiss",                  // bara för profil nisch
  "demo": "Exempelsajt från Elevate Studio – företaget är påhittat.",
  "namn": "Fullständigt namn AB",
  "kortnamn": "Ordbild",            // 1–2 ord, står i loggan (versaler i stilen)
  "slug": "ordbild",                // a–z, 0–9, bindestreck; unik i gruppen
  "typ": "Etikett i heron",          // t.ex. "Bröllopsfotograf i Göteborg", max ~40 tecken
  "tagline": "Max fyra ord",        // står bredvid loggan
  "slogan": "En mening som sammanfattar företaget",
  "hero_rubrik": "Max 45 tecken, 2–3 rader",
  "hero_text": "1–2 meningar, max 200 tecken",
  "intro_rubrik": "Rubrik till siffersektionen",
  "om": ["Stycke 1 (2–3 meningar)", "Stycke 2 (2–3 meningar)"],
  "vagval_rubrik": "Rubrik över tjänsterutorna",
  "tjanster": [ {"titel": "Max 3 ord", "ikon": "<ikon>", "href": "verksamhet.html", "text": "En mening (visas i dragspelsvarianten)"} ],  // exakt 8
  "affarsomraden": [ {"titel": "", "text": "2 meningar", "text2": "1–2 meningar", "tagg": "<bildtagg>"} ],  // exakt 4 (tjänsteområden)
  "bolag": [ {"namn": "", "segment": "", "rubrik": "", "text": "", "tagg": "<bildtagg>"} ],  // 3–4: team, avdelningar eller dotterbolag (se profil)
  "berattelser": [ {"rubrik": "", "text": "1–2 meningar", "tagg": ""} ],  // exakt 3 aktuella händelser
  "nyckeltal": [ {"varde": "38", "enhet": "år", "etikett": "Kort etikett"} ],  // exakt 4
  "projekt": [ {"namn": "", "ort": "", "typ": "", "ar": "2025", "text": "1 mening", "tagg": ""} ],  // exakt 6
  "process": [ {"titel": "", "text": "1–2 meningar", "tagg": ""} ],  // exakt 4 steg
  "hallbarhet": {"rubrik": "", "text": "2–3 meningar", "mal": [["100 %", "kort text"], ["", ""], ["", ""]]},
  "karriar": {"rubrik": "", "text": "", "jobb": [["Titel", "Ort"]]},  // 0–4 jobb (foto/djur: panelen handlar om första mötet/besöket, jobb får vara [])
  "kultur": "En mening till panelen",
  "citat": {"text": "Ett citat från grundaren/vd", "namn": "Förnamn Efternamn", "roll": "Grundare", "tagg": ""},
  "omdomen": [ {"text": "1–3 meningar, konkret", "namn": "Förnamn E.", "ort": "Ort"} ],  // exakt 3
  "faq": [ ["Fråga?", "Svar i 1–3 meningar."] ],  // 6–8
  "priser": [ {"namn": "", "pris": "fr. 4 900 kr", "enhet": "per tillfälle", "text": "", "punkter": ["", "", "", ""], "utvald": true} ],  // 3 st (foto, djur, arborist; valfritt för övriga). Exakt en utvald.
  "prislista": [ ["Tjänst", "Pris"] ],  // valfri, 6–12 rader (djur, arborist, vissa nischer)
  "certifikat": [ {"titel": "", "text": "", "ikon": "skold"} ],  // 4 st (bygg, arborist, nisch). Riktiga svenska certifieringar är ok att nämna (ID06, BF9K, ISA, ISO 9001 …)
  "kunder": ["Påhittat kundnamn", "…"],  // 6–8, bara nisch och bygg (valfritt). Påhittade bostadsrättsföreningar, fastighetsbolag, kommuner är ok (”Brf Lärkan”, ”Kommunen”)
  "galleri_taggar": ["brollop", "detalj", "fest"],  // foto och djur
  "nyheter": [ ["2026-10-14", "Rubrik", "Ingress, en mening", "<bildtagg>"] ],  // 3–4, datum 2025–2026
  "kontakt": {"adress": "Gata 12", "postnr": "123 45", "ort": "Ort", "telefon": "070-174 06 xx", "epost": "hej@ordbild.se", "orgnr": ""},
  "oppettider": "Mån–fre 7–16",
  "omrade": "Serviceområde, t.ex. Storgöteborg och Kungsbacka",
  "fot_cta": "Uppmaning i sidfoten (1 mening)",
  "bild": {"panel": "<bildtagg>", "hb": "<bildtagg>"},   // valfritt: byt bild för en roll
  "text": {"ber_rubrik": "", "proj_rubrik": "", "...": ""}   // valfritt: egna rubriker (se KONCERN_T i koncern/profiler.py)
}
```

Telefon: använd **070-174 06 05 till 070-174 06 99** (PTS nummerserie för fiktion), olika nummer per sajt i gruppen.
Org.nr: lämna tomt. E-post: hitta på en domän utifrån namnet.

Mega (profil `mega`) använder dessutom: `investerare` {aktie, lista, kurs, forandring, rapporter[[titel,datum]], kalender[[titel,datum]]},
`kontor_lista` [[land/ort, text]] (6–10), `tidslinje` [[år, text]] (5–8), `lokala_bolag` (8–16 namn) och gärna `trend` på nyckeltal.

## Ikoner
blixt, bro, dokument, fabrik, folk, glob, graf, hem, hjalm, hus, karta, kontor, kran, kugge, lada, laddning, lov, megafon, nyckel,
pil, portfolj, ritning, robot, ror, skog, skola, skold, sok, sol, upp, vag, vard, vatten, vind, telefon, kamera, hjarta, trad, sax,
tass, ringar, eld, hiss, pensel, bat, bil, kalender, stjarna, las, verktyg, hamare, lampa, sten, kors

## Bildtaggar
Bygg/koncern: bygg, people, kontor, bostad, hem, stad, natur, tra, infra, interior, industri, el, anlaggning
Bröllop: brollop, brudpar, detalj, fest, kamera · Arborist: arborist, trad, ved, tradgard · Djur: hund, trimning, valp, katt, hundtraning
Nischer: hiss, brand, ventilation, tak, skorsten, las, golv, rivning, mark, solel, vvs, maleri, skadedjur, stadning, maskin,
begravning, korskola, bat, svets, glas, sten, hast

Välj taggar som passar ämnet. Kör `python3 koncern/validera.py <fil>` och rätta tills den säger OK.
