import re
import pandas as pd


def process_tables(dfs, patterns):
    """Verwerk de camelot output.

    Camelot weet niet wanneer een tabel meer dan één pagina in beslag neemt.
    In die gevallen levert elke pagina een nieuwe eigen tabel op in de output
    van Camelot. Daarnaast herkent Camelot niet uitzichzelf de kolomnamen van
    een tabel. Deze functie zorgt ervoor dat tabellen die meerdere pagina's
    bestrijken worden samengevoegd en dat elke tabel de juiste kolomnamen
    krijgt.

    Daarnaast wordt sommige informatie in de bestandsbeschrijvingen bewerkt, of
    er wordt nieuwe informatie toegevoegd. Het belangrijkste mechanisme
    hiervoor is een serie regex substituties die via `patterns` klaargezet en
    uitgevoerd kan worden. Zie functie `process_table` voor meer informatie.

    Gebruik deze functie om de volgende acties uit te voeren voor elke tabel in
    `dfs`:
    - Voeg gesplitste tabellen samen
    - Voeg gesplitste rijen samen
    - Voeg nieuwe kolommen toe
    - Schoon bestaande data op
    """
    output = []
    for df in dfs:
        cols = df.iloc[0].map(normalize_names)
        df = df.rename(columns=cols).drop(0)
        if df.iloc[0,0] == 'Recordsoort':
            output.append(df)
        else:
            output[-1] = pd.concat([output[-1], df])
    return [process_table(df, patterns) for df in output]


def process_table(df, patterns):
    """Verwerk tabel:
    - Voeg gesplitste rijen samen
    - Voeg nieuwe kolommen toe
    - Schoon bestaande data op

    Na samenvoegen van een geknipte tabel kunnen rijen op de randen van de
    pagina in tweëen zijn geknipt. Deze functie zorgt er allereerst voor dat de rij weer hersteld wordt door de in tweëen geknipte rijen samen te voegen.

    Vervolgens worden verschillende in `patterns` gedefinieerde substituties
    uitgevoerd op de tabellen. Hierbij kunnen bestaande kolommen worden
    bijgewerkt of nieuwe kolommen worden toegevoegd.

    Tot slot worden de waarden in de nieuwe aangemaakte kolom
    'alternatieve_naam' genormaliseerd (kleine letters en spaties vervangen met
    underscore) en de waarden in de kolom 'verplicht' geconverteerd naar bools.
    """
    df = concat_splits(df)
    for key, spec in patterns.items():
        target = spec['target']
        pats = spec['patterns']
        df[target] = replace_pats(df[key], pats)
    return df.assign(
        alternatieve_naam = df.alternatieve_naam.map(normalize_names),
        verplicht = boolify(df.verplicht),
    )


def concat_splits(df):
    "Voeg gesplitste rijen samen."
    concat_rows = lambda s: s.str.cat(sep=' ')
    veld0 = df.columns[0]
    return (
        df
        .replace({'': pd.NA})
        .assign(**{veld0: lambda df: df[veld0].ffill()})
        .groupby(veld0, sort=False)
        .agg(lambda grp: grp.apply(concat_rows, axis=0))
        .reset_index()
    )


normalize_names = lambda x: re.sub('\W+', '_', x.lower())


def boolify(s, true='ja', false='nee', astype=bool):
    "Converteer Series `s` naar een boolean dtype."
    return s.replace({true: True, false: False}).astype(astype)


def replace_pats(s, patterns):
    "Vervang in Series `s` de keys met de values in `patterns`."
    for pat, repl in patterns.items():
        s = s.str.replace(pat, repl, regex=True)
    return s
