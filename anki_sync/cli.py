import click

from .core.gsheets import GoogleSheetsManager
from .core.anki import AnkiDeckManager
from .core.word_processor import WordProcessor
from .core.synthesizers.audio_synthesizer import AudioSynthesizer
from .core.models import Word
from .core.stats import Stats


@click.group()
def main() -> None:
    """
    Anki-Sync: A CLI tool to synchronize words from Google Sheets to Anki.
    """
    pass


@main.command()
@click.option(
    "--sheet-id", required=True, envvar="GOOGLE_SHEET_ID", help="The ID of the Google Sheet."
)
@click.option(
    "--sheet-name",
    envvar="GOOGLE_SHEET_NAME",
    show_default=True,
    help="The name of the sheet/page containing the words.",
)
@click.option(
    "--deck-name",
    required=True,
    envvar="ANKI_DECK_NAME",
    help="The name of the Anki deck to create or update.",
)
@click.option(
    "--output-file",
    default="anki_sync_deck.apkg",
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
    help="Optional. Path to the directory containing sound files referenced in the sheet. If provided, sounds will be packaged.",
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
    sheet_name: str,
    deck_name: str,
    output_file: str,
    anki_audio_directory: str,
    synthesizer: str,
) -> None:
    """
    Fetches words from Google Sheets and creates an Anki package.
    """
    stats = Stats()

    try:
        audio_synthesizer = AudioSynthesizer(
            output_directory=anki_audio_directory,
            stats=stats,
            synthesizer_type=synthesizer
        )
        word_processor = WordProcessor(audio_synthesizer=audio_synthesizer)
        sheets_manager = GoogleSheetsManager(word_processor=word_processor, stats=stats)
        words: list[Word] = sheets_manager.get_words_from_sheet(sheet_id, sheet_name)

        if not words:
            click.secho(
                "No words fetched or an error occurred during fetching. Exiting.",
                fg="yellow",
            )
            return

        anki_manager = AnkiDeckManager()
        anki_manager.create_deck(words, deck_name, output_file, audio_directory=anki_audio_directory)

        # Print statistics summary
        stats.print_summary()

    except Exception as e:
        click.secho(
            f"An unexpected error occurred during the sync process: {e}",
            fg="red",
            err=True,
        )
        import traceback
        click.secho(
            traceback.format_exc(), fg="red", err=True
        )  # For more detailed debugging


if __name__ == "__main__":
    main()
