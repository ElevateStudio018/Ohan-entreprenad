# Ohan Entreprenad AB – webbplats

Ny webbplats för Ohan Entreprenad AB (mark och anläggning samt maskinuthyrning i Göteborg med omnejd). Samma kod och
samma UI som S-Bygg-sajten: kolsvart sidhuvud och sidfot, runda ”Ring”-knappar, piller-knappar, stor och lättläst text
(Plus Jakarta Sans), stora foton med rundade hörn och enkla staplade sektioner. Accentfärgen är maskingul (`#f5b400`)
i stället för S-Byggs röda.

## Logga

Ohan har ingen logga i filerna här, så sidan använder en enkel ordbild: ett gult märke (`docs/img/favicon.svg`) och
namnet OHAN / ENTREPRENAD i sidans typsnitt (`logo()` i `scripts/build.py`). Byt mot den riktiga loggan när den finns.

## Sidor

Allt ligger i [`docs/`](docs/) och kräver inga verktyg – öppna `docs/index.html` i en webbläsare.

- `index.html` – startsidan: hero, intro, tjänster, maskinuthyrning, om oss med arbetsgång, kontakt med
  offertformulär, vanliga frågor, SEO-text med interna länkar och karta
- åtta tjänstesidor: `tjanst-va-arbeten.html`, `tjanst-draneringar.html`, `tjanst-husgrunder.html`,
  `tjanst-parkeringsytor.html`, `tjanst-sten-och-murarbeten.html`, `tjanst-schakt-och-transport.html`,
  `tjanst-infrastruktur.html`, `tjanst-uthyrning.html`
- `404.html`, `sitemap.xml`, `robots.txt`

## Ändra text

Sidorna genereras av `scripts/build.py`, där all text, alla tjänster och kontaktuppgifter finns. Ändra där och kör:

```bash
python3 scripts/build.py docs
```

## Fakta och förslag – gå igenom före lansering

ohanentreprenad.se gick inte att hämta direkt från byggmiljön (nätverket blockerade domänen), så innehållet är
hämtat via sökmotorernas index av sajten och företagsregister. Texterna är därför omskrivna, inte ordagranna kopior.

**Från ohanentreprenad.se:** namn, telefon 0720-49 82 90, info@ohanentreprenad.se, c/o Kungälvsvägen 66, 442 39 Kungälv,
org.nr 559341-9335, ”Göteborg med omnejd”, ”pålitlig samarbetspartner för maskintjänster för både företag och
privatpersoner”, tjänsterna i menyn (VA-arbeten, Dräneringar, Husgrunder, Parkeringsytor, Sten- och murarbeten, Schakt
och transport, Infrastruktur, Uthyrning) och innehållet på sidorna VA, Dräneringar, Husgrunder, Infrastruktur och
Uthyrning (grävmaskiner, hjullastare, kompaktlastare, dumprar, lyftkranar, med eller utan förare).

**Förslag (genererad text) som Ohan bör bekräfta eller ändra:**

- Texterna för Parkeringsytor, Sten- och murarbeten och Schakt och transport (sökresultaten gav ingen text därifrån).
- Listorna ”Det kan ingå” på tjänstesidorna, arbetsprocessen, ”Om oss”-texten och svaren i Vanliga frågor.
- Öppettider saknas och visas inte.

Inga certifieringar, garantier, priser, kundomdömen eller antal anställda anges.

## Offertformuläret

Formuläret skickar e-post via [FormSubmit](https://formsubmit.co) (gratis) och visar ett tackmeddelande när det
gått fram. Under förhandsvisningen går förfrågningarna till Elevate Studio; byt `FORM_EMAIL` i `scripts/build.py`
till Ohans adress (t.ex. info@ohanentreprenad.se) vid lansering. Första förfrågan till en ny adress skickar bara ett
aktiveringsmejl. En tjänstesidas ”Begär offert” fyller i jobbtypen automatiskt (`index.html?typ=…#offert`).

## Bilder

Bilderna från ohanentreprenad.se gick inte att hämta (se ovan). Alla foton i `docs/img/` är därför stockbilder från
[Pexels](https://www.pexels.com) (fria att använda) och märks på sidan som illustrationsbilder. Byt mot Ohans egna
bilder genom att ersätta filerna med samma namn (både `namn.jpg`, 1800 px bred, och `namn-s.jpg`, 800 px bred).

| Fil | Pexels-ID |
| --- | --- |
| `hero-grav.jpg` | [12063807](https://www.pexels.com/photo/12063807/) |
| `intro.jpg` | [11680715](https://www.pexels.com/photo/11680715/) |
| `om-oss.jpg` | [10884323](https://www.pexels.com/photo/10884323/) |
| `va.jpg` | [29301874](https://www.pexels.com/photo/29301874/) |
| `dranering.jpg` | [9389356](https://www.pexels.com/photo/9389356/) |
| `husgrund.jpg` | [26107204](https://www.pexels.com/photo/26107204/) |
| `parkering.jpg` | [16239805](https://www.pexels.com/photo/16239805/) |
| `stenmur.jpg` | [6156557](https://www.pexels.com/photo/6156557/) |
| `schakt.jpg` | [28442180](https://www.pexels.com/photo/28442180/) |
| `infrastruktur.jpg` | [19394246](https://www.pexels.com/photo/19394246/) |
| `uthyrning.jpg` | [95687](https://www.pexels.com/photo/95687/) |

## Publicera

Sidan publiceras automatiskt av `.github/workflows/deploy-pages.yml` vid varje push (GitHub Pages, källa *GitHub
Actions*). Byt `SITE_URL` i `scripts/build.py` om sidan får en egen domän.
