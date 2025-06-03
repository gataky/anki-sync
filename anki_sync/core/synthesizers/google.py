import os
from typing import Optional
from google.cloud import texttospeech
from google.cloud.texttospeech_v1.types import SynthesizeSpeechResponse
from .base import BaseSynthesizer

class GoogleSynthesizer(BaseSynthesizer):
    """Google Cloud text-to-speech synthesizer implementation."""

    def __init__(self):
        """Initialize the Google Cloud synthesizer."""
        if not texttospeech:
            self.client = None
            print("Google Cloud TTS library not found")
            return
        try:
            self.client: texttospeech.TextToSpeechClient = (
                texttospeech.TextToSpeechClient()
            )
        except Exception as e:
            print(f"Failed to initialize Google Cloud TTS: {e}")
            self.client = None

    def synthesize(self, text: str, output_directory: str) -> None:
        """Synthesize text to speech using Google Cloud TTS.

        Args:
            text: The text to synthesize
            output_directory: Directory where the audio file will be saved
        """
        if not (text and output_directory and self.client):
            return

        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="el-GR",
            name="el-GR-Standard-B",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        try:
            response: SynthesizeSpeechResponse = self.client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice,
                    "audio_config": audio_config,
                }
            )
            filepath = os.path.join(output_directory, f"{text}.mp3")
            with open(filepath, "wb") as f:
                f.write(response.audio_content)
        except Exception as e:
            print(f"Error synthesizing '{text}': {e}")
