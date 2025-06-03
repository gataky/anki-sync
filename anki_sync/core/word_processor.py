import os
from typing import Any, Optional, List, Dict, Tuple
from .models import Word
from anki_sync.utils.guid import generate_guid
from .audio_synthesizer import AudioSynthesizer

class WordProcessor:
    """Handles processing and transformation of word data."""

    GENDER_TO_ARTICLE_MAP = {
        "masculine": "ο",
        "feminine": "η",
        "neuter": "το",
        "masculine pl.": "οι",
        "feminine pl.": "οι",  # Note: feminine pl. is also οι
        "neuter pl.": "τα",
        None: "", # If there is no gender then return an empty string.
    }

    def __init__(self, audio_synthesizer: AudioSynthesizer):
        """Initialize the word processor.

        Args:
            audio_synthesizer: The AudioSynthesizer instance to use for audio synthesis
        """
        self.audio_synthesizer = audio_synthesizer

    def _process_guid_for_row(
        self, guid_cell_value: Any, row_idx: int, sheet_name: str
    ) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Processes the GUID for a row. Uses existing GUID or generates a new one."""
        guid_to_use = str(guid_cell_value or "").strip()
        guid_update_item = None
        if not guid_to_use:
            new_guid_value = generate_guid()
            guid_to_use = new_guid_value
            actual_sheet_row_num = row_idx + 2
            print(
                f"Info: Row {actual_sheet_row_num} in sheet '{sheet_name}' is missing GUID. Generated: {guid_to_use}"
            )
            guid_update_item = {
                "range": f"{sheet_name}!A{actual_sheet_row_num}",
                "values": [[guid_to_use]],
            }
        return guid_to_use, guid_update_item

    def _prefix_article_to_greek_word(
        self, original_greek_word: str, gender_string_for_article: str
    ) -> str:
        """Prefixes the correct Greek article to the Greek word based on gender."""
        processed_greek_word = original_greek_word
        if gender_string_for_article and original_greek_word:
            article = self.GENDER_TO_ARTICLE_MAP.get(gender_string_for_article, "")
            if article:
                processed_greek_word = f"{article} {original_greek_word}"
        return processed_greek_word

    def _compile_tags_for_word(
        self,
        raw_class: Optional[str],
        original_gender_from_sheet: Optional[str],
        hierarchical_tag_cells: List[Any],
    ) -> List[str]:
        """Compiles a list of tags from class, gender, and hierarchical columns."""
        tags_list = []
        class_tag_value = str(raw_class or "").strip()
        if class_tag_value:
            tags_list.append(f"class::{class_tag_value}".replace(" ", "\u00a0"))

        gender_tag_value = str(original_gender_from_sheet or "").strip()
        if gender_tag_value:
            gender_base_tag = gender_tag_value.split(" ")[0]
            tags_list.append(f"class::{gender_base_tag}".replace(" ", "\u00a0"))

        current_hierarchy_parts = []
        for cell_content_raw in hierarchical_tag_cells:
            cell_content = str(cell_content_raw or "").strip()
            if not cell_content:
                break
            current_hierarchy_parts.append(cell_content.replace(" ", "\u00a0"))
            tags_list.append("::".join(current_hierarchy_parts))
        return sorted(list(set(tags_list)))

    def process_row(
        self, padded_row: List[Any], row_idx: int, sheet_name: str
    ) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Processes a single row of data into a Word object and any necessary updates."""
        guid_to_use, guid_update_item = self._process_guid_for_row(
            padded_row[0], row_idx, sheet_name
        )

        raw_english = padded_row[1]
        original_greek_word = str(padded_row[2] or "").strip()
        raw_class = padded_row[3]
        original_gender_from_sheet = padded_row[4]

        gender_string_for_article = str(original_gender_from_sheet or "").strip().lower()
        processed_greek_word = self._prefix_article_to_greek_word(
            original_greek_word, gender_string_for_article
        )

        # Handle audio synthesis
        sound_filename = self.audio_synthesizer.generate_sound_filename(original_greek_word)
        if sound_filename:
            self.audio_synthesizer.synthesize_if_needed(processed_greek_word, sound_filename)

        hierarchical_tag_cells = padded_row[5:]
        tags = self._compile_tags_for_word(
            raw_class, original_gender_from_sheet, hierarchical_tag_cells
        )

        word_args = {
            "guid": guid_to_use,
            "english": raw_english or "",
            "greek": processed_greek_word,
            "word_class": raw_class or "",
            "gender": original_gender_from_sheet,
            "sound_file": sound_filename,
            "tags": tags,
        }

        if (
            not word_args["english"]
            or not original_greek_word
            or not word_args["word_class"]
        ):
            print(
                f"Skipping malformed row {row_idx + 2} (Sheet row): Missing essential data (English, Greek, or Class). Content: {padded_row[:6]}"
            )
            return None, guid_update_item

        return word_args, guid_update_item
