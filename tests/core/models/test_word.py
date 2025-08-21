import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from anki_sync.core.models.word import (
    AudioMeta,
    BaseWord,
    Noun,
    PartOfSpeech,
)


@pytest.fixture
def noun_data() -> dict:
    return {
        "english": "test english",
        "greek": "test greek",
        "part_of_speech": PartOfSpeech.NOUN,
        "gender": "masculine",
        "tag": "test tag",
        "sub tag 1": "test sub tag 1",
        "guid": "test_guid",
    }


@pytest.fixture
def noun_series(noun_data: dict) -> pd.Series:
    return pd.Series(noun_data)


class TestBaseWord:
    def test_init(self, noun_data: dict):
        word = BaseWord(**noun_data)
        assert word.english == "test english"
        assert word.greek == "test greek"

    def test_process_tags(self, noun_data: dict):
        series = pd.Series(noun_data)
        word = Noun(**noun_data)
        word.process_tags(series)
        assert word.tags == ["test tag", "test sub tag 1"]

    @patch("anki_sync.core.models.word.generate_guid")
    def test_from_sheets(self, mock_generate_guid: MagicMock, noun_series: pd.Series):
        mock_generate_guid.return_value = "test_guid"
        row = (0, noun_series)
        word = Noun.from_sheets(row)

        assert isinstance(word, Noun)
        assert word.english == "test english"
        assert word.greek == "test greek"
        assert word.part_of_speech == PartOfSpeech.NOUN
        assert word.gender == "masculine"
        assert word.tags == ["test tag", "test sub tag 1"]
        assert word.audio_filename == "test greek.mp3"
        assert word._google_sheet_cell == "A2"

    def test_from_ankidb(self):
        note_data = {
            "data": json.dumps(
                {
                    "english": "test english",
                    "greek": "test greek",
                    "part_of_speech": "noun",
                    "gender": "masculine",
                }
            ),
            "name": "test_guid",
            "id": 123,
        }
        note = pd.Series(note_data)
        word = Noun.from_ankidb(note)

        assert isinstance(word, Noun)
        assert word.english == "test english"
        assert word.greek == "test greek"
        assert word.guid == "test_guid"
        assert word.id == 123

    def test_from_ankidb_with_no_data(self):
        note_data = {"data": None, "name": "test_guid", "id": 123}
        note = pd.Series(note_data)
        word = Noun.from_ankidb(note)
        assert word is None

    def test_to_note(self, noun_data: dict):
        mock_anki_db = MagicMock()
        mock_anki_db.get_note_id_by_guid.return_value = (123, True)
        word = Noun(**noun_data)
        note = word.to_note(mock_anki_db)

        assert note.id == 123
        assert note.guid == "test_guid"
        assert note.fields[0] == "test english"
        assert note.fields[1] == "test greek"
        assert note.fields[3] == "noun masculine"
        assert "grammar::noun" in note.tags

    @patch("anki_sync.core.models.word.generate_guid")
    def test_to_note_with_new_guid(
        self, mock_generate_guid: MagicMock, noun_data: dict
    ):
        mock_generate_guid.return_value = "new_guid"
        mock_anki_db = MagicMock()
        mock_anki_db.get_note_id_by_guid.return_value = (None, False)
        word = Noun(**noun_data)
        note = word.to_note(mock_anki_db)

        assert note.id is None
        assert note.guid == "new_guid"

    def test_get_note_tags(self, noun_data: dict):
        word = Noun(**noun_data)
        word.tags = ["tag1", "tag2"]
        tags = word.get_note_tags()
        assert tags == ["grammar::noun", "tag1", "tag1::tag2"]

    def test_get_note_tags_with_no_tags(self, noun_data: dict):
        word = Noun(**noun_data)
        word.tags = []
        tags = word.get_note_tags()
        assert tags == ["grammar::noun"]

    def test_get_audio_meta(self, noun_data: dict):
        word = Noun(**noun_data)
        word.audio_filename = "test.mp3"
        audio_meta = word.get_audio_meta()
        assert isinstance(audio_meta, AudioMeta)
        assert audio_meta.phrase == "test greek"
        assert audio_meta.filename == "test.mp3"

    def test_process_audio_filename(self, noun_data: dict):
        word = Noun(**noun_data)
        filename = word.process_audio_filename()
        assert filename == "test greek.mp3"



