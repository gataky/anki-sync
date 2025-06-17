import os
from typing import Literal, Optional

from .base import BaseSynthesizer
from .elevenlabs import ElevenLabsSynthesizer
from .google import GoogleSynthesizer


class AudioSynthesizer:
    """Handles audio synthesis for words.

    This class manages the synthesis of audio files for words, using either
    ElevenLabs or Google Cloud TTS as the backend synthesizer. It tracks
    statistics about the synthesis process and handles file management.
    """

    def __init__(
        self,
        output_directory: str,
        synthesizer_type: Literal["elevenlabs", "google"] = "elevenlabs",
    ):
        """Initialize the audio synthesizer.

        Args:
            output_directory: Directory where sound files will be stored
            synthesizer_type: Type of synthesizer to use ("elevenlabs" or "google")
        """
        self.output_directory = output_directory
        self.synthesizer: BaseSynthesizer = (
            ElevenLabsSynthesizer()
            if synthesizer_type == "elevenlabs"
            else GoogleSynthesizer()
        )

    def generate_sound_filename(self, word: str) -> Optional[str]:
        """Generates the sound filename for a word.

        Args:
            word: The word to generate a filename for

        Returns:
            The filename as "{word}.mp3" if word is not empty, None otherwise
        """
        if word:
            return f"{word}.mp3"
        return None

    def synthesize_if_needed(self, phrase: str, audio_filename: str) -> None:
        """Synthesizes audio for a word if it doesn't exist.

        Args:
            phrase: The word to synthesize audio for
            audio_filename: The filename to save the audio as

        This method will:
        1. Check if the audio file already exists
        2. If not, synthesize it using the configured synthesizer
        """
        if not (phrase and audio_filename and self.output_directory):
            return

        full_sound_path = os.path.join(self.output_directory, audio_filename)
        if not os.path.exists(full_sound_path):
            try:
                self.synthesizer.synthesize(phrase, full_sound_path)
                print(f"generating new audio {phrase}")
            except Exception as e:
                raise e
        else:
            print(f"audio exists for {phrase}")
