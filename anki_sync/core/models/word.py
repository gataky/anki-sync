
import genanki
import pandas
import attr

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.utils.guid import generate_guid

ANKI_SHARED_CSS = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } .note_type { font-size:0.8em; color:grey; }"

ANKI_WORD_MODEL_ID = 1607392319  # Keep this consistent for words
ANKI_WORD_MODEL_NAME = "Anki-Sync Basic Eng-Gr"
ANKI_WORD_MODEL_FIELDS = [
    {"name": "English"},
    {"name": "Greek"},
    {"name": "Part of Speach"},
    {"name": "Gender"},
    {"name": "Audio Filename"},
]
ANKI_WORD_MODEL_TEMPLATES = [
    {
        "name": "Card 1 (English to Greek)",
        "qfmt": "{{English}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{Greek}}<br>{{Audio Filename}}',
    },
    {
        "name": "Card 2 (Greek to English)",
        "qfmt": "{{Greek}}<br>{{Audio Filename}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{English}}',
    },
]

WORD_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(ANKI_WORD_MODEL_FIELDS)
]
WORD_MODEL = genanki.Model(
    ANKI_WORD_MODEL_ID,
    ANKI_WORD_MODEL_NAME,
    fields=WORD_MODEL_FIELDS,
    templates=ANKI_WORD_MODEL_TEMPLATES,
    css=ANKI_SHARED_CSS,
)


@attr.s(auto_attribs=True, init=False)
class Word(BaseWord):

    # Required fields
    english: str
    greek: str
    gender: str

    # Fields with defaults
    guid: str = attr.ib(factory=lambda: generate_guid(10))
    part_of_speach: str = ""
    audio_filename: str = ""
    tags: list[str] = attr.ib(factory=list)

    def get_audio_meta(self) -> AudioMeta:
        return AudioMeta(phrase=self.greek, filename=f"{self.greek}.mp3")

    def to_note(self) -> genanki.Note:
        note_fields = [
            self.english,
            self.greek,
            self.part_of_speach,
            self.gender,
            f"[sound:{self.audio_filename}]",
        ]
        return genanki.Note(
            model=WORD_MODEL,
            fields=note_fields,
            tags=self.tags,
            guid=self.guid,
        )

    def _post_process_dataframe(self, data: pandas.DataFrame):
        data = data.fillna("")
        self._pp_df_tags(data)
        self._pp_df_audio(data)

    def _post_process_ankinote(self, note: genanki.Note):
        self._pp_an_audio(note)

    def _pp_df_tags(self, data: pandas.DataFrame):
        category_index = data.index.get_loc("Tag") if "Tag" in data.index else -1
        hierarchical_tag_cells = (
            data.iloc[category_index:].tolist() if category_index >= 0 else []
        )

        tags_list = []
        current_hierarchy_parts = []
        for cell_content_raw in hierarchical_tag_cells:
            cell_content = str(cell_content_raw or "").strip()
            if not cell_content:
                break
            current_hierarchy_parts.append(cell_content.replace(" ", "\u00a0"))
            tags_list.append("::".join(current_hierarchy_parts))
        self.tags = sorted(list(set(tags_list)))

    def _pp_df_audio(self, data: pandas.DataFrame):
        self.audio_filename = f"{self.greek}.mp3"

    def _pp_an_audio(self, note: genanki.Note):
        filename = self.audio_filename
        match = self.filename_re.match(filename)
        if match:
            self.audio_filename = match.groupdict().get("filename", "")
