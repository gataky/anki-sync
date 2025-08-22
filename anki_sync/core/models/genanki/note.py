import time
from typing import List

import genanki
import pandas as pd
from cached_property import cached_property

from anki_sync.core.sql import AnkiDatabase
from .card import Card


class Note(genanki.Note):
    """Custom Note class that extends genanki.Note with additional functionality."""

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
    def cards(self) -> List[Card]:
        """Get cards associated with this note."""
        if not self.old_db_conn:
            return []

        card_data = self.old_db_conn.get_cards_by_note_id(self.id)

        self._cards = []
        for idx, data in card_data.iterrows():
            self._cards.append(Card(data, self.old_db_conn))
        return self._cards

    def write_to_db(self, new_db_conn, *args):
        """Write the note to the database."""
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
        """Attach an Anki database connection to this note."""
        self.old_db_conn = old_db_conn
