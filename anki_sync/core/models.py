from dataclasses import dataclass
from typing import List, Optional  # Added Optional and List

from pydantic import BaseModel, Field

from ..utils.guid import generate_guid


@dataclass
class Audio:
    phrase: str
    filename: str


class Word(BaseModel):
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

    def get_audio(self) -> Audio:
        return Audio(phrase=self.greek, filename=f"{self.greek}.mp3")


class Verb(BaseModel):
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


class VerbConjugation(BaseModel):
    guid: str = Field(
        default_factory=lambda: generate_guid(10),
        description="Unique identifier for the verb (10 characters). Auto-generated if not provided.",
        alias="GUID",
    )
    id: int = Field(
        ..., alias="ID", description="Unique identifier for the conjugation entry."
    )
    verb: str = Field(
        ..., alias="Verb", description="The infinitive or base form of the Greek verb."
    )
    conjugated: str = Field(
        ..., alias="Conjugated", description="The conjugated form of the Greek verb."
    )
    english: str = Field(
        ..., alias="English", description="English translation of the conjugated verb."
    )
    greek_sentence: str = Field(
        ...,
        alias="Greek Sentence",
        description="A Greek sentence using the conjugated verb.",
    )
    english_sentence: str = Field(
        ...,
        alias="English Sentence",
        description="English translation of the Greek sentence.",
    )
    tense: str = Field(
        ...,
        alias="Tense",
        description="The grammatical tense of the conjugation (e.g., 'Past Simple').",
    )
    person: str = Field(
        ...,
        alias="Person",
        description="The grammatical person (e.g., '1st', '2nd', '3rd').",
    )
    number: str = Field(
        ...,
        alias="Number",
        description="The grammatical number (e.g., 'Singular', 'Plural').",
    )

    def get_audio(self) -> Audio:
        return Audio(phrase=self.conjugated, filename=f"{self.verb}-{self.id}.mp3")

    def get_example_audio(self) -> Audio:
        return Audio(
            phrase=self.greek_sentence, filename=f"{self.verb}-{self.id}-ex.mp3"
        )
