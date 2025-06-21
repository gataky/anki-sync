import re

import attr
from genanki import Note


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
    def from_dataframe(cls, df):
        obj = cls(**df.to_dict())
        obj._post_process_dataframe(df)
        return obj

    @classmethod
    def from_ankinote(cls, note: Note):
        data = {
            "GUID": note.guid,
            "Tags": list(note.tags),
        }
        for field in note.model.fields:
            name = field["name"]
            indx = field["ord"]
            data[name] = note.fields[indx]

        obj = cls(**data)
        obj._post_process_ankinote(note)
        return obj
