import json
import attr
import genanki
import pandas

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.core.models.note import Note
from anki_sync.utils.guid import generate_guid

ANKI_SHARED_CSS = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } .note_type { font-size:0.8em; color:grey; }"

ANKI_NOUN_MODEL_ID = 1517392319  # Keep this consistent for words
ANKI_NOUN_MODEL_NAME = "Test (Noun)"
ANKI_NOUN_MODEL_FIELDS = [
    {"name": "english"},
    {"name": "greek"},
    {"name": "audio filename"},
]
ANKI_NOUN_MODEL_TEMPLATES = [
    {
        "name": "Card 1 (English to Greek)",
        "qfmt": "{{english}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{greek}}<br>{{audio filename}}',
    },
    {
        "name": "Card 2 (Greek to English)",
        "qfmt": "{{greek}}<br>{{audio filename}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{english}}',
    },
]

NOUN_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(ANKI_NOUN_MODEL_FIELDS)
]
NOUN_MODEL = genanki.Model(
    ANKI_NOUN_MODEL_ID,
    ANKI_NOUN_MODEL_NAME,
    fields=NOUN_MODEL_FIELDS,
    templates=ANKI_NOUN_MODEL_TEMPLATES,
    css=ANKI_SHARED_CSS,
)


@attr.s(auto_attribs=True, init=False)
class Noun(BaseWord):

    # Required fields
    english: str
    greek: str
    gender: str

    # Fields with defaults
    audio_filename: str = ""
    tags: list[str] = attr.ib(factory=list)

    guid: str = attr.ib(factory=lambda: generate_guid(10))
    id: int | None = None
    n_s: str = "-"
    n_p: str = "-"
    a_s: str = "-"
    a_p: str = "-"
    g_s: str = "-"
    g_p: str = "-"

    _gender_mapping = {
        "masculine": "ο",
        "feminine": "η",
        "neuter": "το",
    }

    def get_audio_meta(self) -> AudioMeta:
        return AudioMeta(phrase=self.greek, filename=self.audio)

    def to_note(self) -> Note:
        article = self._gender_mapping.get(self.gender, "")

        note_fields = [
            self.english,
            f"{article} {self.greek}",
            f"[sound:{self.audio_filename}]",
        ]
        return Note(
            model=NOUN_MODEL,
            fields=note_fields,
            tags=self.generate_note_tags(),
            guid=self.guid,
            id=self.id,
            data=self.generate_note_meta(),
        )

    def _post_process_dataframe(self, data: pandas.DataFrame):
        data = data.fillna("")
        self._pp_df_tags(data)
        self._pp_df_audio(data)

    def _pp_df_tags(self, data: pandas.DataFrame):
        category_index = data.index.get_loc("Tag") if "Tag" in data.index else -1
        tags = (
            data.iloc[category_index:].tolist() if category_index >= 0 else []
        )
        self.tags = tags

    def _pp_df_audio(self, data: pandas.DataFrame):
        self.audio_filename = f"{self.greek}.mp3"

    def generate_note_tags(self):
        tags_list = []
        current_hierarchy_parts = []
        for cell_content_raw in self.tags:
            cell_content = str(cell_content_raw or "").strip()
            if not cell_content:
                break
            current_hierarchy_parts.append(cell_content.replace(" ", "\u00a0"))
            tags_list.append("::".join(current_hierarchy_parts))
        return sorted(list(set(tags_list)))

    def generate_note_meta(self) -> str:
        meta = {
            "english": self.english,
            "greek": self.greek,
            "gender": self.gender,
            "tags": self.tags,
            "n_s": self.n_s,
            "n_p": self.n_p,
            "a_s": self.a_s,
            "a_p": self.a_p,
            "g_s": self.g_s,
            "g_p": self.g_p,
            "audio_filename": self.audio_filename,
        }


        return json.dumps(meta)
