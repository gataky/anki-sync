from pydantic import BaseModel, Field
from typing import List, Optional # Added Optional and List
from ..utils.guid import generate_guid


class Word(BaseModel):
    """Represents a vocabulary word with its translations and metadata.

    This class stores all information about a word, including its Greek and English
    translations, associated audio file, and tags for organization.
    """

    guid: str = Field(
        default_factory=lambda: generate_guid(10),
        description="Unique identifier for the word (10 characters). Auto-generated if not provided.",
    )
    english: str = Field(..., description="The English word.")
    greek: str = Field(..., description="The Greek translation.")
    word_class: str = Field(
        default="", description="Class of the word (e.g., noun, verb, adjective)."
    )
    gender: str | None = Field(
        None,
        description="Gender of the word (e.g., masculine, feminine, neuter, masculine pl.).",
    )
    sound: str = Field(
        default="",
        description="Filename of the sound file for the Greek word (e.g., 'word.mp3').",
    )
    tags: list[str] = Field(
        default_factory=list, description="A list of tags for the word."
    )

    class Config:
        validate_assignment = True
        # If you want to allow extra fields from the sheet that are not defined in the model:
        # extra = "ignore" # or "allow"


class Verb(BaseModel):
    """Represents a verb with its conjugations and metadata."""

    guid: str = Field(
        default_factory=lambda: generate_guid(10),
        description="Unique identifier for the verb (10 characters). Auto-generated if not provided.",
    )
    english: str = Field(..., description="The English meaning of the verb.")
    greek_citation: str = Field(
        ..., description="The main Greek verb form (e.g., for audio, primary display)."
    )
    group: Optional[str] = Field(None, description="Verb group (e.g., A, B1, B2).")
    # Removed irregular, imperfective_stem, perfective_stem as per new headers
    # New tense fields based on the updated sheet headers
    present_tense: Optional[str] = Field(
        None, description="The present tense form of the verb."
    )
    past_simple: Optional[str] = Field(
        None, description="The past simple (e.g., aorist) form of the verb."
    )
    past_continuous: Optional[str] = Field(
        None, description="The past continuous (e.g., imperfect) form of the verb."
    )
    future_continuous: Optional[str] = Field(
        None, description="The future continuous tense form of the verb."
    )
    future_simple: Optional[str] = Field(
        None, description="The future simple tense form of the verb."
    )
    sound: str = Field(
        default="",
        description="Filename of the sound file for the Greek verb (e.g., 'verb.mp3').",
    )
    tags: List[str] = Field(
        default_factory=list, description="A list of tags for the verb."
    )

    class Config:
        validate_assignment = True
