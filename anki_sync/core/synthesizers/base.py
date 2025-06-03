from abc import ABC, abstractmethod


class BaseSynthesizer(ABC):
    """Abstract base class for text-to-speech synthesizers.

    This class defines the interface that all synthesizer implementations must follow.
    Each implementation should provide its own way of converting text to speech and
    saving the audio file to the specified directory.
    """

    @abstractmethod
    def synthesize(self, text: str, output_directory: str) -> None:
        """Synthesize text to speech and save to the output directory.

        Args:
            text: The text to synthesize into speech
            output_directory: Directory where the audio file will be saved
        """
