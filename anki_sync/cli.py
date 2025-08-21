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


@main.command(name="sync")
def sync() -> None:
    # Load configuration from environment
    load_config_from_env()
    config = get_config()

    # Validate configuration
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

    adje_di = DeckInfo(
        sheet="adjectives", note_class=Adjective, synthesizer=config.audio_synthesizer
    )
    aver_di = DeckInfo(
        sheet="adverbs", note_class=Adverb, synthesizer=config.audio_synthesizer
    )
    conj_di = DeckInfo(
        sheet="conjunctions",
        note_class=Conjunction,
        synthesizer=config.audio_synthesizer,
    )
    prep_di = DeckInfo(
        sheet="prepositions",
        note_class=Preposition,
        synthesizer=config.audio_synthesizer,
    )
    noun_di = DeckInfo(
        sheet="nouns", note_class=Noun, synthesizer=config.audio_synthesizer
    )
    verb_di = DeckInfo(
        sheet="verbs conjugated", note_class=Verb, synthesizer=config.audio_synthesizer
    )
    # decks = [noun_di, verb_di, adje_di, aver_di, prep_di, conj_di]
    decks = [noun_di]

    gsheets = GoogleSheetsManager(config.google_sheet_id)
    deck = Deck("Test", config.anki_media_path)
    package = genanki.Package(deck)
    rows_to_update = []

    with AnkiDatabase(config.anki_db_path) as anki_db:

        click.secho("processing sheet:", fg="yellow")
        for deck_meta in decks:
            click.secho(f"   * {deck_meta.sheet}", fg="yellow")
            rtu = deck.generate(anki_db, gsheets, deck_meta)
            rows_to_update.extend(rtu)

        click.secho(f"writing package to {config.output_filename}", fg="yellow")
        package.media_files.extend(deck.audio_files)
        package.write_to_file(config.output_filename)

    if len(rows_to_update) > 0:
        click.secho(f"updating sheets with missing guids")
        gsheets.batch_update(rows_to_update)

    click.secho(f"deck created successfully", fg="green")


if __name__ == "__main__":
    main()
