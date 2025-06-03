import os
from typing import Optional
from .base import BaseSynthesizer
from elevenlabs.client import ElevenLabs

class ElevenLabsSynthesizer(BaseSynthesizer):
    """ElevenLabs text-to-speech synthesizer implementation."""

    def __init__(self):
        """Initialize the ElevenLabs synthesizer."""
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )

    def synthesize(self, text: str, output_directory: str) -> None:
        """Synthesize text to speech using ElevenLabs.

        Args:
            text: The text to synthesize
            output_directory: Directory where the audio file will be saved
        """
        if not (text and output_directory and self.client):
            return

        output_filename = f"{output_directory}/{text.split(' ', 1)[1]}.mp3"
        voice_id = "2Lb1en5ujrODDIqmp7F3"
        model_id = "eleven_multilingual_v2"

        try:
            audio_stream = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id=model_id,
                output_format="mp3_44100_128",
            )

            # Collect all audio chunks from the generator
            full_audio_bytes = b""  # Initialize an empty bytes object
            for chunk in audio_stream:
                if chunk:  # Ensure chunk is not empty
                    full_audio_bytes += chunk

            # Write the collected bytes to the file
            with open(output_filename, "wb") as f:
                f.write(full_audio_bytes)
        except Exception as e:
            print(f"Error synthesizing '{text}': {e}")
