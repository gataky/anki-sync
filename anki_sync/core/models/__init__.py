"""Anki Sync Models Package."""

from .constants import (
    ANKI_MODEL_NAME,
    ANKI_NOTE_MODEL,
    ANKI_NOTE_MODEL_FIELDS,
    Gender,
    Number,
    PartOfSpeech,
    Person,
    Tense,
)
from .genanki import Card, Deck, DeckInfo, Note, Rev
from .word import AudioMeta, Word

__all__ = [
    # Word models
    "Word",
    "AudioMeta",
    # Genanki models
    "Deck",
    "DeckInfo",
    "Note",
    "Card",
    "Rev",
    # Constants
    "ANKI_NOTE_MODEL",
    "ANKI_MODEL_NAME",
    "ANKI_NOTE_MODEL_FIELDS",
    # Enums
    "PartOfSpeech",
    "Gender",
    "Person",
    "Number",
    "Tense",
]
