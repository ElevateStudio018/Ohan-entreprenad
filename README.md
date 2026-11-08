# Koncernsajter – undersökning, 10 exempel och agent

Elevate Studios verktygslåda för hemsidor med **koncernkänsla** åt bygg- och fastighetsbolag.

- **Undersökningen:** [`research/rapport/Koncernkansla-undersokning.pdf`](research/rapport/Koncernkansla-undersokning.pdf)
  – 100 svenska bygg- och fastighetskoncerners hemsidor, uppmätta och granskade. Där står vad som skiljer de bästa från resten
  och vilka nio stilarketyper som finns.
- **10 exempelsajter:** `site/exempel/<namn>/` – fiktiva koncerner, var och en med eget grafiskt paket.
  Översikt i `site/index.html`, publicerad med GitHub Pages.
- **Agenten `koncern`:** skriv till exempel *"@koncern gör en hemsida åt Exempelbolaget AB"* eller `/koncern Exempelbolaget AB`
  i Claude Code. Agenten tar reda på fakta om företaget, skriver innehållet, skapar ett grafiskt paket som skiljer sig från alla
  tidigare sajter och bygger och granskar sajten (`site/kunder/<slug>/`). Instruktionerna finns i `.claude/agents/koncern.md`.

## Undersökningen (`research/`)

| Fil | Vad den gör |
| --- | --- |
| `kandidater.csv` | 116 koncerner med webbadress |
| `analysera.py` | Öppnar varje sajt i Chromium, klickar bort cookie-rutan, tar skärmdumpar och mäter typsnitt, färger, rundning, header, hero och menyord → `data/resultat.json`, `data/shots/` |
| `data/manuell.json` | Min manuella genomgång: med/utesluten, arketyp, betyg 1–5, kommentar |
| `typsnitt_manuell.py` | Handklassning av rubriktypsnittet för de 100 (kategori, eget typsnitt) |
| `sammanstall.py` | Räknar ihop allt → `data/sammanstallning.json` |
| `rapport.py` | Bygger PDF:en (`rapport/`) |

Göra om undersökningen:

```bash
python3 research/analysera.py research/kandidater.csv research/data
python3 research/sammanstall.py research/data
python3 research/rapport.py
```

## Generatorn (`koncern/`)

| Fil | Vad den gör |
| --- | --- |
| `paket.py` | Skapar grafiska paket. Axlar och alternativ kommer från undersökningen: 23 typsnittspar, 14 paletter med djupa varumärkesfärger och ljusa toner, 5 formfamiljer, 6 hero-layouter, 3 headers, 4 stilar på vägvalsrutor, 3 panelfärger, 4 rytmer, 3 sektionsordningar, 11 loggformer och 10 arketyper. Väljer det paket som ligger längst ifrån alla i `register.json`. |
| `generera.py` | Bygger en sajt med åtta sidor (Start, Verksamhet, Våra bolag, Projekt, Vårt ansvar, Investerare, Jobba hos oss, Om oss) från `brief.json` + `paket.json`. Startsidan följer hur toppsajterna är uppbyggda hela vägen ned: topprad, hero med bildspel, vägval med ikoner, berättelser, bild + färgpanel, våra bolag, nyckeltal, projekt med status, hållbarhet, investerare, nyheter, snabbrutor, helfärgad sidfot |
| `mall/bas.css`, `mall/sajt.js`, `mall/ikoner.py` | Den gemensamma koden. Paketet styr den via `tokens.css` och `data-*`-attribut på `<body>` |
| `skarmdump.py` | Skärmdumpar på dator och mobil + kontroll av horisontell scroll |
| `bildbank/`, `bildbank.tsv` | 83 taggade stockfoton från Pexels |
| `exempel/` | Innehållet till de 10 exemplen och `bygg_exempel.py`, som bygger dem |
| `register.json` | Alla paket som använts – så att nästa sajt blir annorlunda |

```bash
python3 koncern/paket.py arketyper                     # visa arketyperna
python3 koncern/paket.py lista                         # visa använda paket
python3 koncern/paket.py ny "Bolag AB" --bransch fastighet --ut paket.json --registrera
python3 koncern/generera.py brief.json paket.json site/kunder/bolag
python3 koncern/exempel/bygg_exempel.py                # bygg om de 10 exemplen och site/index.html
```

## Bra att veta

- De 10 exempelkoncernerna är **fiktiva**. Alla bilder är stockfoton från Pexels och märks som illustrationsbilder.
- Sajterna har typsnitt från Google Fonts, så att de fungerar utan licenser. Många av de bästa koncernerna i undersökningen har
  egna typsnitt; för en riktig kund kan rubriktypsnittet bytas i `paket.json` (`typsnitt.rubrik`, `google: false`) när kunden har
  licens.
- `site/` publiceras automatiskt av `.github/workflows/deploy-pages.yml` vid varje push.
