# Haninge Riv & Sanering – bygget

Sajten byggs med koncern-generatorn i samma stil som systerbolaget Haninge Byggteam (ElevateStudio018/HB-AB):
Byggteams grafiska paket (`hb-paket.json`) med HRS färger (orange #DB6E2D, svart #0E1218, blågrå #283D49).

```bash
python3 prep_bilder.py          # gör bilder/ av kalla/
python3 brief.py                # skriver brief.json och paket.json
python3 bygg_hrs.py ../../.. ../../../site/kunder/haningeriv <mapp med node_modules för purgecss + lightningcss>
```

Före lansering: byt `FORM_EMAIL` i `bygg_hrs.py` till info@haningeriv.se, ta bort `demo` i `brief.py` och fyll i organisationsnummer.
