import io
import logging
import os
from typing import cast

import pandas as pd

from anki_sync.core.anki import AnkiDeckManager
from anki_sync.core.gemini_client import GeminiClient
from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.models import VerbConjugation
from anki_sync.core.synthesizers.audio_synthesizer import AudioSynthesizer

# Configure basic logging for the script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


# --- Configuration ---
def process_verbs():
    logger.info("Starting Gemini API query script using GeminiClient...")
    sheets = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))
    client = GeminiClient()

    # Get verb data and format columns
    data = sheets.get_rows("Verbs")
    data["Learning"] = pd.to_numeric(data["Learning"])
    data["Processed"] = pd.to_numeric(data["Processed"])
    # I only want fields that I'm learning and haven't been processed yet.
    verbs = data[(data["Learning"] == 1) & (data["Processed"] != 1)]

    column_names = [
        "Conjugated",
        "English",
        "Greek Sentence",
        "English Sentence",
        "Tense",
        "Person",
        "Number",
    ]

    conjugated = []
    for i, verb in verbs.iterrows():
        lex: str = cast(str, verb["Greek"])

        resp = client.query(lex)
        csv_data_string = "\n".join(resp.split("\n")[1:-2])
        print(csv_data_string)
        print("=" * 100)
        csv_file_object = io.StringIO(csv_data_string)

        df = pd.read_csv(csv_file_object, header=None, names=column_names)
        df.insert(loc=0, column="Verb", value=lex)
        conjugated.append(df)

    all = pd.concat(conjugated)
    clean = all[all["Conjugated"] != "```"]

    clean.to_csv("output.csv")


def create_verb_deck():
    sheets = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))
    data = sheets.get_rows("Verbs Conjugated")
    synth = AudioSynthesizer("./media", "elevenlabs")

    anki = AnkiDeckManager()

    for i, verb in data.iterrows():
        v = VerbConjugation(**verb.to_dict())
        print(v.guid, verb["GUID"])
        verb["GUID"] = v.guid

        audio = v.get_audio()
        synth.synthesize_if_needed(audio.phrase, audio.filename)

        audio = v.get_example_audio()
        synth.synthesize_if_needed(audio.phrase, audio.filename)
        print("=" * 25)

    anki.create_verb_deck(data, "Greek Verbs", "verbs.apkg", "./media")


if __name__ == "__main__":
    create_verb_deck()
