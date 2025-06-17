import hashlib
import os
from typing import List, Optional, Union, Any

from genanki import Deck, Model, Note, Package
import pandas as pd

from .models import Word, Verb, VerbConjugation
from ..utils.guid import generate_guid


class AnkiDeckManager:
    """Manages the creation and packaging of Anki decks.

    This class handles the creation of Anki decks from a list of Word objects,
    including the creation of notes, models, and packaging the deck with any
    associated media files.
    """

    # --- Word Model Definition ---
    ANKI_WORD_MODEL_ID = 1607392319  # Keep this consistent for words
    ANKI_WORD_MODEL_NAME = "Anki-Sync Basic (Eng-Gr with Sound)"
    ANKI_WORD_MODEL_FIELDS = [
        {"name": "GUID"},
        {"name": "English"},
        {"name": "Greek"},
        {"name": "Class"},
        {"name": "Gender"},
        {"name": "Sound"},  # For the sound file
    ]
    ANKI_WORD_MODEL_TEMPLATES = [
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

    # --- Verb Model Definition ---
    ANKI_VERB_MODEL_ID = 1607392321  # New Randomly generated ID for verbs
    ANKI_VERB_MODEL_NAME = "Anki-Sync Verb (Eng-Gr with Sound)"
    # Updated fields based on new Verb model and sheet structure
    ANKI_VERB_MODEL_FIELDS = [
        {"name": "GUID"},
        {"name": "Greek"}, # Main citation form
        {"name": "English"},
        {"name": "Example"},
        {"name": "Sound"},
        {"name": "SoundEx"},
        {"name": "Tense"},
        {"name": "Person"},
        {"name": "Number"},
    ]
    # Updated template to include a table for tenses
    ANKI_VERB_MODEL_TEMPLATES = [
        {
            "name": "Card 1 (English to Greek Verb)",
            "qfmt": '''
{{English}}
<br><small>{{Tense}} {{Person}} person {{Number}}</small>
''',
            "afmt": '''
{{FrontSide}}
<hr id="answer">
{{Greek}} {{Sound}}<br>{{Example}} {{SoundEx}}
''',
        },


        {
            "name": "Card 2 (Greek Verb to English)",
            "qfmt": '''
{{Greek}} {{Sound}}<br>{{Example}} {{SoundEx}}
<br><small>{{Tense}} {{Person}} person {{Number}}</small>
''',
            "afmt": '''
{{FrontSide}}
<hr id="answer">
{{English}}
''',
        },
    ]

    # Shared CSS or define ANKI_VERB_MODEL_CSS if different
    ANKI_SHARED_CSS = ".card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; } .note_type { font-size:0.8em; color:grey; }"

    def __init__(self) -> None:
        """Initialize the AnkiDeckManager with note models."""
        # Word Model
        word_model_fields = [
            {"name": field["name"], "ord": idx}
            for idx, field in enumerate(self.ANKI_WORD_MODEL_FIELDS)
        ]
        self.word_model = Model(
            self.ANKI_WORD_MODEL_ID,
            self.ANKI_WORD_MODEL_NAME,
            fields=word_model_fields,
            templates=self.ANKI_WORD_MODEL_TEMPLATES,
            css=self.ANKI_SHARED_CSS,
        )

        # Verb Model
        verb_model_fields = [
            {"name": field["name"], "ord": idx}
            for idx, field in enumerate(self.ANKI_VERB_MODEL_FIELDS)
        ]
        self.verb_model = Model(
            self.ANKI_VERB_MODEL_ID,
            self.ANKI_VERB_MODEL_NAME,
            fields=verb_model_fields,
            templates=self.ANKI_VERB_MODEL_TEMPLATES,
            css=self.ANKI_SHARED_CSS,
        )

    def _create_deck(self, deck_name: str) -> Deck:
        """Creates a new Anki deck with the given name."""
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        return Deck(deck_id, deck_name)

    def _process_item_sound_file(
        self, item: Union[Word, Verb], sound_files_dir: Optional[str]
    ) -> tuple[str, List[str]]:
        """Process sound file for an item (Word or Verb) and return the sound field value and media files list."""
        sound_field_value = ""
        media_files: List[str] = []

        if item.sound: # Both Word and Verb have a .sound attribute
            if sound_files_dir:
                sound_file_path = os.path.join(sound_files_dir, item.sound)
                if os.path.exists(sound_file_path):
                    media_files.append(sound_file_path)
                    sound_field_value = f"[sound:{item.sound}]"
        return sound_field_value, media_files

    def _create_word_note(self, word: Word, sound_field_value: str) -> Note:
        """Creates an Anki note for a Word object."""
        note_fields = [
            word.guid,
            word.english,
            word.greek,
            word.word_class or "",
            word.gender or "",
            sound_field_value,
        ]
        return Note(
            model=self.word_model,
            fields=note_fields,
            tags=word.tags,
            guid=word.guid,  # Explicitly set the note's GUID
        )

    def create_word_deck(
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
            sound_field_value, word_media_files = self._process_item_sound_file(word, audio_directory)
            media_files.extend(word_media_files)

            # Create note using the helper method
            note = self._create_word_note(word, sound_field_value)
            deck.add_note(note)

        # Create and write the package
        package = Package(deck)
        if media_files:
            package.media_files = media_files
        package.write_to_file(output_file)

    def create_verb_deck(
        self,
        verbs_df: pd.DataFrame,
        deck_name: str,
        output_file: str,
        audio_directory: Optional[str] = None,
    ) -> None:
        """Create an Anki deck from a DataFrame of verb conjugations and save it as a package.

        Args:
            verbs_df: DataFrame containing verb conjugation data
            deck_name: Name of the Anki deck to create
            output_file: Path where the .apkg file will be saved
            audio_directory: Optional path to directory containing sound files
        """
        deck = self._create_deck(deck_name)
        media_files = []

        for _, row in verbs_df.iterrows():
            # Create VerbConjugation object from row
            verb_conj = VerbConjugation(**row.to_dict())

            # Get sound files for both conjugated form and example
            conjugated_sound, conjugated_phrase = verb_conj.get_conjugated_audio()
            example_sound, example_phrase = verb_conj.get_example_audio()

            # Process sound files
            sound_field_value = ""
            example_sound_field_value = ""
            if audio_directory:
                conjugated_path = os.path.join(audio_directory, conjugated_sound)
                example_path = os.path.join(audio_directory, example_sound)
                if os.path.exists(conjugated_path):
                    media_files.append(conjugated_path)
                    sound_field_value = f"[sound:{conjugated_sound}]"
                if os.path.exists(example_path):
                    media_files.append(example_path)
                    example_sound_field_value = f"[sound:{example_sound}]"

            # Create note with the new fields
            note_fields = [
                verb_conj.guid,  # Using ID as GUID
                verb_conj.conjugated,  # Greek conjugated form
                verb_conj.english,  # English translation
                verb_conj.greek_sentence,  # Example sentence
                sound_field_value,  # Sound for conjugated form
                example_sound_field_value,  # Sound for example sentence
                verb_conj.tense.lower(),
                verb_conj.person.lower(),
                verb_conj.number.lower(),
            ]

            note = Note(
                model=self.verb_model,
                fields=note_fields,
                tags=[f"verb::{verb_conj.verb}"],  # Tag with base verb
                guid=str(verb_conj.id),  # Use ID as GUID
            )
            deck.add_note(note)

        package = Package(deck)
        if media_files:
            package.media_files = list(set(media_files))  # Ensure unique media files
        package.write_to_file(output_file)
