import hashlib
import os

import genanki

from .models import Word

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

anki_model_instance = genanki.Model(
    ANKI_MODEL_ID,
    ANKI_MODEL_NAME,
    fields=ANKI_MODEL_FIELDS,
    templates=ANKI_MODEL_TEMPLATES,
    css=ANKI_MODEL_CSS,
)



def create_anki_deck(
    words: list[Word],
    deck_name: str,
    output_abs_path: str,
    sound_files_dir: str | None = None,
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

    deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
    anki_deck = genanki.Deck(deck_id, deck_name)
    media_files_to_package: list[str] = []

    for word in words:
        sound_field_value = ""
        if word.sound_file:
            if sound_files_dir:
                sound_file_path = os.path.join(sound_files_dir, word.sound_file)
                if os.path.exists(sound_file_path):
                    media_files_to_package.append(sound_file_path)
                    sound_field_value = (
                        f"[sound:{word.sound_file}]"  # Anki format for sound
                    )
                else:
                    print(
                        f"Warning: Sound file '{word.sound_file}' not found in '{sound_files_dir}' for word GUID {word.guid}."
                    )
            else:
                print(
                    f"Warning: Sound file '{word.sound_file}' specified for word GUID {word.guid}, but no sound_files_dir provided. Sound will not be packaged."
                )

        note_fields = [
            word.guid,
            word.english,
            word.greek,
            word.word_class,
            word.gender or "",
            sound_field_value,
        ]
        anki_note = genanki.Note(
            model=anki_model_instance,
            fields=note_fields,
            tags=word.tags,
            guid=word.guid,  # Explicitly set the note's GUID
        )
        anki_deck.add_note(anki_note)

    anki_package = genanki.Package(anki_deck)
    if media_files_to_package:
        anki_package.media_files = media_files_to_package

    anki_package.write_to_file(output_abs_path)
    print(f"Anki deck successfully saved to {output_abs_path}")
    if media_files_to_package:
        print(f"Included {len(media_files_to_package)} media files in the package.")
