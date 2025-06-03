import os
from typing import Literal, Optional

from .stats import Stats
from .synthesizers.base import BaseSynthesizer
from .synthesizers.elevenlabs import ElevenLabsSynthesizer
from .synthesizers.google import GoogleSynthesizer


class AudioSynthesizer:
    """Handles audio synthesis for words."""

    def __init__(
        self,
        output_directory: str,
        stats: Stats,
        synthesizer_type: Literal["elevenlabs", "google"] = "elevenlabs",
    ):
        """Initialize the audio synthesizer.

        Args:
            output_directory: Directory where sound files will be stored
            stats: Stats instance to track audio generation
            synthesizer_type: Type of synthesizer to use ("elevenlabs" or "google")
        """
        self.output_directory = output_directory
        self.stats = stats
        self.synthesizer: BaseSynthesizer = (
            ElevenLabsSynthesizer()
            if synthesizer_type == "elevenlabs"
            else GoogleSynthesizer()
        )

    def generate_sound_filename(self, word: str) -> Optional[str]:
        """Generates the sound filename for a word."""
        if word:
            return f"{word}.mp3"
        return None

    def synthesize_if_needed(self, word: str, sound_filename: str) -> None:
        """Synthesizes audio for a word if it doesn't exist.

        Args:
            word: The word to synthesize audio for
            sound_filename: The filename to save the audio as
        """
        if not (word and sound_filename and self.output_directory):
            return

        full_sound_path = os.path.join(self.output_directory, sound_filename)
        if not os.path.exists(full_sound_path):
            try:
                self.synthesizer.synthesize(word, self.output_directory)
                self.stats.audio_files_generated += 1
            except Exception:
                self.stats.errors["audio_synthesis"] = (
                    self.stats.errors.get("audio_synthesis", 0) + 1
                )
