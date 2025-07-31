"""
Shared constants for Anki models.
"""

ANKI_SHARED_CSS = """
.card {
   font-family: arial;
   font-size: 20px;
   text-align: center;
   color: black;
   background-color: white;
}
.note_type {
    font-size:0.8em; color:grey;
}
table {
    margin-left: auto;
    margin-right: auto;
}
"""

# Basic word model fields (for simple word types)
BASIC_WORD_MODEL_FIELDS = [
    {"name": "english"},
    {"name": "greek"},
    {"name": "audio filename"},
]

# Basic word model templates
BASIC_WORD_MODEL_TEMPLATES = [
    {
        "name": "Card 1 (English to Greek)",
        "qfmt": "{{english}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{greek}}<br>{{audio filename}}',
    },
    {
        "name": "Card 2 (Greek to English)",
        "qfmt": "{{greek}}<br>{{audio filename}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{english}}',
    },
]

# Model IDs for different word types
MODEL_IDS = {
    "noun": 1607392322,
    "verb": 1607392321,
    "adjective": 1607392323,
    "adverb": 1607402323,
    "preposition": 1608405323,
    "conjunction": 1708405223,
} 