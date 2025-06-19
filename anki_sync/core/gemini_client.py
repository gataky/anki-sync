from typing import Optional

import google.generativeai as genai
from google import genai
from google.genai import types

from anki_sync.core.auth.auth import GoogleAuth


class GeminiClientError(Exception):
    """Base exception for GeminiClient errors."""


my_system_instruction = """
You are a factual, to the point, and knowledgeable modern Greek tool.

Do not include Romanization and I would like the output to be in CSV form.

You will be given a verb and I would like you conjugate the verb in this order:
    Past Simple 1st person singular.
    Past Simple 2nd person singular.
    Past Simple 3rd person singular.
    Past Simple 1st person plural.
    Past Simple 2nd person plural.
    Past Simple 3rd person plural.
    Past Continuous 1st person singular.
    Past Continuous 2nd person singular.
    Past Continuous 3rd person singular.
    Past Continuous 1st person plural.
    Past Continuous 2nd person plural.
    Past Continuous 3rd person plural.
    Present 1st person singular.
    Present 2nd person singular.
    Present 3rd person singular.
    Present 1st person plural.
    Present 2nd person plural.
    Present 3rd person plural.
    Future Continuous 1st person singular.
    Future Continuous 2nd person singular.
    Future Continuous 3rd person singular.
    Future Continuous 1st person plural.
    Future Continuous 2nd person plural.
    Future Continuous 3rd person plural.
    Future Simple 1st person singular.
    Future Simple 2nd person singular.
    Future Simple 3rd person singular.
    Future Simple 1st person plural.
    Future Simple 2nd person plural.
    Future Simple 3rd person plural.

Each conjugation above should be a row and should have the following fields:
    The conjugated Greek verb.
    The English translation of the verb.
    An example in Greek using the verb.
    English translation of the example.
    The tense.
    The person.
    The number (i.e. singular or plural).
    """


class GeminiClient(GoogleAuth):

    def __init__(
        self,
        system_instruction: Optional[str] = my_system_instruction,
        model_name="gemini-1.5-flash",
    ):
        super().__init__()
        self.client = genai.Client(api_key=self.key)  # Uses GOOGLE_API_KEY
        self.model_name = model_name
        self.system_instruction = system_instruction

    def query(self, prompt_text: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt_text,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction
            ),
        )

        if response.prompt_feedback and response.prompt_feedback.block_reason:
            raise GeminiClientError(
                f"Gemini response blocked: {response.prompt_feedback.block_reason}"
            )
        return response.text
