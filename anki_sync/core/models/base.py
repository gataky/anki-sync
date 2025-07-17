import json
import re
from typing import Hashable

import attr
import pandas


class BaseWord:
    filename_re = re.compile(r"\[sound:(?P<filename>.*)\]")

    def __init__(self, **kwargs):
        self._exists_in_anki: bool = False
        self._google_sheet_cell: str = ""
        self.init(self, **kwargs)

    @staticmethod
    def init(cls, **kwargs):
        transformed_kwargs = {
            key.lower().replace(" ", "_"): value for key, value in kwargs.items()
        }

        cls_fields = {f.name for f in attr.fields(cls.__class__)}
        init_kwargs = {k: v for k, v in transformed_kwargs.items() if k in cls_fields}

        cls.__attrs_init__(**init_kwargs)

    @classmethod
    def from_sheets(cls, row: tuple[Hashable, pandas.Series]):
        index, df = row
        data = df.to_dict()
        data["guid"] = df.guid
        obj = cls(**data)
        obj._post_process_dataframe(df)
        obj._google_sheet_cell = f"A{index+2}"
        return obj

    @classmethod
    def from_ankidb(cls, note: pandas.DataFrame):
        data = note.data
        if not data:
            return None
        data = json.loads(data)
        data["guid"] = note.name
        data["id"] = int(note.id)

        obj = cls(**data)
        return obj

    def _post_process_dataframe(self, *args):
        pass

    def exists_in_anki(self):
        return self._exists_in_anki
