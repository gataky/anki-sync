"""Anki vocabulary enums and constants."""

from enum import Enum


class PartOfSpeech(Enum):
    """Parts of speech for vocabulary words."""

    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    CONJUNCTION = "conjunction"
    NOUN = "noun"
    PREPOSITION = "preposition"
    VERB = "verb"
    UNKNOWN = "unknown"


class Gender(Enum):
    """Grammatical gender for vocabulary words."""

    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"
    A = "a"
    B1 = "b1"
    B2 = "b2"
    IRREGULAR = "irregular"
    UNKNOWN = ""


class Person(Enum):
    """Grammatical person for verbs."""

    FIRST = "1st"
    SECOND = "2nd"
    THIRD = "3rd"
    UNKNOWN = ""


class Number(Enum):
    """Grammatical number (singular/plural)."""

    SINGULAR = "singular"
    PLURAL = "plural"
    UNKNOWN = ""


class Tense(Enum):
    """Grammatical tense for verbs."""

    UNKNOWN = ""
