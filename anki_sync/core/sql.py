import itertools
import pathlib
import sqlite3
import time
from enum import Enum

import pandas as pd


class Table(Enum):
    NOTES = "notes"
    CARDS = "cards"
    REVLOG = "revlog"


class AnkiDatabase:

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.conn: sqlite3.Connection | None = None
        self.id_gen = itertools.count(int(time.time() * 1000))

        if self.path.is_file() is False:
            raise FileNotFoundError(f"file not found: {self.path.resolve()}")

        self.conn = sqlite3.connect(self.path.resolve())

    def __enter__(self) -> "AnkiDatabase":
        self.conn = sqlite3.connect(self.path.resolve())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type:
                self.conn.rollback()
            else:
                self.conn.commit()
            self.close()

    def close(self):
        if self.conn:
            self.conn.close()

    def get_notes(self) -> pd.DataFrame:
        return self._get_table(Table.NOTES)

    def get_cards(self) -> pd.DataFrame:
        return self._get_table(Table.CARDS)

    def get_cards_by_note_id(self, note_id: int) -> pd.DataFrame:
        query = "SELECT * FROM cards WHERE nid = ? ORDER BY ord"
        return self.execute(query, (note_id,))

    def get_revlog(self) -> pd.DataFrame:
        return self._get_table(Table.REVLOG)

    def get_revlog_by_card_id(self, card_id: int) -> pd.DataFrame:
        query = "SELECT * FROM revlog WHERE cid = ?"
        return self.execute(query, (card_id,))

    def get_note_id_by_guid(self, guid: str) -> tuple[int, bool]:
        """Will get the note id by guid.  If there is no note then we will generate one
        otherwise we'll return the existing note id.

        If we found an existing note id we will return true as the second return arg else false.
        This is used to know if we should populate the guid back to google sheets.
        """
        if guid == "":
            return next(self.id_gen), False

        query = "SELECT id FROM notes WHERE guid = ?"
        row = self.execute(query, (guid,))
        if len(row) == 0:
            return next(self.id_gen), False
        else:
            return row["id"].item(), True

    def _get_table(self, table: Table) -> pd.DataFrame:
        query = f"SELECT * FROM {table.value}"
        notes = self.execute(query)
        notes.set_index("id", inplace=True)
        return notes

    def execute(self, query, params=None) -> pd.DataFrame:
        return pd.read_sql(query, self.conn, params=params)
