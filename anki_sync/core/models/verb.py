from typing import Optional

import attr
import genanki
import pandas

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.utils.guid import generate_guid

ANKI_VERB_MODEL_ID = 1607392321  # New Randomly generated ID for verbs
ANKI_VERB_MODEL_NAME = "Anki-Sync Verb (Eng-Gr)"
# Updated fields based on new Verb model and sheet structure
ANKI_VERB_MODEL_FIELDS = [
    {"name": "ID"},
    {"name": "Conjugated"},  # Main citation form
    {"name": "English"},
    {"name": "Audio Filename"},
    {"name": "Tense"},
    {"name": "Person"},
    {"name": "Number"},
]
# Updated template to include a table for tenses
ANKI_VERB_MODEL_TEMPLATES = [
    {
        "name": "Card 1 (English to Greek Verb)",
        "qfmt": """
            {{English}}
            <br><small>{{Tense}} {{Person}} person {{Number}}</small>""",
        "afmt": """
            {{FrontSide}}
            <hr id="answer">
            {{Greek}} {{Audio Filename}}""",
    },
    {
        "name": "Card 2 (Greek Verb to English)",
        "qfmt": """
            {{Greek}} {{Audio Filename}}""",
        "afmt": """
            {{FrontSide}}
            <hr id="answer">
            {{English}}""",
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
    id: int
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

    def to_note(self) -> genanki.Note:
        # Create note with the new fields
        note_fields = [
            self.id,
            self.conjugated,
            self.english,
            f"[sound:{self.audio_filename}]",
            self.tense.lower(),
            self.person.lower(),
            self.number.lower(),
        ]

        return genanki.Note(
            model=VERB_MODEL,
            fields=note_fields,
            tags=self.tags,
            guid=self.guid,
        )

    def get_audio(self) -> AudioMeta:
        return AudioMeta(phrase=self.conjugated, filename=f"{self.verb}-{self.id}.mp3")

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
        self.audio_filename = f"{self.verb}-{self.id}.mp3"

    def _pp_df_tags(self, data: pandas.DataFrame):
        self.tags = [f"class::verb::{self.verb}"]

    def _pp_an_audio(self, note: genanki.Note):
        filename = self.audio_filename
        match = self.filename_re.match(filename)
        if match:
            self.audio_filename = match.groupdict().get("filename", "")
