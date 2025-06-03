import hashlib
import os
from typing import List, Optional

import genanki

from .models import Word

class AnkiDeckManager:
    """Manages the creation and configuration of Anki decks."""

    # Define a simple Anki note model
    ANKI_MODEL_ID = 1607392319  # Randomly generated ID, keep this consistent
    ANKI_MODEL_NAME = "Anik-Sync Basic (Eng-Gr with Sound)"
    ANKI_MODEL_FIELDS = [
        {"name": "GUID"},
        {"name": "English"},
        {"name": "Greek"},
        {"name": "Class"},
        {"name": "Gender"},
        {"name": "Sound"},  # For the sound file
    ]
    ANKI_MODEL_TEMPLATES = [
        {
            "name": "Card 1 (English to Greek)",
            "qfmt": "{{English}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{Greek}}<br>{{Sound}}',
        },
        {
            "name": "Card 2 (Greek to English)",
            "qfmt": "{{Greek}}<br>{{Sound}}",
            "afmt": '{{FrontSide}}<hr id="answer">{{English}}',
        },
    ]

    ANKI_MODEL_CSS = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } .note_type { font-size:0.8em; color:grey; }"

    def __init__(self):
        """Initialize the Anki deck manager with the model configuration."""
        self.model = genanki.Model(
            self.ANKI_MODEL_ID,
            self.ANKI_MODEL_NAME,
            fields=self.ANKI_MODEL_FIELDS,
            templates=self.ANKI_MODEL_TEMPLATES,
            css=self.ANKI_MODEL_CSS,
        )

    def _create_deck(self, deck_name: str) -> genanki.Deck:
        """Creates a new Anki deck with the given name."""
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        return genanki.Deck(deck_id, deck_name)

    def _process_sound_file(self, word: Word, sound_files_dir: Optional[str]) -> tuple[str, List[str]]:
        """Process sound file for a word and return the sound field value and media files list."""
        sound_field_value = ""
        media_files: List[str] = []

        if word.sound_file:
            if sound_files_dir:
                sound_file_path = os.path.join(sound_files_dir, word.sound_file)
                if os.path.exists(sound_file_path):
                    media_files.append(sound_file_path)
                    sound_field_value = f"[sound:{word.sound_file}]"  # Anki format for sound

        return sound_field_value, media_files

    def _create_note(self, word: Word, sound_field_value: str) -> genanki.Note:
        """Creates an Anki note for a word."""
        note_fields = [
            word.guid,
            word.english,
            word.greek,
            word.word_class,
            word.gender or "",
            sound_field_value,
        ]
        return genanki.Note(
            model=self.model,
            fields=note_fields,
            tags=word.tags,
            guid=word.guid,  # Explicitly set the note's GUID
        )

    def create_deck(
        self,
        words: List[Word],
        deck_name: str,
        output_abs_path: str,
        audio_directory: Optional[str] = None,
    ) -> None:
        """
        Creates an Anki deck package (.apkg) from a list of words.

        Args:
            words: A list of Word objects.
            deck_name: The desired name for the Anki deck.
            output_abs_path: The absolute file path to save the .apkg file.
            sound_files_dir: Optional. Directory where sound files (e.g., word.sound_file) are located.
        """
        print(f"Creating Anki deck '{deck_name}' with {len(words)} words.")

        anki_deck = self._create_deck(deck_name)
        media_files_to_package: List[str] = []

        for word in words:
            sound_field_value, word_media_files = self._process_sound_file(word, audio_directory)
            media_files_to_package.extend(word_media_files)

            anki_note = self._create_note(word, sound_field_value)
            anki_deck.add_note(anki_note)

        anki_package = genanki.Package(anki_deck)
        if media_files_to_package:
            anki_package.media_files = media_files_to_package

        anki_package.write_to_file(output_abs_path)
        print(f"Anki deck successfully saved to {output_abs_path}")
        if media_files_to_package:
            print(f"Included {len(media_files_to_package)} media files in the package.")
