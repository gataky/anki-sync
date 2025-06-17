import click

from .core.anki import AnkiDeckManager
from .core.gsheets import GoogleSheetsManager
from .core.models import Word, Verb # Added Verb
from .core.synthesizers.audio_synthesizer import AudioSynthesizer
from .core.word_processor import WordProcessor
from .core.verb_processor import VerbProcessor # Added VerbProcessor

@click.group()
def main() -> None:
    """Anki-Sync: A CLI tool to synchronize words from Google Sheets to Anki.

    This tool reads vocabulary data from a Google Sheet, processes it (including
    prepending articles and generating tags), optionally synthesizes audio for
    Greek words, and creates an Anki package (.apkg) file.
    """


@main.command(name="sync")
@click.option(
    "--sheet-id",
    required=True,
    envvar="GOOGLE_SHEET_ID",
    help="The ID of the Google Sheet containing 'Words' and 'Verbs' sheets.",
)
@click.option(
    "--deck-name",
    required=True,
    envvar="ANKI_DECK_NAME", # Changed from ANKI_DECK_NAME_COMBINED
    help="Name for the combined Anki deck.",
)
@click.option(
    "--output-file",
    default="anki_combined_deck.apkg", # Changed default
    show_default=True,
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    help="The path to save the generated Anki package (.apkg) file. Will be an absolute path.",
)
@click.option(
    "--anki-audio-directory",
    envvar="ANKI_AUDIO_DIRECTORY",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True
    ),
    help="Optional. Path to the directory for storing/finding sound files.",
)
@click.option(
    "--synthesizer",
    type=click.Choice(["elevenlabs", "google"]),
    default="elevenlabs",
    show_default=True,
    help="The text-to-speech synthesizer to use for generating audio.",
)
def sync(
    sheet_id: str,
    deck_name: str,
    output_file: str,
    anki_audio_directory: str | None,
    synthesizer: str,
) -> None:
    """Fetches words and verbs from a Google Sheet and creates a combined Anki package.

    This command:
    1. Reads data from 'Words' and 'Verbs' sheets in the specified Google Sheet.
    2. Processes items, generates tags, and synthesizes audio.
    3. Creates a single Anki package (.apkg) file with both words and verbs.

    All options can be set via environment variables or command-line arguments.
    Command-line arguments take precedence over environment variables.
    """
    WORDS_SHEET_NAME = "Words"  # Corrected typo
    VERBS_SHEET_NAME = "Verbs"  # Corrected typo

    audio_synthesizer = AudioSynthesizer(
        output_directory=anki_audio_directory,
        synthesizer_type=synthesizer,
    )

    words_data = []
    try:
        click.echo(f"Attempting to fetch words from sheet: '{WORDS_SHEET_NAME}'...")
        word_processor = WordProcessor(audio_synthesizer=audio_synthesizer)
        gsheets_manager_words = GoogleSheetsManager(sheet_id=sheet_id, item_processor=word_processor)
        words_data = gsheets_manager_words.get_items_from_sheet(WORDS_SHEET_NAME)
        click.echo(f"Fetched {len(words_data)} words from sheet '{WORDS_SHEET_NAME}'.")
    except Exception as e:
        click.secho(f"Could not fetch or process words from sheet '{WORDS_SHEET_NAME}'. Error: {e}", fg="yellow")

    verbs_data = []
    try:
        click.echo(f"Attempting to fetch verbs from sheet: '{VERBS_SHEET_NAME}'...")
        verb_processor = VerbProcessor(audio_synthesizer=audio_synthesizer)
        gsheets_manager_verbs = GoogleSheetsManager(sheet_id=sheet_id, item_processor=verb_processor)
        verbs_data = gsheets_manager_verbs.get_items_from_sheet(VERBS_SHEET_NAME)

        click.echo(f"Fetched {len(verbs_data)} verbs from sheet '{VERBS_SHEET_NAME}'.")
    except Exception as e:
        click.secho(f"Could not fetch or process verbs from sheet '{VERBS_SHEET_NAME}'. Error: {e}", fg="yellow")
        # verbs_data remains empty, process continues

    if not words_data and not verbs_data:
        click.secho("No data fetched for either words or verbs. Exiting.", fg="yellow")
        return

    anki_manager = AnkiDeckManager()
    anki_manager.create_combined_deck(
        deck_name=deck_name,
        output_file=output_file,
        words=words_data if words_data else None,
        verbs=verbs_data if verbs_data else None,
        audio_directory=anki_audio_directory,
    )
    click.secho(f"Combined deck '{deck_name}' created successfully at {output_file}", fg="green")


if __name__ == "__main__":
    main()
