# Haninge Riv & Sanering – bygget

Sajten byggs med koncern-generatorn i samma stil som systerbolaget Haninge Byggteam (ElevateStudio018/HB-AB):
Byggteams grafiska paket (`hb-paket.json`) med HRS färger (orange #DB6E2D, svart #0E1218, blågrå #283D49).
SEO och teknik (tjänstesidor, titlar, strukturerad data, sajtkarta, 404, omdirigeringar, bilder, typsnitt) ligger i `seo.py`.

```bash
npm install                     # purgecss, lightningcss, Poppins (+ lighthouse för testerna)
python3 prep_bilder.py          # gör bilder/ av kalla/
python3 brief.py                # skriver brief.json och paket.json
# förslag (noindex) -> site/kunder/haningeriv/
python3 bygg_hrs.py <Ohan-entreprenad> ../../../site/kunder/haningeriv .
# produktion (sökbar) -> site/kunder/haningeriv-produktion/
HRS_LAGE=produktion HRS_SAJT=https://www.haningeriv.se/ python3 bygg_hrs.py <Ohan-entreprenad> ../../../site/kunder/haningeriv-produktion .
```

Produktionsmappen är färdig för Cloudflare Pages eller Netlify: `_headers` (säkerhetsrubriker, cache) och `_redirects`
(301 från de gamla WordPress-adresserna /tjanster/, /om-oss/, /kontakt/, /offertforfragan/).

Före lansering: sätt `FORM_TILL` i `bygg_hrs.py` till info@haningeriv.se (HRS) och info@haningebyggteam.se (Byggteam),
fyll i organisationsnummer, lägg till DMARC i DNS hos one.com och skicka in sajtkartan i Google Search Console.

## Tester

`test/djupanalys.mjs` kör Elevate Studios Djupanalys lokalt (serverkoden i elevate-studio-pre + samma poängsättning) med
Lighthouse som Googles test. `test/serve.mjs` serverar en byggd mapp som Cloudflare Pages/Netlify. Resultat i `rapport/`.

```bash
node test/serve.mjs <byggd mapp> 8443 &
NODE_TLS_REJECT_UNAUTHORIZED=0 ELEVATE=<elevate-studio-pre> node test/djupanalys.mjs https://127.0.0.1:8443/ rapport/efter.json haningeriv.se
```
