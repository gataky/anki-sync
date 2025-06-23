import genanki


class Note(genanki.Note):

    def __init__(self, model=None, fields=None, sort_field=None, tags=None, guid=None, due=0, data="", id=None):
        super().__init__(model, fields, sort_field, tags, guid, due)
        self.data = data
        self.id = id

    def write_to_db(self, cursor, timestamp: float, deck_id, id_gen):
        self.fields = genanki.builtin_models._fix_deprecated_builtin_models_and_warn(self.model, self.fields)
        self._check_number_model_fields_matches_num_fields()
        self._check_invalid_html_tags_in_fields()

        if self.id is None:
            next_id = next(id_gen)
        else:
            next_id = self.id

        cursor.execute('INSERT INTO notes VALUES(?,?,?,?,?,?,?,?,?,?,?);', (
            next_id,               # id
            self.guid,             # guid
            self.model.model_id,   # mid
            int(timestamp),        # mod
            -1,                    # usn
            self._format_tags(),   # TODO tags
            self._format_fields(), # flds
            self.sort_field,       # sfld
            0,                     # csum, can be ignored
            0,                     # flags
            self.data,             # data
        ))

        note_id = cursor.lastrowid
        for card in self.cards:
          card.write_to_db(cursor, timestamp, deck_id, note_id, id_gen, self.due)
