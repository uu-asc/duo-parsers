import json
import pickle
from pathlib import Path

import pandas as pd


LIBPATH = Path(__file__).parent.absolute()


class DuoBestand:
    filename_tabledefs = ''

    def __init__(self, data, tabledefs, alternatieve_namen=True):
        self.keys = tabledefs['recordsoorten']
        self.tabledefs = tabledefs
        self.alternatieve_namen = alternatieve_namen
        self.add_records(data)

    def __getitem__(self, key):
        return getattr(self, key)

    def add_records(self, data):
        for key, data in data.items():
            if isinstance(data, list):
                data = self.records_to_df(key, data)
            setattr(self, key, data)

    def records_to_df(self, key, data):
        "Convert records to dataframe."

        key = key.lower()
        velden = self.veldinfo_per_recordsoort(key)
        kwargs = dict(data=data, columns=velden)
        df = pd.DataFrame(**kwargs).replace(r'', pd.NA)

        convert_ints = lambda x: 'int64' if x == 'int' else x
        dtypes = {k:convert_ints(v) for k,v in velden.items()}

        booleans = [k for k,v in dtypes.items() if v == 'boolean']
        for veld in booleans:
            df[veld] = boolify(df[veld], astype='boolean')
        datum_velden = [k for k,v in dtypes.items() if v == 'datum']
        for veld in datum_velden:
            df[veld] = pd.to_datetime(df[veld], errors='coerce')

        exclude = booleans + datum_velden
        overig = {k:v for k,v in dtypes.items() if k not in exclude}
        df = df.astype(overig)
        return df

    def veldinfo_per_recordsoort(self, recordsoort, key='dtype'):
        td = self.tabledefs['velden'][recordsoort]
        if self.alternatieve_namen:
            get_name = lambda item, spec: spec.get('alternatieve_naam', item)
            return {get_name(i,j):j[key] for i,j in td.items()}
        return {k:v[key] for k,v in td.items()}

    def to_pickle(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)

    @classmethod
    def from_pickle(cls, path):
        with open(path, 'rb') as f:
            dct = pickle.load(f)
        tabledefs = dct['tabledefs']
        recordsoorten = tabledefs['recordsoorten']
        data = {k:v for k,v in dct.items() if k in recordsoorten}
        return cls(data, tabledefs)

    @classmethod
    def from_csv(cls, filepath, alternatieve_namen=True):
        tabledefs = cls.load_tabledefs(LIBPATH / cls.filename_tabledefs)
        encoding = tabledefs['eigenschappen']['encoding']
        sep = tabledefs['eigenschappen']['separator']
        records = cls.read_csv(filepath, encoding=encoding, sep=sep)
        return cls(records, tabledefs, alternatieve_namen=alternatieve_namen)

    @staticmethod
    def read_csv(filepath, encoding='utf8', sep='|'):
        with open(filepath, 'r', encoding=encoding) as f:
            csv = f.readlines()
        records = dict()

        for line in csv:
            key = line[:3].lower()
            row = [item.strip('\n') for item in line.split(sep)]
            if key not in records:
                records[key] = [row]
            else:
                records[key].append(row)
        return records

    @staticmethod
    def load_tabledefs(file):
        with open(file, encoding='utf8') as f:
            return json.load(f)


class Obo(DuoBestand):
    filename_tabledefs = 'tabledefs.obo.1.json'


class Obov(DuoBestand):
    filename_tabledefs = 'tabledefs.obov.1.json'

    @classmethod
    def from_csv(cls, path):
        path = Path(path)
        records = {}
        for file in path.glob('OBOV_*.csv'):
            records.update(cls.read_csv(file))
        tabledefs = cls.load_tabledefs(LIBPATH / cls.filename_tabledefs)
        return cls(records, tabledefs)


class Dab(DuoBestand):
    filename_tabledefs = 'tabledefs.anbs.1.json'

    def __init__(self, *args, use_old_layout=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_old_layout = use_old_layout

    @classmethod
    def from_csv(cls, filepath, use_old_layout=False):
        records = cls.read_csv(filepath)
        tabledefs = cls.load_tabledefs(LIBPATH / cls.filename_tabledefs)
        if use_old_layout:
            cls.load_old_layout()
        return cls(records, tabledefs)

    def load_old_layout(self):
        for key, values in self.tabledefs['velden_per_recordsoort_oud'].items():
            self.tabledefs['velden_per_recordsoort'][key] = values


def boolify(s, true='J', false='N', astype=bool):
    return pd.Series(s.replace({true: True, false: False}), dtype=astype)
