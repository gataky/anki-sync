import click
import genanki

from anki_sync.config import get_config, load_config_from_env
from anki_sync.core.gsheets import GoogleSheetsManager
from anki_sync.core.models.genanki import Deck, DeckInfo
from anki_sync.core.models.word import (
    Adjective,
    Adverb,
    Conjunction,
    Noun,
    Preposition,
    Verb,
)
from anki_sync.core.sql import AnkiDatabase


@click.group()
def main() -> None:
    """Anki-Sync: A CLI tool to synchronize words from Google Sheets to Anki.

    This tool reads vocabulary data from a Google Sheet, processes it (including
    prepending articles and generating tags), optionally synthesizes audio for
    Greek words, and creates an Anki package (.apkg) file.
    """


@main.command(name="config")
def show_config() -> None:
    """Show current configuration."""
    load_config_from_env()
    config = get_config()
    config.print_config()


def get_deck_infos(synthesizer: str) -> list[DeckInfo]:
    """Create and return a list of DeckInfo objects."""
    return [
        DeckInfo(
            sheet="nouns",
            note_class=Noun,
            synthesizer=synthesizer,
        ),
        DeckInfo(
            sheet="verbs",
            note_class=Verb,
            synthesizer=synthesizer,
        ),
        DeckInfo(
            sheet="adjectives",
            note_class=Adjective,
            synthesizer=synthesizer,
        ),
        DeckInfo(
            sheet="adverbs",
            note_class=Adverb,
            synthesizer=synthesizer,
        ),
        DeckInfo(
            sheet="prepositions",
            note_class=Preposition,
            synthesizer=synthesizer,
        ),
        DeckInfo(
            sheet="conjunctions",
            note_class=Conjunction,
            synthesizer=synthesizer,
        ),
    ]


def process_decks(
    anki_db: AnkiDatabase,
    gsheets: GoogleSheetsManager,
    deck: Deck,
    decks: list[DeckInfo],
) -> list[dict]:
    """Process decks and return rows to update."""
    rows_to_update = []
    with click.progressbar(
        decks, label="Processing decks", item_show_func=lambda d: d.sheet if d else ""
    ) as bar:
        for deck_meta in bar:
            rtu = deck.generate(anki_db, gsheets, deck_meta)
            rows_to_update.extend(rtu)
    return rows_to_update


@main.command(name="sync")
def sync() -> None:
    """Sync command to synchronize data from Google Sheets to Anki."""
    load_config_from_env()
    config = get_config()

    if not config.validate():
        click.secho(
            "Configuration validation failed. Please check your environment variables.",
            fg="red",
        )
        return

    click.secho(f"USER           : {config.user}", fg="blue")
    click.secho(f"ANKI_PATH      : {config.anki_path}", fg="blue")
    click.secho(f"ANKI_DB_PATH   : {config.anki_db_path}", fg="blue")
    click.secho(f"ANKI_MEDIA_PATH: {config.anki_media_path}", fg="blue")

    decks = get_deck_infos(config.audio_synthesizer)
    gsheets = GoogleSheetsManager(config.google_sheet_id)
    deck = Deck("Greek", config.anki_media_path)
    package = genanki.Package(deck)

    with AnkiDatabase(config.anki_db_path) as anki_db:
        rows_to_update = process_decks(anki_db, gsheets, deck, decks)

        click.secho(f"writing package to {config.output_filename}", fg="yellow")
        package.media_files.extend(deck.audio_files)
        package.write_to_file(config.output_filename)

    if rows_to_update:
        click.secho("Updating sheets with missing GUIDs")
        gsheets.batch_update(rows_to_update)

    click.secho("Deck created successfully", fg="green")


if __name__ == "__main__":
    main()
