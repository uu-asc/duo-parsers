import re
import pandas as pd


normalize_names = lambda x: re.sub('\W', '_', x.lower())


def make_table(df):
    return df.rename(columns=df.iloc[0]).rename(columns=normalize_names).drop(0)


def concat_cells(df):
    concat_rows = lambda s: s.str.cat(sep=' ')
    return df.replace({'': None}
    ).assign(omschrijving = lambda df: df.omschrijving.ffill()
    ).groupby('omschrijving', sort=False
    ).agg(lambda grp: grp.apply(concat_rows, axis=0)
    )

def process_list_of_tables(tables, skip=None):
    if skip:
        tables = [j for i,j in enumerate(tables) if i not in skip]
    
    new_list = list()
    n_tables = len(tables)
    counter = -1
    previous_df = pd.DataFrame()

    for i, table in enumerate(tables):
        df = make_table(tables[i].df)
        if i > 0 and i < n_tables and df.iloc[0,0] != 'Recordsoort':
            df = previous_df.append(df)
            new_list[counter] = df
        else:
            counter += 1
            new_list.append(df)
        previous_df = df
    
    new_list = [concat_cells(df) for df in new_list]
    return new_list

def extend_table(df):
    def make_names(df):
        andere_namen = dict(
            burgerservicenummer = 'bsn',
            onderwijsnummer = 'own',
            opleidingscode = 'croho',
            voldoet_aan_beperking_wsf2000 = 'voldoet_aan_wsf',
        )
        replacements = {
            'omschrijving': 'oms',
            'verblijfsvergunning': 'vvr',
            '.*volgnummer': 'volgnummer',
        }
        s = pd.Series(df.index.map(normalize_names)).replace(andere_namen)
        for pat, repl in replacements.items():
            s = s.str.replace(pat, repl)
        return s.values

    def add_dtypes(df):
        dtypes = {
            'A': 'string',
            'N': 'int',
            'B': 'boolean',
        }
        s = df.formaat___lengte.str[0].apply(lambda s: dtypes.get(s))
        s.loc[df.index.str.contains('datum', case=False)] = 'datum'
        return s

    def fix_definitie_toelichting(df):
        def fix_strings(x):
            replacements = {
                " ogelijke":   " Mogelijke",
                " anvullende": " Aanvullende",
                " oelichting": " Toelichting",
                " aarde":      " Waarde",
                "^[A-Z]{2}":   lambda i: i.group(0)[1:],
            }
            for pat, repl in replacements.items():
                x = re.sub(pat, repl, x)
            return x
        return df.definitie_toelichting.apply(fix_strings)
    
    return df.assign(
        alternatieve_naam=make_names,
        dtype=add_dtypes,
        definitie_toelichting=fix_definitie_toelichting,
    )


def boolify(s, true='ja', false='nee', astype=bool):
    return s.replace({true: True, false: False}).astype(astype)