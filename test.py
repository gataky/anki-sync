import io
import logging
import os
import pathlib
from typing import cast

import genanki
import pandas as pd
from pandas._libs import pandas

from anki_sync.core.gemini_client import GeminiClient
from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.models.adjective import Adjective
from anki_sync.core.models.deck import Deck, DeckInfo
from anki_sync.core.models.noun import Noun
from anki_sync.core.models.verb import VerbConjugation
from anki_sync.core.synthesizers.audio_synthesizer import AudioSynthesizer
from anki_sync.utils.sql import AnkiDatabase

# Configure basic logging for the script
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Configuration ---
USER = "User 1"
ANKI_PATH = pathlib.Path(
    f"{os.environ.get("HOME")}/Library/Application Support/Anki2/{USER}"
)
ANKI_DB_PATH = pathlib.Path(os.path.join(ANKI_PATH, "collection.anki2"))
ANKI_MEDIA_PATH = pathlib.Path(os.path.join(ANKI_PATH, "collection.media"))


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


"""
1. Get notes from google sheets
2. Get notes from anki database

3. Match notes between the two gnote <-> anote
    a. match by GUID and fill gnote.id with anote.id

4. Organize into groups
    a. gnote | anote : notes exist in both locations
    b. gnote |   -   : note only exists in google sheets
    c.   -   | anote : note only exists in anki database
    d.   -   |   -   : n/a


4a. Cases when we have notes in both locations
    1. anki note has data field
        a. desired case, we can compare notes
    2. anki note missing data field
        a. we take google sheet note as source of truth
        b. copy data from google sheet note to anki note data field which should, on the
           next sync, behave like case 1

"""


def get_notes_from_google_sheets(
    sheet: str, source: str = "remote"
) -> pandas.DataFrame:
    if source == "remote":
        gsheet = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))
        data = gsheet.get_rows(sheet)
    else:
        data = pd.read_csv("./data/nouns.csv")
        data = data.drop(columns="Unnamed: 0")

    if sheet == "nouns":
        for col in ["tag", "sub tag 1", "sub tag 2"]:
            data[col] = data[col].fillna("")
    return data


def generate_deck(anki_db: AnkiDatabase, deck: Deck, deck_info: DeckInfo):
    gnotes = get_notes_from_google_sheets(deck_info.sheet, source="remote")

    synth = AudioSynthesizer(ANKI_MEDIA_PATH, deck_info.synthesizer)

    rows_to_update = []
    for row in gnotes.iterrows():
        gnote = deck_info.note_class.from_sheets(row)
        anote = gnote.to_note(anki_db)

        deck.add_audio(gnote.audio_filename)
        deck.add_note(anote)

        audio = gnote.get_audio_meta()
        synth.synthesize_if_needed(audio.phrase, audio.filename)

        if not gnote.exists_in_anki():
            cell = f"{deck_info.sheet}!{gnote._google_sheet_cell}"
            rows_to_update.append(
                {
                    "range": cell,
                    "values": [[gnote.guid]],
                }
            )

            print(f"new note found {gnote.guid}: {gnote.english} - {gnote.greek}")

    return rows_to_update


if __name__ == "__main__":
    sheets = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))

    ndi = DeckInfo(
        sheet="nouns",
        note_class=Noun,
    )
    vdi = DeckInfo(
        sheet="verbs conjugated",
        note_class=VerbConjugation,
    )
    adi = DeckInfo(
        sheet="adjectives",
        note_class=Adjective,
    )

    deck = Deck("Greek", ANKI_MEDIA_PATH)
    package = genanki.Package(deck)
    rows_to_update = []

    with AnkiDatabase(ANKI_DB_PATH) as anki_db:

        for deck_meta in [ndi, vdi, adi]:
            rtu = generate_deck(anki_db, deck, deck_meta)
            rows_to_update.extend(rtu)

        package.media_files.extend(deck.audio_files)
        package.write_to_file("greek.apkg")

    sheets.batch_update(rows_to_update)
