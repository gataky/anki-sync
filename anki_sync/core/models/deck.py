import hashlib
import os
import pathlib
from typing import Literal

import attr
import genanki

from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.sql import AnkiDatabase
from anki_sync.core.synthesizers.audio_synthesizer import AudioSynthesizer

from .adjective import Adjective
from .noun import Noun
from .verb import VerbConjugation


@attr.s(auto_attribs=True, init=True)
class DeckInfo:
    sheet: str
    note_class: type[Noun | VerbConjugation | Adjective]
    synthesizer: Literal["elevenlabs", "google"] = "google"
    source: str = "remote"


class Deck(genanki.Deck):

    def __init__(self, deck_name: str, media_dir: pathlib.Path):
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        super().__init__(deck_id, deck_name)
        self.media_dir = media_dir
        self.audio_files = []

    def add_audio(self, audio_filename: str):
        path = os.path.join(self.media_dir, audio_filename)
        self.audio_files.append(path)

    def generate(
        self, anki_db: AnkiDatabase, gsheet: GoogleSheetsManager, deck_info: DeckInfo
    ):
        gnotes = gsheet.get_notes(deck_info.sheet)

        synth = AudioSynthesizer(self.media_dir, deck_info.synthesizer)

        rows_to_update = []
        for row in gnotes.iterrows():
            gnote = deck_info.note_class.from_sheets(row)
            anote = gnote.to_note(anki_db)

            self.add_audio(gnote.audio_filename)
            self.add_note(anote)

            audio = gnote.get_audio_meta()
            synth.synthesize_if_needed(audio.phrase, audio.filename)

            if not gnote.exists_in_anki():
                cell = f"{deck_info.sheet}!{gnote._google_sheet_cell}"
                rows_to_update.append(
                    {
                        "range": cell,
                        "values": [[gnote.guid]],
                    }
                )

                print(f"        + {gnote.guid}: {gnote.english}")

        return rows_to_update
