"""
Adverb model for Greek adverbs.
"""

from anki_sync.core.models.simple_word import SimpleWord


class Adverb(SimpleWord):
    """Represents a Greek adverb."""
    
    def _get_word_type(self) -> str:
        return "adverb"
