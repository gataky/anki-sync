import json
import re

import attr
from genanki import Note
import pandas


class BaseWord:
    filename_re = re.compile(r"\[sound:(?P<filename>.*)\]")

    def __init__(self, **kwargs):
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
    def from_sheets(cls, df: pandas.DataFrame):
        obj = cls(**df.to_dict())
        obj._post_process_dataframe(df)
        return obj

    @classmethod
    def from_ankidb(cls, note: pandas.DataFrame):
        data = json.loads(note.ndata.item())
        data["guid"] = note.nguid.item()
        data["id"] = note.nid.item()

        # declensions = dict(zip(
        #     ["n_s", "n_p", "a_s", "a_p", "g_s", "g_p"],
        #     data["declensions"],
        # ))
        # data.update(declensions)

        obj = cls(**data)
        return obj
