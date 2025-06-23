import sqlite3
import pathlib
import pandas as pd
from enum import Enum

from anki_sync.core.models.note import Note


class Table(Enum):
    NOTES = "notes"
    CARDS = "cards"
    REVLOG = "revlog"


class Database:

    def __init__(self, path: str):
        self.path: pathlib.Path = pathlib.Path(path)
        self.conn: sqlite3.Connection | None = None

        if not self.path.is_file():
            raise FileNotFoundError(f"file not found: {self.path.absolute()}")

    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.path.resolve())
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.conn.close()

    def get_notes(self) -> pd.DataFrame:
        return self._get_table(Table.NOTES)

    def set_note_data(self, note: Note):
        with self as conn:
            conn.execute(
                "UPDATE notes SET data = ? WHERE id = ?",
                (note.data, note.id)
            )

    def get_cards(self) -> pd.DataFrame:
        return self._get_table(Table.Table)

    def get_revlog(self) -> pd.DataFrame:
        return self._get_table(Table.REVLOG)

    def _get_table(self, table: Table) -> pd.DataFrame:
        with self as conn:
            notes = pd.read_sql(f"SELECT * FROM {table.value}", conn)
            notes.set_index("id", inplace=True)
        return notes
