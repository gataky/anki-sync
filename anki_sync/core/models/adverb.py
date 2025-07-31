import attr
import genanki
import pandas

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.core.models.note import Note
from anki_sync.core.sql import AnkiDatabase
from anki_sync.utils.guid import generate_guid

ANKI_SHARED_CSS = """
.card {
   font-family: arial;
   font-size: 20px;
   text-align: center;
   color: black;
   background-color: white;
}
.note_type {
    font-size:0.8em; color:grey;
}
table {
    margin-left: auto;
    margin-right: auto;
}
"""

ANKI_ADV_MODEL_ID = 1607402323  # Keep this consistent for words
ANKI_ADV_MODEL_NAME = "greek adverb"
ANKI_ADV_MODEL_FIELDS = [
    {"name": "english"},
    {"name": "greek"},
    {"name": "audio filename"},
]
ANKI_ADV_MODEL_TEMPLATES = [
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

ADV_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(ANKI_ADV_MODEL_FIELDS)
]
ADV_MODEL = genanki.Model(
    ANKI_ADV_MODEL_ID,
    ANKI_ADV_MODEL_NAME,
    fields=ADV_MODEL_FIELDS,
    templates=ANKI_ADV_MODEL_TEMPLATES,
    css=ANKI_SHARED_CSS,
)


@attr.s(auto_attribs=True, init=False)
class Adverb(BaseWord):

    # Required fields
    english: str
    greek: str

    # Fields with defaults
    audio_filename: str = ""
    tags: list[str] = attr.ib(factory=list)

    guid: str = attr.ib(factory=lambda: generate_guid(10))
    id: int | None = None

    def get_audio_meta(self) -> AudioMeta:
        return AudioMeta(phrase=self.greek, filename=self.audio_filename)

    def to_note(self, old_db_conn: AnkiDatabase) -> Note:
        self.id, self._exists_in_anki = old_db_conn.get_note_id_by_guid(self.guid)
        if self._exists_in_anki is False:
            self.guid = generate_guid()

        note_fields = [
            self.english,
            self.greek,
            f"[sound:{self.audio_filename}]",
        ]
        return Note(
            model=ADV_MODEL,
            guid=self.guid,
            id=self.id,
            fields=note_fields,
            tags=self.generate_note_tags(),
            old_db_conn=old_db_conn,
        )

    def _post_process_dataframe(self, data: pandas.DataFrame):
        data = data.fillna("")
        self._pp_df_tags(data)
        self._pp_df_audio(data)

    def _pp_df_tags(self, data: pandas.DataFrame):
        category_index = data.index.get_loc("tag") if "tag" in data.index else -1
        tags = data.iloc[category_index:].tolist() if category_index >= 0 else []
        self.tags = list(filter(lambda x: x, tags))

    def _pp_df_audio(self, data: pandas.DataFrame):
        self.audio_filename = f"{self.greek}.mp3"

    def generate_note_tags(self):
        tags_list = ["grammar::adverb"]
        current_hierarchy_parts = []
        for cell_content_raw in self.tags:
            cell_content = str(cell_content_raw or "").strip()
            if not cell_content:
                break
            current_hierarchy_parts.append(cell_content.replace(" ", "\u00a0"))
            tags_list.append("::".join(current_hierarchy_parts))
        return sorted(list(set(tags_list)))

    def generate_note_meta(self) -> str:
        return ""
