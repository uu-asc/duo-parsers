# DUO-parser
l.c.vriend@uu.nl

Tool om diverse DUO bestanden voor het HO zoals OBO en Analysebestand te parsen. Splitst op basis van definities die geëxtraheerd zijn uit het [programma van eisen ROD HO](https://duo.nl/zakelijk/hoger-onderwijs/studentenadministratie/programma-van-eisen-bron-ho.jsp) (pve) de diverse recordsoorten naar hun eigen tabellen met bijbehorende veldnamen en datatypes. Op dit moment zijn de volgende DUO bestanden beschikbaar:

- OBO
- OBO verschillenlijst
- Analysebestand

## Voorbeeld

```python
from duo_parsers import Obo
obo = Obo.from_csv('pad/naar/obo.csv')

>>> obo
```
```raw
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

De verschillende recordsoorten worden als pandas `DataFrame` opgeslagen in het `DuoBestand`. De attribuutnaam voor elke recordsoort komt overeen met de sleutel zoals deze in pve is vermeld. In het OBO krijgen de inschrijvings-(deelname-)gegevens dus bv. de sleutel 'isg'. In het `Obo` object zijn deze gegevens dan te benaderen met `obo.isg`. 

De data wordt opgeslagen als een `Data` object. De `DataFrame` is raadpleegbaar via het `data` attribuut. Verder is alle veldinformatie die in het pve is vastgelegd bij het recordsoort ook in te zien via `veldinfo`. Daarnaast is het mogelijk om specifieke sleutels in de veldinformatie te benaderen via de naam van de sleutel: bv. `obo.isg.dtype` geeft per veld het dtype terug.

Resultaten kunnen verder bewerkt worden in python maar evt. ook geëxporteerd worden naar excel: `obo.to_excel('pad/naar/obo.xlsx)`. Elk recordsoort wordt dan weggeschreven naar een eigen sheet.

## PvE Parser
De definities op basis waarvan de records geparsed worden, liggen vast in de diverse .json files. Deze kunnen (semi-)geautomatiseerd uit het pve van DUO gedestilleerd worden. Zie hiervoor de [pve_parser](pve_parser/pve_parser.ipynb) (eveneens onderdeel van deze repo).

- **meta** : informatie over het pve dat gebruikt is
    - versie
    - url
    - datum
- **eigenschappen** : informatie over bestandsbeschrijving
    - naam
    - paginas
    - encoding
    - separator
    - datum_formaat
- **recordsoorten** : sleutel en naam van de recordsoorten in het bestand
- **velden** : per tabel de veldinformatie
    - zoals deze is vastgelegd in het pve:
        - omschrijving (sleutel)
        - formaat_lengte
        - verplicht
        - definitie_toelichting
    - toegevoegde velden:
        - alternatieve naam (handzame korte naam)
        - dtype (data type)
