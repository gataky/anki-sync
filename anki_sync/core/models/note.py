import genanki

class Card(genanki.Card):
  def __init__(self, ord, suspend=False):
      self.ord = ord
      self.suspend = suspend

  def write_to_db(self, cursor, timestamp: float, deck_id, note_id, id_gen, due=0):
      queue = -1 if self.suspend else 0
      cursor.execute('INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);', (
          next(id_gen),    # id
          note_id,         # nid
          deck_id,         # did
          self.ord,        # ord
          int(timestamp),  # mod
          -1,              # usn
          0,               # type (=0 for non-Cloze)
          queue,           # queue
          due,             # due
          0,               # ivl
          0,               # factor
          0,               # reps
          0,               # lapses
          0,               # left
          0,               # odue
          0,               # odid
          0,               # flags
          "",              # data
      ))

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

    def _front_back_cards(self):
        """Create Front/Back cards"""
        rv = []
        for card_ord, any_or_all, required_field_ords in self.model._req:
            op = {'any': any, 'all': all}[any_or_all]
            if op(self.fields[ord_] for ord_ in required_field_ords):
                rv.append(Card(card_ord))
        return rv
