import hashlib
import os
from typing import List, Optional

from genanki import Deck, Model, Note, Package

from .models import Word


class AnkiDeckManager:
    """Manages the creation and packaging of Anki decks.

    This class handles the creation of Anki decks from a list of Word objects,
    including the creation of notes, models, and packaging the deck with any
    associated media files.
    """

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

    def __init__(self) -> None:
        """Initialize the AnkiDeckManager with the default note model."""
        # Format fields with both name and ord
        fields = [
            {"name": field["name"], "ord": idx}
            for idx, field in enumerate(self.ANKI_MODEL_FIELDS)
        ]

        self.model = Model(
            self.ANKI_MODEL_ID,
            self.ANKI_MODEL_NAME,
            fields=fields,
            templates=self.ANKI_MODEL_TEMPLATES,
            css=self.ANKI_MODEL_CSS,
        )

    def _create_deck(self, deck_name: str) -> Deck:
        """Creates a new Anki deck with the given name."""
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        return Deck(deck_id, deck_name)

    def _process_sound_file(
        self, word: Word, sound_files_dir: Optional[str]
    ) -> tuple[str, List[str]]:
        """Process sound file for a word and return the sound field value and media files list."""
        sound_field_value = ""
        media_files: List[str] = []

        if word.sound:
            if sound_files_dir:
                sound_file_path = os.path.join(sound_files_dir, word.sound)
                if os.path.exists(sound_file_path):
                    media_files.append(sound_file_path)
                    sound_field_value = f"[sound:{word.sound}]"  # Anki format for sound

        return sound_field_value, media_files

    def _create_note(self, word: Word, sound_field_value: str) -> Note:
        """Creates an Anki note for a word."""
        note_fields = [
            word.guid,
            word.english,
            word.greek,
            word.word_class or "",
            word.gender or "",
            sound_field_value,
        ]
        return Note(
            model=self.model,
            fields=note_fields,
            tags=word.tags,
            guid=word.guid,  # Explicitly set the note's GUID
        )

    def create_deck(
        self,
        words: List[Word],
        deck_name: str,
        output_file: str,
        audio_directory: Optional[str] = None,
    ) -> None:
        """Create an Anki deck from a list of words and save it as a package.

        Args:
            words: List of Word objects to include in the deck
            deck_name: Name of the Anki deck to create
            output_file: Path where the .apkg file will be saved
            audio_directory: Optional path to directory containing sound files
        """
        deck = self._create_deck(deck_name)
        media_files = []

        for word in words:
            # Process sound file and get media files
            sound_field_value, word_media_files = self._process_sound_file(word, audio_directory)
            media_files.extend(word_media_files)

            # Create note using the helper method
            note = self._create_note(word, sound_field_value)
            deck.add_note(note)

        # Create and write the package
        package = Package(deck)
        if media_files:
            package.media_files = media_files
        package.write_to_file(output_file)
