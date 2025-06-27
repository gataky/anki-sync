import hashlib
import os
from typing import List, Optional, Union

import pandas as pd
from genanki import Deck, Model, Note, Package

from .models.noun import Noun
from .models.verb import Verb, VerbConjugation


class AnkiDeckManager:
    """Manages the creation and packaging of Anki decks.

    This class handles the creation of Anki decks from a list of Word objects,
    including the creation of notes, models, and packaging the deck with any
    associated media files.
    """

    # --- Word Model Definition ---

    # --- Verb Model Definition ---

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

    def _augment_english_verb_phrase(
        self,
        english_phrase: str,
        tense: str,
        number: str,
        person: str,
    ) -> str:
        """
        Augments an English verb phrase with subscripts for aspect and number.
        e.g., "I was running" (Imperfective, Singular) -> "I<sub>IS</sub> was running<sub>IS</sub>"
        e.g., "I ran" (Perfective, Singular) -> "I<sub>PS</sub> ran<sub>PS</sub>"
        """
        tense_lower = tense.lower()
        if "continuous" in tense_lower or "present" in tense_lower:
            aspect_subscript = "⟳"  # Imperfective
        else:  # simple tenses
            aspect_subscript = "●"  # Perfective

        if person == "2nd":
            number_subscript = "👤" if number.lower() == "singular" else "👥"
        else:
            number_subscript = ""

        parts = english_phrase.strip().split(" ")
        if not parts or not parts[0]:
            return english_phrase  # Return original if empty or malformed

        middle_part = " ".join(parts[1:-1])
        return f"{parts[0]}<sup>{number_subscript}</sup> {middle_part} {parts[-1]}<sup>{aspect_subscript}</sup>".replace(
            "  ", " "
        )

    def _create_deck(self, deck_name: str) -> Deck:
        """Creates a new Anki deck with the given name."""
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        return Deck(deck_id, deck_name)

    def _process_item_sound_file(
        self, item: Union[Noun, Verb], sound_files_dir: Optional[str]
    ) -> tuple[str, List[str]]:
        """Process sound file for an item (Word or Verb) and return the sound field value and media files list."""
        sound_field_value = ""
        media_files: List[str] = []

        if item.sound:  # Both Word and Verb have a .sound attribute
            if sound_files_dir:
                sound_file_path = os.path.join(sound_files_dir, item.sound)
                if os.path.exists(sound_file_path):
                    media_files.append(sound_file_path)
                    sound_field_value = f"[sound:{item.sound}]"
        return sound_field_value, media_files

    def _create_word_note(self, word: Noun, sound_field_value: str) -> Note:
        """Creates an Anki note for a Word object."""
        note_fields = [
            # word.guid,
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
        words: List[Noun],
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
            sound_field_value, word_media_files = self._process_item_sound_file(
                word, audio_directory
            )
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

            # Augment the English phrase with aspect and number subscripts
            augmented_english = self._augment_english_verb_phrase(
                verb_conj.english, verb_conj.tense, verb_conj.number, verb_conj.person
            )

            # Get sound files for both conjugated form and example
            conjugated_sound = verb_conj.get_audio()
            example_sound = verb_conj.get_example_audio()

            # Process sound files
            sound_field_value = ""
            example_sound_field_value = ""
            if audio_directory:
                conjugated_path = os.path.join(
                    audio_directory, conjugated_sound.filename
                )
                example_path = os.path.join(audio_directory, example_sound.filename)
                if os.path.exists(conjugated_path):
                    media_files.append(conjugated_path)
                    sound_field_value = f"[sound:{conjugated_sound.filename}]"
                if os.path.exists(example_path):
                    media_files.append(example_path)
                    example_sound_field_value = f"[sound:{example_sound.filename}]"

            # Create note with the new fields
            note_fields = [
                verb_conj.guid,  # Using ID as GUID
                verb_conj.conjugated,  # Greek conjugated form
                augmented_english,  # Augmented English translation
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
