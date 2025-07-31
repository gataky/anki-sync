"""
Base class for simple word models (adverb, preposition, conjunction).
"""

import attr
import genanki
import pandas

from anki_sync.core.models.audio import AudioMeta
from anki_sync.core.models.base import BaseWord
from anki_sync.core.models.constants import (
    ANKI_SHARED_CSS,
    BASIC_WORD_MODEL_FIELDS,
    BASIC_WORD_MODEL_TEMPLATES,
    MODEL_IDS,
)
from anki_sync.core.models.note import Note
from anki_sync.core.sql import AnkiDatabase
from anki_sync.utils.guid import generate_guid


def create_simple_word_model(word_type: str):
    """Create a genanki Model for simple word types."""
    model_id = MODEL_IDS.get(word_type, 1600000000)
    model_name = f"greek {word_type}"
    
    model_fields = [
        {"name": field["name"], "ord": idx}
        for idx, field in enumerate(BASIC_WORD_MODEL_FIELDS)
    ]
    
    return genanki.Model(
        model_id,
        model_name,
        fields=model_fields,
        templates=BASIC_WORD_MODEL_TEMPLATES,
        css=ANKI_SHARED_CSS,
    )


@attr.s(auto_attribs=True, init=False)
class SimpleWord(BaseWord):
    """Base class for simple word types (adverb, preposition, conjunction)."""

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
        
        # Get the model for this word type
        model = create_simple_word_model(self._get_word_type())
        
        return Note(
            model=model,
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

    def generate_note_tags(self) -> list[str]:
        tags_list = [f"grammar::{self._get_word_type()}"]
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
            "tags": self.tags,
            "audio_filename": self.audio_filename,
        }
        return str(meta)

    def _get_word_type(self) -> str:
        """Override this method in subclasses to return the word type."""
        raise NotImplementedError("Subclasses must implement _get_word_type()") 