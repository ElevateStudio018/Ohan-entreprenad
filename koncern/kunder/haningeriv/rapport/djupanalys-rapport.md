# Djupanalys före och efter – Haninge Riv & Sanering

Körd 2026-11-14 med Elevate Studios egen kod för Djupanalys (`elevate-studio-pre/worker/crawl.js` och `sitecheck.js`)
och samma poängsättning som `assets/js/sitetest-deep.js`. Googles test är Lighthouse (mobil, simulerad 4G) – samma motor som
PageSpeed Insights – körd lokalt, en ren körning per sida. Den nya sajten testades i produktionsläge på en lokal HTTPS-server
som beter sig som Cloudflare Pages/Netlify (`test/serve.mjs`). Mejl och certifikat läses från domänen haningeriv.se i båda fallen.

## Betyg (Elevate Studios Djupanalys)

| | SEO | Tillgänglighet | Bästa praxis | Prestanda | Säkerhet och mejl | Länkar |
|---|---|---|---|---|---|---|
| Gamla haningeriv.se (5 sidor) | 83 | 88 | 95 | 77 | 50 | 100 |
| Nya sajten (14 sidor) | 100 | 100 | 100 | 99 | 50 | 100 |

Googles test, snitt över de 12 viktigaste sidorna (SEO / Tillgänglighet / Bästa praxis / Prestanda):
gamla 88 | 86 | 92 | 73 – nya 100 | 100 | 100 | 99.

## Vad som återstår och varför

- **Säkerhet och mejl 50**: DMARC saknas i haningeriv.se:s DNS. Det är en DNS-post hos one.com, inte en del av
  sajten. Lägg till TXT-posten `_dmarc.haningeriv.se` med värdet `v=DMARC1; p=quarantine; rua=mailto:info@haningeriv.se`.
  DKIM finns redan (one.com, väljarna `rsa1` och `rsa2`) men verktyget letar inte efter de väljarna, se nedan.
  Certifikatet för haningeriv.se går ut om 21 dagar enligt crt.sh (gäller nuvarande webbhotell; vid flytt får sajten ett nytt certifikat).
  Betyget växlar mellan 50 och 67 beroende på om crt.sh svarar. Med DMARC på plats, verktygets DKIM-fel rättat och ett certifikat med mer än 30 dagar kvar blir det 100.
- **Prestanda 99**: verktyget sätter max 99 så fort Googles test har ett enda förslag. Det som återstår är att
  skicka ännu mindre bilder till mobiler än skärmen behöver, vilket skulle göra fotona suddiga. Googles prestanda per sida: / 96, /bemanning.html 99, /betonghaltagning.html 100, /bolag.html 100, /byggkonsult.html 100, /faq.html 99, /frilaggning-av-ror.html 99, /hallbarhet.html 97, /karriar.html 99, /om-oss.html 97, /projekt.html 100, /rivning.html 99.

## Fel i verktyget som påverkar resultatet

1. **Sajtkartindex följs inte.** WordPress-sajter (som gamla haningeriv.se) har `sitemap.xml` som pekar på `page-sitemap.xml`.
   Verktyget läser då bara startsidan och `page-sitemap.xml` som om den vore en sida. Utan rättning fick gamla sajten SEO 26,
   Tillgänglighet 63, Bästa praxis 67, Prestanda 71 – därför kördes den gamla sajten här med sina fem riktiga sidor.
2. **Säkerhetsrubrikerna mäts fel.** Steget `headers` kör svaret genom `withHeaders()` – Elevate Studios egna rubriker – så
   alla sajter får CSP, HSTS m.fl. i testet oavsett vad de har.
3. **Stilfilens cache** kontrolleras alltid på `/assets/css/site.min.css` (Elevate Studios egen sökväg).
4. **DKIM**: väljarlistan saknar one.com:s `rsa1`/`rsa2`, så one.com-kunder får alltid "DKIM hittades inte".

## Sökordstäckning – vilken sida svarar på sökningen?

A = sökordet i adressen, T = i titeln, H = i rubriken (h1), B = i metabeskrivningen.

| Sökning | Gamla sajten | Nya sajten |
|---|---|---|
| rivning haninge | index.html –––– | rivning.html ATHB |
| rivningsfirma | index.html –––– | index.html –THB |
| stambytesrivning | index.html –––– | index.html –––B |
| asbestsanering | index.html –––– | sanering.html –T–B |
| mögelsanering | index.html –––– | sanering.html –T–B |
| sanering vattenskada | index.html ––H– | sanering.html ATHB |
| betonghåltagning haninge | tjanster.html –––– | betonghaltagning.html –TH– |
| kärnborrning | index.html –––– | betonghaltagning.html –T–B |
| friläggning av rör fuktskada | om-oss.html –––– | frilaggning-av-ror.html –TH– |
| byggkonsult | om-oss.html –––– | byggkonsult.html ATHB |
| bemanning byggpersonal | om-oss.html –––– | bemanning.html ATH– |

Gamla sajten har ingen metabeskrivning på någon sida och titlar som "Hem" och "Tjänster", och ingen sida per tjänst.
Nya sajten har en egen sida per tjänst (rivning, sanering, betonghåltagning, friläggning av rör, byggkonsult, bemanning),
unika titlar och beskrivningar, strukturerad data (HomeAndConstructionBusiness, Service, FAQPage, BreadcrumbList),
canonical, Open Graph, sajtkarta och 301-omdirigeringar från de gamla adresserna (/tjanster/, /om-oss/, /kontakt/, /offertforfragan/).

## Så mäter vi placeringen i Google (före/efter)

Placeringar går inte att mäta förrän den nya sajten ligger på haningeriv.se och Google har läst om den. Mätningen:

1. **Nollmätning nu**: Google Search Console för haningeriv.se – exportera visningar, klick och snittposition per sökord för de
   senaste 3 månaderna (kräver att HRS ger Elevate Studio åtkomst till egendomen, eller skapar den).
2. **Lansering**: produktionsversionen läggs upp, sajtkartan skickas in i Search Console, omdirigeringarna tar med de gamla länkarna.
3. **Uppföljning** efter 2, 4, 8 och 12 veckor: samma export, jämförd med nollmätningen per sökord ovan.

Placeringen beror också på Google-företagsprofilen, recensioner och länkar från andra sajter; sajten är den del vi styr.
