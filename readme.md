# DUO-parser
l.c.vriend@uu.nl

Tool om diverse DUO bestanden zoals OBO en Analysebestand mee te parsen. Splitst op basis van definities die geëxtraheerd zijn uit het pve de diverse recordsoorten naar hun eigen tabellen met bijbehorende veldnamen en datatypes. Op dit moment zijn de volgende DUO bestanden beschikbaar:

- OBO
- OBO verschillenlijst
- Analysebestand

## Voorbeeld

```python
from duo_parsers import Obo

obo = Obo.from_csv('pad/naar/obo.csv')

>>> obo
<DuoBestand|Obo>
brin  bekostigingsjaar datum_aanvraag
21PD              2017     2018-01-14
                                       records  velden
vlp Voorlooprecord                           1       4
per Persoongegevens                      36437       5
nat Nationaliteitsgegevens               36820       7
isg Inschrijvings-(deelname-)gegevens    66250      12
grd Graad-(resultaat-)gegevens            9347      10
vbt Verblijfstitelgegevens                4408       7
vbv Verblijfsvergunninggegevens           1256       8
ctr Controletotalen                          1       5
```

De verschillende recordsoorten zijn raadpleegbaar als attributen. In bovenstaand voorbeeld zijn inschrijvingsgegevens bv. te benaderen met `obo.isg`.. De data wordt opgeslagen als een pandas `DataFrame` die raadpleegbaar is via `obo.isg.data`. Verder is alle veldinformatie die in het pve is vastgelegd ook in te zien. Alle definities benader je met `obo.isg.veldinfo`. Maar als je bv. alleen geïnteresseerd bent in de waarden bij `dtype` dan kun je deze ook direct benaderen met `obo.isg.dtype`.

Resultaten kunnen verder bewerkt worden in python maar evt. ook geëxporteerd worden naar excel: `obo.to_excel('pad/naar/obo.xlsx)`. Elk recordsoort wordt dan weggeschreven naar een eigen sheet.

## PvE Parser
De definities op basis waarvan de records geparsed worden, liggen vast in de diverse .json files. Deze kunnen (semi-)geautomatiseerd uit het pve van DUO gedestilleerd worden. Zie hiervoor de `pve_parser` (eveneens onderdeel van deze repo). Dit is nog een work-in-progress.
