import hashlib
import io
import logging
import os
import pathlib
from typing import cast

import genanki
import pandas as pd
from pandas._libs import pandas
import ankipandas as ap

from anki_sync.core.anki import AnkiDeckManager
from anki_sync.core.gemini_client import GeminiClient
from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.models.verb import VerbConjugation
from anki_sync.core.models.noun import Noun
from anki_sync.core.synthesizers.audio_synthesizer import AudioSynthesizer
from anki_sync.utils.sql import Database

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


class Deck(genanki.Deck):

    def __init__(self, deck_name: str, media_dir: str):
        deck_id = int(hashlib.md5(deck_name.encode("utf-8")).hexdigest(), 16) % (10**10)
        super().__init__(deck_id, deck_name)
        self.media_dir = media_dir
        self.audio_files = []

    def add_audio(self, audio_filename: str):
        path = os.path.join(self.media_dir, audio_filename)
        self.audio_files.append(path)


if __name__ == "__main__":
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
    # TODO
    db_path = pathlib.Path("/Users/jeffor/Library/Application Support/Anki2/User 1/collection.anki2")

    def get_notes_from_google_sheets(source="remote") -> pandas.DataFrame:
        if source == "remote":
            gsheet = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))
            data = gsheet.get_rows("nouns")
        else:
            data = pd.read_csv("gnotes.csv")
            data = data.drop(columns="Unnamed: 0")

        for col in ["tag", "sub tag 1", "sub tag 2"]:
            data[col] = data[col].fillna("")
        return data


    def get_notes_from_anki_database(source="remote") -> pandas.DataFrame:
        if source == "remote":
            # TODO
            db = Database(db_path)
            return db.get_notes()
        else:
            data = pd.read_csv("anotes.csv")
            data = data.set_index("id")

        return data


    def group_notes(gnotes: pandas.DataFrame, anotes: pandas.DataFrame) -> dict[str, set[str]]:

        gnote_guids: set[str] = set(gnotes["guid"])
        anote_guids: set[str] = set(anotes["guid"])

        in_both = gnote_guids.intersection(anote_guids)
        only_g = gnote_guids.difference(anote_guids)
        only_a = anote_guids.difference(gnote_guids)

        groupings = {
            "in_both": in_both,
            "only_google_sheets": only_g,
            "only_anki_database": only_a,
        }

        return groupings



    # gnotes = get_notes_from_google_sheets()
    # anotes = get_notes_from_anki_database()

    gnotes = get_notes_from_google_sheets()
    anotes = get_notes_from_anki_database()

    groups = group_notes(gnotes, anotes)

    # sync note id from anki to google sheet note.
    antoes_by_guid = anotes.reset_index().set_index("guid")
    gnotes_by_guid = gnotes.reset_index().set_index("guid")
    notes = []
    for guid in groups.get("in_both", {}):
        # get both notes by their guids
        gnote = gnotes_by_guid.loc[guid]
        anote = antoes_by_guid.loc[guid]

        # populate the google sheet note with the note id from anki
        g = Noun.from_sheets(gnote)
        g.id = int(anote.id)

        # create the anki note from the data field in the database
        a = Noun.from_ankidb(anote)

        notes.append((g, a))






    # deck = Deck("test", "/Users/jeff/Library/Application Support/Anki2/User 1/collection.media")
    # deck.add_audio(w1.audio_filename)
    # deck.add_note(n1)
    #
    # p = genanki.Package(deck)
    # p.media_files = deck.audio_files
    # p.write_to_file("./test.apkg")
