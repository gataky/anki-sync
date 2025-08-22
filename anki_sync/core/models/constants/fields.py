"""Anki note field definitions."""

ANKI_NOTE_MODEL_FIELDS = [
    {"name": field["name"], "ord": idx}
    for idx, field in enumerate(
        [
            {"name": "english"},
            {"name": "greek"},
            {"name": "audio filename"},
            # -------------------------
            {"name": "part of speech"},
            {"name": "definitions"},
            {"name": "synonyms"},
            {"name": "antonyms"},
            {"name": "etymology"},
            {"name": "notes"},
        ]
    )
]
