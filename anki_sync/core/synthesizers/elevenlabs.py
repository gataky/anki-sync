import os

from elevenlabs.client import ElevenLabs

from .base import BaseSynthesizer


class ElevenLabsSynthesizer(BaseSynthesizer):
    """ElevenLabs text-to-speech synthesizer implementation.

    Uses the ElevenLabs API to generate high-quality speech synthesis.
    Requires an ELEVENLABS_API_KEY environment variable to be set.
    """

    def __init__(self):
        """Initialize the ElevenLabs synthesizer.

        Creates a new ElevenLabs client using the API key from environment variables.
        """
        self.client = ElevenLabs(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
        )

    def synthesize(self, text: str, output_filename: str) -> None:
        """Synthesize text to speech using ElevenLabs.

        Args:
            text: The text to synthesize into speech
            output_filename: Where the audio file will be saved

        The audio file will be saved as {text}.mp3 in the output directory.
        Uses the multilingual v2 model with a standard Greek voice.
        """

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
