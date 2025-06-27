import time
import itertools
import pathlib
import sqlite3
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

        if not self.path.is_file():
            raise FileNotFoundError(f"file not found: {self.path.resolve()}")

        self.conn = sqlite3.connect(self.path.resolve())

    def __enter__(self) -> sqlite3.Connection:
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
        self.conn.close()

    def get_notes(self) -> pd.DataFrame:
        return self._get_table(Table.NOTES)

    def get_cards(self) -> pd.DataFrame:
        return self._get_table(Table.Table)

    def get_cards_by_note_id(self, note_id: int) -> pd.DataFrame:
        query = "SELECT * FROM cards WHERE nid = ? ORDER BY ord"
        return self.execute(query, (note_id,))

    def get_revlog(self) -> pd.DataFrame:
        return self._get_table(Table.REVLOG)

    def get_revlog_by_card_id(self, card_id: int) -> pd.DataFrame:
        query = "SELECT * FROM revlog WHERE cid = ?"
        return self.execute(query, (card_id,))

    def get_note_id_by_guid(self, guid: str) -> int:
        query = "SELECT id FROM notes WHERE guid = ?"
        row = self.execute(query, (guid,))
        if len(row) == 0:
            id = next(self.id_gen)
        else:
            id = row["id"].item()
        return id

    def _get_table(self, table: Table) -> pd.DataFrame:
        query = f"SELECT * FROM {table.value}"
        notes = self.execute(query)
        notes.set_index("id", inplace=True)
        return notes

    def execute(self, query, params=None) -> pd.DataFrame:
        return pd.read_sql(query, self.conn, params=params)
