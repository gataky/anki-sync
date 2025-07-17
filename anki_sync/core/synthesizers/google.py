from google.cloud import texttospeech
from google.cloud.texttospeech_v1.types import SynthesizeSpeechResponse

from .base import BaseSynthesizer


class GoogleSynthesizer(BaseSynthesizer):
    """Google Cloud text-to-speech synthesizer implementation.

    Uses Google Cloud Text-to-Speech API to generate speech synthesis.
    Requires Google Cloud credentials to be set up via GOOGLE_APPLICATION_CREDENTIALS.
    """

    def __init__(self):
        """Initialize the Google Cloud synthesizer.

        Creates a new Text-to-Speech client using Google Cloud credentials.
        Handles initialization errors gracefully and sets client to None if failed.
        """
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

    def synthesize(self, text: str, filepath: str) -> None:
        """Synthesize text to speech using Google Cloud TTS.

        Args:
            text: The text to synthesize into speech
            output_directory: Directory where the audio file will be saved

        The audio file will be saved as {text}.mp3 in the output directory.
        Uses a Greek female voice (el-GR-Standard-B) for synthesis.
        """
        if not (text and filepath and self.client):
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
            with open(filepath, "wb") as f:
                f.write(response.audio_content)
        except Exception as e:
            print(f"Error synthesizing '{text}': {e}")
