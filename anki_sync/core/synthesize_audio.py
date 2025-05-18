import os
try:
    from google.cloud import texttospeech
    from google.cloud.texttospeech_v1.types import SynthesizeSpeechResponse
except ImportError:
    texttospeech = None  # Handle gracefully if not installed
    SynthesizeSpeechResponse = None # Define for type hinting if needed, or handle client init

class Synthesize:
    def __init__(self):
        if not texttospeech:
            self.client = None
            print("TextToSpeech client not initialized: google-cloud-texttospeech library not found or failed to import.")
            return
        try:
            self.client: texttospeech.TextToSpeechClient = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Error initializing TextToSpeech client: {e}. Audio synthesis may not work.")
            self.client = None

    def text(self,
             text_to_synthesize: str,
             output_directory: str, # Expects the base directory like sound_dir
             language_code: str = "el-GR",
             language_name: str = "el-GR-Standard-B") -> bool:
        if not self.client or not output_directory or not text_to_synthesize:
            print(f"Synthesis skipped for '{text_to_synthesize}': Missing client, output directory, or text.")
            return False

        input_text = texttospeech.SynthesisInput(text=text_to_synthesize)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, name=language_name, ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        try:
            response: SynthesizeSpeechResponse = self.client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            # The filename is derived from the text_to_synthesize
            filepath = os.path.join(output_directory, f"{text_to_synthesize}.mp3")
            with open(filepath, "wb") as f:
                f.write(response.audio_content)
                print(f'++ Synthesized audio for: {text_to_synthesize} at {filepath}')
            return True
        except Exception as e:
            print(f"Error during speech synthesis for '{text_to_synthesize}': {e}")
            return False
