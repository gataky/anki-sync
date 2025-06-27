import sqlite3
import time

import genanki
import pandas as pd
from cached_property import cached_property

from anki_sync.utils.sql import AnkiDatabase

class Rev:
    order = ["id", "cid", "usn", "ease", "ivl", "lastIvl", "factor", "time", "type"]

    def __init__(self, data: pd.DataFrame):
        data = data.to_dict()
        self.values = []
        for ord in self.order:
            self.values.append(data[ord])

    def write_to_db(self, new_db_conn: sqlite3.Connection):
        new_db_conn.execute(
            "INSERT INTO revlog VALUES(?,?,?,?,?,?,?,?,?);", self.values
        )


class Card(genanki.Card):

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
        super().__init__(data["ord"], data["queue"])
        self.old_db_conn = old_db_conn
        self.id = data["id"]
        self._revlog = []

    @cached_property
    def revlog(self) -> Rev:
        revlog_data = self.old_db_conn.get_revlog_by_card_id(self.id)
        for idx, data in revlog_data.iterrows():
            self._revlog.append(Rev(data))
        return self._revlog

    def write_to_db(self, new_db_conn: sqlite3.Connection, deck_id):
        self.values[2] = deck_id
        new_db_conn.execute(
            "INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);",
            self.values,
        )

        for revlog in self.revlog:
            revlog.write_to_db(new_db_conn)


class Note(genanki.Note):

    def __init__(
        self,
        model=None,
        fields=None,
        sort_field=None,
        tags=None,
        guid=None,
        due=0,
        data="",
        id=None,
        old_db_conn=None,
    ):
        super().__init__(model, fields, sort_field, tags, guid, due)
        self.data = data
        self.id: int = id
        self.old_db_conn = old_db_conn

    @cached_property
    def cards(self) -> list[Card]:
        card_data = self.old_db_conn.get_cards_by_note_id(self.id)
        # if we can't find card data in the old database this means
        # we don't have a note generated in anki yet.  Let the normal
        # flow of genanki take over and create a new card
        if len(card_data) == 0:
            return self._front_back_cards()
        else:
            self._cards = []
            for idx, data in card_data.iterrows():
                self._cards.append(Card(data, self.old_db_conn))
            return self._cards

    def write_to_db(self, new_db_conn: sqlite3.Connection, *args):
        deck_id = args[1]
        self.fields = genanki.builtin_models._fix_deprecated_builtin_models_and_warn(
            self.model, self.fields
        )
        self._check_number_model_fields_matches_num_fields()
        self._check_invalid_html_tags_in_fields()

        new_db_conn.execute(
            "INSERT INTO notes VALUES(?,?,?,?,?,?,?,?,?,?,?);",
            (
                self.id,  # id
                self.guid,  # guid
                self.model.model_id,  # mid
                int(time.time()),  # mod
                -1,  # usn
                self._format_tags(),  # TODO tags
                self._format_fields(),  # flds
                self.sort_field,  # sfld
                0,  # csum, can be ignored
                0,  # flags
                self.data,  # data
            ),
        )

        for card in self.cards:
            card.write_to_db(new_db_conn, deck_id)

    def _front_back_cards(self):
        """Create Front/Back cards"""
        rv = []
        for card_ord, any_or_all, required_field_ords in self.model._req:
            op = {"any": any, "all": all}[any_or_all]
            if op(self.fields[ord_] for ord_ in required_field_ords):
                rv.append(genanki.Card(card_ord, self.old_db_conn))
        return rv

    def attach_anki_db(self, old_db_conn: AnkiDatabase):
        self.old_db_conn = old_db_conn
