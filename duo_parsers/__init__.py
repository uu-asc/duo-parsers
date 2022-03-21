from collections import defaultdict
import json
import pickle
from pathlib import Path

import pandas as pd


LIBPATH = Path(__file__).parent.absolute()


class DuoBestand:
    filename_tabledefs = None

    def __init__(self, data, tabledefs, use_altnaam=True):
        self.recordsoorten = tabledefs['recordsoorten']
        self.tabledefs = tabledefs
        self.use_altnaam = use_altnaam
        self.add_records(data)

    def __getitem__(self, obj):
        return self.__dict__[obj]

    def __len__(self):
        return len(self.recordsoorten)

    def __iter__(self):
        return iter([
            v for k,v in self.__dict__.items()
            if k in self.recordsoorten
        ])

    def __repr__(self):
        vlp = self['vlp'].iloc[:,1:].to_string(index=False)
        tuples = [(item.key, item.name) for item in self]
        data = pd.DataFrame(
            data=[item.shape for item in self],
            index=pd.MultiIndex.from_tuples(tuples),
            columns=['records', 'velden']
        ).to_string()
        return '\n'.join([self.name, vlp, data])

    def add_records(self, data):
        for key, data in data.items():
            if isinstance(data, list):
                data = self.get_record(key, data)
            setattr(self, key, data)

    def get_record(self, key, data):
        naam = self.recordsoorten[key]
        veldinfo = self.tabledefs['velden'][key]
        return Data(key, naam, data, veldinfo, self.use_altnaam)

    def to_pickle(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.__dict__, f)

    def to_excel(self, path):
        with pd.ExcelWriter(path) as writer:
            for item in self:
                item.data.to_excel(writer, sheet_name=item.key)

    @property
    def name(self):
        return f"<{self.__class__.__base__.__name__}|{self.__class__.__name__}>"

    @classmethod
    def from_pickle(cls, path):
        with open(path, 'rb') as f:
            dct = pickle.load(f)
        tabledefs = dct['tabledefs']
        recordsoorten = tabledefs['recordsoorten']
        data = {k:v for k,v in dct.items() if k in recordsoorten}
        return cls(data, tabledefs)

    @classmethod
    def from_csv(cls, filepath, use_altnaam=True):
        tabledefs = cls.load_tabledefs(LIBPATH / cls.filename_tabledefs)
        encoding = tabledefs['eigenschappen']['encoding']
        sep = tabledefs['eigenschappen']['separator']
        records = cls.read_csv(filepath, encoding=encoding, sep=sep)
        return cls(records, tabledefs, use_altnaam=use_altnaam)

    @staticmethod
    def read_csv(filepath, encoding='utf8', sep='|'):
        with open(filepath, 'r', encoding=encoding) as f:
            csv = f.readlines()
        records = defaultdict(list)
        for line in csv:
            key = line[:3].lower()
            row = [item.strip('\n') for item in line.split(sep)]
            records[key].append(row)
        return records

    @staticmethod
    def load_tabledefs(file):
        with open(file, encoding='utf8') as f:
            return json.load(f)


class Data:
    MAP_DTYPES = {
        'int': 'int64'
    }

    def __init__(self, key, name, data, veldinfo, use_altnaam=True):
        self.key = key
        self.name = name
        self.use_altnaam = use_altnaam
        self.veldinfo = self.read_veldinfo(veldinfo, use_altnaam)
        self.data = self.data_to_frame(data)

    def __getattr__(self, name):
        """Indien `name` voorkomt als sleutel in veldinfo, geef dan voor elk
        veld die informatie terug. Indien `name` niet voorkomt als sleutel,
        probeer deze data dan op te halen bij `data`.
        """
        if name.startswith('_'):
            raise AttributeError(name)
        if name in self.veldeigenschappen:
            return {k:v.get(name) for k,v in self.veldinfo.items()}
        return getattr(self.data, name)

    def _repr_html_(self):
        html = self.data.to_html(
            max_rows=10,
            show_dimensions=True,
            notebook=True,
        )
        return f"<h3>[{self.key.upper()}] {self.name}</h3>{html}"

    def read_veldinfo(self, veldinfo, use_altnaam):
        """Integreer veldinfo in het configuratiebestand in de data.
        - Sla originele veldnamen op onder 'originele_naam'.
        - Vertaal dtypes in configuratiebestand naar pandas dtypes.
        - Indien `use_altnaam`: vervang sleutels met alternatieve naam.
        """
        map_dtypes = lambda x: self.MAP_DTYPES.get(x, x)
        for key, info in veldinfo.items():
            info['originele_naam'] = key
            info['dtype'] = map_dtypes(info['dtype'])
        if not use_altnaam:
            return veldinfo
        return {v.get('alternatieve_naam', k):v for k,v in veldinfo.items()}

    @property
    def veldnamen(self):
        "Lijst met alle veldnamen."
        return list(self.veldinfo.keys())

    @property
    def veldeigenschappen(self):
        "Lijst met alle veldeigenschappen."
        return {item for items in self.veldinfo.values() for item in items}

    def data_to_frame(self, data):
        "Converteer records naar dataframe."
        df = pd.DataFrame(
            data=data,
            columns=self.veldnamen,
        ).replace(r'', pd.NA)

        for veld, dtype in self.dtype.items():
            if dtype == 'boolean':
                df[veld] = boolify(df[veld], astype='boolean')
            elif dtype == 'datum':
                df[veld] = pd.to_datetime(df[veld], errors='coerce')
            else:
                df[veld] = df[veld].astype(dtype)
        return df


class Obo(DuoBestand):
    filename_tabledefs = 'tabledefs.obo.json'


class Obov(DuoBestand):
    filename_tabledefs = 'tabledefs.obov.json'

    @classmethod
    def from_csv(cls, path):
        path = Path(path)
        records = {}
        for file in path.glob('OBOV_*.csv'):
            records.update(cls.read_csv(file))
        tabledefs = cls.load_tabledefs(LIBPATH / cls.filename_tabledefs)
        return cls(records, tabledefs)


class Dab(DuoBestand):
    filename_tabledefs = 'tabledefs.anbs.json'

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
