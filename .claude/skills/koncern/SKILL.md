---
name: koncern
description: Gör en hemsida med koncernkänsla åt ett företag (bygg, fastighet, infrastruktur, installation, konsult), med ett grafiskt paket som skiljer sig från alla tidigare sajter. Använd när användaren skriver "/koncern <företag>" eller "gör en hemsida åt <företag>" och nämner koncern.
---

Starta agenten **koncern** (Agent-verktyget med `subagent_type: "koncern"`) och ge den:

- företagets namn och webbadress (om användaren angav den),
- önskemål om stil, färg eller arketyp, om användaren nämnde något,
- att resultatet ska ligga i `site/kunder/<slug>/`.

Agentens instruktioner finns i `.claude/agents/koncern.md`. När den är klar: berätta för användaren vilken arketyp och vilket
grafiskt paket sajten fick, var den ligger och vad i texterna som behöver bekräftas av kunden.

Bygger du flera sajter i samma omgång: kör agenten för en i taget, så att varje nytt paket registreras innan nästa skapas
(det är registret i `koncern/register.json` som garanterar att de blir olika).
