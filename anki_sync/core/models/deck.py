import hashlib
import os
import pathlib
from typing import Literal

import attr
import genanki

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
