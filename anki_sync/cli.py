import click

from .core.anki import AnkiDeckManager
from .core.gsheets import GoogleSheetsManager
from .core.models import Word
from .core.synthesizers.audio_synthesizer import AudioSynthesizer
from .core.word_processor import WordProcessor


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
    envvar="ANKI_DECK_NAME",  # Changed from ANKI_DECK_NAME_COMBINED
    help="Name for the combined Anki deck.",
)
@click.option(
    "--output-file",
    default="anki_combined_deck.apkg",  # Changed default
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
    WORDS_SHEET_NAME = "Words"

    audio_synthesizer = AudioSynthesizer(
        output_directory=anki_audio_directory,
        synthesizer_type=synthesizer,
    )

    words_data: list[Word] = []
    guid_updates_batch = []
    try:
        click.echo(f"Attempting to fetch words from sheet: '{WORDS_SHEET_NAME}'...")
        word_processor = WordProcessor(audio_synthesizer=audio_synthesizer)
        gsheets_manager_words = GoogleSheetsManager(sheet_id=sheet_id)
        rows = gsheets_manager_words.get_rows(WORDS_SHEET_NAME)

        for idx, row in rows.iterrows():
            item, guid_update = word_processor.process_row(row, WORDS_SHEET_NAME, idx)
            if guid_update:
                guid_updates_batch.append(guid_update)
            words_data.append(item)

        print(guid_updates_batch)
        gsheets_manager_words.batch_update(guid_updates_batch)

        click.echo(f"Fetched {len(rows)} words from sheet '{WORDS_SHEET_NAME}'.")
    except Exception as e:
        click.secho(
            f"Could not fetch or process words from sheet '{WORDS_SHEET_NAME}'. Error: {e}",
            fg="yellow",
        )

    anki_manager = AnkiDeckManager()
    anki_manager.create_word_deck(
        words=words_data,
        deck_name=deck_name,
        output_file=output_file,
        audio_directory=anki_audio_directory,
    )
    click.secho(
        f"Combined deck '{deck_name}' created successfully at {output_file}", fg="green"
    )


if __name__ == "__main__":
    main()
