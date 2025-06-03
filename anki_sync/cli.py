import click

from .core.gsheets import get_words_from_sheet
from .core.anki import create_anki_deck
from .core.models import Word


@click.group()
def main() -> None:
    """
    Anki-Sync: A CLI tool to synchronize words from Google Sheets to Anki.
    """
    pass


@main.command()
@click.option(
    "--sheet-id", required=True, envvar="SHEET_ID", help="The ID of the Google Sheet."
)
@click.option(
    "--sheet-name",
    default="Words",
    show_default=True,
    help="The name of the sheet/page containing the words.",
)
@click.option(
    "--deck-name",
    required=True,
    envvar="DECK_NAME",
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
    "--sound-dir",
    envvar="SOUND_DIR",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True
    ),
    help="Optional. Path to the directory containing sound files referenced in the sheet. If provided, sounds will be packaged.",
)
def sync(
    sheet_id: str, sheet_name: str, deck_name: str, output_file: str, sound_dir: str
) -> None:
    """
    Fetches words from Google Sheets and creates an Anki package.
    """
    click.echo("Starting sync process...")
    click.echo(f"  Google Sheet ID: {sheet_id}")
    click.echo(f"  Sheet Name: {sheet_name}")
    click.echo(f"  Anki Deck Name: {deck_name}")
    click.echo(f"  Output .apkg File: {output_file}")
    if sound_dir:
        click.echo(f"  Sound files directory: {sound_dir}")

    try:
        click.echo("Fetching words from Google Sheets...")
        words: list[Word] = get_words_from_sheet(sheet_id, sheet_name, sound_dir)
        if not words:
            click.secho(
                "No words fetched or an error occurred during fetching. Exiting.",
                fg="yellow",
            )
            return
        click.echo(f"Fetched {len(words)} words.")

        click.echo("Creating Anki deck...")
        create_anki_deck(words, deck_name, output_file, sound_files_dir=sound_dir)
        click.echo(f"Sync process completed. Anki package saved to {output_file}")
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
