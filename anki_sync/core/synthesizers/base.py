from abc import ABC, abstractmethod
from typing import Optional

class BaseSynthesizer(ABC):
    """Abstract base class for text-to-speech synthesizers."""

    @abstractmethod
    def synthesize(self, text: str, output_directory: str) -> None:
        """Synthesize text to speech and save to the output directory.

        Args:
            text: The text to synthesize
            output_directory: Directory where the audio file will be saved
        """
        pass
