"""Anki model definitions."""

import genanki

from .templates import ANKI_NOTE_MODEL_CARDS
from .styles import ANKI_SHARED_CSS
from .fields import ANKI_NOTE_MODEL_FIELDS

# Core model identifiers
ANKI_MODEL_ID = 2607392323
ANKI_MODEL_NAME = "greek"

# Main Anki note model
ANKI_NOTE_MODEL = genanki.Model(
    ANKI_MODEL_ID,
    ANKI_MODEL_NAME,
    fields=ANKI_NOTE_MODEL_FIELDS,
    templates=ANKI_NOTE_MODEL_CARDS,
    css=ANKI_SHARED_CSS,
)
