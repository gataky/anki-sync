import hashlib
import os
from typing import List, Optional, Union, Any

from genanki import Deck, Model, Note, Package

from .models import Word, Verb # Added Verb


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
    ANKI_VERB_MODEL_ID = 1607392320  # New Randomly generated ID for verbs
    ANKI_VERB_MODEL_NAME = "Anki-Sync Verb (Eng-Gr with Stems)"
    # Updated fields based on new Verb model and sheet structure
    ANKI_VERB_MODEL_FIELDS = [
        {"name": "GUID"},
        {"name": "English"},
        {"name": "Greek"}, # Main citation form
        {"name": "Group"},
        {"name": "Present Tense"},
        {"name": "Past Simple"},
        {"name": "Past Continuous"},
        {"name": "Future Continuous"},
        {"name": "Future Simple"},
        {"name": "Sound"},
    ]
    # Updated template to include a table for tenses
    ANKI_VERB_MODEL_TEMPLATES = [
        {
            "name": "Card 1 (English to Greek Verb)",
            "qfmt": "{{English}}",
            "afmt": '''{{FrontSide}}
<hr id="answer">
{{Greek}} {{Sound}}<br><br>
<table style="text-align: left; margin-left: auto; margin-right: auto; border-collapse: collapse; color: black;">
  {{#Past Simple}}<tr style="background-color: #ffe598; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Past Simple:</td><td style="padding: 5px 0;">{{Past Simple}}</td></tr>{{/Past Simple}}
  {{#Past Continuous}}<tr style="background-color: #fff2cc; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Past Continuous:</td><td style="padding: 5px 0;">{{Past Continuous}}</td></tr>{{/Past Continuous}}
  {{#Present Tense}}<tr style="border-bottom: 1px solid #eee; color: white;"><td style="padding: 5px 10px 5px 0;">Present:</td><td style="padding: 5px 0;">{{Present Tense}}</td></tr>{{/Present Tense}}
  {{#Future Continuous}}<tr style="background-color: #c9daf8; color: black;"><td style="padding: 5px 10px 5px 0;">Future Continuous:</td><td style="padding: 5px 0;">{{Future Continuous}}</td></tr>{{/Future Continuous}}
  {{#Future Simple}}<tr style="background-color: #a4c2f4; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Future Simple:</td><td style="padding: 5px 0;">{{Future Simple}}</td></tr>{{/Future Simple}}
</table>
<br><small>{{#Group}}Group: {{Group}}{{/Group}}</small>''',
        },
        {
            "name": "Card 2 (Greek Verb to English)",
            "qfmt": "{{Greek}}<br>{{Sound}}",
            "afmt": '''{{FrontSide}}
<hr id="answer">
{{English}}<br><br>
<table style="text-align: left; margin-left: auto; margin-right: auto; border-collapse: collapse; color: black;">
  {{#Past Simple}}<tr style="background-color: #ffe598; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Past Simple:</td><td style="padding: 5px 0;">{{Past Simple}}</td></tr>{{/Past Simple}}
  {{#Past Continuous}}<tr style="background-color: #fff2cc; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Past Continuous:</td><td style="padding: 5px 0;">{{Past Continuous}}</td></tr>{{/Past Continuous}}
  {{#Present Tense}}<tr style="border-bottom: 1px solid #eee; color: white;"><td style="padding: 5px 10px 5px 0;">Present:</td><td style="padding: 5px 0;">{{Present Tense}}</td></tr>{{/Present Tense}}
  {{#Future Continuous}}<tr style="background-color: #c9daf8; color: black;"><td style="padding: 5px 10px 5px 0;">Future Continuous:</td><td style="padding: 5px 0;">{{Future Continuous}}</td></tr>{{/Future Continuous}}
  {{#Future Simple}}<tr style="background-color: #a4c2f4; color: black; border-bottom: 1px solid #eee;"><td style="padding: 5px 10px 5px 0;">Future Simple:</td><td style="padding: 5px 0;">{{Future Simple}}</td></tr>{{/Future Simple}}
</table>
<br><small>{{#Group}}Group: {{Group}}{{/Group}}</small>''',
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

    def _create_verb_note(self, verb: Verb, sound_field_value: str) -> Note:
        """Creates an Anki note for a Verb object."""
        note_fields = [
            verb.guid,
            verb.english,
            verb.greek_citation, # Main Greek form
            verb.group or "",
            verb.present_tense or "",
            verb.past_simple or "",
            verb.past_continuous or "",
            verb.future_continuous or "",
            verb.future_simple or "",
            sound_field_value,
        ]
        return Note(
            model=self.verb_model,
            fields=note_fields,
            tags=verb.tags,
            guid=verb.guid, # Explicitly set the note's GUID
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

    def create_combined_deck(
        self,
        deck_name: str,
        output_file: str,
        words: Optional[List[Word]] = None,
        verbs: Optional[List[Verb]] = None,
        audio_directory: Optional[str] = None,
    ) -> None:
        """
        Creates a single Anki deck containing notes from different models (words and verbs).
        """
        deck = self._create_deck(deck_name)
        # Models (self.word_model, self.verb_model) are automatically included in the package
        # by genanki if notes using them are added to the deck.

        media_files = []

        if words:
            for word_obj in words:
                sound_field_value, item_media_files = self._process_item_sound_file(word_obj, audio_directory)
                media_files.extend(item_media_files)
                note = self._create_word_note(word_obj, sound_field_value)
                deck.add_note(note)

        if verbs:
            for verb_obj in verbs:
                sound_field_value, item_media_files = self._process_item_sound_file(verb_obj, audio_directory)
                media_files.extend(item_media_files)
                note = self._create_verb_note(verb_obj, sound_field_value)
                deck.add_note(note)

        package = Package(deck)
        if media_files:
            # Ensure media files are unique if some sounds happen to be identical
            # though unlikely with current naming.
            package.media_files = list(set(media_files))
        package.write_to_file(output_file)



    def create_verb_deck(
        self,
        verbs: List[Verb],
        deck_name: str,
        output_file: str,
        audio_directory: Optional[str] = None,
    ) -> None:
        """Create an Anki deck from a list of verbs and save it as a package.

        Args:
            verbs: List of Verb objects to include in the deck
            deck_name: Name of the Anki deck to create
            output_file: Path where the .apkg file will be saved
            audio_directory: Optional path to directory containing sound files
        """
        deck = self._create_deck(deck_name)
        media_files = []

        for verb in verbs:
            sound_field_value, verb_media_files = self._process_item_sound_file(verb, audio_directory)
            media_files.extend(verb_media_files)

            note = self._create_verb_note(verb, sound_field_value)
            deck.add_note(note)

        package = Package(deck)
        if media_files:
            package.media_files = media_files
        package.write_to_file(output_file)
