"""
Preposition model for Greek prepositions.
"""

from anki_sync.core.models.simple_word import SimpleWord


class Preposition(SimpleWord):
    """Represents a Greek preposition."""
    
    def _get_word_type(self) -> str:
        return "preposition"
