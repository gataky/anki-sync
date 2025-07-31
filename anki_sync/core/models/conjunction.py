"""
Conjunction model for Greek conjunctions.
"""

from anki_sync.core.models.simple_word import SimpleWord


class Conjunction(SimpleWord):
    """Represents a Greek conjunction."""
    
    def _get_word_type(self) -> str:
        return "conjunction"
