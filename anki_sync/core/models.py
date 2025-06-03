from pydantic import BaseModel, Field

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
