"""Anki Sync Models Package."""

from .word import Word, AudioMeta
from .genanki import Deck, DeckInfo, Note, Card, Rev
from .constants import (
    ANKI_NOTE_MODEL,
    ANKI_MODEL_NAME,
    ANKI_NOTE_MODEL_FIELDS,
    PartOfSpeech,
    Gender,
    Person,
    Number,
    Tense,
)

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
