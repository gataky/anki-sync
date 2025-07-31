import os
import pathlib

import click
import genanki

from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.models.adjective import Adjective
from anki_sync.core.models.adverb import Adverb
from anki_sync.core.models.conjunction import Conjunction
from anki_sync.core.models.deck import Deck, DeckInfo
from anki_sync.core.models.noun import Noun
from anki_sync.core.models.preposition import Preposition
from anki_sync.core.models.verb import VerbConjugation
from anki_sync.core.sql import AnkiDatabase

# --- Configuration ---
USER = "User 1"
ANKI_PATH = pathlib.Path(
    f"{os.environ.get("HOME")}/Library/Application Support/Anki2/{USER}"
)
ANKI_DB_PATH = pathlib.Path(os.path.join(ANKI_PATH, "collection.anki2"))
ANKI_MEDIA_PATH = pathlib.Path(os.path.join(ANKI_PATH, "collection.media"))


@click.group()
def main() -> None:
    """Anki-Sync: A CLI tool to synchronize words from Google Sheets to Anki.

    This tool reads vocabulary data from a Google Sheet, processes it (including
    prepending articles and generating tags), optionally synthesizes audio for
    Greek words, and creates an Anki package (.apkg) file.
    """


@main.command(name="sync")
def sync() -> None:

    click.secho(f"USER           : {USER}", fg="blue")
    click.secho(f"ANKI_PATH      : {ANKI_PATH}", fg="blue")
    click.secho(f"ANKI_DB_PATH   : {ANKI_DB_PATH}", fg="blue")
    click.secho(f"ANKI_MEDIA_PATH: {ANKI_MEDIA_PATH}", fg="blue")

    noun_di = DeckInfo(sheet="nouns", note_class=Noun)
    verb_di = DeckInfo(sheet="verbs conjugated", note_class=VerbConjugation)
    adje_di = DeckInfo(sheet="adjectives", note_class=Adjective)
    aver_di = DeckInfo(sheet="adverbs", note_class=Adverb)
    prep_di = DeckInfo(sheet="prepositions", note_class=Preposition)
    conj_di = DeckInfo(sheet="conjunctions", note_class=Conjunction)
    decks = [noun_di, verb_di, adje_di, aver_di, prep_di, conj_di]

    gsheets = GoogleSheetsManager(os.environ.get("GOOGLE_SHEET_ID", ""))
    deck = Deck("Greek", ANKI_MEDIA_PATH)
    package = genanki.Package(deck)
    rows_to_update = []

    with AnkiDatabase(ANKI_DB_PATH) as anki_db:

        click.secho("processing sheet:", fg="yellow")
        for deck_meta in decks:
            click.secho(f"   * {deck_meta.sheet}", fg="yellow")
            rtu = deck.generate(anki_db, gsheets, deck_meta)
            rows_to_update.extend(rtu)

        click.secho(f"writing package to greek.apkg", fg="yellow")
        package.media_files.extend(deck.audio_files)
        package.write_to_file("greek.apkg")

    if len(rows_to_update) > 0:
        click.secho(f"updating sheets with missing guids")
        gsheets.batch_update(rows_to_update)

    click.secho(f"deck created successfully", fg="green")


if __name__ == "__main__":
    main()
