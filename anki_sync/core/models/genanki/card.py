import pandas as pd
from cached_property import cached_property

from anki_sync.core.sql import AnkiDatabase
from .rev import Rev


class Card:
    """Custom Card class that extends genanki.Card with additional functionality."""

    order = [
        "id",
        "nid",
        "did",
        "ord",
        "mod",
        "usn",
        "type",
        "queue",
        "due",
        "ivl",
        "factor",
        "reps",
        "lapses",
        "left",
        "odue",
        "odid",
        "flags",
        "data",
    ]

    def __init__(self, data: pd.DataFrame, old_db_conn: AnkiDatabase):
        data = data.to_dict()
        self.values = []
        for ord in self.order:
            self.values.append(data[ord])
        self.old_db_conn = old_db_conn
        self.id = data["id"]
        self._revlog = []

    @cached_property
    def revlog(self) -> list[Rev]:
        """Get revision log for this card."""
        revlog_data = self.old_db_conn.get_revlog_by_card_id(self.id)
        for idx, data in revlog_data.iterrows():
            self._revlog.append(Rev(data))
        return self._revlog

    def write_to_db(self, new_db_conn, deck_id):
        """Write the card to the database."""
        self.values[2] = deck_id
        new_db_conn.execute(
            "INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
            self.values,
        )

        for revlog in self.revlog:
            revlog.write_to_db(new_db_conn)
