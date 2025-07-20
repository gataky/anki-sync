from typing import Optional

import attr
import genanki
import pandas

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.core.models.note import Note
from anki_sync.core.sql import AnkiDatabase
from anki_sync.utils.guid import generate_guid

ANKI_VERB_MODEL_ID = 1607392321  # New Randomly generated ID for verbs
ANKI_VERB_MODEL_NAME = "greek verb"
# Updated fields based on new Verb model and sheet structure
ANKI_VERB_MODEL_FIELDS = [
    {"name": "english"},
    {"name": "greek"},  # Main citation form
    {"name": "audio filename"},
    {"name": "tense"},
    {"name": "person"},
    {"name": "number"},
]
# Updated template to include a table for tenses
ANKI_VERB_MODEL_TEMPLATES = [
    {
        "name": "Card 1 (English to Greek Verb)",
        "qfmt": """
            {{english}}
            <br><small>{{tense}} {{person}} person {{number}}</small>""",
        "afmt": """
            {{FrontSide}}
            <hr id="answer">
            {{greek}} {{audio filename}}""",
    },
    {
        "name": "Card 2 (Greek Verb to English)",
        "qfmt": """
            {{greek}} {{audio filename}}""",
        "afmt": """
            {{FrontSide}}
            <hr id="answer">
            {{english}}""",
    },
]

ANKI_SHARED_CSS = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } .note_type { font-size:0.8em; color:grey; }"

VERB_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(ANKI_VERB_MODEL_FIELDS)
]
VERB_MODEL = genanki.Model(
    ANKI_VERB_MODEL_ID,
    ANKI_VERB_MODEL_NAME,
    fields=VERB_MODEL_FIELDS,
    templates=ANKI_VERB_MODEL_TEMPLATES,
    css=ANKI_SHARED_CSS,
)


@attr.s(auto_attribs=True, init=False)
class Verb(BaseWord):

    # Required fields
    english: str
    greek: str

    # Fields with defaults
    guid: str = attr.ib(factory=lambda: generate_guid(10))
    group: Optional[str] = None
    tags: list[str] = attr.ib(factory=list)


@attr.s(auto_attribs=True, init=False)
class VerbConjugation(BaseWord):

    # Required fields
    ord: int
    conjugated: str
    english: str
    tense: str
    person: str
    number: str

    # Field with default
    guid: str = attr.ib(factory=lambda: generate_guid(10))
    verb: str = ""
    audio_filename: str = ""
    tags: list[str] = attr.ib(factory=list)

    def get_audio_meta(self) -> AudioMeta:
        return AudioMeta(phrase=self.conjugated, filename=f"{self.verb}-{self.ord}.mp3")

    def to_note(self, old_db_conn: AnkiDatabase) -> Note:
        # Create note with the new fields
        self.id, self._exists_in_anki = old_db_conn.get_note_id_by_guid(self.guid)
        if self._exists_in_anki is False:
            self.guid = generate_guid()
        note_fields = [
            self.english,
            self.conjugated,
            f"[sound:{self.audio_filename}]",
            self.tense.lower(),
            self.person.lower(),
            self.number.lower(),
        ]

        return Note(
            model=VERB_MODEL,
            guid=self.guid,
            id=self.id,
            fields=note_fields,
            tags=self.generate_note_tags(),
            old_db_conn=old_db_conn,
        )

    def _post_process_dataframe(self, data: pandas.DataFrame):
        self._pp_df_audio(data)
        self._pp_df_tags(data)
        self.tense = self.tense.lower()
        self.person = self.person.lower()
        self.number = self.number.lower()

    def _post_process_ankinote(self, note: genanki.Note):
        self.verb = note.tags[0].split("::")[-1]
        self._pp_an_audio(note)

    def _pp_df_audio(self, data: pandas.DataFrame):
        self.audio_filename = f"{self.verb}-{self.ord}.mp3"

    def _pp_df_tags(self, data: pandas.DataFrame):
        self.tags = [f"class::verb::{self.verb}"]

    def _pp_an_audio(self, note: genanki.Note):
        filename = self.audio_filename
        match = self.filename_re.match(filename)
        if match:
            self.audio_filename = match.groupdict().get("filename", "")

    def generate_note_tags(self) -> list[str]:
        tag = f"verb::{self.verb}::{self.tense}"
        tag = tag.replace(" ", "\u00a0")
        return [tag]
