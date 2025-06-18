import logging
import os
from pathlib import Path
from typing import Optional

import google.generativeai as genai

# Configure logging for the module
logger = logging.getLogger(__name__)


class GeminiClientError(Exception):
    """Base exception for GeminiClient errors."""


class GeminiAuthError(GeminiClientError):
    """Exception raised for authentication/configuration errors."""


class GeminiQueryError(GeminiClientError):
    """Exception raised for errors during API query."""


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


class GeminiClient:
    """
    A client for interacting with the Google Gemini API using service account authentication.
    """

    def __init__(self, system_instruction: Optional[str] = my_system_instruction):
        """
        Initializes the GeminiClient.

        Args:
            service_account_key_path: Path to the Google service account JSON key file.
            model_name: The name of the Gemini model to use (e.g., "gemini-1.5-flash").
            system_instruction: Optional system-level instructions for the model.

        Raises:
            FileNotFoundError: If the service account key file is not found.
            GeminiAuthError: If there's an error configuring the Gemini API.
        """
        home_directory = str(Path.home())
        service_account_key_path = os.path.join(
            home_directory, ".bunes-service-account.json"
        )
        model_name = "gemini-1.5-flash"

        self.service_account_key_path = service_account_key_path
        self.model_name = model_name
        self.system_instruction = system_instruction
        self._configure_authentication()

    def _configure_authentication(self):
        """
        Configures authentication for the Gemini API using the service account.
        Sets the GOOGLE_APPLICATION_CREDENTIALS environment variable and initializes genai.
        """
        if not os.path.exists(self.service_account_key_path):
            raise FileNotFoundError(
                f"Service account key file not found at {self.service_account_key_path}."
            )

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.service_account_key_path
        logger.info(
            f"GOOGLE_APPLICATION_CREDENTIALS set to: {self.service_account_key_path}"
        )

        try:
            genai.configure(api_key=None)  # Uses GOOGLE_APPLICATION_CREDENTIALS
            logger.info("Gemini API configured successfully using service account.")
        except Exception as e:
            logger.error(
                f"Error configuring Gemini API with service account: {e}", exc_info=True
            )
            raise GeminiAuthError(
                "Failed to configure Gemini API. Ensure key file is valid and has API access."
            ) from e

    def query(self, prompt_text: str) -> str:
        """
        Queries the configured Gemini model.

        Args:
            prompt_text: The prompt to send to the model.

        Returns:
            The text response from the model.

        Raises:
            GeminiQueryError: If an error occurs during the API call or response is problematic.
        """
        try:
            model = genai.GenerativeModel(
                self.model_name, system_instruction=self.system_instruction
            )
            logger.info(f"Sending prompt to Gemini model '{self.model_name}'.")
            response = model.generate_content(prompt_text)

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                raise GeminiQueryError(
                    f"Gemini response blocked: {response.prompt_feedback.block_reason}"
                )
            return response.text
        except Exception as e:
            logger.error(
                f"An error occurred during the Gemini API call: {e}", exc_info=True
            )
            raise GeminiQueryError(f"Gemini API call failed: {e}") from e
