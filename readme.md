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

### Obov
#### Verschillenlijst
Geeft voor elk record in een lijst weer welke velden verschillen. Hiermee is het mogelijk om een snel overzicht te maken van het aantal verschillen per categorie:

```python
isgv = obov.isg.verschil()
isgv.value_counts()
```
```raw
[datum_uitschrijving]                                                  1299
[eerste_inschrijving]                                                    53
[opleidingsfase]                                                          5
[datum_inschrijving, datum_uitschrijving, datum_eerste_aanlevering]       2
[datum_uitschrijving, eerste_inschrijving]                                2
dtype: int64
```

#### Verschillenmatrix
Geeft voor elk record aan op welke velden er verschillen zijn. Alleen als er een verschil in een veld is wordt deze opgenomen (in de kolom `vkolomnaam`). Ook wordt voor elk record vastgelegd hoeveel verschillen er zijn gevonden (in de kolom `nverschil`).

```python
obov.isg.vmatrix()
```

|      | vdatum_inschrijving   | vdatum_uitschrijving   | veerste_inschrijving   | vopleidingsfase   |   nverschil |
|-----:|:----------------------|:-----------------------|:-----------------------|:------------------|------------:|
|    0 | False                 | True                   | True                   | False             |           2 |
|    1 | False                 | True                   | False                  | False             |           1 |
|    2 | False                 | False                  | False                  | True              |           1 |
|    3 | False                 | False                  | False                  | True              |           1 |
|    4 | False                 | True                   | False                  | False             |           1 |
|    5 | False                 | True                   | False                  | False             |           1 |
|    6 | False                 | True                   | True                   | False             |           2 |
|    7 | True                  | True                   | False                  | True              |           3 |

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
